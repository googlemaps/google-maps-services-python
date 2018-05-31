#
# Copyright 2015 Google Inc. All rights reserved.
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

"""Tests for the roads module."""


import responses

import googlemaps
import googlemaps.test as _test


class RoadsTest(_test.TestCase):

    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_snap(self):
        responses.add(responses.GET,
                      "https://roads.googleapis.com/v1/snapToRoads",
                      body='{"snappedPoints":["foo"]}',
                      status=200,
                      content_type="application/json")

        results = self.client.snap_to_roads((40.714728, -73.998672))
        self.assertEqual("foo", results[0])

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://roads.googleapis.com/v1/snapToRoads?"
                            "path=40.714728%%2C-73.998672&key=%s" % self.key,
                            responses.calls[0].request.url)

    @responses.activate
    def test_nearest_roads(self):
        responses.add(responses.GET,
                      "https://roads.googleapis.com/v1/nearestRoads",
                      body='{"snappedPoints":["foo"]}',
                      status=200,
                      content_type="application/json")

        results = self.client.nearest_roads((40.714728, -73.998672))
        self.assertEqual("foo", results[0])

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://roads.googleapis.com/v1/nearestRoads?"
                            "points=40.714728%%2C-73.998672&key=%s" % self.key,
                            responses.calls[0].request.url)

    @responses.activate
    def test_path(self):
        responses.add(responses.GET,
                      "https://roads.googleapis.com/v1/speedLimits",
                      body='{"speedLimits":["foo"]}',
                      status=200,
                      content_type="application/json")

        results = self.client.snapped_speed_limits([(1, 2),(3, 4)])
        self.assertEqual("foo", results["speedLimits"][0])

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://roads.googleapis.com/v1/speedLimits?"
                            "path=1%%2C2|3%%2C4"
                            "&key=%s" % self.key,
                            responses.calls[0].request.url)

    @responses.activate
    def test_speedlimits(self):
        responses.add(responses.GET,
                      "https://roads.googleapis.com/v1/speedLimits",
                      body='{"speedLimits":["foo"]}',
                      status=200,
                      content_type="application/json")

        results = self.client.speed_limits("id1")
        self.assertEqual("foo", results[0])
        self.assertEqual("https://roads.googleapis.com/v1/speedLimits?"
                         "placeId=id1&key=%s" % self.key,
                         responses.calls[0].request.url)

    @responses.activate
    def test_speedlimits_multiple(self):
        responses.add(responses.GET,
                      "https://roads.googleapis.com/v1/speedLimits",
                      body='{"speedLimits":["foo"]}',
                      status=200,
                      content_type="application/json")

        results = self.client.speed_limits(["id1", "id2", "id3"])
        self.assertEqual("foo", results[0])
        self.assertEqual("https://roads.googleapis.com/v1/speedLimits?"
                         "placeId=id1&placeId=id2&placeId=id3"
                         "&key=%s" % self.key,
                         responses.calls[0].request.url)

    def test_clientid_not_accepted(self):
        client = googlemaps.Client(client_id="asdf", client_secret="asdf")

        with self.assertRaises(ValueError):
            client.speed_limits("foo")

    @responses.activate
    def test_retry(self):
        class request_callback:
            def __init__(self):
                self.first_req = True

            def __call__(self, req):
                if self.first_req:
                    self.first_req = False
                    return (500, {}, 'Internal Server Error.')
                return (200, {}, '{"speedLimits":[]}')

        responses.add_callback(responses.GET,
                "https://roads.googleapis.com/v1/speedLimits",
                content_type="application/json",
                callback=request_callback())

        self.client.speed_limits([])

        self.assertEqual(2, len(responses.calls))
        self.assertEqual(responses.calls[0].request.url, responses.calls[1].request.url)
