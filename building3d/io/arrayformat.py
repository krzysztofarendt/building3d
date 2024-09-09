import numpy as np

from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.types import FLOAT, INT


def to_array_format(bdg: Building) -> tuple:
    """Converts Building to a numba-friendly format.

    The building is represented as a tuple of arrays defining
    points, faces, polygons, walls, solids, and zones.

    The tuple structure is as follows:
    - array of points, shape (num_points, 3)
    - array of face point indices, shape (num_faces, 3)
    - array of polygon faces indices, shape (num_faces, )
    - array of wall face indices, shape (num_faces, )
    - array of solid face indices, shape (num_faces, )
    - array of zone face indices, shape (num_faces, )

    Args:
        bdg: Building instance

    Returns:
        tuple of arrays as described above
    """
    _, _, _, _, num_faces, num_pts = count_objects(bdg)

    points = np.zeros((num_pts, 3), dtype=FLOAT)
    faces = np.zeros((num_faces, 3), dtype=INT)
    polygons = np.zeros(num_faces, dtype=INT)
    walls = np.zeros(num_faces, dtype=INT)
    solids = np.zeros(num_faces, dtype=INT)
    zones = np.zeros(num_faces, dtype=INT)

    pt_offset = 0
    face_offset = 0
    for z in bdg.zones.values():
        for s in z.solids.values():
            for w in s.walls.values():
                for p in w.polygons.values():

                    points[pt_offset:pt_offset + p.pts.shape[0]] = p.pts.copy()
                    pt_offset += p.pts.shape[0]

                    faces[face_offset:face_offset + p.tri.shape[0]] = p.tri.copy() + face_offset

                    for fi in range(face_offset, face_offset + p.tri.shape[0]):
                        polygons[fi] = p.num
                        walls[fi] = w.num
                        solids[fi] = s.num
                        zones[fi] = z.num

                    face_offset += p.tri.shape[0]

    return points, faces, polygons, walls, solids, zones


def from_array_format(points, faces, polygons, walls, solids, zones) -> Building:
    """Creates a building from the array format.

    Object UUIDs and names are not part of the format, so they will be random.

    Args:
        points: array of points
        faces: array of face point indices
        polygons: array of polygon face indices
        walls: array of wall face indices
        solids: array of solid face indices
        zones: array of zone face indices

    Return:
        a new Building instance
    """
    # Create polygons
    ...  # TODO


def count_objects(bdg: Building) -> tuple[int, int, int, int, int, int]:
    """Returns a tuple with the number of: zones, solids, walls, polygons, faces, points."""
    num_zones = 0
    num_solids = 0
    num_walls = 0
    num_polys = 0
    num_faces = 0
    num_pts = 0

    for z in bdg.zones.values():
        num_zones += 1
        for s in z.solids.values():
            num_solids += 1
            for w in s.walls.values():
                num_walls += 1
                for p in w.polygons.values():
                    num_polys += 1
                    num_faces += p.tri.shape[0]
                    num_pts += p.pts.shape[0]

    return num_zones, num_solids, num_walls, num_polys, num_faces, num_pts
