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

"""Tests for the solar module."""

import responses
import googlemaps
from . import TestCase


class SolarTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_find_closest_building_insights(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/buildingInsights:findClosest",
            body='{"name":"buildings/123","center":{"latitude":37.4,"longitude":-122.1}}',
            status=200,
            content_type="application/json",
        )

        res = self.client.find_closest_building_insights(
            location=(37.4, -122.1), required_quality="HIGH"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://solar.googleapis.com/v1/buildingInsights:findClosest"
            "?location.latitude=37.4&location.longitude=-122.1"
            "&requiredQuality=HIGH&key=" + self.key,
            responses.calls[0].request.url,
        )
        self.assertEqual("buildings/123", res["name"])

    @responses.activate
    def test_get_solar_data_layers(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/dataLayers:get",
            body='{"imageryDate":{"year":2026,"month":1,"day":1}}',
            status=200,
            content_type="application/json",
        )

        res = self.client.get_solar_data_layers(
            location={"lat": 37.4, "lng": -122.1},
            radius_meters=50,
            view="FULL_LAYERS",
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://solar.googleapis.com/v1/dataLayers:get"
            "?location.latitude=37.4&location.longitude=-122.1"
            "&radiusMeters=50&view=FULL_LAYERS&key=" + self.key,
            responses.calls[0].request.url,
        )
        self.assertEqual(2026, res["imageryDate"]["year"])

    @responses.activate
    def test_solar_extra_options_and_errors(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/buildingInsights:findClosest",
            body='{"error":{"status":"NOT_FOUND","message":"Building not found"}}',
            status=404,
            content_type="application/json",
        )

        with self.assertRaises(googlemaps.exceptions.ApiError):
            self.client.find_closest_building_insights(
                location=(37.4, -122.1),
                exact_quality_required=True
            )

        call = responses.calls[0]
        self.assertURLEqual(
            "https://solar.googleapis.com/v1/buildingInsights:findClosest"
            "?location.latitude=37.4&location.longitude=-122.1"
            "&exactQualityRequired=true&key=" + self.key,
            call.request.url,
        )

    @responses.activate
    def test_get_solar_data_layers_extra_options(self):
        responses.add(
            responses.GET,
            "https://solar.googleapis.com/v1/dataLayers:get",
            body='{}',
            status=200,
            content_type="application/json",
        )

        self.client.get_solar_data_layers(
            location=(37.4, -122.1),
            radius_meters=100,
            required_quality="HIGH",
            exact_quality_required=True,
            pixel_size_meters=0.5,
        )

        call = responses.calls[0]
        self.assertURLEqual(
            "https://solar.googleapis.com/v1/dataLayers:get"
            "?location.latitude=37.4&location.longitude=-122.1"
            "&radiusMeters=100&requiredQuality=HIGH&exactQualityRequired=true"
            "&pixelSizeMeters=0.5&key=" + self.key,
            call.request.url,
        )
