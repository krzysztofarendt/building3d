from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.geom.building import Building
from building3d.simulators.rays.find_transparent import find_transparent


def test_find_transparent():
    sld_0 = box(1, 1, 1, (0, 0, 0), name="s0")
    sld_1 = box(1, 1, 1, (1, 0, 0), name="s1")
    zon = Zone([sld_0, sld_1], name="z")
    bdg = Building([zon], name="b")

    transp = find_transparent(bdg)
    assert len(transp) == 2
    assert "b/z/s0/wall-1/wall-1" in transp
    assert "b/z/s1/wall-3/wall-3" in transp


if __name__ == "__main__":
    test_find_transparent()
