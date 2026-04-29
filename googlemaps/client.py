#
# Copyright 2014 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""
Core client functionality, common across all API requests (including performing
HTTP requests).
"""

import base64
import collections
import contextlib
import functools
import hashlib
import hmac
import logging
import math
import random
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests

import googlemaps
from googlemaps.cache import make_cache_key

logger = logging.getLogger(__name__)

_X_GOOG_MAPS_EXPERIENCE_ID = "X-Goog-Maps-Experience-ID"
_USER_AGENT = f"GoogleGeoApiClientPython/{googlemaps.__version__}"
_DEFAULT_BASE_URL = "https://maps.googleapis.com"

_RETRIABLE_STATUSES = {500, 503, 504}


class Client:
    """Performs requests to the Google Maps API web services."""

    def __init__(
        self,
        key=None,
        client_id=None,
        client_secret=None,
        timeout=None,
        connect_timeout=None,
        read_timeout=None,
        retry_timeout=60,
        requests_kwargs=None,
        queries_per_second=60,
        queries_per_minute=6000,
        channel=None,
        retry_over_query_limit=True,
        experience_id=None,
        requests_session=None,
        base_url=_DEFAULT_BASE_URL,
    ):
        """
        :param key: Maps API key. Required, unless "client_id" and
            "client_secret" are set. Most users should use an API key.
        :type key: string

        :param client_id: (for Maps API for Work customers) Your client ID.
            Most users should use an API key instead.
        :type client_id: string

        :param client_secret: (for Maps API for Work customers) Your client
            secret (base64 encoded). Most users should use an API key instead.
        :type client_secret: string

        :param channel: (for Maps API for Work customers) When set, a channel
            parameter with this value will be added to the requests.
            This can be used for tracking purpose.
            Can only be used with a Maps API client ID.
        :type channel: str

        :param timeout: Combined connect and read timeout for HTTP requests, in
            seconds. Specify "None" for no timeout.
        :type timeout: int

        :param connect_timeout: Connection timeout for HTTP requests, in
            seconds. You should specify read_timeout in addition to this option.
            Note that this requires requests >= 2.4.0.
        :type connect_timeout: int

        :param read_timeout: Read timeout for HTTP requests, in
            seconds. You should specify connect_timeout in addition to this
            option. Note that this requires requests >= 2.4.0.
        :type read_timeout: int

        :param retry_timeout: Timeout across multiple retriable requests, in
            seconds.
        :type retry_timeout: int

        :param queries_per_second: Number of queries per second permitted. Unset queries_per_minute to None. If set smaller number will be used.
            If the rate limit is reached, the client will sleep for the
            appropriate amount of time before it runs the current query.
        :type queries_per_second: int

        :param queries_per_minute: Number of queries per minute permitted. Unset queries_per_second to None. If set smaller number will be used.
            If the rate limit is reached, the client will sleep for the
            appropriate amount of time before it runs the current query.
        :type queries_per_minute: int

        :param retry_over_query_limit: If True, requests that result in a
            response indicating the query rate limit was exceeded will be
            retried. Defaults to True.
        :type retry_over_query_limit: bool

        :param experience_id: The value for the HTTP header field name
            'X-Goog-Maps-Experience-ID'.
        :type experience_id: str

        :raises ValueError: when either credentials are missing, incomplete
            or invalid.
        :raises NotImplementedError: if connect_timeout and read_timeout are
            used with a version of requests prior to 2.4.0.

        :param requests_kwargs: Extra keyword arguments for the requests
            library, which among other things allow for proxy auth to be
            implemented. See the official requests docs for more info:
            http://docs.python-requests.org/en/latest/api/#main-interface
        :type requests_kwargs: dict

        :param requests_session: Reused persistent session for flexibility.
        :type requests_session: requests.Session

        :param base_url: The base URL for all requests. Defaults to the Maps API
            server. Should not have a trailing slash.
        :type base_url: string

        """
        if not key and not (client_secret and client_id):
            raise ValueError("Must provide API key or enterprise credentials when creating client.")

        if key and not key.startswith("AIza"):
            raise ValueError("Invalid API key provided.")

        if channel and not re.match("^[a-zA-Z0-9._-]*$", channel):
            raise ValueError(
                "The channel argument must be an ASCII "
                "alphanumeric string. The period (.), underscore (_)"
                "and hyphen (-) characters are allowed. If used without "
                "client_id, it must be 0-999."
            )

        self.session = requests_session or requests.Session()
        self.key = key

        if timeout and (connect_timeout or read_timeout):
            raise ValueError("Specify either timeout, or connect_timeout and read_timeout")

        if connect_timeout and read_timeout:
            # Check that the version of requests is >= 2.4.0
            chunks = requests.__version__.split(".")
            if int(chunks[0]) < 2 or (int(chunks[0]) == 2 and int(chunks[1]) < 4):
                raise NotImplementedError("Connect/Read timeouts require requests v2.4.0 or higher")
            self.timeout = (connect_timeout, read_timeout)
        else:
            self.timeout = timeout

        self.client_id = client_id
        self.client_secret = client_secret
        self.channel = channel
        self.retry_timeout = timedelta(seconds=retry_timeout)
        self.requests_kwargs = requests_kwargs or {}
        headers = self.requests_kwargs.pop("headers", {})
        headers.update({"User-Agent": _USER_AGENT})
        self.requests_kwargs.update(
            {
                "headers": headers,
                "timeout": self.timeout,
                "verify": True,  # NOTE(cbro): verify SSL certs.
            }
        )

        self.queries_per_second = queries_per_second
        self.queries_per_minute = queries_per_minute
        qps_int = isinstance(queries_per_second, int) and not isinstance(queries_per_second, bool)
        qpm_int = isinstance(queries_per_minute, int) and not isinstance(queries_per_minute, bool)
        if qps_int and qpm_int:
            self.queries_quota = math.floor(min(queries_per_second, queries_per_minute / 60))
        elif qps_int and queries_per_second:
            self.queries_quota = math.floor(queries_per_second)
        elif qpm_int and queries_per_minute:
            self.queries_quota = math.floor(queries_per_minute / 60)
        else:
            raise ValueError(
                "Must provide a valid integer for queries_per_second or queries_per_minute."
            )
        logger.info("API queries_quota: %s", self.queries_quota)

        self.retry_over_query_limit = retry_over_query_limit
        self.sent_times = collections.deque(maxlen=self.queries_quota)
        self.set_experience_id(experience_id)
        self.base_url = base_url
        # Optional response cache; see googlemaps.cache.
        self.cache = None
        # Optional metrics collector; see googlemaps.metrics.
        self.metrics = None

    def set_experience_id(self, *experience_id_args):
        """Sets the value for the HTTP header field name
        'X-Goog-Maps-Experience-ID' to be used on subsequent API calls.

        :param experience_id_args: the experience ID
        :type experience_id_args: string varargs
        """
        if len(experience_id_args) == 0 or experience_id_args[0] is None:
            self.clear_experience_id()
            return

        headers = self.requests_kwargs.pop("headers", {})
        headers[_X_GOOG_MAPS_EXPERIENCE_ID] = ",".join(experience_id_args)
        self.requests_kwargs["headers"] = headers

    def get_experience_id(self):
        """Gets the experience ID for the HTTP header field name
        'X-Goog-Maps-Experience-ID'

        :return: The experience ID if set
        :rtype: str
        """
        headers = self.requests_kwargs.get("headers", {})
        return headers.get(_X_GOOG_MAPS_EXPERIENCE_ID, None)

    def clear_experience_id(self):
        """Clears the experience ID for the HTTP header field name
        'X-Goog-Maps-Experience-ID' if set.
        """
        headers = self.requests_kwargs.get("headers")
        if headers is None:
            return
        headers.pop(_X_GOOG_MAPS_EXPERIENCE_ID, {})
        self.requests_kwargs["headers"] = headers

    def _request(
        self,
        url,
        params,
        first_request_time=None,
        retry_counter=0,
        base_url=None,
        accepts_clientid=True,
        extract_body=None,
        requests_kwargs=None,
        post_json=None,
    ):
        """Performs HTTP GET/POST with credentials, returning the body as
        JSON.

        :param url: URL path for the request. Should begin with a slash.
        :type url: string

        :param params: HTTP GET parameters.
        :type params: dict or list of key/value tuples

        :param first_request_time: The time of the first request (None if no
            retries have occurred).
        :type first_request_time: datetime.datetime

        :param retry_counter: The number of this retry, or zero for first attempt.
        :type retry_counter: int

        :param base_url: The base URL for the request. Defaults to the Maps API
            server. Should not have a trailing slash.
        :type base_url: string

        :param accepts_clientid: Whether this call supports the client/signature
            params. Some APIs require API keys (e.g. Roads).
        :type accepts_clientid: bool

        :param extract_body: A function that extracts the body from the request.
            If the request was not successful, the function should raise a
            googlemaps.HTTPError or googlemaps.ApiError as appropriate.
        :type extract_body: function

        :param requests_kwargs: Same extra keywords arg for requests as per
            __init__, but provided here to allow overriding internally on a
            per-request basis.
        :type requests_kwargs: dict

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
            exceute a request.
        """

        if base_url is None:
            base_url = self.base_url

        if not first_request_time:
            first_request_time = datetime.now()

        elapsed = datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise googlemaps.exceptions.Timeout()

        # Cache lookup (GET-only, no extract_body override, only on first attempt
        # so retries don't double-count). The cache key intentionally excludes
        # auth params; see googlemaps.cache.make_cache_key.
        cache_key = None
        cacheable = (
            self.cache is not None
            and post_json is None
            and extract_body is None
            and retry_counter == 0
        )
        if cacheable:
            param_items = params.items() if isinstance(params, dict) else params
            cache_key = make_cache_key(url, param_items)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        if retry_counter > 0:
            # 0.5 * (1.5 ^ i) is an increased sleep time of 1.5x per iteration,
            # starting at 0.5s when retry_counter=0. The first retry will occur
            # at 1, so subtract that first.
            delay_seconds = 0.5 * 1.5 ** (retry_counter - 1)

            # Jitter this value by 50% and pause.
            time.sleep(delay_seconds * (random.random() + 0.5))

        authed_url = self._generate_auth_url(url, params, accepts_clientid)

        # Default to the client-level self.requests_kwargs, with method-level
        # requests_kwargs arg overriding.
        requests_kwargs = requests_kwargs or {}
        final_requests_kwargs = dict(self.requests_kwargs, **requests_kwargs)

        # Determine GET/POST.
        requests_method = self.session.get
        if post_json is not None:
            requests_method = self.session.post
            final_requests_kwargs["json"] = post_json

        try:
            response = requests_method(base_url + authed_url, **final_requests_kwargs)
        except requests.exceptions.Timeout as err:
            raise googlemaps.exceptions.Timeout() from err
        except Exception as e:
            raise googlemaps.exceptions.TransportError(e) from e

        if response.status_code in _RETRIABLE_STATUSES:
            # Retry request.
            return self._request(
                url,
                params,
                first_request_time,
                retry_counter + 1,
                base_url,
                accepts_clientid,
                extract_body,
                requests_kwargs,
                post_json,
            )

        # Check if the time of the nth previous query (where n is
        # queries_per_second) is under a second ago - if so, sleep for
        # the difference.
        if self.sent_times and len(self.sent_times) == self.queries_quota:
            elapsed_since_earliest = time.time() - self.sent_times[0]
            if elapsed_since_earliest < 1:
                time.sleep(1 - elapsed_since_earliest)

        try:
            result = extract_body(response) if extract_body else self._get_body(response)
            self.sent_times.append(time.time())
            if cacheable and cache_key is not None:
                self.cache.set(cache_key, result)
            return result
        except googlemaps.exceptions._RetriableRequest as e:
            if (
                isinstance(e, googlemaps.exceptions._OverQueryLimit)
                and not self.retry_over_query_limit
            ):
                raise

            # Retry request.
            return self._request(
                url,
                params,
                first_request_time,
                retry_counter + 1,
                base_url,
                accepts_clientid,
                extract_body,
                requests_kwargs,
                post_json,
            )

    def _get(self, *args, **kwargs):  # Backwards compatibility.
        return self._request(*args, **kwargs)

    def _get_body(self, response):
        if response.status_code != 200:
            raise googlemaps.exceptions.HTTPError(response.status_code)

        body = response.json()

        api_status = body["status"]
        if api_status in {"OK", "ZERO_RESULTS"}:
            return body

        if api_status == "OVER_QUERY_LIMIT":
            raise googlemaps.exceptions._OverQueryLimit(api_status, body.get("error_message"))

        raise googlemaps.exceptions.ApiError(api_status, body.get("error_message"))

    def _generate_auth_url(self, path, params, accepts_clientid):
        """Returns the path and query string portion of the request URL, first
        adding any necessary parameters.

        :param path: The path portion of the URL.
        :type path: string

        :param params: URL parameters.
        :type params: dict or list of key/value tuples

        :rtype: string

        """
        # Deterministic ordering through sorting by key.
        # Useful for tests, and in the future, any caching.
        extra_params = getattr(self, "_extra_params", None) or {}
        if isinstance(params, dict):
            params = sorted(dict(extra_params, **params).items())
        else:
            params = sorted(extra_params.items()) + params[:]  # Take a copy.

        if accepts_clientid and self.client_id and self.client_secret:
            if self.channel:
                params.append(("channel", self.channel))
            params.append(("client", self.client_id))

            path = "?".join([path, urlencode_params(params)])
            sig = sign_hmac(self.client_secret, path)
            return path + "&signature=" + sig

        if self.key:
            params.append(("key", self.key))
            return path + "?" + urlencode_params(params)

        raise ValueError(
            "Must provide API key for this API. It does not accept enterprise credentials."
        )


from googlemaps.addressvalidation import addressvalidation
from googlemaps.directions import directions
from googlemaps.distance_matrix import distance_matrix
from googlemaps.elevation import elevation, elevation_along_path
from googlemaps.geocoding import geocode, reverse_geocode
from googlemaps.geolocation import geolocate
from googlemaps.maps import static_map
from googlemaps.places import (
    find_place,
    place,
    places,
    places_autocomplete,
    places_autocomplete_query,
    places_nearby,
    places_photo,
)
from googlemaps.roads import nearest_roads, snap_to_roads, snapped_speed_limits, speed_limits
from googlemaps.timezone import timezone


def make_api_method(func):
    """
    Provides a single entry point for modifying all API methods.
    For now this is limited to allowing the client object to be modified
    with an `extra_params` keyword arg to each method, that is then used
    as the params for each web service request.

    Please note that this is an unsupported feature for advanced use only.
    It's also currently incompatibile with multiple threads, see GH #160.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args[0]._extra_params = kwargs.pop("extra_params", None)
        result = func(*args, **kwargs)
        with contextlib.suppress(AttributeError):
            del args[0]._extra_params
        return result

    return wrapper


Client.directions = make_api_method(directions)
Client.distance_matrix = make_api_method(distance_matrix)
Client.elevation = make_api_method(elevation)
Client.elevation_along_path = make_api_method(elevation_along_path)
Client.geocode = make_api_method(geocode)
Client.reverse_geocode = make_api_method(reverse_geocode)
Client.geolocate = make_api_method(geolocate)
Client.timezone = make_api_method(timezone)
Client.snap_to_roads = make_api_method(snap_to_roads)
Client.nearest_roads = make_api_method(nearest_roads)
Client.speed_limits = make_api_method(speed_limits)
Client.snapped_speed_limits = make_api_method(snapped_speed_limits)
Client.find_place = make_api_method(find_place)
Client.places = make_api_method(places)
Client.places_nearby = make_api_method(places_nearby)
Client.place = make_api_method(place)
Client.places_photo = make_api_method(places_photo)
Client.places_autocomplete = make_api_method(places_autocomplete)
Client.places_autocomplete_query = make_api_method(places_autocomplete_query)
Client.static_map = make_api_method(static_map)
Client.addressvalidation = make_api_method(addressvalidation)


def sign_hmac(secret, payload):
    """Returns a base64-encoded HMAC-SHA1 signature of a given string.

    :param secret: The key used for the signature, base64 encoded.
    :type secret: string

    :param payload: The payload to sign.
    :type payload: string

    :rtype: string
    """
    payload = payload.encode("ascii", "strict")
    secret = secret.encode("ascii", "strict")
    sig = hmac.new(base64.urlsafe_b64decode(secret), payload, hashlib.sha1)
    out = base64.urlsafe_b64encode(sig.digest())
    return out.decode("utf-8")


def urlencode_params(params):
    """URL encodes the parameters.

    :param params: The parameters
    :type params: list of key/value tuples.

    :rtype: string
    """
    # urlencode does not handle unicode strings in Python 2.
    # Firstly, normalize the values so they get encoded correctly.
    extended = []
    for key, val in params:
        if isinstance(val, (list, tuple)):
            for v in val:
                extended.append((key, normalize_for_urlencode(v)))
        else:
            extended.append((key, normalize_for_urlencode(val)))
    # Secondly, unquote unreserved chars which are incorrectly quoted
    # by urllib.urlencode, causing invalid auth signatures. See GH #72
    # for more info.
    return requests.utils.unquote_unreserved(urlencode(extended))


def normalize_for_urlencode(value):
    """Coerce a value into a ``str`` suitable for ``urllib.parse.urlencode``."""
    if isinstance(value, str):
        return value
    return normalize_for_urlencode(str(value))
