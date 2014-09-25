"""Tests across modules (or common module)."""

import googlemaps
from googlemaps import common
import unittest
import urlparse

# NOTE: the current version of "sesponses" doesn't have request_callback.
# Use the master version until it's released.
import responses_master as responses


class CommonTest(unittest.TestCase):

    def test_no_api_key(self):
        with self.assertRaises(Exception):
            ctx = googlemaps.Context()
            googlemaps.directions(ctx, "Sydney", "Melbourne")

    def test_invalid_api_key(self):
        with self.assertRaises(Exception):
            ctx = googlemaps.Context(key="Invalid key.")
            googlemaps.directions(ctx, "Sydney", "Melbourne")

    @responses.activate
    def test_key_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        ctx = googlemaps.Context(key="AIzaasdf")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEquals(1, len(responses.calls))

        url = urlparse.urlparse(responses.calls[0].request.url)
        self.assertEquals("key=AIzaasdf&address=Sesame+St.", url.query)

    def test_hmac(self):
        """
        From http://en.wikipedia.org/wiki/Hash-based_message_authentication_code

        HMAC_SHA1("key", "The quick brown fox jumps over the lazy dog")
           = 0xde7c9b85b8b78aa6bc8a7a36f70a90701c9db4d9
        """

        message = "The quick brown fox jumps over the lazy dog"
        key = "a2V5" # "key" -> base64
        signature = "3nybhbi3iqa8ino29wqQcBydtNk="

        self.assertEquals(signature, common._hmac_sign(key, message))

    @responses.activate
    def test_url_signed(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        ctx = googlemaps.Context(client_id="foo", client_secret="a2V5")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEquals(1, len(responses.calls))

        url = urlparse.urlparse(responses.calls[0].request.url)
        expected = "client=foo&address=Sesame+St.&signature=Ao1r8ULP1g_vPwnf7Fvf2TSCYBQ="
        self.assertEquals(expected, url.query)

    @responses.activate
    def test_ua_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        ctx = googlemaps.Context(key="AIzaasdf")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEquals(1, len(responses.calls))
        user_agent = responses.calls[0].request.headers["User-Agent"]
        self.assertTrue(user_agent.startswith("GoogleGeoApiClientPython"))

    @responses.activate
    def test_retry(self):
        class request_callback:
            def __init__(self):
                self.first_req = True

            def __call__(self, req):
                if self.first_req:
                    self.first_req = False
                    return (200, {}, '{"status":"OVER_QUERY_LIMIT"}')
                return (200, {}, '{"status":"OK","results":[]}')

        responses.add_callback(responses.GET,
                "https://maps.googleapis.com/maps/api/geocode/json",
                content_type='application/json',
                callback=request_callback())

        ctx = googlemaps.Context(key="AIzaasdf")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEquals(2, len(responses.calls))

    @responses.activate
    def test_retry_intermittent(self):
        class request_callback:
            def __init__(self):
                self.first_req = True

            def __call__(self, req):
                if self.first_req:
                    self.first_req = False
                    return (500, {}, 'Internal Server Error.')
                return (200, {}, '{"status":"OK","results":[]}')

        responses.add_callback(responses.GET,
                "https://maps.googleapis.com/maps/api/geocode/json",
                content_type='application/json',
                callback=request_callback())

        ctx = googlemaps.Context(key="AIzaasdf")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEquals(2, len(responses.calls))
