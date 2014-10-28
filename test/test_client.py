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


"""Tests for client module."""

import responses

import googlemaps
from googlemaps import client as _client
import test as _test

class ClientTest(_test.TestCase):

    def test_no_api_key(self):
        with self.assertRaises(Exception):
            client = googlemaps.Client()
            client.directions("Sydney", "Melbourne")

    def test_invalid_api_key(self):
        with self.assertRaises(Exception):
            client = googlemaps.Client(key="Invalid key.")
            client.directions("Sydney", "Melbourne")

    @responses.activate
    def test_key_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

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

        self.assertEqual(signature, _client.sign_hmac(key, message))

    @responses.activate
    def test_url_signed(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        client = googlemaps.Client(client_id="foo", client_secret="a2V5")
        client.geocode("Sesame St.")

        self.assertEqual(1, len(responses.calls))

        # Check ordering of parameters.
        self.assertIn("address=Sesame+St.&client=foo&signature",
                responses.calls[0].request.url)
        self.assertURLEqual("https://maps.googleapis.com/maps/api/geocode/json?"
                            "address=Sesame+St.&client=foo&"
                            "signature=fxbWUIcNPZSekVOhp2ul9LW5TpY=",
                            responses.calls[0].request.url)

    @responses.activate
    def test_ua_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

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

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

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

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

        self.assertEqual(2, len(responses.calls))