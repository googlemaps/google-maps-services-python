"""Advanced parametrized tests for googlemaps.maps."""

from __future__ import annotations

import pytest
import responses

import googlemaps
from googlemaps.maps import (
    MAPS_IMAGE_FORMATS,
    MAPS_MAP_TYPES,
    StaticMapMarker,
    StaticMapPath,
)

# ---------------------------------------------------------------------------
# StaticMapMarker
# ---------------------------------------------------------------------------

def test_marker_locations_only():
    m = StaticMapMarker(locations=[(1, 2), (3, 4)])
    assert "1,2|3,4" in str(m)


@pytest.mark.parametrize("size", ["tiny", "mid", "small", "100"])
def test_marker_size(size):
    m = StaticMapMarker(locations=[(1, 2)], size=size)
    assert f"size:{size}" in str(m)


@pytest.mark.parametrize(
    "color",
    ["red", "blue", "green", "yellow", "0xFFAABB", "0x000000"],
)
def test_marker_color(color):
    m = StaticMapMarker(locations=[(1, 2)], color=color)
    assert f"color:{color}" in str(m)


@pytest.mark.parametrize("label", ["A", "Z", "0", "9", "X", "M", "1", "5"])
def test_marker_valid_label(label):
    m = StaticMapMarker(locations=[(1, 2)], label=label)
    assert f"label:{label}" in str(m)


@pytest.mark.parametrize("label", ["a", "ab", "AB", "12", "@", "z"])
def test_marker_invalid_label(label):
    with pytest.raises(ValueError):
        StaticMapMarker(locations=[(1, 2)], label=label)


def test_marker_combined_params_order():
    m = StaticMapMarker(
        locations=[(1, 2)], size="tiny", color="red", label="A"
    )
    s = str(m)
    assert s.index("size:tiny") < s.index("color:red") < s.index("label:A") < s.index("1,2")


# ---------------------------------------------------------------------------
# StaticMapPath
# ---------------------------------------------------------------------------

def test_path_points_only():
    p = StaticMapPath(points=[(1, 2), (3, 4)])
    assert "1,2|3,4" in str(p)


@pytest.mark.parametrize("weight", [1, 2, 5, 10, 100])
def test_path_weight(weight):
    p = StaticMapPath(points=[(1, 2), (3, 4)], weight=weight)
    assert f"weight:{weight}" in str(p)


@pytest.mark.parametrize("color", ["red", "0x00FF00", "blue"])
def test_path_color(color):
    p = StaticMapPath(points=[(1, 2), (3, 4)], color=color)
    assert f"color:{color}" in str(p)


@pytest.mark.parametrize("fillcolor", ["red", "0x00FF00FF", "0xAA0000"])
def test_path_fillcolor(fillcolor):
    p = StaticMapPath(points=[(1, 2), (3, 4)], fillcolor=fillcolor)
    assert f"fillcolor:{fillcolor}" in str(p)


@pytest.mark.parametrize("geodesic", [True, False])
def test_path_geodesic_truthy(geodesic):
    p = StaticMapPath(points=[(1, 2), (3, 4)], geodesic=geodesic)
    if geodesic:
        assert "geodesic:" in str(p)
    else:
        assert "geodesic:" not in str(p)


def test_path_combined():
    p = StaticMapPath(
        points=[(1, 2), (3, 4)], weight=5, color="red", fillcolor="blue", geodesic=True
    )
    s = str(p)
    for token in ("weight:5", "color:red", "fillcolor:blue", "geodesic:True", "1,2", "3,4"):
        assert token in s


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["png8", "png", "png32", "gif", "jpg", "jpg-baseline"])
def test_image_format_supported(fmt):
    assert fmt in MAPS_IMAGE_FORMATS


@pytest.mark.parametrize("bad", ["bmp", "tif", "webp", "svg", ""])
def test_image_format_unsupported(bad):
    assert bad not in MAPS_IMAGE_FORMATS


@pytest.mark.parametrize("mt", ["roadmap", "satellite", "terrain", "hybrid"])
def test_maptype_supported(mt):
    assert mt in MAPS_MAP_TYPES


@pytest.mark.parametrize("bad", ["street", "topo", "watercolor", ""])
def test_maptype_unsupported(bad):
    assert bad not in MAPS_MAP_TYPES


# ---------------------------------------------------------------------------
# static_map (integration with mocked responses)
# ---------------------------------------------------------------------------

def _add_map_response():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/staticmap",
        body=b"\x89PNG\r\n",
        status=200,
        content_type="image/png",
    )


@responses.activate
def test_static_map_requires_center_or_markers():
    c = googlemaps.Client(key="AIzaasdf")
    with pytest.raises(ValueError):
        list(c.static_map(size=(400, 400)))


@responses.activate
def test_static_map_with_center_and_zoom():
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    list(c.static_map(size=(400, 400), center=(1, 2), zoom=5))
    url = responses.calls[0].request.url
    assert "size=400x400" in url
    assert "center=1%2C2" in url or "center=1,2" in url
    assert "zoom=5" in url


@responses.activate
def test_static_map_with_markers_no_center():
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    markers = StaticMapMarker(locations=[(1, 2)])
    list(c.static_map(size=(400, 400), markers=markers))
    assert "markers=" in responses.calls[0].request.url


@responses.activate
@pytest.mark.parametrize("fmt", sorted(MAPS_IMAGE_FORMATS))
def test_static_map_valid_format(fmt):
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, format=fmt))


@responses.activate
def test_static_map_invalid_format():
    c = googlemaps.Client(key="AIzaasdf")
    with pytest.raises(ValueError):
        list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, format="bmp"))


@responses.activate
@pytest.mark.parametrize("mt", sorted(MAPS_MAP_TYPES))
def test_static_map_valid_maptype(mt):
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, maptype=mt))


@responses.activate
def test_static_map_invalid_maptype():
    c = googlemaps.Client(key="AIzaasdf")
    with pytest.raises(ValueError):
        list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, maptype="watercolor"))


@responses.activate
@pytest.mark.parametrize("scale", [1, 2, 4])
def test_static_map_scale(scale):
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, scale=scale))
    assert f"scale={scale}" in responses.calls[0].request.url


@responses.activate
@pytest.mark.parametrize("language", ["en", "fr", "de", "es", "ja"])
def test_static_map_language(language):
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, language=language))
    assert f"language={language}" in responses.calls[0].request.url


@responses.activate
@pytest.mark.parametrize("region", ["us", "uk", "au", "jp"])
def test_static_map_region(region):
    _add_map_response()
    c = googlemaps.Client(key="AIzaasdf")
    list(c.static_map(size=(1, 1), center=(0, 0), zoom=1, region=region))
    assert f"region={region}" in responses.calls[0].request.url
