"""Tests for the directions module."""

import unittest
import datetime

import googlemaps

class DirectionsTest(unittest.TestCase):

    def setUp(self):
        self.c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    def test_simple_directions(self):
        # Simplest directions request. Driving directions by default.
        routes = googlemaps.directions(self.c, "Sydney", "Melbourne")
        self.assertIsNotNone(routes)
        self.assertEquals(1, len(routes))
        self.assertEquals('Sydney NSW, Australia',
                          routes[0]['legs'][0]['start_address'])
    	self.assertEquals('Melbourne VIC, Australia',
                          routes[0]['legs'][0]['end_address'])

    def test_complex_request(self):
        routes = googlemaps.directions(self.c,
                                        'Sydney',
                                        'Melbourne',
                                        mode='bicycling',
                                        avoid=['highways', 'tolls', 'ferries'],
                                        units='metric',
                                        region='us')
        self.assertIsNotNone(routes)

