import numpy as np
import pytest

from building3d import random_id
from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.mesh.tetrahedralization import delaunay_tetrahedralization
from building3d.mesh.triangulation import delaunay_triangulation


def test_tetrahedralization():
    delta = 1.0

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 0.5)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.5)

    floor_id = random_id()
    wall0_id = random_id()
    wall1_id = random_id()
    wall2_id = random_id()
    wall3_id = random_id()
    roof_id = random_id()

    floor = Wall(floor_id, [p0, p3, p2, p1])
    wall0 = Wall(wall0_id, [p0, p1, p5, p4])
    wall1 = Wall(wall1_id, [p1, p2, p6, p5])
    wall2 = Wall(wall2_id, [p3, p7, p6, p2])
    wall3 = Wall(wall3_id, [p0, p4, p7, p3])
    roof = Wall(roof_id, [p4, p5, p6, p7])

    floor_vertices, floor_faces = delaunay_triangulation(floor)
    wall0_vertices, wall0_faces = delaunay_triangulation(wall0)
    wall1_vertices, wall1_faces = delaunay_triangulation(wall1)
    wall2_vertices, wall2_faces = delaunay_triangulation(wall2)
    wall3_vertices, wall3_faces = delaunay_triangulation(wall3)
    roof_vertices, roof_faces = delaunay_triangulation(roof)
    zone = Zone(random_id(), [floor, wall0, wall1, wall2, wall3, roof])

    # If delta is too big, the solid mesh cannot be generated
    with pytest.raises(GeometryError):
        vertices, tetrahedra = delaunay_tetrahedralization(
            sld=zone,
            boundary_vertices={
                floor_id: floor_vertices,
                wall0_id: wall0_vertices,
                wall1_id: wall1_vertices,
                wall2_id: wall2_vertices,
                wall3_id: wall3_vertices,
                roof_id: roof_vertices,
            },
            delta=delta,
        )

    # If delta is small enough, the number of returned vertices will be larger
    # than polygon mesh vertices
    delta = 0.25
    vertices, tetrahedra = delaunay_tetrahedralization(
        sld=zone,
        boundary_vertices={
            floor_id: floor_vertices,
            wall0_id: wall0_vertices,
            wall1_id: wall1_vertices,
            wall2_id: wall2_vertices,
            wall3_id: wall3_vertices,
            roof_id: roof_vertices,
        },
        delta=delta,
    )

    assert len(np.unique(tetrahedra)) == len(
        vertices
    ), "More points used in tetrahedra than available vertices"
    assert (
        np.max(np.array(tetrahedra)) == len(vertices) - 1
    ), "Not all vertices used in the solid mesh"

    # Make sure points are not duplicated
    for i in range(len(vertices) - 1):
        for j in range(i + 1, len(vertices)):
            assert vertices[i] != vertices[j]

    boundary_vertices = (
        floor_vertices
        + wall0_vertices
        + wall1_vertices
        + wall2_vertices
        + wall3_vertices
        + roof_vertices
    )

    assert len(vertices) > len(boundary_vertices)

    # Assert tetrahedra have non-zero volume
    for i, el in enumerate(tetrahedra):
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        vol = tetrahedron_volume(p0, p1, p2, p3)
        min_volume = delta**3 / 50.0
        assert vol > min_volume, f"Volume[{i}]={vol} < minimum ({min_volume})"

    # Assert tetrahedra vertices are not coplanar
    pass
