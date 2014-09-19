"""Tests for the elevation module."""

import unittest
import datetime

import googlemaps

class ElevationTest(unittest.TestCase):

    def setUp(self):
        self.c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    def test_elevation_single(self):
        results = googlemaps.elevation(self.c, (40.714728, -73.998672))
        self.assertAlmostEqual(8.8836946, results[0]['elevation'])
        self.assertAlmostEqual(76.3516159, results[0]['resolution'])

    def test_elevation_single_list(self):
        results = googlemaps.elevation(self.c, [(40.714728, -73.998672)])
        self.assertAlmostEqual(8.8836946, results[0]['elevation'])
        self.assertAlmostEqual(76.3516159, results[0]['resolution'])

    def test_elevation_multiple(self):
        locations = [(40.714728, -73.998672), (-34.397, 150.644)]
        results = googlemaps.elevation(self.c, locations)

        self.assertTrue(2, len(results))

        self.assertAlmostEqual(8.8836946, results[0]['elevation'], 4)
        self.assertAlmostEqual(76.3516159, results[0]['resolution'])
        self.assertAlmostEqual(392.5118713, results[1]['elevation'])
        self.assertAlmostEqual(152.7032318, results[1]['resolution'])

    def test_elevation_along_path_single(self):
        with self.assertRaises(Exception):
          results = googlemaps.elevation_along_path(self.c,
                    [(40.714728, -73.998672)], 5)

    def test_elevation_along_path(self):
        path = [(40.714728, -73.998672), (-34.397, 150.644)]
        
        results = googlemaps.elevation_along_path(self.c, path, 5)

        self.assertTrue(5, len(results))

        self.assertAlmostEqual(8.8836946, results[0]['elevation'])
        self.assertAlmostEqual(76.3516159, results[0]['resolution'])
        self.assertAlmostEqual(392.5118713, results[4]['elevation'])
        self.assertAlmostEqual(152.7032318, results[4]['resolution'])

