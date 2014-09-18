"""Tests for the directions module."""

from datetime import datetime
from datetime import timedelta
import googlemaps
import unittest


class DirectionsTest(unittest.TestCase):

    def setUp(self):
        self.ctx = googlemaps.Context(
            "AIzaSyAZ0_yiPw2Zp2huKxug49ZYi-pytL6NZ-c")

    def test_simple_directions(self):
        # Simplest directions request. Driving directions by default.
        routes = googlemaps.directions(self.ctx,
                                       "Sydney, NSW", "Melbourne, VIC")
        self.assertIsNotNone(routes)
        self.assertEquals(1, len(routes))
        self.assertEquals("Sydney NSW, Australia",
                          routes[0]["legs"][0]["start_address"])
        self.assertEquals("Melbourne VIC, Australia",
                          routes[0]["legs"][0]["end_address"])

    def test_complex_request(self):
        routes = googlemaps.directions(self.ctx,
                                       "Sydney",
                                       "Melbourne",
                                       mode="bicycling",
                                       avoid=["highways", "tolls", "ferries"],
                                       units="metric",
                                       region="us")
        self.assertIsNotNone(routes)

    def test_transit_without_time(self):
        # With mode of transit, we need a departure_time or an
        # arrival_time specified
        with self.assertRaises(Exception):
            googlemaps.directions(self.ctx,
                                  "Sydney Town Hall",
                                  "Parramatta, NSW",
                                  mode="transit")

    def test_transit_with_departure_time(self):
        # Transit directions with a departure_time specified
        routes = googlemaps.directions(self.ctx,
                                       "Sydney Town Hall",
                                       "Parramatta, NSW",
                                       mode="transit",
                                       departure_time=datetime.now())
        self.assertIsNotNone(routes)

    def test_transit_with_arrival_time(self):
        # Transit directions with an arrival_time specified
        an_hour_from_now = datetime.now() + timedelta(hours=1)
        routes = googlemaps.directions(self.ctx, "Sydney Town Hall",
                                       "Parramatta, NSW",
                                       mode="transit",
                                       arrival_time=an_hour_from_now)
        self.assertIsNotNone(routes)

    # TODO(mdr): Convert error returns into exceptions
    # def test_crazy_travel_mode(self):
    #     # An invalid travel mode throws a ValueError
    #     with self.assertRaises(Exception):
    #         googlemaps.directions(self.ctx, "48 Pirrama Road, Pyrmont, NSW",
    #                               "Sydney Town Hall",
    #                               mode="crawling")

    def test_travel_mode_round_trip(self):
        routes = googlemaps.directions(self.ctx, "Town Hall, Sydney",
                                       "Parramatta, NSW",
                                       mode="bicycling")
        self.assertIsNotNone(routes)
        self.assertEquals("BICYCLING",
                          routes[0]["legs"][0]["steps"][0]["travel_mode"])

    def test_brooklyn_to_queens_by_transit(self):
        routes = googlemaps.directions(self.ctx, "Brooklyn",
                                       "Queens",
                                       mode="transit",
                                       departure_time=datetime.now())
        self.assertIsNotNone(routes)
        self.assertEquals("WALKING",
                          routes[0]["legs"][0]["steps"][0]["travel_mode"])
        self.assertEquals("TRANSIT",
                          routes[0]["legs"][0]["steps"][1]["travel_mode"])

    def test_boston_to_concord_via_charlestown_and_lexignton(self):
        routes = googlemaps.directions(self.ctx, "Boston, MA",
                                       "Concord, MA",
                                       waypoints=["Charlestown, MA",
                                                  "Lexington, MA"])
        self.assertIsNotNone(routes)
        self.assertEquals("Boston, MA, USA",
                          routes[0]["legs"][0]["start_address"])
        self.assertEquals("Charlestown, Boston, MA, USA",
                          routes[0]["legs"][0]["end_address"])
        self.assertEquals("Lexington, MA, USA",
                          routes[0]["legs"][1]["end_address"])
        self.assertEquals("Concord, MA, USA",
                          routes[0]["legs"][2]["end_address"])

    # TODO(mdr): Implement optimize_waypoints
    # def test_adelaide_wine_tour(self):
    #     routes = googlemaps.directions(self.ctx, "Adelaide, SA",
    #                                    "Adelaide, SA",
    #                                    waypoints=["Barossa Valley, SA",
    #                                               "Clare, SA",
    #                                               "Connawarra, SA",
    #                                               "McLaren Vale, SA"],
    #                                    optimize_waypoints=True)
    #     self.assertEquals([1, 0, 2, 3], routes[0]["waypoint_order"])

    def test_toledo_to_madrid_in_spain(self):
        routes = googlemaps.directions(self.ctx, "Toledo", "Madrid",
                                       region="es")
        self.assertIsNotNone(routes)
        self.assertEquals("Toledo, Toledo, Spain",
                          routes[0]["legs"][0]["start_address"])
        self.assertEquals("Madrid, Madrid, Spain",
                          routes[0]["legs"][0]["end_address"])

    # TODO(mdr): Convert ZERO_RETURNS into zero length arrays.
    # def test_toledo_to_madrid_not_in_spain(self):
    #     routes = googlemaps.directions(self.ctx, "Toledo", "Madrid")
    #     self.assertIsNotNone(routes)
    #     self.assertEquals(0, len(routes))

    def test_language_parameter(self):
        routes = googlemaps.directions(self.ctx, "Toledo", "Madrid",
                                       region="es",
                                       language="es")
        self.assertIsNotNone(routes)
        self.assertEquals(u"Toledo, Toledo, Espa\xf1a",
                          routes[0]["legs"][0]["start_address"])
        self.assertEquals(u"Madrid, Madrid, Espa\xf1a",
                          routes[0]["legs"][0]["end_address"])

    def test_alternatives(self):
        routes = googlemaps.directions(self.ctx, "Sydney Town Hall",
                                       "Parramatta Town Hall",
                                       alternatives=True)
        self.assertTrue(len(routes) > 1)

    _EPSILON = 0.000001

    def _expected_location(self, expected_lat, expected_lng, results):
        location = results[0]["geometry"]["location"]
        lat_delta = abs(location["lat"] - expected_lat)
        lng_delta = abs(location["lng"] - expected_lng)

        self.assertTrue(lat_delta < DirectionsTest._EPSILON)
        self.assertTrue(lng_delta < DirectionsTest._EPSILON)

    def _check_sydney_results(self, results):
        self.assertIsNotNone(results)
        self.assertIsNotNone(results[0]["geometry"])
        self.assertIsNotNone(results[0]["geometry"]["location"])
        self._expected_location(-33.8674869, 151.2069902, results)

    # TODO(mdr): Enforce API Key
    # def test_no_api_key(self):
    #     with self.assertRaises(Exception):
    #         ctx = googlemaps.Context()
    #         googlemaps.directions(ctx, "Sydney", "Melbourne")

    def test_invalid_api_key(self):
        with self.assertRaises(Exception):
            ctx = googlemaps.Context(key="Invalid key.")
            googlemaps.directions(ctx, "Sydney", "Melbourne")