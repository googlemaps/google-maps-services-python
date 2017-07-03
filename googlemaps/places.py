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

"""Performs requests to the Google Places API."""

from googlemaps import convert


def places(client, query, location=None, radius=None, language=None,
           min_price=None, max_price=None, open_now=False, type=None,
           page_token=None):
    """
    Places search.

    :param query: The text string on which to search, for example: "restaurant".
    :type query: string

    :param location: The latitude/longitude value for which you wish to obtain the
        closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param language: The language in which to return results.
    :type langauge: string

    :param min_price: Restricts results to only those places with no less than
        this price level. Valid values are in the range from 0 (most affordable)
        to 4 (most expensive).
    :type min_price: int

    :param max_price: Restricts results to only those places with no greater
        than this price level. Valid values are in the range from 0 (most
        affordable) to 4 (most expensive).
    :type max_price: int

    :param open_now: Return only those places that are open for business at
        the time the query is sent.
    :type open_now: bool

    :param type: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/supported_types
    :type type: string

    :param page_token: Token from a previous search that when provided will
        returns the next page of results for the same search.
    :type page_token: string

    :rtype: result dict with the following keys:
        results: list of places
        html_attributions: set of attributions which must be displayed
        next_page_token: token for retrieving the next page of results
    """
    return _places(client, "text", query=query, location=location,
                   radius=radius, language=language, min_price=min_price,
                   max_price=max_price, open_now=open_now, type=type,
                   page_token=page_token)


def places_nearby(client, location, radius=None, keyword=None, language=None,
                  min_price=None, max_price=None, name=None, open_now=False,
                  rank_by=None, type=None, page_token=None):
    """
    Performs nearby search for places.

    :param location: The latitude/longitude value for which you wish to obtain the
                     closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param keyword: A term to be matched against all content that Google has
                    indexed for this place.
    :type keyword: string

    :param language: The language in which to return results.
    :type langauge: string

    :param min_price: Restricts results to only those places with no less than
                      this price level. Valid values are in the range from 0
                      (most affordable) to 4 (most expensive).
    :type min_price: int

    :param max_price: Restricts results to only those places with no greater
                      than this price level. Valid values are in the range
                      from 0 (most affordable) to 4 (most expensive).
    :type max_price: int

    :param name: One or more terms to be matched against the names of places.
    :type name: string or list of strings

    :param open_now: Return only those places that are open for business at
                     the time the query is sent.
    :type open_now: bool

    :param rank_by: Specifies the order in which results are listed.
                    Possible values are: prominence (default), distance
    :type rank_by: string

    :param type: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/supported_types
    :type type: string

    :param page_token: Token from a previous search that when provided will
                       returns the next page of results for the same search.
    :type page_token: string

    :rtype: result dict with the following keys:
            status: status code
            results: list of places
            html_attributions: set of attributions which must be displayed
            next_page_token: token for retrieving the next page of results

    """
    if rank_by == "distance":
        if not (keyword or name or type):
          raise ValueError("either a keyword, name, or type arg is required "
                           "when rank_by is set to distance")
        elif radius is not None:
          raise ValueError("radius cannot be specified when rank_by is set to "
                           "distance")

    return _places(client, "nearby", location=location, radius=radius,
                   keyword=keyword, language=language, min_price=min_price,
                   max_price=max_price, name=name, open_now=open_now,
                   rank_by=rank_by, type=type, page_token=page_token)


def places_radar(client, location, radius, keyword=None, min_price=None,
                 max_price=None, name=None, open_now=False, type=None):
    """
    Performs radar search for places.

    :param location: The latitude/longitude value for which you wish to obtain the
                     closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param keyword: A term to be matched against all content that Google has
                    indexed for this place.
    :type keyword: string

    :param min_price: Restricts results to only those places with no less than
                      this price level. Valid values are in the range from 0
                      (most affordable) to 4 (most expensive).
    :type min_price: int

    :param max_price: Restricts results to only those places with no greater
                      than this price level. Valid values are in the range
                      from 0 (most affordable) to 4 (most expensive).
    :type max_price: int

    :param name: One or more terms to be matched against the names of places.
    :type name: string or list of strings

    :param open_now: Return only those places that are open for business at
                     the time the query is sent.
    :type open_now: bool

    :param type: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/supported_types
    :type type: string

    :rtype: result dict with the following keys:
            status: status code
            results: list of places
            html_attributions: set of attributions which must be displayed

    """
    if not (keyword or name or type):
        raise ValueError("either a keyword, name, or type arg is required")

    from warnings import warn
    warn("places_radar is deprecated, see http://goo.gl/BGiumE",
         DeprecationWarning)

    return _places(client, "radar", location=location, radius=radius,
                   keyword=keyword, min_price=min_price, max_price=max_price,
                   name=name, open_now=open_now, type=type)


def _places(client, url_part, query=None, location=None, radius=None,
            keyword=None, language=None, min_price=0, max_price=4, name=None,
            open_now=False, rank_by=None, type=None, page_token=None):
    """
    Internal handler for ``places``, ``places_nearby``, and ``places_radar``.
    See each method's docs for arg details.
    """

    params = {"minprice": min_price, "maxprice": max_price}

    if query:
        params["query"] = query
    if location:
        params["location"] = convert.latlng(location)
    if radius:
        params["radius"] = radius
    if keyword:
        params["keyword"] = keyword
    if language:
        params["language"] = language
    if name:
        params["name"] = convert.join_list(" ", name)
    if open_now:
        params["opennow"] = "true"
    if rank_by:
        params["rankby"] = rank_by
    if type:
        params["type"] = type
    if page_token:
        params["pagetoken"] = page_token

    url = "/maps/api/place/%ssearch/json" % url_part
    return client._request(url, params)


def place(client, place_id, language=None):
    """
    Comprehensive details for an individual place.

    :param place_id: A textual identifier that uniquely identifies a place,
        returned from a Places search.
    :type place_id: string

    :param language: The language in which to return results.
    :type langauge: string

    :rtype: result dict with the following keys:
        result: dict containing place details
        html_attributions: set of attributions which must be displayed
    """
    params = {"placeid": place_id}
    if language:
        params["language"] = language
    return client._request("/maps/api/place/details/json", params)


def places_photo(client, photo_reference, max_width=None, max_height=None):
    """
    Downloads a photo from the Places API.

    :param photo_reference: A string identifier that uniquely identifies a
        photo, as provided by either a Places search or Places detail request.
    :type photo_reference: string

    :param max_width: Specifies the maximum desired width, in pixels.
    :type max_width: int

    :param max_height: Specifies the maximum desired height, in pixels.
    :type max_height: int

    :rtype: iterator containing the raw image data, which typically can be
        used to save an image file locally. For example:

        ```
        f = open(local_filename, 'wb')
        for chunk in client.photo(photo_reference, max_width=100):
            if chunk:
                f.write(chunk)
        f.close()
        ```
    """

    if not (max_width or max_height):
        raise ValueError("a max_width or max_height arg is required")

    params = {"photoreference": photo_reference}

    if max_width:
        params["maxwidth"] = max_width
    if max_height:
        params["maxheight"] = max_height

    # "extract_body" and "stream" args here are used to return an iterable
    # response containing the image file data, rather than converting from
    # json.
    response = client._request("/maps/api/place/photo", params,
                           extract_body=lambda response: response,
                           requests_kwargs={"stream": True})
    return response.iter_content()


def places_autocomplete(client, input_text, offset=None, location=None,
                        radius=None, language=None, types=None,
                        components=None, strict_bounds=False):
    """
    Returns Place predictions given a textual search string and optional
    geographic bounds.

    :param input_text: The text string on which to search.
    :type input_text: string

    :param offset: The position, in the input term, of the last character
                   that the service uses to match predictions. For example,
                   if the input is 'Google' and the offset is 3, the
                   service will match on 'Goo'.
    :type offset: int

    :param location: The latitude/longitude value for which you wish to obtain the
                     closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: int

    :param language: The language in which to return results.
    :type langauge: string

    :param types: Restricts the results to places matching the specified type.
        The full list of supported types is available here:
        https://developers.google.com/places/web-service/autocomplete#place_types
    :type type: string

    :param components: A component filter for which you wish to obtain a geocode,
                       for example:
                       ``{'administrative_area': 'TX','country': 'US'}``
    :type components: dict

    :param strict_bounds: Returns only those places that are strictly within
        the region defined by location and radius.
    :type strict_bounds: bool

    :rtype: list of predictions

    """
    return _autocomplete(client, "", input_text, offset=offset,
                         location=location, radius=radius, language=language,
                         types=types, components=components,
                         strict_bounds=strict_bounds)


def places_autocomplete_query(client, input_text, offset=None, location=None,
                              radius=None, language=None):
    """
    Returns Place predictions given a textual search query, such as
    "pizza near New York", and optional geographic bounds.

    :param input_text: The text query on which to search.
    :type input_text: string

    :param offset: The position, in the input term, of the last character
        that the service uses to match predictions. For example, if the input
        is 'Google' and the offset is 3, the service will match on 'Goo'.
    :type offset: int

    :param location: The latitude/longitude value for which you wish to obtain the
        closest, human-readable address.
    :type location: string, dict, list, or tuple

    :param radius: Distance in meters within which to bias results.
    :type radius: number

    :param language: The language in which to return results.
    :type langauge: string

    :rtype: list of predictions
    """
    return _autocomplete(client, "query", input_text, offset=offset,
                         location=location, radius=radius, language=language)


def _autocomplete(client, url_part, input_text, offset=None, location=None,
                  radius=None, language=None, types=None, components=None,
                  strict_bounds=False):
    """
    Internal handler for ``autocomplete`` and ``autocomplete_query``.
    See each method's docs for arg details.
    """

    params = {"input": input_text}

    if offset:
        params["offset"] = offset
    if location:
        params["location"] = convert.latlng(location)
    if radius:
        params["radius"] = radius
    if language:
        params["language"] = language
    if types:
        params["types"] = types
    if components:
        params["components"] = convert.components(components)
    if strict_bounds:
        params["strictbounds"] = "true"

    url = "/maps/api/place/%sautocomplete/json" % url_part
    return client._request(url, params)["predictions"]
