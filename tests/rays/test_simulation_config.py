import pytest

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.sim.rays.simulation_config import SimulationConfig
from building3d.io.arrayformat import to_array_format


def test_simulation_config():
    """

    The polygon and wall names in each "box" are hardcoded:
    - floor
    - wall_0 (XZ at ymin)
    - wall_1 (YZ at xmax)
    - wall_2 (XZ at ymax)
    - wall_3 (YZ at xmin)
    - roof
    """
    solid_0 = box(1, 1, 1, (0, 0, 0), "s0")
    solid_1 = box(1, 1, 1, (1, 0, 0), "s1")
    solid_2 = box(1, 1, 1, (1, 1, 0), "s2")
    zone = Zone([solid_0, solid_1, solid_2], "z")
    building = Building([zone], "b")

    sim_cfg = SimulationConfig(building)
    default_absorption = sim_cfg.surfaces["absorption"]["default"]
    sim_cfg.set_surface_param("absorption", "b/z/s0", 1.0, building)
    assert sim_cfg.surfaces["absorption"]["b/z/s0/floor/floor"] == 1.0
    assert sim_cfg.surfaces["absorption"]["b/z/s0/wall_0/poly_0"] == 1.0
    assert sim_cfg.surfaces["absorption"]["b/z/s0/wall_1/poly_1"] == 1.0
    assert sim_cfg.surfaces["absorption"]["b/z/s0/wall_2/poly_2"] == 1.0
    assert sim_cfg.surfaces["absorption"]["b/z/s0/wall_3/poly_3"] == 1.0
    assert sim_cfg.surfaces["absorption"]["b/z/s0/ceiling/ceiling"] == 1.0

    sim_cfg.set_surface_param("absorption", "b/z/s1/wall_0", 2.0, building)
    assert sim_cfg.surfaces["absorption"]["b/z/s1/floor/floor"] == default_absorption
    assert sim_cfg.surfaces["absorption"]["b/z/s1/wall_0/poly_0"] == 2.0
    assert sim_cfg.surfaces["absorption"]["b/z/s1/wall_1/poly_1"] == default_absorption
    assert sim_cfg.surfaces["absorption"]["b/z/s1/wall_2/poly_2"] == default_absorption
    assert sim_cfg.surfaces["absorption"]["b/z/s1/wall_3/poly_3"] == default_absorption
    assert sim_cfg.surfaces["absorption"]["b/z/s1/ceiling/ceiling"] == default_absorption

    with pytest.raises(RuntimeError):
        # Polygons are not numbered yet, because the building was not converted to the array format
        # An exception should be raised
        surf_vals = sim_cfg.surface_params_to_array("absorption", building)

    # Convert the building to the array format to number the polygons
    _ = to_array_format(building)

    surf_vals = sim_cfg.surface_params_to_array("absorption", building)

    polygon_paths = building.get_polygon_paths()
    for pp in polygon_paths:
        poly = building.get(pp)
        assert isinstance(poly, Polygon)
        assert surf_vals[poly.num] == sim_cfg.surfaces["absorption"][pp]
