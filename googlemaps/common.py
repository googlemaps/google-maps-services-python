"""
Common functionality for modules in the googlemaps package, such as performing
HTTP requests.
"""

import base64
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
                 timeout=None):
        """
        :param key: Maps API key. Required, unless "client_id" and
            "client_secret" are set.
        :type key: basestring

        :param timeout: Timeout for requests, in seconds.
        :type timeout: int

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
        self.timeout = timeout
        self.client_id = client_id
        self.client_secret = client_secret

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

def _get(ctx, url, params):
    """Performs HTTP GET request with credentials, returning the body as JSON.

    :param ctx: Shared context parameters.
    :type ctx: googlemaps.Context
    :param url: URL path for the request
    :type url: basestring
    :param params: HTTP GET parameters
    :type params: dict
    """

    # TODO(mdr-eng): implement rate limiting, retries, etc.
    # TODO(mdr-eng): add jitter (might not be necessary since most uses will be
    #       single threaded)
    resp = requests.get(
        "https://maps.googleapis.com" + ctx._auth_url(url, params),
        headers={"User-Agent": _USER_AGENT},
        verify=True) # NOTE(cbro): verify SSL certs.

    # TODO(mdr-eng): better error handling
    if resp.status_code != 200:
        raise Exception(
            "Unexpected response: [%d] %s" %
            (resp.status_code, resp.text))

    body = resp.json()

    if body["status"] == "OK" or body["status"] == "ZERO_RESULTS":
        return body

    # TODO(mdr-eng): use body["error_message"] if present.
    raise Exception("API error: %s" % body["status"])
