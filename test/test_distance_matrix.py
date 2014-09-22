"""Tests for the distance matrix module."""

import unittest
import googlemaps


class DistanceMatrixTest(unittest.TestCase):

    def setUp(self):
        self.ctx = googlemaps.Context(
            "AIzaSyAZ0_yiPw2Zp2huKxug49ZYi-pytL6NZ-c")

    def test_basic_params(self):
        origins = ["Perth, Australia", "Sydney, Australia",
                   "Melbourne, Australia", "Adelaide, Australia",
                   "Brisbane, Australia", "Darwin, Australia",
                   "Hobart, Australia", "Canberra, Australia"]
        destinations = ["Uluru, Australia",
                        "Kakadu, Australia",
                        "Blue Mountains, Australia",
                        "Bungle Bungles, Australia",
                        "The Pinnacles, Australia"]

        matrix = googlemaps.distance_matrix(self.ctx, origins, destinations)

        self.assertEqual(len(matrix["rows"]), 8)
        self.assertEqual(len(matrix["rows"][0]["elements"]), 5)

    def test_mixed_params(self):
        origins = ["Bobcaygeon ON", [41.43206, -81.38992]]
        destinations = [(43.012486, -83.6964149),
                        {"lat": 42.8863855, "lng": -78.8781627}]

        matrix = googlemaps.distance_matrix(self.ctx, origins, destinations)

        self.assertEqual(len(matrix["rows"]), 2)
        self.assertEqual(len(matrix["rows"][0]["elements"]), 2)

    def test_all_params(self):
        origins = ["Perth, Australia", "Sydney, Australia",
                   "Melbourne, Australia", "Adelaide, Australia",
                   "Brisbane, Australia", "Darwin, Australia",
                   "Hobart, Australia", "Canberra, Australia"]
        destinations = ["Uluru, Australia",
                        "Kakadu, Australia",
                        "Blue Mountains, Australia",
                        "Bungle Bungles, Australia",
                        "The Pinnacles, Australia"]

        matrix = googlemaps.distance_matrix(self.ctx, origins, destinations,
                                            mode="driving",
                                            language="en-AU",
                                            avoid="tolls",
                                            units="imperial")

        self.assertEqual(len(matrix["rows"]), 8)
        self.assertEqual(len(matrix["rows"][0]["elements"]), 5)
        self.assertTrue(matrix["rows"][0]["elements"][0]["distance"]["text"]
                        .endswith("mi"))

    def test_lang_param(self):
        origins = ["Vancouver BC", "Seattle"]
        destinations = ["San Francisco", "Victoria BC"]

        matrix = googlemaps.distance_matrix(self.ctx, origins, destinations,
                                            language="fr-FR",
                                            mode="bicycling")

        # Ensure San Francisco is in les E'tats-Unis
        self.assertTrue(matrix["destination_addresses"][0]
                        .endswith(u'\xc9tats-Unis'))
        # Ensure we get results in heures
        self.assertTrue(matrix["rows"][0]["elements"][0]["duration"]["text"]
                        .endswith(u'heures'))
