import logging

from building3d.geom.point import Point
from building3d.geom.tetrahedron import tetrahedron_volume


logger = logging.getLogger(__name__)


def total_volume(vertices: list[Point], elements: list[tuple[int, ...]]) -> float:
    """Return the sum of volumes of all mesh tetrahedra."""
    tot_vol = 0
    for el in elements:
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        tot_vol += tetrahedron_volume(p0, p1, p2, p3)

    return tot_vol
