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

"""Tests for the directions module."""

from datetime import datetime
from datetime import timedelta
import time

import responses

import googlemaps
from . import TestCase


class DirectionsTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_simple_directions(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        # Simplest directions request. Driving directions by default.
        routes = self.client.directions("Sydney", "Melbourne")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json"
            "?origin=Sydney&destination=Melbourne&key=%s" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_complex_request(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions(
            "Sydney",
            "Melbourne",
            mode="bicycling",
            avoid=["highways", "tolls", "ferries"],
            units="metric",
            region="us",
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Sydney&avoid=highways%%7Ctolls%%7Cferries&"
            "destination=Melbourne&mode=bicycling&key=%s"
            "&units=metric&region=us" % self.key,
            responses.calls[0].request.url,
        )

    def test_transit_without_time(self):
        # With mode of transit, we need a departure_time or an
        # arrival_time specified
        with self.assertRaises(googlemaps.exceptions.ApiError):
            self.client.directions(
                "Sydney Town Hall", "Parramatta, NSW", mode="transit"
            )

    @responses.activate
    def test_transit_with_departure_time(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        now = datetime.now()
        routes = self.client.directions(
            "Sydney Town Hall",
            "Parramatta, NSW",
            mode="transit",
            traffic_model="optimistic",
            departure_time=now,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?origin="
            "Sydney+Town+Hall&key=%s&destination=Parramatta%%2C+NSW&"
            "mode=transit&departure_time=%d&traffic_model=optimistic"
            % (self.key, time.mktime(now.timetuple())),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_transit_with_arrival_time(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        an_hour_from_now = datetime.now() + timedelta(hours=1)
        routes = self.client.directions(
            "Sydney Town Hall",
            "Parramatta, NSW",
            mode="transit",
            arrival_time=an_hour_from_now,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Sydney+Town+Hall&arrival_time=%d&"
            "destination=Parramatta%%2C+NSW&mode=transit&key=%s"
            % (time.mktime(an_hour_from_now.timetuple()), self.key),
            responses.calls[0].request.url,
        )

    def test_invalid_travel_mode(self):
        with self.assertRaises(ValueError):
            self.client.directions(
                "48 Pirrama Road, Pyrmont, NSW", "Sydney Town Hall", mode="crawling"
            )

    @responses.activate
    def test_travel_mode_round_trip(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions(
            "Town Hall, Sydney", "Parramatta, NSW", mode="bicycling"
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Town+Hall%%2C+Sydney&destination=Parramatta%%2C+NSW&"
            "mode=bicycling&key=%s" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_brooklyn_to_queens_by_transit(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        now = datetime.now()
        routes = self.client.directions(
            "Brooklyn", "Queens", mode="transit", departure_time=now
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Brooklyn&key=%s&destination=Queens&mode=transit&"
            "departure_time=%d" % (self.key, time.mktime(now.timetuple())),
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_boston_to_concord_via_charlestown_and_lexington(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions(
            "Boston, MA", "Concord, MA", waypoints=["Charlestown, MA", "Lexington, MA"]
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Boston%%2C+MA&destination=Concord%%2C+MA&"
            "waypoints=Charlestown%%2C+MA%%7CLexington%%2C+MA&"
            "key=%s" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_adelaide_wine_tour(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions(
            "Adelaide, SA",
            "Adelaide, SA",
            waypoints=[
                "Barossa Valley, SA",
                "Clare, SA",
                "Connawarra, SA",
                "McLaren Vale, SA",
            ],
            optimize_waypoints=True,
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Adelaide%%2C+SA&destination=Adelaide%%2C+SA&"
            "waypoints=optimize%%3Atrue%%7CBarossa+Valley%%2C+"
            "SA%%7CClare%%2C+SA%%7CConnawarra%%2C+SA%%7CMcLaren+"
            "Vale%%2C+SA&key=%s" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_toledo_to_madrid_in_spain(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions("Toledo", "Madrid", region="es")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Toledo&region=es&destination=Madrid&key=%s" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_zero_results_returns_response(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"ZERO_RESULTS","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions("Toledo", "Madrid")
        self.assertIsNotNone(routes)
        self.assertEqual(0, len(routes))

    @responses.activate
    def test_language_parameter(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions("Toledo", "Madrid", region="es", language="es")

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Toledo&region=es&destination=Madrid&key=%s&"
            "language=es" % self.key,
            responses.calls[0].request.url,
        )

    @responses.activate
    def test_alternatives(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            body='{"status":"OK","routes":[]}',
            status=200,
            content_type="application/json",
        )

        routes = self.client.directions(
            "Sydney Town Hall", "Parramatta Town Hall", alternatives=True
        )

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://maps.googleapis.com/maps/api/directions/json?"
            "origin=Sydney+Town+Hall&destination=Parramatta+Town+Hall&"
            "alternatives=true&key=%s" % self.key,
            responses.calls[0].request.url,
        )
