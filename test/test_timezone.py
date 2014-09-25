# This Python file uses the following encoding: utf-8

"""Tests for the timezone module."""

import unittest
import datetime

import googlemaps

class TimezoneTest(unittest.TestCase):

    def setUp(self):
        self.c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    def test_los_angeles(self):
        timezone = googlemaps.timezone(self.c, (39.6034810,-119.6822510), 1331766000)
        self.assertIsNotNone(timezone)
        self.assertEquals(3600.0, timezone['dstOffset'])
        self.assertEquals('America/Los_Angeles', timezone['timeZoneId'])
        self.assertEquals('Pacific Daylight Time', timezone['timeZoneName'])

    def test_los_angeles_es(self):
        timezone = googlemaps.timezone(self.c, (39.6034810,-119.6822510), 1331766000, language='es')
        self.assertIsNotNone(timezone)
        self.assertEquals(3600.0, timezone['dstOffset'])
        self.assertEquals('America/Los_Angeles', timezone['timeZoneId'])
        self.assertEquals(u'Hora de verano del Pacífico', timezone['timeZoneName'])

    def test_los_angeles_with_no_timestamp(self):
        timezone = googlemaps.timezone(self.c, (39.6034810,-119.6822510))
        self.assertIsNotNone(timezone)
        self.assertEquals('America/Los_Angeles', timezone['timeZoneId'])
