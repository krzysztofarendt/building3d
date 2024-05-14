from building3d.config import MESH_DELTA


def minimum_triangle_area(delta: float = MESH_DELTA) -> float:
    """Calculate min. face area for PolyMesh quality assurance."""
    return delta ** 2 / 8.0
