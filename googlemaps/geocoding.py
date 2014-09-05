import common
import convert


# TODO(mdr-eng): test unicode parameters (e.g. in addresses).
def geocode(ctx, address=None, components=None, bounds=None, region=None, language=None):
    """
    Geocoding is the process of converting addresses
    (like "1600 Amphitheatre Parkway, Mountain View, CA") into geographic
    coordinates (like latitude 37.423021 and longitude -122.083739), which you
    can use to place markers or position the map.
    """

    params = {}

    if address:
        params["address"] = address

    if components:
        params["components"] = convert.components(components)

    if bounds:
        params["bounds"] = convert.bounds(bounds)

    if region:
        params["region"] = region

    if language:
        params["language"] = language

    return common._get(ctx, "/maps/api/geocode/json", params)["results"]


def reverse_geocode(ctx, latlng, result_type=None, location_type=None, language=None):
    """
    Reverse geocoding is the process of converting geographic coordinates into a
    human-readable address.
    """
    # TODO(mdr-eng): Add ReST style doc comments.

    params = {
        "latlng": convert.latlng(latlng)
    }

    if result_type:
        params["result_type"] = convert.join_list("|", result_type)

    if location_type:
        params["location_type"] = convert.join_list("|", location_type)

    if language:
        params["language"] = language

    return common._get(ctx, "/maps/api/geocode/json", params)["results"]
