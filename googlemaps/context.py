import requests


class Context(object):

    def __init__(self, key, timeout=None):
        """
        :param key: Maps API key. Required, unless "client_id" and "client_secret" are set.
        :type key: basestring

        :param timeout: Timeout for requests, in seconds.
        :type timeout: int
        """
        # TODO(lukem): simple key validation.
        self.key = key
        self.timeout = timeout
