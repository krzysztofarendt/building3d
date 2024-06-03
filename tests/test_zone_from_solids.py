from building3d.geom.building import Building
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.solid import Solid
from building3d.geom.zone import Zone


def test_zone_from_solids():
    """Code taken from examples/example_2.py."""
    xa = 0.0
    xb = 10.0
    xc = 3.0
    xd = 4.0
    xe = 6.0
    xf = 7.5

    ya = 0.0
    yb = 5.0
    yc = 1.5

    za = 0.0
    zb = 3.0
    zc = 5.0
    zd = 1.0
    ze = 2.0

    # WALL_A
    p_aaa = Point(xa, ya, za)
    p_baa = Point(xb, ya, za)
    p_caa = Point(xc, ya, za)
    p_daa = Point(xd, ya, za)
    p_aab = Point(xa, ya, zb)
    p_cae = Point(xc, ya, ze)
    p_dae = Point(xd, ya, ze)
    p_ead = Point(xe, ya, zd)
    p_eae = Point(xe, ya, ze)
    p_fae = Point(xf, ya, ze)
    p_fad = Point(xf, ya, zd)
    p_bab = Point(xb, ya, zb)

    # WALL_B
    # p_baa - already defined
    # p_bab - already defined
    p_bba = Point(xb, yb, za)
    p_bbb = Point(xb, yb, zb)

    # WALL_C
    # p_bba - already defined
    # p_bbb - already defined
    p_aba = Point(xa, yb, za)
    p_abb = Point(xa, yb, zb)

    # WALL_D
    # p_aaa - already defined
    # p_aba - already defined
    # p_abb - already defined
    # p_aab - already defined

    # Roof
    p_acc = Point(xa, yc, zc)
    p_bcc = Point(xb, yc, zc)

    # Floor 0
    wall_a_poly = Polygon([p_aaa, p_baa, p_bab, p_aab], "wall_a_poly")
    wall_b_poly = Polygon([p_baa, p_bba, p_bbb, p_bab], "wall_b_poly")
    wall_c_poly = Polygon([p_aba, p_abb, p_bbb, p_bba], "wall_c_poly")
    wall_d_poly = Polygon([p_aaa, p_aab, p_abb, p_aba], "wall_d_poly")
    door_poly = Polygon([p_caa, p_daa, p_dae, p_cae], "door_poly")
    window_poly = Polygon([p_ead, p_fad, p_fae, p_eae], "window_poly")
    floor_0_poly = Polygon([p_aaa, p_aba, p_bba, p_baa], "floor_0_poly")
    ceiling_poly = Polygon([p_aab, p_bab, p_bbb, p_abb], "ceiling_poly")

    wall_bcd = Wall([wall_b_poly, wall_c_poly, wall_d_poly], "wall_bcd")
    wall_a = Wall([wall_a_poly], "wall_a")
    wall_a.add_polygon(door_poly, parent=wall_a_poly.name)
    wall_a.add_polygon(window_poly, parent=wall_a_poly.name)
    floor_0 = Wall([floor_0_poly], "floor_0")
    ceiling = Wall([ceiling_poly], "ceiling")

    zone = Zone()
    solid1 = Solid(walls=[wall_a, wall_bcd, floor_0, ceiling], name="solid_floor_0")
    zone.add_solid_instance(solid1)

    # Floor 1
    floor_1_poly = Polygon([p_aab, p_abb, p_bbb, p_bab], "floor_1_poly")
    roof_a_poly = Polygon([p_aab, p_bab, p_bcc, p_acc], "roof_a_poly")
    roof_b_poly = Polygon([p_bab, p_bbb, p_bcc], "roof_b_poly")
    roof_c_poly = Polygon([p_abb, p_acc, p_bcc, p_bbb], "roof_c_poly")
    roof_d_poly = Polygon([p_aab, p_acc, p_abb], "roof_d_poly")

    floor_1 = Wall([floor_1_poly], "floor_1")
    roof = Wall([roof_a_poly, roof_b_poly, roof_c_poly, roof_d_poly], "roof")

    solid2 = Solid(walls=[floor_1, roof], name="solid_floor_1")
    zone.add_solid_instance(solid2)

    assert len(zone.solids) == 2
    assert len(zone.solids[solid1.name].polygons()) == 6
    assert len(zone.solids[solid2.name].polygons()) == 5

    # Make building instance
    building = Building(name="example_2")
    building.add_zone_instance(zone)
