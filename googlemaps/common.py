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
import urllib


_VERSION = "0.1"
_USER_AGENT = "GoogleGeoApiClientPython/%s" % _VERSION

class Context(object):
    """Holds state between requests, such as credentials (API key), timeout
    settings"""

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
        :type connect_timeout: int

        :param read_timeout: Read timeout for HTTP requests, in
            seconds. You should specify connect_timeout in addition to this
            option.
        :type read_timeout: int

        :param retry_timeout: Timeout across multiple retriable requests, in seconds.
        :type retry_timeout: int

        :param client_id: (for Maps API for Work customers) Your client ID.
        :type client_id: basestring

        :param client_secret: (for Maps API for Work customers) Your client
            secret (base64 encoded).
        :type client_secret: basestring
        """
        if not key and not (client_secret and client_id):
            raise Exception("Must provide API key or enterprise credentials "
                            "with context object.")

        if key and not key.startswith("AIza"):
            raise Exception("Invalid API key provided.")

        self.key = key

        if timeout and (connect_timeout or read_timeout):
            raise ValueError("Specify either timeout, or connect_timeout and read_timeout")

        self.timeout = timeout or (connect_timeout, read_timeout)
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
            return path + "?" + urllib.urlencode(params)

        if self.client_id and self.client_secret:
            params["client"] = self.client_id

            path = path + "?" + urllib.urlencode(params)
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
    sig = hmac.new(base64.urlsafe_b64decode(secret), s, hashlib.sha1)
    return base64.urlsafe_b64encode(sig.digest())

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

    # TODO(mdr-eng): use body["error_message"] if present.
    raise Exception("API error: %s" % body["status"])
