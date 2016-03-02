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
from datetime import datetime
from datetime import timedelta
import hashlib
import hmac
import requests
import random
import time

import googlemaps

try: # Python 3
    from urllib.parse import urlencode
except ImportError: # Python 2
    from urllib import urlencode


_USER_AGENT = "GoogleGeoApiClientPython/%s" % googlemaps.__version__
_DEFAULT_BASE_URL = "https://maps.googleapis.com"

_RETRIABLE_STATUSES = set([500, 503, 504])

class Client(object):
    """Performs requests to the Google Maps API web services."""

    def __init__(self, key=None, client_id=None, client_secret=None,
                 timeout=None, connect_timeout=None, read_timeout=None,
                 retry_timeout=60, requests_kwargs=None,
                 queries_per_second=10):
        """
        :param key: Maps API key. Required, unless "client_id" and
            "client_secret" are set.
        :type key: string

        :param client_id: (for Maps API for Work customers) Your client ID.
        :type client_id: string

        :param client_secret: (for Maps API for Work customers) Your client
            secret (base64 encoded).
        :type client_secret: string

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

        :param queries_per_second: Number of queries per second permitted.
            If the rate limit is reached, the client will sleep for the
            appropriate amount of time before it runs the current query.
        :type queries_per_second: int

        :raises ValueError: when either credentials are missing, incomplete
            or invalid.
        :raises NotImplementedError: if connect_timeout and read_timeout are
            used with a version of requests prior to 2.4.0.

        :param requests_kwargs: Extra keyword arguments for the requests
            library, which among other things allow for proxy auth to be
            implemented. See the official requests docs for more info:
            http://docs.python-requests.org/en/latest/api/#main-interface
        :type requests_kwargs: dict

        """
        if not key and not (client_secret and client_id):
            raise ValueError("Must provide API key or enterprise credentials "
                             "when creating client.")

        if key and not key.startswith("AIza"):
            raise ValueError("Invalid API key provided.")

        self.key = key

        if timeout and (connect_timeout or read_timeout):
            raise ValueError("Specify either timeout, or connect_timeout " +
                             "and read_timeout")

        if connect_timeout and read_timeout:
            # Check that the version of requests is >= 2.4.0
            chunks = requests.__version__.split(".")
            if chunks[0] < 2 or (chunks[0] == 2 and chunks[1] < 4):
                raise NotImplementedError("Connect/Read timeouts require "
                                          "requests v2.4.0 or higher")
            self.timeout = (connect_timeout, read_timeout)
        else:
            self.timeout = timeout

        self.client_id = client_id
        self.client_secret = client_secret
        self.retry_timeout = timedelta(seconds=retry_timeout)
        self.requests_kwargs = requests_kwargs or {}
        self.requests_kwargs.update({
            "headers": {"User-Agent": _USER_AGENT},
            "timeout": self.timeout,
            "verify": True,  # NOTE(cbro): verify SSL certs.
        })

        self.queries_per_second = queries_per_second
        self.sent_times = collections.deque("", queries_per_second)

    def _get(self, url, params, first_request_time=None, retry_counter=0,
             base_url=_DEFAULT_BASE_URL, accepts_clientid=True,
             extract_body=None, requests_kwargs=None):
        """Performs HTTP GET request with credentials, returning the body as
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

        if not first_request_time:
            first_request_time = datetime.now()

        elapsed = datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise googlemaps.exceptions.Timeout()

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
        requests_kwargs = dict(self.requests_kwargs, **(requests_kwargs or {}))
        try:
            resp = requests.get(base_url + authed_url, **requests_kwargs)
        except requests.exceptions.Timeout:
            raise googlemaps.exceptions.Timeout()
        except Exception as e:
            raise googlemaps.exceptions.TransportError(e)

        if resp.status_code in _RETRIABLE_STATUSES:
            # Retry request.
            return self._get(url, params, first_request_time, retry_counter + 1,
                             base_url, accepts_clientid, extract_body)

        # Check if the time of the nth previous query (where n is queries_per_second)
        # is under a second ago - if so, sleep for the difference.
        if self.sent_times and len(self.sent_times) == self.queries_per_second:
            elapsed_since_earliest = time.time() - self.sent_times[0]
            if elapsed_since_earliest < 1:
                time.sleep(1 - elapsed_since_earliest)

        try:
            if extract_body:
                result = extract_body(resp)
            else:
                result = self._get_body(resp)
            self.sent_times.append(time.time())
            return result
        except googlemaps.exceptions._RetriableRequest:
            # Retry request.
            return self._get(url, params, first_request_time, retry_counter + 1,
                             base_url, accepts_clientid, extract_body)

    def _get_body(self, resp):
        if resp.status_code != 200:
            raise googlemaps.exceptions.HTTPError(resp.status_code)

        body = resp.json()

        api_status = body["status"]
        if api_status == "OK" or api_status == "ZERO_RESULTS":
            return body

        if api_status == "OVER_QUERY_LIMIT":
            raise googlemaps.exceptions._RetriableRequest()

        if "error_message" in body:
            raise googlemaps.exceptions.ApiError(api_status,
                    body["error_message"])
        else:
            raise googlemaps.exceptions.ApiError(api_status)

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
        if type(params) is dict:
            params = sorted(params.items())
        else:
            params = params[:] # Take a copy.

        if accepts_clientid and self.client_id and self.client_secret:
            params.append(("client", self.client_id))

            path = "?".join([path, urlencode_params(params)])
            sig = sign_hmac(self.client_secret, path)
            return path + "&signature=" + sig

        if self.key:
            params.append(("key", self.key))
            return path + "?" + urlencode_params(params)

        raise ValueError("Must provide API key for this API. It does not accept "
                         "enterprise credentials.")


from googlemaps.directions import directions
from googlemaps.distance_matrix import distance_matrix
from googlemaps.elevation import elevation
from googlemaps.elevation import elevation_along_path
from googlemaps.geocoding import geocode
from googlemaps.geocoding import reverse_geocode
from googlemaps.timezone import timezone
from googlemaps.roads import snap_to_roads
from googlemaps.roads import speed_limits
from googlemaps.roads import snapped_speed_limits
from googlemaps.places import places
from googlemaps.places import places_nearby
from googlemaps.places import places_radar
from googlemaps.places import place
from googlemaps.places import places_photo
from googlemaps.places import places_autocomplete
from googlemaps.places import places_autocomplete_query

Client.directions = directions
Client.distance_matrix = distance_matrix
Client.elevation = elevation
Client.elevation_along_path = elevation_along_path
Client.geocode = geocode
Client.reverse_geocode = reverse_geocode
Client.timezone = timezone
Client.snap_to_roads = snap_to_roads
Client.speed_limits = speed_limits
Client.snapped_speed_limits = snapped_speed_limits
Client.places = places
Client.places_nearby = places_nearby
Client.places_radar = places_radar
Client.place = place
Client.places_photo = places_photo
Client.places_autocomplete = places_autocomplete
Client.places_autocomplete_query = places_autocomplete_query


def sign_hmac(secret, payload):
    """Returns a base64-encoded HMAC-SHA1 signature of a given string.

    :param secret: The key used for the signature, base64 encoded.
    :type secret: string

    :param payload: The payload to sign.
    :type payload: string

    :rtype: string
    """
    payload = payload.encode('ascii', 'strict')
    secret = secret.encode('ascii', 'strict')
    sig = hmac.new(base64.urlsafe_b64decode(secret), payload, hashlib.sha1)
    out = base64.urlsafe_b64encode(sig.digest())
    return out.decode('utf-8')


def urlencode_params(params):
    """URL encodes the parameters.

    :param params: The parameters
    :type params: list of key/value tuples.

    :rtype: string
    """
    # urlencode does not handle unicode strings in Python 2.
    # Firstly, normalize the values so they get encoded correctly.
    params = [(key, normalize_for_urlencode(val)) for key, val in params]
    # Secondly, unquote unreserved chars which are incorrectly quoted
    # by urllib.urlencode, causing invalid auth signatures. See GH #72
    # for more info.
    return requests.utils.unquote_unreserved(urlencode(params))


try:
    unicode
    # NOTE(cbro): `unicode` was removed in Python 3. In Python 3, NameError is
    # raised here, and caught below.

    def normalize_for_urlencode(value):
        """(Python 2) Converts the value to a `str` (raw bytes)."""
        if isinstance(value, unicode):
            return value.encode('utf8')

        if isinstance(value, str):
            return value

        return normalize_for_urlencode(str(value))

except NameError:
    def normalize_for_urlencode(value):
        """(Python 3) No-op."""
        # urlencode in Python 3 handles all the types we are passing it.
        return value
