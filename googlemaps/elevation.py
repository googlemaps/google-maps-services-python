"""Performs requests to the Google Maps Elevation API."""
from googlemaps import common
from googlemaps import convert

def elevation(ctx, locations):
    """
    Provides elevation data for locations provided on the surface of the
    earth, including depth locations on the ocean floor (which return negative
    values)

    :param ctx: Shared googlemaps.Context
    :type ctx: googlemaps.Context

    :param locations: A single latitude/longitude tuple, or a list of
            latitude/longitude tuples from which you wish to calculate
            elevation data.
    :type locations: list or tuple

    :rtype: list of elevation data responses
    """
    params = {}
    if type(locations) is tuple:
        locations = [locations]

    params["locations"] = convert.join_list("|",
            [convert.latlng(k) for k in convert.as_list(locations)])

    return common._get(ctx, "/maps/api/elevation/json", params)["results"]

def elevation_along_path(ctx, path, samples):
    """
    Provides elevation data sampled along a path on the surface of the earth.

    :param ctx: Shared googlemaps.Context
    :type ctx: googlemaps.Context

    :param path: A encoded polyline string, or a list of
            latitude/longitude tuples from which you wish to calculate
            elevation data.
    :type path: str or list

    :param samples: The number of sample points along a path for which to
            return elevation data.
    :type samples: int

    :rtype: list of elevation data responses
    """

    if type(path) is str:
        path = "enc:%s" % path
    else:
        path = convert.join_list("|",
                [convert.latlng(k) for k in convert.as_list(path)])

    params = {
        "path": path,
        "samples": samples
    }

    return common._get(ctx, "/maps/api/elevation/json", params)["results"]
