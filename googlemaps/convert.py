"""Converts Python types to string representations suitable for Maps API server.

    For example:

    sydney = {
        "lat" : -33.8674869,
        "lng" : 151.2069902
    }

    convert.latlng(sydney)
    # '-33.8674869,151.2069902'
"""

import time as _time


def latlng(arg):
    """Converts a lat/lon pair to a comma-separated string.

    Accepts various representations:
    1) comma-separated string
    2) dict with two entries - "lat" and "lng"
    3) list or tuple - e.g. (-33, 151) or [-33, 151]

    For example:

    sydney = {
        "lat" : -33.8674869,
        "lng" : 151.2069902
    }

    convert.latlng(sydney)
    # '-33.8674869,151.2069902'

    :param arg: The lat/lon pair.
    :type arg: basestring or dict or list
    """
    if isinstance(arg, basestring):
        return arg

    if isinstance(arg, dict):
        if "lat" in arg and "lng" in arg:
            return "%f,%f" % (arg["lat"], arg["lng"])

    # List or tuple.
    if _is_list(arg):
        return "%f,%f" % (arg[0], arg[1])

    raise TypeError(
        "Expected a string or lat/lng dict, "
        "but got %s" % type(arg).__name__)


def join_list(sep, arg):
    """If arg is list-like, then joins it with sep.
    :param sep: Separator string.
    :type sep: basestring
    :param arg: Value to coerce into a list.
    :type arg: basestring or list
    :rtype: basestring
    """
    return sep.join(as_list(arg))


def as_list(arg):
    """Coerces arg into a list. If arg is already list-like, returns arg.
    Otherwise, returns a one-element list containing arg.
    :rtype: list
    """
    if _is_list(arg):
        return arg
    return [arg]


def _is_list(arg):
    """Checks if arg is list-like. This excludes strings."""
    return (not _has_method(arg, "strip")
            and _has_method(arg, "__getitem__")
            or _has_method(arg, "__iter__"))


def time(arg):
    """Converts the value into a unix time (seconds since unix epoch).

    For example:
        convert.time(datetime.now())
        # '1409810596'

    :param arg: The time.
    :type arg: datetime.datetime or int
    """
    # handle datetime instances.
    if _has_method(arg, "timetuple"):
        arg = _time.mktime(arg.timetuple())

    if isinstance(arg, float):
        arg = int(arg)

    return str(arg)


def _has_method(arg, method):
    """Returns true if the given object has a method with the given name.

    :param arg: the object
    :param method: the method name
    :type method: basestring
    :rtype: bool
    """
    return hasattr(arg, method) and callable(getattr(arg, method))


def components(arg):
    """Converts a dict of components to the format expected by the Google Maps
    server.

    For example:
    c = {"country": "US", "postal_code": "94043"}
    convert.components(c)
    # 'country:US|postal_code:94043'

    :param arg: The component filter.
    :type arg: dict or basestring
    :rtype basestring:
    """
    if isinstance(arg, basestring):
        return arg

    if isinstance(arg, dict):
        arg = ["%s:%s" % (k, arg[k]) for k in arg]
        return "|".join(arg)

    raise TypeError(
        "Expected a string or dict for components, "
        "but got %s" % type(arg).__name__)


def bounds(arg):
    """Converts a lat/lon bounds to a comma- and pipe-separated string.

    Accepts two representations:
    1) string: pipe-separated pair of comma-separated lat/lon pairs.
    2) dict with two entries - "southwest" and "northeast". See convert.latlng
    for information on how these can be represented.

    For example:

    sydney_bounds = {
        "northeast" : {
            "lat" : -33.4245981,
            "lng" : 151.3426361
        },
        "southwest" : {
            "lat" : -34.1692489,
            "lng" : 150.502229
        }
    }

    convert.bounds(sydney_bounds)
    # '-34.169249,150.502229|-33.424598,151.342636'

    :param arg: The bounds.
    :type arg: basestring or dict
    """

    if isinstance(arg, basestring):
        return arg

    if isinstance(arg, dict):
        if "southwest" in arg and "northeast" in arg:
            return "%s|%s" % (latlng(arg["southwest"]),
                              latlng(arg["northeast"]))

    raise TypeError(
        "Expected a string or bounds (southwest/northeast) dict, "
        "but got %s" % type(arg).__name__)

