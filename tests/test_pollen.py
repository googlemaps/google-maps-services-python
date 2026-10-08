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

"""Tests for the pollen module."""

import responses
import googlemaps
from . import TestCase


class PollenTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_pollen_forecast(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"dailyInfo":[{"date":{"year":2026,"month":7,"day":14}}]}',
            status=200,
            content_type="application/json",
        )

        res = self.client.pollen_forecast(
            location=(37.4, -122.1), days=3
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://pollen.googleapis.com/v1/forecast:lookup"
            "?location.latitude=37.4&location.longitude=-122.1"
            "&days=3&key=" + self.key,
            responses.calls[0].request.url,
        )
        self.assertEqual(2026, res["dailyInfo"][0]["date"]["year"])

    @responses.activate
    def test_pollen_extra_options(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{}',
            status=200,
            content_type="application/json",
        )

        self.client.pollen_forecast(
            location=(37.4, -122.1),
            days=5,
            language_code="ja",
            plants_description=True,
        )

        call = responses.calls[0]
        self.assertURLEqual(
            "https://pollen.googleapis.com/v1/forecast:lookup"
            "?location.latitude=37.4&location.longitude=-122.1"
            "&days=5&languageCode=ja&plantsDescription=true&key=" + self.key,
            call.request.url,
        )

    @responses.activate
    def test_pollen_error_handling(self):
        responses.add(
            responses.GET,
            "https://pollen.googleapis.com/v1/forecast:lookup",
            body='{"error":{"status":"INVALID_ARGUMENT","message":"Invalid days"}}',
            status=400,
            content_type="application/json",
        )

        with self.assertRaises(googlemaps.exceptions.ApiError):
            self.client.pollen_forecast(location=(37.4, -122.1))
