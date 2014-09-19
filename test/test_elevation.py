"""Tests for the geocoding module."""

import unittest
import datetime

import googlemaps

class ElevationTest(unittest.TestCase):

    def setUp(self):
        self.c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    _EPSILON = 0.000001

    def _expected_elevation(self, expected_elevation, elevation):
      elevation_delta = abs(elevation - expected_elevation)
      self.assertTrue(elevation_delta < self._EPSILON)
    
    def _expected_resolution(self, expected_resolution, resolution):
      resolution_delta = abs(resolution - expected_resolution)
      self.assertTrue(resolution_delta < self._EPSILON)

    def test_elevation_single(self):
        results = googlemaps.elevation(self.c, (40.714728, -73.998672))
        self._expected_elevation(8.883694, results[0]['elevation'])
        self._expected_resolution(76.351615, results[0]['resolution'])

    def test_elevation_single_list(self):
        results = googlemaps.elevation(self.c, [(40.714728, -73.998672)])
        self._expected_elevation(8.883694, results[0]['elevation'])
        self._expected_resolution(76.351615, results[0]['resolution'])

    def test_elevation_multiple(self):
        locations = [(40.714728, -73.998672), (-34.397, 150.644)]
        results = googlemaps.elevation(self.c, locations)

        self.assertTrue(2, len(results))

        self._expected_elevation(8.883694, results[0]['elevation'])
        self._expected_resolution(76.351615, results[0]['resolution'])
        self._expected_elevation(392.511871, results[1]['elevation'])
        self._expected_resolution(152.703231, results[1]['resolution'])

    def test_elevation_along_path_single(self):
        with self.assertRaises(Exception):
          results = googlemaps.elevation_along_path(self.c, [(40.714728, -73.998672)], 5)

    def test_elevation_along_path(self):
        path = [(40.714728, -73.998672), (-34.397, 150.644)]
        
        results = googlemaps.elevation_along_path(self.c, path, 5)

        self.assertTrue(5, len(results))

        self._expected_elevation(8.883694, results[0]['elevation'])
        self._expected_resolution(76.351615, results[0]['resolution'])
        self._expected_elevation(392.511871, results[4]['elevation'])
        self._expected_resolution(152.703231, results[4]['resolution'])

