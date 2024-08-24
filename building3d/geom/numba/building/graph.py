from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.building import Building


def graph(bdg: Building) -> dict[str, str | None]:
    g = {}
    adj_solids = bdg.find_adjacent_solids()
    # breakpoint()

    for zn, zv in bdg.children.items():
        for sn, sv in zv.children.items():
            for wn, wv in sv.children.items():
                for pn, pv in wv.children.items():
                    found = False

                    ...


