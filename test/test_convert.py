"""Tests for the convert module."""

import unittest
import datetime

from googlemaps import convert

class ConvertTest(unittest.TestCase):

    def test_latlng(self):
        ll = {"lat": 1, "lng": 2}
        self.assertEqual("1.000000,2.000000", convert.latlng(ll))

        ll = [1, 2]
        self.assertEqual("1.000000,2.000000", convert.latlng(ll))

        ll = (1, 2)
        self.assertEqual("1.000000,2.000000", convert.latlng(ll))

        with self.assertRaises(TypeError):
            convert.latlng(1)

        with self.assertRaises(TypeError):
            convert.latlng("test")


    def test_join_list(self):
        self.assertEquals("asdf", convert.join_list("|", "asdf"))

        self.assertEquals("1,2,A", convert.join_list(",", ["1", "2", "A"]))

        self.assertEquals("", convert.join_list(",", []))

        self.assertEquals("a,B", convert.join_list(",", ("a", "B")))

    def test_as_list(self):
        self.assertEquals([1], convert.as_list(1))

        self.assertEquals([1, 2, 3], convert.as_list([1, 2, 3]))

        self.assertEquals(["string"], convert.as_list("string"))

        self.assertEquals((1, 2), convert.as_list((1, 2)))

    def test_time(self):
        self.assertEquals("1409810596", convert.time(1409810596))

        dt = datetime.datetime.fromtimestamp(1409810596)
        self.assertEquals("1409810596", convert.time(dt))

    def test_components(self):
        c = {"country": "US"}
        self.assertEquals("country:US", convert.components(c))

        c = {"country": "US", "foo": 1}
        self.assertEquals("country:US|foo:1", convert.components(c))

        with self.assertRaises(TypeError):
            convert.components("test")

        with self.assertRaises(TypeError):
            convert.components(1)

        with self.assertRaises(TypeError):
            convert.components(("c", "b"))


    def test_bounds(self):
        ne = {"lat": 1, "lng": 2}
        sw = (3, 4)
        b = {"northeast": ne, "southwest": sw}
        self.assertEquals("3.000000,4.000000|1.000000,2.000000",
                          convert.bounds(b))

        with self.assertRaises(TypeError):
            convert.bounds("test")
