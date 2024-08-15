from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.mesh import vstack_mesh


def get_mesh_from_walls(walls: list[Wall]) -> tuple[PointType, IndexType]:
    """Get vertices and faces of this solid's walls.

    This function returns faces generated by the ear-clipping algorithm.

    Args:
        walls: list of Wall instances

    Return:
        tuple of vertices, shaped (num_pts, 3), and faces, shaped (num_tri, 3)
    """
    object_meshes = tuple(w.get_mesh() for w in walls)
    t_pts = tuple(msh[0] for msh in object_meshes)
    t_tri = tuple(msh[1] for msh in object_meshes)
    return vstack_mesh(t_pts, t_tri)