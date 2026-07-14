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

"""Tests for the airquality module."""

import json
import responses
import googlemaps
from . import TestCase


class AirQualityTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_air_quality_current_conditions(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{"indexes":[{"code":"uaqi","displayName":"Universal AQI","aqi":75}]}',
            status=200,
            content_type="application/json",
        )

        res = self.client.air_quality_current_conditions(
            location=(37.4, -122.1)
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertURLEqual(
            "https://airquality.googleapis.com/v1/currentConditions:lookup?key="
            + self.key,
            call.request.url,
        )

        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual(
            {"latitude": 37.4, "longitude": -122.1}, body["location"]
        )
        self.assertEqual(75, res["indexes"][0]["aqi"])

    @responses.activate
    def test_air_quality_extra_options(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{}',
            status=200,
            content_type="application/json",
        )

        self.client.air_quality_current_conditions(
            location=(37.4, -122.1),
            extra_computations=["HEALTH_RECOMMENDATIONS"],
            language_code="es",
            uaqi_color_palette="RED_GREEN",
        )

        call = responses.calls[0]
        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual(["HEALTH_RECOMMENDATIONS"], body["extraComputations"])
        self.assertEqual("es", body["languageCode"])
        self.assertEqual("RED_GREEN", body["uaqiColorPalette"])

    @responses.activate
    def test_air_quality_error_handling(self):
        responses.add(
            responses.POST,
            "https://airquality.googleapis.com/v1/currentConditions:lookup",
            body='{"error":{"status":"PERMISSION_DENIED","message":"Access denied"}}',
            status=403,
            content_type="application/json",
        )

        with self.assertRaises(googlemaps.exceptions.ApiError):
            self.client.air_quality_current_conditions(location=(37.4, -122.1))
