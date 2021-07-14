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

import time

import responses
import requests
import uuid

import googlemaps
import googlemaps.client as _client
from . import TestCase
from googlemaps.client import _X_GOOG_MAPS_EXPERIENCE_ID


class ClientTest(TestCase):
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
            responses.add(
                responses.GET,
                "https://maps.googleapis.com/maps/api/geocode/json",
                body='{"status":"OK","results":[]}',
                status=200,
                content_type="application/json",
            )
        client = googlemaps.Client(
            key="AIzaasdf", queries_per_second=queries_per_second
        )
        start = time.time()
        for _ in query_range:
            client.geocode("Sesame St.")
        end = time.time()
        self.assertTrue(start + 1 < end < start + 2)

    @responses.activate
    def test_key_sent(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/geocode/json?"
            "key=AIzaasdf&address=Sesame+St.",
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_extra_params(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.", extra_params={"foo": "bar"})

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/geocode/json?"
            "key=AIzaasdf&address=Sesame+St.&foo=bar",
            responses.calls[0].request.url,
        )

    def test_hmac(self):
        """
        From http://en.wikipedia.org/wiki/Hash-based_message_authentication_code

        HMAC_SHA1("key", "The quick brown fox jumps over the lazy dog")
           = 0xde7c9b85b8b78aa6bc8a7a36f70a90701c9db4d9
        """

        message = "The quick brown fox jumps over the lazy dog"
        key = "a2V5"  # "key" -> base64
        signature = "3nybhbi3iqa8ino29wqQcBydtNk="

        self.assertEqual(signature, _client.sign_hmac(key, message))

    @responses.activate
    def test_url_signed(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = googlemaps.Client(client_id="foo", client_secret="a2V5")
        client.geocode("Sesame St.")

        self.assertEqual(1, len(responses.calls))

        # Check ordering of parameters.
        self.assertIn(
            "address=Sesame+St.&client=foo&signature", responses.calls[0].request.url
        )
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/geocode/json?"
            "address=Sesame+St.&client=foo&"
            "signature=fxbWUIcNPZSekVOhp2ul9LW5TpY=",
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_ua_sent(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

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

        responses.add_callback(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            content_type="application/json",
            callback=request_callback(),
        )

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

        self.assertEqual(2, len(responses.calls))
        self.assertEqual(responses.calls[0].request.url, responses.calls[1].request.url)

    @responses.activate
    def test_transport_error(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            status=404,
            content_type="application/json",
        )

        client = googlemaps.Client(key="AIzaasdf")
        with self.assertRaises(googlemaps.exceptions.HTTPError) as e:
            client.geocode("Foo")

        self.assertEqual(e.exception.status_code, 404)

    @responses.activate
    def test_host_override_on_init(self):
        responses.add(
            responses.GET,
            "https://foo.com/bar",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = googlemaps.Client(key="AIzaasdf", base_url="https://foo.com")
        client._get("/bar", {})

        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_host_override_per_request(self):
        responses.add(
            responses.GET,
            "https://foo.com/bar",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

        client = googlemaps.Client(key="AIzaasdf")
        client._get("/bar", {}, base_url="https://foo.com")

        self.assertEqual(1, len(responses.calls))

    @responses.activate
    def test_custom_extract(self):
        def custom_extract(resp):
            return resp.json()

        responses.add(
            responses.GET,
            "https://maps.googleapis.com/bar",
            body='{"error":"errormessage"}',
            status=403,
            content_type="application/json",
        )

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
                    return (500, {}, "Internal Server Error.")
                return (200, {}, '{"status":"OK","results":[]}')

        responses.add_callback(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            content_type="application/json",
            callback=request_callback(),
        )

        client = googlemaps.Client(key="AIzaasdf")
        client.geocode("Sesame St.")

        self.assertEqual(2, len(responses.calls))

    def test_invalid_channel(self):
        # Cf. limitations here:
        # https://developers.google.com/maps/premium/reports
        # /usage-reports#channels
        with self.assertRaises(ValueError):
            client = googlemaps.Client(
                client_id="foo", client_secret="a2V5", channel="auieauie$? "
            )

    def test_auth_url_with_channel(self):
        client = googlemaps.Client(
            key="AIzaasdf", client_id="foo", client_secret="a2V5", channel="MyChannel_1"
        )

        # Check ordering of parameters + signature.
        auth_url = client._generate_auth_url(
            "/test", {"param": "param"}, accepts_clientid=True
        )
        self.assertEqual(
            auth_url,
            "/test?param=param"
            "&channel=MyChannel_1"
            "&client=foo"
            "&signature=OH18GuQto_mEpxj99UimKskvo4k=",
        )

        # Check if added to requests to API with accepts_clientid=False
        auth_url = client._generate_auth_url(
            "/test", {"param": "param"}, accepts_clientid=False
        )
        self.assertEqual(auth_url, "/test?param=param&key=AIzaasdf")

    def test_requests_version(self):
        client_args_timeout = {
            "key": "AIzaasdf",
            "client_id": "foo",
            "client_secret": "a2V5",
            "channel": "MyChannel_1",
            "connect_timeout": 5,
            "read_timeout": 5,
        }
        client_args = client_args_timeout.copy()
        del client_args["connect_timeout"]
        del client_args["read_timeout"]

        requests.__version__ = "2.3.0"
        with self.assertRaises(NotImplementedError):
            googlemaps.Client(**client_args_timeout)
        googlemaps.Client(**client_args)

        requests.__version__ = "2.4.0"
        googlemaps.Client(**client_args_timeout)
        googlemaps.Client(**client_args)

    def test_single_experience_id(self):
        experience_id1 = "Exp1"
        client = googlemaps.Client(key="AIzaasdf", experience_id=experience_id1)
        self.assertEqual(experience_id1, client.get_experience_id())

        experience_id2 = "Exp2"
        client.set_experience_id(experience_id2)
        self.assertEqual(experience_id2, client.get_experience_id())

    def test_multiple_experience_id(self):
        client = googlemaps.Client(key="AIzaasdf")

        experience_id1 = "Exp1"
        experience_id2 = "Exp2"
        client.set_experience_id(experience_id1, experience_id2)

        result = "%s,%s" % (experience_id1, experience_id2)
        self.assertEqual(result, client.get_experience_id())

    def test_no_experience_id(self):
        client = googlemaps.Client(key="AIzaasdf")
        self.assertIsNone(client.get_experience_id())

    def test_clearing_experience_id(self):
        client = googlemaps.Client(key="AIzaasdf")
        client.set_experience_id("ExpId")
        client.clear_experience_id()
        self.assertIsNone(client.get_experience_id())

    def test_experience_id_sample(self):
        # [START maps_experience_id]
        experience_id = str(uuid.uuid4())

        # instantiate client with experience id
        client = googlemaps.Client(key="AIza-Maps-API-Key", experience_id=experience_id)

        # clear the current experience id
        client.clear_experience_id()

        # set a new experience id
        other_experience_id = str(uuid.uuid4())
        client.set_experience_id(experience_id, other_experience_id)

        # make API request, the client will set the header
        # X-GOOG-MAPS-EXPERIENCE-ID: experience_id,other_experience_id

        # get current experience id
        ids = client.get_experience_id()
        # [END maps_experience_id]

        result = "%s,%s" % (experience_id, other_experience_id)
        self.assertEqual(result, ids)

    @responses.activate
    def _perform_mock_request(self, experience_id=None):
        # Mock response
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            body='{"status":"OK","results":[]}',
            status=200,
            content_type="application/json",
        )

        # Perform network call
        client = googlemaps.Client(key="AIzaasdf")
        client.set_experience_id(experience_id)
        client.geocode("Sesame St.")
        return responses.calls[0].request

    def test_experience_id_in_header(self):
        experience_id = "Exp1"
        request = self._perform_mock_request(experience_id)
        header_value = request.headers[_X_GOOG_MAPS_EXPERIENCE_ID]
        self.assertEqual(experience_id, header_value)

    def test_experience_id_no_in_header(self):
        request = self._perform_mock_request()
        self.assertIsNone(request.headers.get(_X_GOOG_MAPS_EXPERIENCE_ID))

    @responses.activate
    def test_no_retry_over_query_limit(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/foo",
            body='{"status":"OVER_QUERY_LIMIT"}',
            status=200,
            content_type="application/json",
        )

        client = googlemaps.Client(key="AIzaasdf", retry_over_query_limit=False)

        with self.assertRaises(googlemaps.exceptions.ApiError):
            client._request("/foo", {})

        self.assertEqual(1, len(responses.calls))
