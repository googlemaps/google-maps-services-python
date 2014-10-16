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
Common functionality for modules in the googlemaps package, such as performing
HTTP requests.
"""

import base64
from datetime import datetime
from datetime import timedelta
import hashlib
import hmac
import requests

try: # Python 3
    from urllib.parse import urlencode
except ImportError: # Python 2
    from urllib import urlencode


_VERSION = "0.1"
_USER_AGENT = "GoogleGeoApiClientPython/%s" % _VERSION

class Context(object):
    """Holds state between requests, such as credentials (API key), timeout
    settings."""

    def __init__(self, key=None, client_id=None, client_secret=None,
                 timeout=None, connect_timeout=None, read_timeout=None,
                 retry_timeout=60):
        """
        :param key: Maps API key. Required, unless "client_id" and
            "client_secret" are set.
        :type key: basestring

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

        :param retry_timeout: Timeout across multiple retriable requests, in seconds.
        :type retry_timeout: int

        :param client_id: (for Maps API for Work customers) Your client ID.
        :type client_id: basestring

        :param client_secret: (for Maps API for Work customers) Your client
            secret (base64 encoded).
        :type client_secret: basestring

        :raises ValueError: when either credentials are missing, incomplete
            or invalid.
        :raises NotImplementedError: if connect_timeout and read_timeout are used
            with a version of requests prior to 2.4.0.
        """
        if not key and not (client_secret and client_id):
            raise ValueError("Must provide API key or enterprise credentials "
                             "with context object.")

        if key and not key.startswith("AIza"):
            raise ValueError("Invalid API key provided.")

        self.key = key

        if timeout and (connect_timeout or read_timeout):
            raise ValueError("Specify either timeout, or connect_timeout and read_timeout")

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

    def _auth_url(self, path, params):
        """Returns the path and query string portion of the request URL, first
        adding any necessary parameters.
        :param path: The path portion of the URL.
        :type path: basestring
        :param params: URL parameters.
        :type params: dict
        :rtype: basestring
        """
        if self.key:
            params["key"] = self.key
            return path + "?" + urlencode(params)

        if self.client_id and self.client_secret:
            params["client"] = self.client_id

            path = path + "?" + urlencode(params)
            sig = _hmac_sign(self.client_secret, path)
            return path + "&signature=" + sig

def _hmac_sign(secret, s):
    """Returns a basee64-encoded HMAC-SHA1 signature of a given string.
    :param secret: The key used for the signature, base64 encoded.
    :type secret: basestring
    :param s: The string.
    :type s: basestring
    :rtype: basestring
    """
    # Encode/decode from UTF-8. In Python 3, this converts to bytes and back;
    # in Python 2, it is a no-op.
    s = s.encode('utf-8')
    sig = hmac.new(base64.urlsafe_b64decode(secret), s, hashlib.sha1)
    out = base64.urlsafe_b64encode(sig.digest())
    return out.decode('utf-8')

def _get(ctx, url, params, first_request_time=None):
    """Performs HTTP GET request with credentials, returning the body as JSON.

    :param ctx: Shared context parameters.
    :type ctx: googlemaps.Context
    :param url: URL path for the request
    :type url: basestring
    :param params: HTTP GET parameters
    :type params: dict
    :param first_request_time: The time of the first request (None if no retries
            have occurred).
    :type first_request_time: datetime.datetime

    :raises ApiException: when the API returns an error.
    """

    if not first_request_time:
        first_request_time = datetime.now()

    # TODO(mdr-eng) implement back-off.
    if datetime.now() - first_request_time > ctx.retry_timeout:
        raise Exception("Timed out while retrying.")

    resp = requests.get(
        "https://maps.googleapis.com" + ctx._auth_url(url, params),
        headers={"User-Agent": _USER_AGENT},
        timeout=ctx.timeout,
        verify=True) # NOTE(cbro): verify SSL certs.

    if resp.status_code in [500, 503, 504]:
        # Retry request.
        return _get(ctx, url, params, first_request_time)

    if resp.status_code != 200:
        resp.raise_for_status() # raises a requests.exceptions.HTTPError

    body = resp.json()

    if body["status"] == "OK" or body["status"] == "ZERO_RESULTS":
        return body

    if body["status"] == "OVER_QUERY_LIMIT":
        # Retry request.
        return _get(ctx, url, params, first_request_time)

    if "error_message" in body:
        raise ApiError(body["status"], body["error_message"])
    else:
        raise ApiError(body["status"])


class ApiError(Exception):
    """Represents an exception returned by the remote API."""
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return self.status
        else:
            return "%s (%s)" % (self.status, self.message)

def _isstr(v):
    """Determines whether the passed value is a string, safe for 2/3.
    
    :param v: Object to check
    :type ctx: basestring or object
    """
    try:
        basestring
    except NameError:
        return isinstance(v, str)
    return isinstance(v, basestring)
