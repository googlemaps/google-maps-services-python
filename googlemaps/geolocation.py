#
# Copyright 2017 Google Inc. All rights reserved.
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

"""Performs requests to the Google Maps Geolocation API."""
from googlemaps import exceptions


_GEOLOCATION_BASE_URL = "https://www.googleapis.com"


def _geolocation_extract(response):
    """
    Mimics the exception handling logic in ``client._get_body``, but
    for geolocation which uses a different response format.
    """
    body = response.json()
    if response.status_code in (200, 404):
        return body

    try:
        error = body["error"]["errors"][0]["reason"]
    except KeyError:
        error = None

    if response.status_code == 403:
        raise exceptions._OverQueryLimit(response.status_code, error)
    else:
        raise exceptions.ApiError(response.status_code, error)


def geolocate(client, home_mobile_country_code=None,
              home_mobile_network_code=None, radio_type=None, carrier=None,
              consider_ip=None, cell_towers=None, wifi_access_points=None):
    """
    The Google Maps Geolocation API returns a location and accuracy
    radius based on information about cell towers and WiFi nodes given.

    See https://developers.google.com/maps/documentation/geolocation/intro
    for more info, including more detail for each parameter below.

    :param home_mobile_country_code: The mobile country code (MCC) for
        the device's home network.
    :type home_mobile_country_code: string

    :param home_mobile_network_code: The mobile network code (MCC) for
        the device's home network.
    :type home_mobile_network_code: string

    :param radio_type: The mobile radio type. Supported values are
        lte, gsm, cdma, and wcdma. While this field is optional, it
        should be included if a value is available, for more accurate
        results.
    :type radio_type: string

    :param carrier: The carrier name.
    :type carrier: string

    :param consider_ip: Specifies whether to fall back to IP geolocation
        if wifi and cell tower signals are not available. Note that the
        IP address in the request header may not be the IP of the device.
    :type consider_ip: bool

    :param cell_towers: A list of cell tower dicts. See
        https://developers.google.com/maps/documentation/geolocation/intro#cell_tower_object
        for more detail.
    :type cell_towers: list of dicts

    :param wifi_access_points: A list of WiFi access point dicts. See
        https://developers.google.com/maps/documentation/geolocation/intro#wifi_access_point_object
        for more detail.
    :type wifi_access_points: list of dicts
    """

    params = {}
    if home_mobile_country_code is not None:
        params["homeMobileCountryCode"] = home_mobile_country_code
    if home_mobile_network_code is not None:
        params["homeMobileNetworkCode"] = home_mobile_network_code
    if radio_type is not None:
        params["radioType"] = radio_type
    if carrier is not None:
        params["carrier"] = carrier
    if consider_ip is not None:
        params["considerIp"] = consider_ip
    if cell_towers is not None:
        params["cellTowers"] = cell_towers
    if wifi_access_points is not None:
        params["wifiAccessPoints"] = wifi_access_points

    return client._request("/geolocation/v1/geolocate", {},  # No GET params
                           base_url=_GEOLOCATION_BASE_URL,
                           extract_body=_geolocation_extract,
                           post_json=params)
