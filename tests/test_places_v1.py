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

"""Tests for the places_v1 module (Places API New)."""

import json
import responses
import googlemaps
from . import TestCase


class PlacesV1Test(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_places_search_text(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:searchText",
            body='{"places":[{"id":"123","displayName":{"text":"Spaghetti House"}}]}',
            status=200,
            content_type="application/json",
        )

        res = self.client.places_search_text(
            text_query="spaghetti in New York",
            fields=["places.id", "places.displayName"],
            open_now=True,
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertURLEqual(
            "https://places.googleapis.com/v1/places:searchText?key=" + self.key,
            call.request.url,
        )
        self.assertEqual("places.id,places.displayName", call.request.headers.get("X-Goog-FieldMask"))

        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual("spaghetti in New York", body["textQuery"])
        self.assertEqual(True, body["openNow"])
        self.assertEqual("123", res["places"][0]["id"])

    @responses.activate
    def test_places_search_nearby(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:searchNearby",
            body='{"places":[{"id":"456"}]}',
            status=200,
            content_type="application/json",
        )

        res = self.client.places_search_nearby(
            location=(37.7749, -122.4194),
            radius=500.0,
            included_types=["restaurant"],
            fields=["places.id"],
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertEqual("places.id", call.request.headers.get("X-Goog-FieldMask"))

        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual(["restaurant"], body["includedTypes"])
        self.assertEqual(
            {
                "circle": {
                    "center": {"latitude": 37.7749, "longitude": -122.4194},
                    "radius": 500.0,
                }
            },
            body["locationRestriction"],
        )
        self.assertEqual("456", res["places"][0]["id"])

    @responses.activate
    def test_place_v1_details(self):
        responses.add(
            responses.GET,
            "https://places.googleapis.com/v1/places/ChIJN1t_tDeuEmsRUsoyG83frY4",
            body='{"id":"ChIJN1t_tDeuEmsRUsoyG83frY4","formattedAddress":"1600 Amphitheatre Pkwy"}',
            status=200,
            content_type="application/json",
        )

        res = self.client.place_v1(
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
            fields=["id", "formattedAddress"],
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertURLEqual(
            "https://places.googleapis.com/v1/places/ChIJN1t_tDeuEmsRUsoyG83frY4?key="
            + self.key,
            call.request.url,
        )
        self.assertEqual("id,formattedAddress", call.request.headers.get("X-Goog-FieldMask"))
        self.assertEqual("1600 Amphitheatre Pkwy", res["formattedAddress"])

    @responses.activate
    def test_places_autocomplete_v1(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:autocomplete",
            body='{"suggestions":[{"placePrediction":{"place":"places/123","text":{"text":"Pizza"}}}]}',
            status=200,
            content_type="application/json",
        )

        res = self.client.places_autocomplete_v1(
            input_text="Piz",
            language_code="en",
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual("Piz", body["input"])
        self.assertEqual("en", body["languageCode"])

    @responses.activate
    def test_place_photo_v1(self):
        responses.add(
            responses.GET,
            "https://places.googleapis.com/v1/places/123/photos/456/media",
            body='{"name":"places/123/photos/456/media","photoUri":"https://lh3.googleusercontent.com/..."}',
            status=200,
            content_type="application/json",
        )

        res = self.client.place_photo_v1(
            name="places/123/photos/456",
            max_width_px=400,
            skip_http_redirect=True,
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertURLEqual(
            "https://places.googleapis.com/v1/places/123/photos/456/media"
            "?maxWidthPx=400&skipHttpRedirect=true&key=" + self.key,
            call.request.url,
        )

    @responses.activate
    def test_places_v1_error_handling(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:searchText",
            body='{"error":{"status":"INVALID_ARGUMENT","message":"Invalid query"}}',
            status=400,
            content_type="application/json",
        )

        with self.assertRaises(googlemaps.exceptions.ApiError) as cm:
            self.client.places_search_text(text_query="invalid")
        self.assertEqual("INVALID_ARGUMENT", cm.exception.status)

    @responses.activate
    def test_places_v1_http_error(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:searchText",
            body='Not Found',
            status=404,
            content_type="text/plain",
        )

        with self.assertRaises(googlemaps.exceptions.HTTPError):
            self.client.places_search_text(text_query="test")

    @responses.activate
    def test_places_search_text_full_options(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:searchText",
            body='{"places":[]}',
            status=200,
            content_type="application/json",
        )

        self.client.places_search_text(
            text_query="pizza",
            included_type="restaurant",
            location_bias={"circle": {"center": {"latitude": 37.7, "longitude": -122.4}, "radius": 100}},
            location_restriction={"rectangle": {"low": {"latitude": 37.7, "longitude": -122.4}, "high": {"latitude": 37.8, "longitude": -122.3}}},
            min_rating=4.5,
            price_levels=["PRICE_LEVEL_MODERATE"],
            max_result_count=10,
            language_code="en",
            region_code="us",
        )

        call = responses.calls[0]
        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual("restaurant", body["includedType"])
        self.assertEqual(4.5, body["minRating"])
        self.assertEqual(["PRICE_LEVEL_MODERATE"], body["priceLevels"])
        self.assertEqual(10, body["maxResultCount"])

    @responses.activate
    def test_places_search_nearby_full_options(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:searchNearby",
            body='{"places":[]}',
            status=200,
            content_type="application/json",
        )

        self.client.places_search_nearby(
            location=(37.7, -122.4),
            radius=1000,
            excluded_types=["bar"],
            max_result_count=5,
            language_code="fr",
            region_code="fr",
        )

        call = responses.calls[0]
        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual(["bar"], body["excludedTypes"])
        self.assertEqual("fr", body["languageCode"])

    @responses.activate
    def test_place_v1_details_with_language(self):
        responses.add(
            responses.GET,
            "https://places.googleapis.com/v1/places/123",
            body='{"id":"123"}',
            status=200,
            content_type="application/json",
        )

        self.client.place_v1(place_id="123", language_code="es", region_code="es")
        call = responses.calls[0]
        self.assertURLEqual(
            "https://places.googleapis.com/v1/places/123?languageCode=es&regionCode=es&key=" + self.key,
            call.request.url,
        )

    @responses.activate
    def test_places_autocomplete_v1_full_options(self):
        responses.add(
            responses.POST,
            "https://places.googleapis.com/v1/places:autocomplete",
            body='{"suggestions":[]}',
            status=200,
            content_type="application/json",
        )

        self.client.places_autocomplete_v1(
            input_text="Piz",
            location_bias={"circle": {"center": {"latitude": 37.7, "longitude": -122.4}, "radius": 100}},
            location_restriction={"circle": {"center": {"latitude": 37.7, "longitude": -122.4}, "radius": 500}},
            included_primary_types=["restaurant"],
            included_region_codes=["us"],
            region_code="us",
            session_token="token123",
            offset=3,
        )

        call = responses.calls[0]
        body = json.loads(call.request.body.decode("utf-8"))
        self.assertEqual("restaurant", body["includedPrimaryTypes"][0])
        self.assertEqual("token123", body["sessionToken"])
        self.assertEqual(3, body["offset"])

    @responses.activate
    def test_place_photo_v1_max_height(self):
        responses.add(
            responses.GET,
            "https://places.googleapis.com/v1/places/123/photos/456/media",
            body='{}',
            status=200,
            content_type="application/json",
        )

        self.client.place_photo_v1("123/photos/456", max_height_px=600)
        call = responses.calls[0]
        self.assertURLEqual(
            "https://places.googleapis.com/v1/places/123/photos/456/media?maxHeightPx=600&key=" + self.key,
            call.request.url,
        )
