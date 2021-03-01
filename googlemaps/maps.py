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

"""Performs requests to the Google Maps Static API."""

from googlemaps import convert


MAPS_IMAGE_FORMATS = {'png8', 'png', 'png32', 'gif', 'jpg', 'jpg-baseline'}

MAPS_MAP_TYPES = {'roadmap', 'satellite', 'terrain', 'hybrid'}

class StaticMapParam:
    """Base class to handle parameters for Maps Static API."""

    def __init__(self):
        self.params = []

    def __str__(self):
        """Converts a list of parameters to the format expected by
        the Google Maps server.

        :rtype: str

        """
        return convert.join_list('|', self.params)


class StaticMapMarker(StaticMapParam):
    """Handles marker parameters for Maps Static API."""

    def __init__(self, locations,
                 size=None, color=None, label=None):
        """
        :param locations: Specifies the locations of the markers on
            the map.
        :type locations: list

        :param size: Specifies the size of the marker.
        :type size: str

        :param color: Specifies a color of the marker.
        :type color: str

        :param label: Specifies a single uppercase alphanumeric
            character to be displaied on marker.
        :type label: str
        """

        super(StaticMapMarker, self).__init__()

        if size:
            self.params.append("size:%s" % size)

        if color:
            self.params.append("color:%s" % color)

        if label:
            if len(label) != 1 or (label.isalpha() and not label.isupper()) or not label.isalnum():
                raise ValueError("Marker label must be alphanumeric and uppercase.")
            self.params.append("label:%s" % label)

        self.params.append(convert.location_list(locations))


class StaticMapPath(StaticMapParam):
    """Handles path parameters for Maps Static API."""

    def __init__(self, points,
                 weight=None, color=None,
                 fillcolor=None, geodesic=None):
        """
        :param points: Specifies the point through which the path
            will be built.
        :type points: list

        :param weight: Specifies the thickness of the path in pixels.
        :type weight: int

        :param color: Specifies a color of the path.
        :type color: str

        :param fillcolor: Indicates both that the path marks off a
            polygonal area and specifies the fill color to use as an
            overlay within that area.
        :type fillcolor: str

        :param geodesic: Indicates that the requested path should be
            interpreted as a geodesic line that follows the curvature
            of the earth.
        :type geodesic: bool
        """

        super(StaticMapPath, self).__init__()

        if weight:
            self.params.append("weight:%s" % weight)

        if color:
            self.params.append("color:%s" % color)

        if fillcolor:
            self.params.append("fillcolor:%s" % fillcolor)

        if geodesic:
            self.params.append("geodesic:%s" % geodesic)

        self.params.append(convert.location_list(points))


def static_map(client, size,
               center=None, zoom=None, scale=None, 
               format=None, maptype=None, language=None, region=None,
               markers=None, path=None, visible=None, style=None):
    """
    Downloads a map image from the Maps Static API.

    See https://developers.google.com/maps/documentation/maps-static/intro
    for more info, including more detail for each parameter below.

    :param size: Defines the rectangular dimensions of the map image.
    :type param: int or list

    :param center: Defines the center of the map, equidistant from all edges
        of the map.
    :type center: dict or list or string

    :param zoom: Defines the zoom level of the map, which determines the
        magnification level of the map.
    :type zoom: int

    :param scale: Affects the number of pixels that are returned.
    :type scale: int

    :param format: Defines the format of the resulting image.
    :type format: string

    :param maptype: defines the type of map to construct. There are several
        possible maptype values, including roadmap, satellite, hybrid,
        and terrain.
    :type maptype: string

    :param language: defines the language to use for display of labels on
        map tiles.
    :type language: string

    :param region: defines the appropriate borders to display, based on
        geo-political sensitivities.
    :type region: string

    :param markers: define one or more markers to attach to the image at
        specified locations.
    :type markers: StaticMapMarker

    :param path: defines a single path of two or more connected points to
        overlay on the image at specified locations.
    :type path: StaticMapPath

    :param visible: specifies one or more locations that should remain visible
        on the map, though no markers or other indicators will be displayed.
    :type visible: list of dict

    :param style: defines a custom style to alter the presentation of
        a specific feature (roads, parks, and other features) of the map.
    :type style: list of dict

    :rtype: iterator containing the raw image data, which typically can be
        used to save an image file locally. For example:

        ```
        f = open(local_filename, 'wb')
        for chunk in client.static_map(size=(400, 400),
                                       center=(52.520103, 13.404871),
                                       zoom=15):
            if chunk:
                f.write(chunk)
        f.close()
        ```
    """

    params = {"size": convert.size(size)}

    if not markers:
        if not (center or zoom is not None):
            raise ValueError(
                "both center and zoom are required"
                "when markers is not specifed"
            )

    if center:
        params["center"] = convert.latlng(center)

    if zoom is not None:
        params["zoom"] = zoom

    if scale is not None:
        params["scale"] = scale

    if format:
        if format not in MAPS_IMAGE_FORMATS:
             raise ValueError("Invalid image format")
        params['format'] = format

    if maptype:
        if maptype not in MAPS_MAP_TYPES:
            raise ValueError("Invalid maptype")
        params["maptype"] = maptype

    if language:
        params["language"] = language

    if region:
        params["region"] = region

    if markers:
        params["markers"] = markers

    if path:
        params["path"] = path

    if visible:
        params["visible"] = convert.location_list(visible)

    if style:
        params["style"] = convert.components(style)

    response = client._request(
        "/maps/api/staticmap",
        params,
        extract_body=lambda response: response,
        requests_kwargs={"stream": True},
    )
    return response.iter_content()
