##############################################################################
# Helper module that encapsulates the HTTPS request so that it can be used
# with multiple runtimes. PK Jan. 16
##############################################################################
import os
import urllib

global requests
requests=None
__all__=[requests]

import requests as requests_requests

# Google App Engine proxy
def _urlfetch_http_request(url, method, **kwds):
    from google.appengine.api import urlfetch
    import json

    method = method.upper()
    payload = None
    if 'data' in kwds:
        payload = kwds.get('data')
    elif 'params' in kwds and kwds['params']:
        qs = urllib.urlencode(kwds['params'])
        url += '?' + qs

    response = urlfetch.fetch(url,
        follow_redirects=True,
        method=method,
        payload=payload,
        validate_certificate=kwds.get('verify', None),
        headers=kwds.get('headers', {}),
        deadline=kwds.get('timeout', None)
    )

    response.ok = response.status_code >= 200 and response.status_code < 300
    response.text = response.content
    response.json = lambda: json.loads(response.content)
    return response

class URLFetchRequests(object):
    @staticmethod
    def get(url, params=None, **kwds):
        kwds['params'] = params
        return _urlfetch_http_request(url, 'GET',  **kwds)

    @staticmethod
    def delete(url, **kwds):
        return _urlfetch_http_request(url, 'DELETE',  **kwds)

    @staticmethod
    def head(url, **kwds):
        return _urlfetch_http_request(url, 'HEAD',  **kwds)

    @staticmethod
    def post(url, data=None, **kwds):
        kwds['data'] = data
        return _urlfetch_http_request(url, 'POST',  **kwds)

    @staticmethod
    def put(url, data=None, **kwds):
        kwds['data'] = data
        return _urlfetch_http_request(url, 'PUT',  **kwds)

    @staticmethod
    def patch(url, data=None, **kwds):
        kwds['data'] = data
        return _urlfetch_http_request(url, 'PATCH',  **kwds)

    utils = requests_requests.utils
    exceptions = requests_requests.exceptions

def _outer_http_request():
    # We use _is_appengine to cache the result of os.environ.get()
    # We do this closure so that _is_appengine is not a file scope variable
    ss = os.environ.get('SERVER_SOFTWARE')
    _is_appengine = (ss and (ss.startswith('Development/') or ss.startswith('Google App Engine/')))
    if _is_appengine:
        return URLFetchRequests
    else:
        return requests_requests
requests = _outer_http_request()
