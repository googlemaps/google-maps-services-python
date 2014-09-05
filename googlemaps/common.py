import requests

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
