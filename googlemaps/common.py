"""
Common functionality for modules in the googlemaps package, such as performing
HTTP requests.
"""

import requests


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
        if not key.startswith("AIza"):
            raise Exception("Must provide API key or enterprise credentials "
                            "with context object.")

        self.key = key
        self.timeout = timeout
        self.client_id = client_id
        self.client_secret = client_secret

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
    # TODO(mdr-eng): implement enterprise key signing
    # TODO(mdr-eng): add jitter (might not be necessary since most uses will be
    #       single threaded)
    params["key"] = ctx.key
    resp = requests.get(
        "https://maps.googleapis.com" + url,
        verify=True, # NOTE(cbro): verify SSL certs.
        params=params)

    # TODO(mdr-eng): better error handling
    if resp.status_code != 200:
        raise Exception(
            "Unexpected response: [%d] %s" %
            (resp.status_code, resp.text))

    body = resp.json()

    # TODO(mdr-eng): NOT_FOUND for directions?
    if body["status"] == "OK" or body["status"] == "NO_RESULTS":
        return body

    # TODO(mdr-eng): use body["error_message"] if present.
    raise Exception("API error: %s" % body["status"])
