from building3d.config import MESH_DELTA
from building3d.geom.point import Point
from building3d.geom.tetrahedron import tetrahedron_volume


def minimum_tetra_volume(delta: float = MESH_DELTA) -> float:
    """Calculate minimum tetrahedron volume for mesh quality assurance."""
    ref_volume = tetrahedron_volume(
        Point(0.0, 0.0, 0.0),
        Point(delta, 0.0, 0.0),
        Point(0.0, delta, 0.0),
        Point(0.0, 0.0, delta),
    )
    min_vol = ref_volume / 50.0
    return min_vol
