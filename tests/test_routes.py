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

"""Tests for the routes module."""

import json
import responses
import googlemaps
from . import TestCase

class RoutesTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_compute_routes_simple(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes":[]}',
            status=200,
            content_type="application/json",
        )

        fields = ["routes.duration", "routes.distanceMeters"]
        
        # This will fail to run until we add compute_routes to Client
        routes = self.client.compute_routes(
            origin="Sydney",
            destination="Melbourne",
            fields=fields
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        
        # Verify URL
        self.assertURLEqual(
            "https://routes.googleapis.com/directions/v2:computeRoutes?key=" + self.key,
            call.request.url
        )
        
        # Verify Headers
        self.assertEqual("routes.duration,routes.distanceMeters", call.request.headers.get("X-Goog-FieldMask"))
        self.assertIn("GoogleGeoApiClientPython", call.request.headers.get("User-Agent"))

        # Verify Body
        body = json.loads(call.request.body.decode('utf-8'))
        self.assertEqual({"address": "Sydney"}, body["origin"])
        self.assertEqual({"address": "Melbourne"}, body["destination"])

    @responses.activate
    def test_compute_routes_complex(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.compute_routes(
            origin=(-33.867, 151.207),
            destination={"lat": -37.814, "lng": 144.963},
            travel_mode="BICYCLE",
            fields=["routes.duration", "routes.distanceMeters"]
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        body = json.loads(call.request.body.decode('utf-8'))
        self.assertEqual(
            {"location": {"latLng": {"latitude": -33.867, "longitude": 151.207}}},
            body["origin"]
        )
        self.assertEqual(
            {"location": {"latLng": {"latitude": -37.814, "longitude": 144.963}}},
            body["destination"]
        )
        self.assertEqual("BICYCLE", body["travelMode"])

    @responses.activate
    def test_compute_route_matrix(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
            body='[{"originIndex":0,"destinationIndex":0,"status":{}}]',
            status=200,
            content_type="application/json",
        )

        matrix = self.client.compute_route_matrix(
            origins=["Sydney", "Canberra"],
            destinations=["Melbourne"],
            fields=["originIndex", "destinationIndex", "duration", "distanceMeters"]
        )

        self.assertEqual(1, len(responses.calls))
        call = responses.calls[0]
        self.assertURLEqual(
            "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix?key=" + self.key,
            call.request.url
        )
        self.assertEqual(
            "originIndex,destinationIndex,duration,distanceMeters",
            call.request.headers.get("X-Goog-FieldMask")
        )

        body = json.loads(call.request.body.decode('utf-8'))
        self.assertEqual(2, len(body["origins"]))
        self.assertEqual({"waypoint": {"address": "Sydney"}}, body["origins"][0])
        self.assertEqual({"waypoint": {"address": "Canberra"}}, body["origins"][1])
        self.assertEqual(1, len(body["destinations"]))
        self.assertEqual({"waypoint": {"address": "Melbourne"}}, body["destinations"][0])

    @responses.activate
    def test_routes_error_handling(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"error":{"status":"INVALID_ARGUMENT","message":"Bad request"}}',
            status=400,
            content_type="application/json",
        )

        with self.assertRaises(googlemaps.exceptions.ApiError):
            self.client.compute_routes(origin="Sydney", destination="Melbourne")

    @responses.activate
    def test_routes_http_error(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='Not Found',
            status=404,
            content_type="text/plain",
        )

        with self.assertRaises(googlemaps.exceptions.HTTPError):
            self.client.compute_routes(origin="Sydney", destination="Melbourne")

    def test_routes_invalid_waypoint(self):
        with self.assertRaises(ValueError):
            self.client.compute_routes(origin=12345, destination="Melbourne")

    def test_route_matrix_empty_validation(self):
        with self.assertRaises(ValueError):
            self.client.compute_route_matrix(origins=[], destinations=["Melbourne"])

    @responses.activate
    def test_routes_place_id_waypoint(self):
        responses.add(
            responses.POST,
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            body='{"routes":[]}',
            status=200,
            content_type="application/json",
        )

        self.client.compute_routes(
            origin="place_id:ChIJ123",
            destination={"placeId": "ChIJ456"}
        )

        call = responses.calls[0]
        body = json.loads(call.request.body.decode('utf-8'))
        self.assertEqual({"placeId": "ChIJ123"}, body["origin"])
        self.assertEqual({"placeId": "ChIJ456"}, body["destination"])
