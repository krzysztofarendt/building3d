import numpy as np
from numba import njit

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.types import FLOAT
from building3d.geom.types import INT
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


def to_array_format(bdg: Building) -> tuple:
    """Converts Building to a numba-friendly array format.

    The building is represented as a tuple of arrays defining
    points, faces, polygons, walls, solids, and zones.

    Note:
        This functions the class variables `num`,
        which should be 0 before constructing a new building.
        Counter reset might be needed if you have many buildings.

    The tuple structure is as follows:
    - points:   array of points, shape `(num_points, 3)`
    - faces:    array mapping points to faces, shape `(num_faces, 3)`
    - polygons: array mapping faces to polygons, shape `(num_faces, )`
    - walls:    array mapping polygons to walls, shape `(num_polygons, )`
    - solids:   array mapping walls to solids, shape `(num_walls, )`
    - zones:    array mapping solids to zones, shape `(num_solids, )`

    Args:
        bdg: Building instance

    Returns:
        tuple of arrays as described above
    """
    num_zones, num_solids, num_walls, num_polys, num_faces, num_pts = count_objects(bdg)

    points = np.zeros((num_pts, 3), dtype=float)
    faces = np.zeros((num_faces, 3), dtype=int)
    polygons = np.zeros(num_faces, dtype=int)
    walls = np.zeros(num_polys, dtype=int)
    solids = np.zeros(num_walls, dtype=int)
    zones = np.zeros(num_solids, dtype=int)

    pn = 0
    wn = 0
    sn = 0
    zn = 0

    pt_offset = 0
    face_offset = 0
    for z in bdg.zones.values():
        for s in z.solids.values():
            # Map solids to zones
            zones[sn] = zn

            for w in s.walls.values():
                # Map walls to solids
                solids[wn] = sn

                for p in w.polygons.values():
                    # Map polygons to walls
                    walls[pn] = wn

                    # Add points
                    points[pt_offset : pt_offset + p.pts.shape[0]] = p.pts.copy()

                    # Map points to faces
                    faces[face_offset : face_offset + p.tri.shape[0]] = (
                        p.tri.copy() + pt_offset
                    )

                    # Map faces to polygons
                    for fi in range(face_offset, face_offset + p.tri.shape[0]):
                        polygons[fi] = pn

                    pt_offset += p.pts.shape[0]
                    face_offset += p.tri.shape[0]

                    pn += 1
                wn += 1
            sn += 1
        zn += 1

    return points, faces, polygons, walls, solids, zones


def from_array_format(
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    solids: IndexType,
    zones: IndexType,
) -> Building:
    """Creates a building from the array format.

    Object UUIDs and names are not part of the format, so they will be random.

    Args:
        points:   array of points, shape `(num_points, 3)`
        faces:    array mapping points to faces, shape `(num_faces, 3)`
        polygons: array mapping faces to polygons, shape `(num_faces, )`
        walls:    array mapping polygons to walls, shape `(num_polys, )`
        solids:   array mapping walls to solids, shape `(num_walls, )`
        zones:    array mapping solids to zones, shape `(num_solids, )`

    Return:
        a new Building instance
    """
    # Create polygons
    num_polys = len(walls)
    num_walls = len(solids)
    num_solids = len(zones)
    num_zones = np.max(zones) + 1

    poly_obj = []
    for pi in range(num_polys):
        pts, tri = get_polygon_points_and_faces(points, faces, polygons, pi)
        poly_obj.append(Polygon(pts, tri=tri))

    # Create walls
    wall_obj = []
    for wi in range(num_walls):
        wp = [pl for i, pl in enumerate(poly_obj) if walls[i] == wi]
        wall_obj.append(Wall(wp))
    assert len(wall_obj) == num_walls

    # Create solids
    sld_obj = []
    for si in range(num_solids):
        sw = [wl for i, wl in enumerate(wall_obj) if solids[i] == si]
        sld_obj.append(Solid(sw))
    assert len(sld_obj) == num_solids

    # Create zones
    zone_obj = []
    for zi in range(num_zones):
        zs = [sld for i, sld in enumerate(sld_obj) if zones[i] == zi]
        zone_obj.append(Zone(zs))

    return Building(zone_obj)


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


@njit
def get_polygon_points_and_faces(
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    poly_num: int,
) -> tuple[PointType, IndexType]:
    """Reconstruct arrays of points and faces for a chosen polygon.

    Args:
        points: array of points in the building
        faces: array of all faces in the building
        polygons: array mapping faces to polygons, shape `(num_faces, )`
        poly_num: selected polygon number

    Returns:
        tuple of points and faces
    """
    # Collect face indices of the chosen polygon
    tri_index = []
    for fci, pli in enumerate(polygons):
        if pli == poly_num:
            tri_index.append(fci)

    # Collect point indices of the chosen polygon
    pt_set = set()
    for fci, f in enumerate(faces):
        if fci in tri_index:
            pt_set.add(int(f[0]))
            pt_set.add(int(f[1]))
            pt_set.add(int(f[2]))
    pt_index = sorted(list(pt_set))

    # Map point indices from `points` to output indices in `poly_pts`
    # This is needed to avoid a situation like this:
    # > poly_pts
    # array([[0., 0., 0.],
    #        [1., 0., 0.],
    #        [1., 0., 1.],
    #        [0., 0., 1.]])
    # > poly_tri
    # array([[7, 4, 5],  <- Indices larger than the shape of poly_pts
    #        [7, 5, 6]])
    recount = {}
    new_num = 0
    for pti in pt_index:
        recount[pti] = new_num
        new_num += 1

    # Create arrays of points and faces for the chosen polygon
    poly_pts = np.zeros((len(pt_index), 3), dtype=FLOAT)
    for i in range(len(pt_index)):
        poly_pts[i] = points[pt_index[i]]

    poly_tri = np.zeros((len(tri_index), 3), dtype=INT)
    for i in range(len(tri_index)):
        for j in range(3):
            # Cannot take original index, because poly_pts.shape[0] < points.shape[0]
            # So the index must be "recounted"
            poly_tri[i, j] = recount[faces[tri_index[i], j]]

    return poly_pts, poly_tri
