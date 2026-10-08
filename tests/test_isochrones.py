# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the isochrones module (Isochrones API)."""

import json
import responses
import googlemaps
from . import TestCase


class IsochronesTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_generate_isochrones(self):
        responses.add(
            responses.POST,
            "https://isochrones.googleapis.com/v1/isochrones:generate",
            body='{"isochrone":{"geoJson":{"type":"MultiPolygon","coordinates":[]}}}',
            status=200,
            content_type="application/json",
        )

        res = self.client.generate_isochrones(
            location=(37.7749, -122.4194),
            travel_mode="DRIVE",
            duration_seconds=900,
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertURLEqual(
            "https://isochrones.googleapis.com/v1/isochrones:generate?key=" + self.key,
            call.request.url,
        )

        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual("DRIVE", body["travelMode"])
        self.assertEqual("FROM", body["travelDirection"])
        self.assertEqual({"latitude": 37.7749, "longitude": -122.4194}, body["location"])
        self.assertEqual("900s", body["travelDuration"])

    @responses.activate
    def test_generate_isochrones_distance_and_routing_pref(self):
        responses.add(
            responses.POST,
            "https://isochrones.googleapis.com/v1/isochrones:generate",
            body='{"isochrone":{}}',
            status=200,
            content_type="application/json",
        )

        self.client.generate_isochrones(
            location=(37.7749, -122.4194),
            travel_mode="WALK",
            travel_direction="TO",
            duration_seconds=600,
            routing_preference="TRAFFIC_AWARE",
        )

        call = responses.calls[0]
        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual("WALK", body["travelMode"])
        self.assertEqual("TO", body["travelDirection"])
        self.assertEqual("600s", body["travelDuration"])
        self.assertEqual("TRAFFIC_AWARE", body["routingPreference"])

    @responses.activate
    def test_isochrones_error_handling(self):
        responses.add(
            responses.POST,
            "https://isochrones.googleapis.com/v1/isochrones:generate",
            body='{"error":{"status":"INVALID_ARGUMENT","message":"Invalid duration"}}',
            status=400,
            content_type="application/json",
        )

        with self.assertRaises(googlemaps.exceptions.ApiError):
            self.client.generate_isochrones(location=(37.7749, -122.4194))
