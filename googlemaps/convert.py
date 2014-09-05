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


def latlng(ll):
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

    :param ll: The lat/lon pair.
    :type ll: basestring or dict or list
    """
    if isinstance(ll, basestring):
        return ll

    if isinstance(ll, dict):
        if "lat" in ll and "lng" in ll:
            return "%f,%f" % (ll["lat"], ll["lng"])

    # List or tuple.
    if _is_list(ll):
        return "%f,%f" % (ll[0], ll[1])

    raise TypeError(
            "Expected a string or lat/lng dict, "
            "but got %s" % type(o).__name__)


def join_list(sep, l):
    return sep.join(as_list(l))


def as_list(l):
    if _is_list(l):
        return l
    return [l]


def _is_list(arg):
    return (not _has_method(arg, "strip")
        and _has_method(arg, "__getitem__")
        or _has_method(arg, "__iter__"))


def time(t):
    """Converts the value into a unix time (seconds since unix epoch).

    For example:
        convert.time(datetime.now())
        # '1409810596'

    :param t: The time.
    :type t: datetime.datetime or int
    """
    # handle datetime instances.
    if _has_method(t, "timetuple"):
        t = _time.mktime(t.timetuple())

    if isinstance(t, float):
        t = int(t)

    return str(t)


def _has_method(arg, method):
    """Returns true if the given object has a method with the given name.

    :param arg: the object
    :param method: the method name
    :type method: basestring
    :rtype: bool
    """
    return hasattr(arg, method) and callable(getattr(arg, method))


def components(c):
    """Converts a dict of components to the format expected by the Google Maps
    server.

    For example:
    c = {"country": "US", "postal_code": "94043"}
    convert.components(c)
    # 'country:US|postal_code:94043'

    :param c: The component filter.
    :type c: dict or basestring
    :rtype basestring:
    """
    if isinstance(c, basestring):
        return c

    if isinstance(c, dict):
        c = ["%s:%s" % (k, c[k]) for k in c]
        return "|".join(c)

    raise TypeError(
            "Expected a string or dict for components, "
            "but got %s" % type(c).__name__)


def bounds(b):
    if isinstance(b, basestring):
        return b

    if isinstance(b, dict):
        if "southwest" in b and "northeast" in b:
            return "%s|%s" % (latlng(b["southwest"]), latlng(b["northeast"]))

    raise TypeError(
            "Expected a string or bounds (southwest/northeast) dict, "
            "but got %s" % type(b).__name__)

