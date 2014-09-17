"""Tests for the geocoding module."""

import unittest
import datetime

import googlemaps

class GeocodingTest(unittest.TestCase):

    def setUp(self):
        self.c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    _EPSILON = 0.000001

    def _expected_location(self, expected_lat, expected_lng, results):
        lat_delta = abs(results[0]['geometry']['location']['lat'] - expected_lat)
        lng_delta = abs(results[0]['geometry']['location']['lng'] - expected_lng)

        self.assertTrue(lat_delta < self._EPSILON)
        self.assertTrue(lng_delta < self._EPSILON)

    def _check_sydney_results(self, results):
        self.assertIsNotNone(results)
        self.assertIsNotNone(results[0]['geometry'])
        self.assertIsNotNone(results[0]['geometry']['location'])
        self._expected_location(-33.8674869, 151.2069902, results)

    def test_simple_geocode(self):
        results = googlemaps.geocode(self.c, 'Sydney')
        self._check_sydney_results(results)

    def test_reverse_geocode(self):
        results = googlemaps.reverse_geocode(self.c, (-33.8674869, 151.2069902))
        self.assertTrue(results[0]['formatted_address'].find('Sydney') != -1)

    def test_geocoding_the_googleplex(self):
        results = googlemaps.geocode(self.c, '1600 Amphitheatre Parkway, '
                                  'Mountain View, CA')
        self.assertEquals('1600 Amphitheatre Parkway, Mountain View, CA 94043, USA',
                      results[0]['formatted_address'])

    def test_geocode_with_bounds(self):
        results = googlemaps.geocode(self.c, 'Winnetka',
                                  bounds={'southwest': (34.172684, -118.604794),
                                          'northeast':(34.236144, -118.500938)})
        self.assertEquals('Winnetka, Los Angeles, CA, USA',
                      results[0]['formatted_address'])

    def test_geocode_with_region_biasing(self):
        results = googlemaps.geocode(self.c, 'Toledo', region='es')
        self.assertEquals('Toledo, Toledo, Spain', results[0]['formatted_address'])

    def test_geocode_with_component_filter(self):
        results = googlemaps.geocode(self.c, 'santa cruz', 
            components={'country': 'ES'})
        self.assertEquals('Santa Cruz de Tenerife, Santa Cruz de Tenerife, Spain',
                      results[0]['formatted_address'])

    def test_geocode_with_multiple_component_filters(self):
        results = googlemaps.geocode(self.c, 'Torun', 
            components={'administrative_area': 'TX','country': 'US'})
        self.assertEquals('Texas, USA', results[0]['formatted_address'])


    def test_geocode_with_just_components(self):
        results = googlemaps.geocode(self.c, 
            components={'route': 'Annegatan',
                        'administrative_area': 'Helsinki', 
                        'country': 'Findland'})
        self.assertEquals('Annegatan, Helsinki, Finland',
                      results[0]['formatted_address'])

    def test_simple_reverse_geocode(self):
        results = googlemaps.reverse_geocode(self.c, (40.714224, -73.961452))
        self.assertEquals('277 Bedford Avenue, Brooklyn, NY 11211, USA',
                      results[0]['formatted_address'])
        self.assertEquals('277', results[0]['address_components'][0]['long_name'])
        self.assertEquals('277', results[0]['address_components'][0]['short_name'])
        self.assertEquals('street_number',
                      results[0]['address_components'][0]['types'][0])
        self.assertEquals('street_address', results[0]['types'][0])

    def test_reverse_geocode_restricted_by_type(self):
        results = googlemaps.reverse_geocode(self.c, (40.714224, -73.961452),
                                          location_type='ROOFTOP',
                                          result_type='street_address')
        self.assertIsNotNone(results)

    def test_reverse_geocode_multiple_location_types(self):
        results = googlemaps.reverse_geocode(self.c, (40.714224, -73.961452),
                                          location_type=['ROOFTOP',
                                                         'RANGE_INTERPOLATED'],
                                          result_type='street_address')
        self.assertIsNotNone(results)

    def test_reverse_geocode_multiple_result_types(self):
        results = googlemaps.reverse_geocode(self.c, (40.714224, -73.961452),
                                          location_type='ROOFTOP',
                                          result_type=['street_address',
                                                       'route'])
        self.assertIsNotNone(results)

    def test_partial_match(self):
        results = googlemaps.geocode(self.c, 'Pirrama Pyrmont')
        self.assertTrue(results[0]['partial_match'])

    def test_utf_results(self):
        results = googlemaps.geocode(self.c, components={'postal_code': '96766'})
        self.assertEquals(u'L\u012bhu\u02bbe, HI 96766, USA',
                      results[0]['formatted_address'])