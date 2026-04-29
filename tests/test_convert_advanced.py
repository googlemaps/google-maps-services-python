"""Advanced parametrized tests for googlemaps.convert.

These tests intentionally lean on ``pytest.mark.parametrize`` to exercise
every branch of every helper across a wide spectrum of inputs.
"""

from __future__ import annotations

import datetime

import pytest

from googlemaps import convert

# ---------------------------------------------------------------------------
# format_float
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [
        (0, "0"),
        (0.0, "0"),
        (-0.0, "-0"),  # IEEE -0 round-trips through f"{-0.0:.8f}" -> "-0.00000000"
        (40, "40"),
        (40.0, "40"),
        (40.1, "40.1"),
        (40.001, "40.001"),
        (40.0010, "40.001"),
        (40.000000001, "40"),
        (40.000000009, "40.00000001"),
        (-33.8674869, "-33.8674869"),
        (151.2069902, "151.2069902"),
        (1.23456789, "1.23456789"),
        (1.234567899, "1.2345679"),
        (1e-9, "0"),
        (1e-8, "0.00000001"),
        (1234567.5, "1234567.5"),
        (-1234567.5, "-1234567.5"),
    ],
)
def test_format_float(value, expected):
    assert convert.format_float(value) == expected


def test_format_float_accepts_int_strings():
    # format_float casts via float(); strings of numbers are valid input.
    assert convert.format_float("10.5") == "10.5"


@pytest.mark.parametrize("bad", ["abc", "", None, [], {}])
def test_format_float_rejects_non_numeric(bad):
    with pytest.raises((TypeError, ValueError)):
        convert.format_float(bad)


# ---------------------------------------------------------------------------
# latlng / normalize_lat_lng
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "arg,expected",
    [
        ({"lat": -33.8674869, "lng": 151.2069902}, "-33.8674869,151.2069902"),
        ({"latitude": -33.8674869, "longitude": 151.2069902}, "-33.8674869,151.2069902"),
        ((-33, 151), "-33,151"),
        ([-33, 151], "-33,151"),
        ((0, 0), "0,0"),
        ((90, 180), "90,180"),
        ((-90, -180), "-90,-180"),
        ((1.0, 2.0), "1,2"),
        ("Sydney", "Sydney"),
        ("-33.8674869,151.2069902", "-33.8674869,151.2069902"),
        ("", ""),
    ],
)
def test_latlng(arg, expected):
    assert convert.latlng(arg) == expected


@pytest.mark.parametrize(
    "bad",
    [123, 1.5, object(), set(), {"x": 1, "y": 2}, {"lat": 1}, {"longitude": 2}],
)
def test_latlng_rejects_invalid(bad):
    with pytest.raises(TypeError):
        convert.latlng(bad)


@pytest.mark.parametrize(
    "arg,expected",
    [
        ({"lat": 1, "lng": 2}, (1, 2)),
        ({"latitude": 3, "longitude": 4}, (3, 4)),
        ([5, 6], (5, 6)),
        ((7, 8), (7, 8)),
        ([5, 6, 99], (5, 6)),  # extra elements ignored
    ],
)
def test_normalize_lat_lng(arg, expected):
    assert convert.normalize_lat_lng(arg) == expected


@pytest.mark.parametrize("bad", [123, "abc", object(), {"x": 1}, set()])
def test_normalize_lat_lng_rejects_invalid(bad):
    with pytest.raises(TypeError):
        convert.normalize_lat_lng(bad)


# ---------------------------------------------------------------------------
# location_list
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "arg,expected",
    [
        ([{"lat": -33.86, "lng": 151.20}, "Sydney"], "-33.86,151.2|Sydney"),
        ([(1, 2), (3, 4)], "1,2|3,4"),
        ([[1, 2], [3, 4], [5, 6]], "1,2|3,4|5,6"),
        ((1, 2), "1,2"),  # single tuple
        (["A", "B", "C"], "A|B|C"),
        ([{"latitude": 0, "longitude": 0}], "0,0"),
        ("Sydney", "Sydney"),  # string is treated as a single location
    ],
)
def test_location_list(arg, expected):
    assert convert.location_list(arg) == expected


def test_location_list_empty():
    assert convert.location_list([]) == ""


# ---------------------------------------------------------------------------
# join_list / as_list / _is_list / is_string
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "sep,arg,expected",
    [
        ("|", ["a", "b", "c"], "a|b|c"),
        (",", ["a", "b"], "a,b"),
        ("|", "single", "single"),
        ("|", ("x", "y"), "x|y"),
        ("|", [], ""),
        ("|", [""], ""),
        (";", ["1", "2", "3"], "1;2;3"),
    ],
)
def test_join_list(sep, arg, expected):
    assert convert.join_list(sep, arg) == expected


@pytest.mark.parametrize(
    "arg,expected",
    [
        ("hello", ["hello"]),
        ([1, 2, 3], [1, 2, 3]),
        ((1, 2, 3), (1, 2, 3)),
        ([], []),
        (1, [1]),
        (None, [None]),
        ({"k": "v"}, [{"k": "v"}]),  # dicts are NOT list-like
    ],
)
def test_as_list(arg, expected):
    assert convert.as_list(arg) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        ("", True),
        ("hello", True),
        ("a", True),
        (b"bytes", False),
        (123, False),
        (1.5, False),
        ([], False),
        ({}, False),
        (None, False),
        ((), False),
        (object(), False),
    ],
)
def test_is_string(val, expected):
    assert convert.is_string(val) is expected


# ---------------------------------------------------------------------------
# time
# ---------------------------------------------------------------------------

def test_time_int():
    assert convert.time(1409810596) == "1409810596"


def test_time_float():
    assert convert.time(1409810596.7) == "1409810596"


def test_time_datetime_naive():
    dt = datetime.datetime(2020, 1, 1, 0, 0, 0)
    out = convert.time(dt)
    assert out.isdigit()
    assert int(out) > 0


def test_time_datetime_now():
    out = convert.time(datetime.datetime.now())
    assert out.isdigit()


@pytest.mark.parametrize("value", [0, 1, 999_999_999_999])
def test_time_extreme_ints(value):
    assert convert.time(value) == str(value)


# ---------------------------------------------------------------------------
# components
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "arg,expected",
    [
        ({"country": "US"}, "country:US"),
        ({"country": "US", "postal_code": "94043"}, "country:US|postal_code:94043"),
        ({"country": ["US", "AU"]}, "country:AU|country:US"),
        ({"country": ("US", "AU")}, "country:AU|country:US"),
        ({"a": "1", "b": "2", "c": "3"}, "a:1|b:2|c:3"),
        ({"x": "z", "a": "b"}, "a:b|x:z"),
        ({}, ""),
        ({"key": ""}, "key:"),
        ({"k": ["a", "b", "c"]}, "k:a|k:b|k:c"),
    ],
)
def test_components(arg, expected):
    assert convert.components(arg) == expected


@pytest.mark.parametrize("bad", ["string", 1, None, [], (), object()])
def test_components_rejects_non_dict(bad):
    with pytest.raises(TypeError):
        convert.components(bad)


# ---------------------------------------------------------------------------
# bounds
# ---------------------------------------------------------------------------

def test_bounds_dict():
    sydney = {
        "northeast": {"lat": -33.4245981, "lng": 151.3426361},
        "southwest": {"lat": -34.1692489, "lng": 150.502229},
    }
    out = convert.bounds(sydney)
    assert "|" in out
    sw, ne = out.split("|")
    assert sw.startswith("-34.16")
    assert ne.startswith("-33.42")


def test_bounds_string_passthrough():
    s = "1,2|3,4"
    assert convert.bounds(s) == s


@pytest.mark.parametrize(
    "bad",
    [
        "not-a-bounds",
        "1,2,3|4,5",
        {"sw": 1, "ne": 2},  # wrong keys
        {"southwest": (1, 2)},  # missing northeast
        123,
        None,
        [],
        (),
    ],
)
def test_bounds_rejects_invalid(bad):
    with pytest.raises(TypeError):
        convert.bounds(bad)


# ---------------------------------------------------------------------------
# size
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "arg,expected",
    [
        (400, "400x400"),
        (1, "1x1"),
        ((400, 200), "400x200"),
        ([100, 50], "100x50"),
        ((0, 0), "0x0"),
    ],
)
def test_size(arg, expected):
    assert convert.size(arg) == expected


@pytest.mark.parametrize("bad", ["400", None, {}, object()])
def test_size_rejects_invalid(bad):
    with pytest.raises(TypeError):
        convert.size(bad)


# ---------------------------------------------------------------------------
# encode / decode polyline (round-trip)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "points",
    [
        [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)],
        [(0.0, 0.0)],
        [(1.0, 1.0), (1.0, 1.0)],
        [(-90, -180), (90, 180)],
        [(0, 0), (1e-5, 1e-5), (2e-5, 2e-5)],
        [{"lat": 38.5, "lng": -120.2}, {"lat": 40.7, "lng": -120.95}],
        [(i * 0.001, i * 0.002) for i in range(50)],
        [(-i * 0.01, i * 0.01) for i in range(20)],
    ],
)
def test_encode_decode_polyline_round_trip(points):
    encoded = convert.encode_polyline(points)
    decoded = convert.decode_polyline(encoded)
    assert len(decoded) == len(points)
    for original, got in zip(points, decoded):
        olat, olng = convert.normalize_lat_lng(original)
        assert abs(got["lat"] - olat) < 1e-5
        assert abs(got["lng"] - olng) < 1e-5


def test_encode_polyline_known_value():
    # Reference value from the Google polyline algorithm spec.
    points = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
    assert convert.encode_polyline(points) == "_p~iF~ps|U_ulLnnqC_mqNvxq`@"


def test_decode_polyline_known_value():
    decoded = convert.decode_polyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@")
    assert len(decoded) == 3
    assert abs(decoded[0]["lat"] - 38.5) < 1e-5
    assert abs(decoded[0]["lng"] + 120.2) < 1e-5


def test_encode_empty_polyline():
    assert convert.encode_polyline([]) == ""


def test_decode_empty_polyline():
    assert convert.decode_polyline("") == []


# ---------------------------------------------------------------------------
# shortest_path
# ---------------------------------------------------------------------------

def test_shortest_path_chooses_encoded_for_many_points():
    # Many points -> encoded version is shorter.
    points = [(i * 0.001, i * 0.001) for i in range(100)]
    out = convert.shortest_path(points)
    assert out.startswith("enc:")


def test_shortest_path_chooses_unencoded_for_one_point():
    out = convert.shortest_path([(1, 2)])
    # encoded form would be "enc:..." which is longer than "1,2"
    assert not out.startswith("enc:")
    assert out == "1,2"


def test_shortest_path_single_tuple():
    assert convert.shortest_path((1, 2)) == "1,2"
