from collections import defaultdict
import logging

import numpy as np
from scipy.spatial import Delaunay

from building3d.mesh.exceptions import MeshError
from building3d.geom.point import Point
from building3d.geom.solid import Solid
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.tetrahedron import tetrahedron_centroid
from building3d.mesh.quality.min_tetra_volume import minimum_tetra_volume
from building3d.mesh.quality.purge_mesh import purge_mesh
from building3d.mesh.quality.count_tetra_neighbors import count_tetra_neighbors
from building3d.mesh.triangulation import delaunay_triangulation
from building3d import random_within
from building3d.config import MESH_JOGGLE
from building3d.config import MESH_DELTA
from building3d.config import TETRA_MAX_TRIES


logger = logging.getLogger(__name__)


def imbalance(vols):
    assert len(vols) > 0, "Empty sequence passed"
    return max(vols) / min(vols)


def recalc_selected_volumes(
    volumes: dict[int, float],
    indices: list[int],
    vertices: list[Point],
    elements: list[tuple[int, ...]],
) -> dict[int, float]:
    """Calculated volumes of selected elements.

    Args:
        volumes: dictionary of volumes (index->volume) to be updated, can be empty
        indices: indices of elements to be recalculated
        vertices: list of mesh points
        elements: list of elements

    Return:
        dictionary {index: volume}
    """
    for i in indices:
        p0 = vertices[elements[i][0]]
        p1 = vertices[elements[i][1]]
        p2 = vertices[elements[i][2]]
        p3 = vertices[elements[i][3]]
        volumes[i] = tetrahedron_volume(p0, p1, p2, p3)
    return volumes


def get_invalid_points(
    vertices: list[Point],
    tetrahedra: list[tuple],
    restricted: list[int],
    min_volume: float,
) -> list[int]:
    """Return a list of indices of vertices connected to imbalanced elements.

    An element is invalid if:
    - volumes of connected elements are imbalanced
    - at least one connected element has volume below threshold

    Args:
        vertices: list of points
        tetrahedra: list of elements
        restricted: list of indices which shouldn't be removed
        min_volume: volume threshold below which element is considered invalid

    Return:
        list of indices of vertices connected to invalid elements
    """
    invalid = []
    # Create a map {vertex number: list of element indices}
    vertex_to_elems = defaultdict(list)

    for i, el in enumerate(tetrahedra):
        for vertex_index in el:
            vertex_to_elems[vertex_index].append(i)

    for i in range(len(vertices)):
        if i in restricted:
            continue

        # Calculate element volumes
        # (need to calculate on demand because mesh may have changed)
        volumes = recalc_selected_volumes(
            volumes={},
            indices=[x for x in range(len(tetrahedra))],
            vertices=vertices,
            elements=tetrahedra,
        )

        # Find connected elements
        connected_elements = vertex_to_elems[i]

        # Find their volumes
        connected_volumes = [volumes[x] for x in connected_elements]

        # If imbalance higher than threshold, add the vertix index to list
        imbalance_threshold = 100  # TODO: Add to config
        if imbalance(connected_volumes) > imbalance_threshold:
            invalid.append(i)
        elif min(connected_volumes) < min_volume:
            invalid.append(i)

    return invalid


def delaunay_tetrahedralization(
    sld: Solid,
    boundary_vmap: dict[str, list[Point]],
    delta: float = MESH_DELTA,
) -> tuple[list[Point], list[tuple[int, ...]]]:
    """Constrained Delaunay tetrahedralization of a solid.

    Args:
        sld: solid to be meshed
        boundary_v: dict with polygon names and respective mesh vertices
        delta: approximate mesh size

    Return:
        (list of mesh points, list of tetrahedra)
    """
    logger.debug(f"Starting tetrahedralization of {sld} with {delta=}")
    logger.debug(
        f"Number of polygons passed in boundary_vertices = {len(boundary_vmap.keys())}"
    )
    for name in boundary_vmap:
        logger.debug(f"boundary vertifces for {name} = {len(boundary_vmap[name])}")

    # Boundary points
    boundary_vertices = []
    boundary_pts = set()

    min_volume = minimum_tetra_volume(delta)
    logger.debug(f"Assuming tetrahedron min. volume = {min_volume}")

    # Collect meshes from the boundary polygons
    # -> boundary_vertices, boundary_faces
    if len(boundary_vmap.keys()) == 0:
        logger.debug(
            "Need to create boundary mesh via triangulation of the surrounding polygons"
        )
        for wall in sld.get_walls():
            for poly in wall.get_polygons(children=False):
                polymesh_vertices, _ = delaunay_triangulation(poly, delta=delta)
                for pt in polymesh_vertices:
                    if pt not in boundary_vertices:
                        boundary_vertices.append(pt)
                        boundary_pts.add(pt)
    else:
        logger.debug("Will take boundary vertices provided by the user")
        for _, poly_points in boundary_vmap.items():
            for pt in poly_points:
                # Do not add duplicate points
                if pt not in boundary_vertices:
                    boundary_vertices.append(pt)
                    boundary_pts.add(pt)

    logger.debug("Add new points inside the solid")
    bbox_pmin, bbox_pmax = sld.bounding_box()
    xmin = bbox_pmin.x
    ymin = bbox_pmin.y
    zmin = bbox_pmin.z
    xmax = bbox_pmax.x
    ymax = bbox_pmax.y
    zmax = bbox_pmax.z

    # Make sure delta smaller than bbox dimensions
    if delta >= xmax - xmin or delta >= ymax - ymin or delta >= zmax - zmin:
        raise MeshError(
            f"Solid {sld.name} cannot be meshed due to too large delta ({delta})"
        )

    xgrid = np.arange(xmin + delta, xmax, delta)
    ygrid = np.arange(ymin + delta, ymax, delta)
    zgrid = np.arange(zmin + delta, zmax, delta)

    # List of all mesh points (including boundary points)
    vertices = []
    vertices.extend(boundary_vertices)

    interior_vertices = []
    for x in xgrid:
        for y in ygrid:
            for z in zgrid:
                pt = Point(
                    x + random_within(MESH_JOGGLE * delta),
                    y + random_within(MESH_JOGGLE * delta),
                    z + random_within(MESH_JOGGLE * delta),
                )
                # Check if point is inside solid
                if sld.is_point_inside(pt):
                    # Check if point is not too close to the boundary polygons
                    distance_to_boundary_ok = True
                    for poly in sld.get_polygons():
                        if poly.distance_point_to_polygon(pt) < delta / 2:
                            # It is too close to at least one polygon, so shouldn't be used
                            distance_to_boundary_ok = False
                            break
                    if distance_to_boundary_ok:
                        interior_vertices.append(pt)

    vertices.extend(interior_vertices)

    logger.debug(f"Number of mesh vertices = {len(vertices)}")

    mesh_ok = False
    pass_num = 0
    tetrahedra = []

    while not mesh_ok:
        pass_num += 1
        logger.debug(f"Meshing pass number {pass_num}")

        if pass_num > TETRA_MAX_TRIES:
            raise MeshError(f"Meshing failed after {pass_num} passes")

        # Delaunay
        pts_arr = np.array([[p.x, p.y, p.z] for p in vertices])

        logger.debug(f"Delaunay pass #{pass_num}")
        logger.debug(f"Passing point array with shape {pts_arr.shape}")
        delaunay = Delaunay(pts_arr, qhull_options="Qt", incremental=False)

        # List comprehension to cast type to list[tuple[int, int, int, int]] - easier to follow
        tetrahedra = [(v0, v1, v2, v3) for v0, v1, v2, v3 in delaunay.simplices]
        logger.debug(f"Number of mesh tetrahedra in {sld.name} = {len(tetrahedra)}")

        # Check if all points has been used
        unique_indices = np.unique(tetrahedra)
        if len(unique_indices) == len(vertices):
            logger.debug("All vertices have been used. Great!")
        else:
            # raise MeshError("Not all vertices have been used for mesh. Does this ever happen?")
            pass

        # Remove tetrahedra with zero volume
        # TODO: Not sure if it ever happens...
        logger.debug("Attempting to find and remove elements with zero volume")
        zero_volume_index = []
        for i, el in enumerate(tetrahedra):
            p0 = vertices[el[0]]
            p1 = vertices[el[1]]
            p2 = vertices[el[2]]
            p3 = vertices[el[3]]
            vol = tetrahedron_volume(p0, p1, p2, p3)
            if np.isclose(vol, 0):
                zero_volume_index.append(i)

        if len(zero_volume_index) > 0:  # TODO: Remove
            print(
                "!!! ZERO VOLUME ELEMENTS REMOVED !!! I DID NOT KNOW IT EVER HAPPENS! :)"
            )

        logger.debug(
            f"Number of removed zero volume elements = {len(zero_volume_index)}"
        )
        tetrahedra = [
            el for i, el in enumerate(tetrahedra) if i not in zero_volume_index
        ]
        vertices, tetrahedra = purge_mesh(vertices, tetrahedra)

        # Remove vertices attached to invalid elements
        # TODO: Potentially a bug here. Sometimes the mesh looks like a spider's web
        logger.debug("Attempting to remove points attached to invalid elements")
        num_vert_before = len(vertices)
        boundary_pts_indices = [i for i, p in enumerate(vertices) if p in boundary_pts]
        invalid_vertices = get_invalid_points(
            vertices, tetrahedra, boundary_pts_indices, min_volume
        )
        vertices = [
            vertices[i] for i in range(len(vertices)) if i not in invalid_vertices
        ]

        logger.debug(
            f"Number of vertices before->after removal: {num_vert_before}->{len(vertices)}"
        )
        if len(invalid_vertices) > 0:
            logger.debug("Remeshing needed")
            continue

        # Check if mesh quality is OK
        zero_volume_ok = len(zero_volume_index) == 0
        invalid_vert_ok = len(invalid_vertices) == 0

        mesh_ok = zero_volume_ok and invalid_vert_ok

        logger.debug(f"(Mesh quality) Elements have volume > 0 is {zero_volume_ok}")
        logger.debug(
            f"(Mesh quality) Vertices connected to good elements is {invalid_vert_ok}"
        )
        logger.debug(f"Mesh quality OK? {mesh_ok}")

    # Remove external elements (can happen in non-convex solids)
    logger.debug(
        "Attempting to find and remove elements with outside (non-convex) solid"
    )
    outside_index = []
    for i, el in enumerate(tetrahedra):
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        # Need to check if the centroid is inside the solid
        # (if it is not, this is a concave edge/corner)
        ctr = tetrahedron_centroid(p0, p1, p2, p3)
        point_is_inside = sld.is_point_inside(ctr)
        if not point_is_inside:
            outside_index.append(i)
    logger.debug(f"Number of external elements found = {len(outside_index)}")
    tetrahedra = [el for i, el in enumerate(tetrahedra) if i not in outside_index]
    vertices, tetrahedra = purge_mesh(vertices, tetrahedra)

    # Sanity checks =====================================================================
    logger.debug("Final mesh verification...")

    # Are all mesh vertices used by elements?
    unique_indices = np.unique(tetrahedra)
    assert len(unique_indices) == len(
        vertices
    ), "Not all vertices have been used for mesh!"

    # Are all solid vertices present in the mesh?
    for pt in sld.get_vertices():
        assert pt in vertices, f"Solid point missing: {pt}"

    # Do all interior elements have 4 neighbors?
    # Do all elements have at least 1 neighbor?
    count = count_tetra_neighbors(vertices, tetrahedra)

    # Check if each element has at least 1 neighbor
    assert np.min(count) > 0, "Some mesh element has no neighbors"

    # Find elements which should have 4 neighbors
    # These are the elements that have less than 3 vertices at the boundary
    boundary_pts_indices = set([i for i, p in enumerate(vertices) if p in boundary_pts])
    boundary_elements = set()
    for i, el in enumerate(tetrahedra):
        num_boundary_pt = 0
        for k in range(4):
            if el[k] in boundary_pts_indices:
                num_boundary_pt += 1

        if num_boundary_pt >= 3:
            boundary_elements.add(i)

    count_interior = np.zeros(count.size, dtype=np.int32)
    for i in range(len(count)):
        if i not in boundary_elements:
            count_interior[i] = count[i]

    if np.sum(count_interior) == 0:
        logger.warning(
            "It seems that there are no interior elements in the mesh. "
            + "Is delta large w.r.t. to the solid dimensions?"
        )
    else:
        # If there are interior elements, they need to have 4 neighbors each
        assert set(np.unique(count_interior)) == set(
            [0, 4]
        ), "Some interior elements have < 4 neighbors"

    # End sanity checks =================================================================

    logger.debug(f"Final number of tetrahedra in {sld.name} = {len(tetrahedra)}")
    logger.debug(
        f"Final number of vertices used in {sld.name} = {len(np.unique(tetrahedra))}"
    )

    return vertices, tetrahedra
