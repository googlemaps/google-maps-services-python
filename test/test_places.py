# This Python file uses the following encoding: utf-8
#
# Copyright 2015 Google Inc. All rights reserved.
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

"""Tests for the places module."""

from types import GeneratorType

import responses

import test as _test
import googlemaps


class PlacesTest(_test.TestCase):

    def setUp(self):
        self.key = 'AIzaasdf'
        self.client = googlemaps.Client(self.key)
        self.location = (-33.86746, 151.207090)
        self.types = ('liquor_store', 'mosque')
        self.language = 'en-AU'
        self.radius = 100

    @responses.activate
    def test_places_text_search(self):
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
        responses.add(responses.GET, url,
                      body='{"status": "OK", "results": [], "html_attributions": []}',
                      status=200, content_type='application/json')

        self.client.places('restaurant', location=self.location,
                           radius=self.radius, language=self.language,
                           min_price=1, max_price=4, open_now=True)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('%s?language=en-AU&location=-33.867460%%2C151.207090&'
                            'maxprice=4&minprice=1&opennow=true&query=restaurant&'
                            'radius=100&key=%s'
                            % (url, self.key), responses.calls[0].request.url)

    @responses.activate
    def test_place_detail(self):
        url = 'https://maps.googleapis.com/maps/api/place/details/json'
        responses.add(responses.GET, url,
                      body='{"status": "OK", "result": {}, "html_attributions": []}',
                      status=200, content_type='application/json')

        self.client.place('ChIJN1t_tDeuEmsRUsoyG83frY4', language=self.language)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('%s?language=en-AU&placeid=ChIJN1t_tDeuEmsRUsoyG83frY4&key=%s'
                            % (url, self.key), responses.calls[0].request.url)

    @responses.activate
    def test_photo(self):
        url = 'https://maps.googleapis.com/maps/api/place/photo'
        responses.add(responses.GET, url, status=200)

        ref = 'CnRvAAAAwMpdHeWlXl-lH0vp7lez4znKPIWSWvgvZFISdKx45AwJVP1Qp37YOrH7sqHMJ8C-vBDC546decipPHchJhHZL94RcTUfPa1jWzo-rSHaTlbNtjh-N68RkcToUCuY9v2HNpo5mziqkir37WU8FJEqVBIQ4k938TI3e7bf8xq-uwDZcxoUbO_ZJzPxremiQurAYzCTwRhE_V0'
        response = self.client.places_photo(ref, max_width=100)

        self.assertTrue(isinstance(response, GeneratorType))
        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('%s?maxwidth=100&photoreference=%s&key=%s'
                            % (url, ref, self.key), responses.calls[0].request.url)

    @responses.activate
    def test_autocomplete(self):
        url = 'https://maps.googleapis.com/maps/api/place/queryautocomplete/json'
        responses.add(responses.GET, url,
                      body='{"status": "OK", "predictions": []}',
                      status=200, content_type='application/json')

        self.client.places_autocomplete('pizza near New York')

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('%s?input=pizza+near+New+York&key=%s' %
                            (url, self.key), responses.calls[0].request.url)
