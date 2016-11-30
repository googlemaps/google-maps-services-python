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
import time

import googlemaps
from googlemaps import client as _client
import test as _test
import requests

class ClientTest(_test.TestCase):

    def test_no_api_key(self):
        with self.assertRaises(Exception):
            client = googlemaps.Client()
            client.directions("Sydney", "Melbourne")

    def test_invalid_api_key(self):
        with self.assertRaises(Exception):
            client = googlemaps.Client(key="Invalid key.")
            client.directions("Sydney", "Melbourne")

    def test_urlencode(self):
        # See GH #72.
        encoded_params = _client.urlencode_params([("address", "=Sydney ~")])
        self.assertEqual("address=%3DSydney+~", encoded_params)

    @responses.activate
    def test_queries_per_second(self):
        # This test assumes that the time to run a mocked query is
        # relatively small, eg a few milliseconds. We define a rate of
        # 3 queries per second, and run double that, which should take at
        # least 1 second but no more than 2.
        queries_per_second = 3
        query_range = range(queries_per_second * 2)
        for _ in query_range:
            responses.add(responses.GET,
                          "https://maps.googleapis.com/maps/api/geocode/json",
                          body='{"status":"OK","results":[]}',
                          status=200,
                          content_type="application/json")
        client = googlemaps.Client(key="AIzaasdf",
                                   queries_per_second=queries_per_second)
        start = time.time()
        for _ in query_range:
            client.geocode("Sesame St.")
        end = time.time()
        self.assertTrue(start + 1 < end < start + 2)

    @responses.activate
    def test_key_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type="application/json")

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://maps.googleapis.com/maps/api/geocode/json?"
                            "key=AIzaasdf&address=Sesame+St.",
                            responses.calls[0].request.url)

    @responses.activate
    def test_extra_params(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type="application/json")

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.", extra_params={"foo": "bar"})

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://maps.googleapis.com/maps/api/geocode/json?"
                            "key=AIzaasdf&address=Sesame+St.&foo=bar",
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
                      content_type="application/json")

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
                      content_type="application/json")

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
        self.assertEqual(responses.calls[0].request.url, responses.calls[1].request.url)

    @responses.activate
    def test_transport_error(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      status=404,
                      content_type='application/json')

        client = googlemaps.Client(key="AIzaasdf")
        with self.assertRaises(googlemaps.exceptions.HTTPError) as e:
            client.geocode("Foo")

        self.assertEqual(e.exception.status_code, 404)

    @responses.activate
    def test_host_override(self):
        responses.add(responses.GET,
                      "https://foo.com/bar",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type="application/json")

        client = googlemaps.Client(key="AIzaasdf")
        client._get("/bar", {}, base_url="https://foo.com")

        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_custom_extract(self):
        def custom_extract(resp):
            return resp.json()

        responses.add(responses.GET,
                      "https://maps.googleapis.com/bar",
                      body='{"error":"errormessage"}',
                      status=403,
                      content_type="application/json")

        client = googlemaps.Client(key="AIzaasdf")
        b = client._get("/bar", {}, extract_body=custom_extract)
        self.assertEqual(1, len(responses.calls))
        self.assertEqual("errormessage", b["error"])

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
                content_type="application/json",
                callback=request_callback())

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

        self.assertEqual(2, len(responses.calls))

    def test_channel_without_client_id(self):
        with self.assertRaises(ValueError):
            client = googlemaps.Client(key="AIzaasdf", channel="mychannel")

    def test_invalid_channel(self):
        # Cf. limitations here:
        # https://developers.google.com/maps/premium/reports
        # /usage-reports#channels
        with self.assertRaises(ValueError):
            client = googlemaps.Client(client_id="foo", client_secret="a2V5",
                                       channel="auieauie$? ")

    def test_auth_url_with_channel(self):
        client = googlemaps.Client(key="AIzaasdf",
                                   client_id="foo",
                                   client_secret="a2V5",
                                   channel="MyChannel_1")

        # Check ordering of parameters + signature.
        auth_url = client._generate_auth_url("/test",
                                             {"param": "param"},
                                             accepts_clientid=True)
        self.assertEqual(auth_url, "/test?param=param"
                            "&channel=MyChannel_1"
                            "&client=foo"
                            "&signature=OH18GuQto_mEpxj99UimKskvo4k=")

        # Check if added to requests to API with accepts_clientid=False
        auth_url = client._generate_auth_url("/test",
                                             {"param": "param"},
                                             accepts_clientid=False)
        self.assertEqual(auth_url, "/test?param=param&key=AIzaasdf")

    def test_requests_version(self):
        client_args_timeout = {
            "key": "AIzaasdf",
            "client_id": "foo",
            "client_secret": "a2V5",
            "channel": "MyChannel_1",
            "connect_timeout": 5,
            "read_timeout": 5
        }
        client_args = client_args_timeout.copy()
        del client_args["connect_timeout"]
        del client_args["read_timeout"]

        requests.__version__ = '2.3.0'
        with self.assertRaises(NotImplementedError):
            googlemaps.Client(**client_args_timeout)
        googlemaps.Client(**client_args)

        requests.__version__ = '2.4.0'
        googlemaps.Client(**client_args_timeout)
        googlemaps.Client(**client_args)
