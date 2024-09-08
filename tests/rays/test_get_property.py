import pytest

from building3d.simulators.rays.properties import get_property


@pytest.fixture
def acoustic_properties():
    properties = {
        "absorption": {
            "b/zone/solid_1/floor": 0.1,
            "b/zone/solid_1/wall-0/wall-0": 0.2,
            "b/zone/solid_1/wall-1": 0.3,
            "b/zone/solid_1/wall-2": 0.4,
            "b/zone/solid_1/wall-3": 0.5,
            "b/zone/solid_1/roof": 0.6,
            "b/zone/solid_2": 0.7,
            "b/zone/solid_3": 0.8,
            "b/zone/solid_4": 0.9,
        },
    }
    return properties


def test_get_property_polygon_from_parent_wall(acoustic_properties):
    t = "b/zone/solid_1/floor/floor"
    v = get_property(t, "absorption", acoustic_properties)
    assert v == 0.1
    assert t in acoustic_properties["absorption"]


def test_get_property_polygon_direct(acoustic_properties):
    t = "b/zone/solid_1/wall-0/wall-0"
    v = get_property(t, "absorption", acoustic_properties)
    assert v == 0.2
    assert t in acoustic_properties["absorption"]


def test_get_property_polygon_from_parent_solid(acoustic_properties):
    t = "b/zone/solid_4/wall-0/wall-0"
    v = get_property(t, "absorption", acoustic_properties)
    assert v == 0.9
    assert t in acoustic_properties["absorption"]


def test_get_property_too_long_path_raise_error(acoustic_properties):
    t = "b/zone/solid_4/wall-0/wall-0/xxx/xxx"
    with pytest.raises(ValueError):
        _ = get_property(t, "absorption", acoustic_properties)


def test_get_property_too_short_path_raise_error(acoustic_properties):
    t = "b/zone/solid_4/wall-0"
    with pytest.raises(ValueError):
        _ = get_property(t, "absorption", acoustic_properties)


def test_get_property_trailing_path_separator_raise_error(acoustic_properties):
    t = "b/zone/solid_4/wall-0/"
    with pytest.raises(ValueError):
        _ = get_property(t, "absorption", acoustic_properties)
