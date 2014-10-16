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


"""Tests across modules (or common module)."""

import googlemaps
import unittest
from googlemaps import common
import test as _test

# NOTE: the current version of "responses" doesn't have request_callback.
# Use the master version until it's released.
import responses_master as responses
if not hasattr(responses, 'activate'): # Python 3.1+
    from responses_master import responses


class CommonTest(_test.TestCase):

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

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://maps.googleapis.com/maps/api/geocode/json?"
                            "key=AIzaasdf&address=Sesame+St.",
                            responses.calls[0].request.url)

    def test_hmac(self):
        """
        From http://en.wikipedia.org/wiki/Hash-based_message_authentication_code

        HMAC_SHA1("key", "The quick brown fox jumps over the lazy dog")
           = 0xde7c9b85b8b78aa6bc8a7a36f70a90701c9db4d9
        """

        message = "The quick brown fox jumps over the lazy dog"
        key = "a2V5" # "key" -> base64
        signature = "3nybhbi3iqa8ino29wqQcBydtNk="

        self.assertEqual(signature, common._hmac_sign(key, message))

    @responses.activate
    def test_url_signed(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        ctx = googlemaps.Context(client_id="foo", client_secret="a2V5")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://maps.googleapis.com/maps/api/geocode/json?"
                            "client=foo&address=Sesame+St.&"
                            "signature=Ao1r8ULP1g_vPwnf7Fvf2TSCYBQ=",
                            responses.calls[0].request.url)

    @responses.activate
    def test_ua_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        ctx = googlemaps.Context(key="AIzaasdf")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEqual(1, len(responses.calls))
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

        self.assertEqual(2, len(responses.calls))

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

        self.assertEqual(2, len(responses.calls))
