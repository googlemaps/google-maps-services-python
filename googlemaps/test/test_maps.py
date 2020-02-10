#
# Copyright 2020 Google Inc. All rights reserved.
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

"""Tests for the maps module."""

from types import GeneratorType

import responses

import googlemaps
import googlemaps.test as _test


class MapsTest(_test.TestCase):

    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_download(self):
        url = 'https://maps.googleapis.com/maps/api/staticmap'
        responses.add(responses.GET, url, status=200)

        response = self.client.maps_download(
            size=(400, 400), zoom=6, center=(63.259591,-144.667969),
            maptype="hybrid", format="png", scale=2, visible=["Tok,AK"],
            path={
                "weight": 5, "color": "red",
                "points": [(62.107733,-145.541936),
                           'Delta+Junction,AK']
            },
            markers=[
                {"color": "blue", "label": "S", "locations": [(62.107733,-145.541936)]},
                {"size": "tiny", "color": "green", "locations": ['Delta+Junction,AK']},
                {"size": "mid", "color": "0xFFFF00", "label": "C", "locations": ["Tok,AK"]}
            ]
        )

        self.assertTrue(isinstance(response, GeneratorType))
        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            '%s?center=63.259591%%2C-144.667969&format=png&maptype=hybrid&'
            'markers=color%%3Ablue%%7Clabel%%3AS%%7C62.107733%%2C-145.541936&'
            'markers=size%%3Atiny%%7Ccolor%%3Agreen%%7CDelta%%2BJunction%%2CAK&'
            'markers=size%%3Amid%%7Ccolor%%3A0xFFFF00%%7Clabel%%3AC%%7CTok%%2CAK&'
            'path=weight%%3A5%%7Ccolor%%3Ared%%7C62.107733%%2C-145.541936%%7CDelta%%2BJunction%%2CAK&'
            'scale=2&size=400x400&visible=Tok%%2CAK&zoom=6&key=%s'
            % (url, self.key), responses.calls[0].request.url)
