import numpy as np

from building3d.geom.polygon.crossing import is_polygon_crossing_cube


def test_is_polygon_crossing_cube():
    """
    This unit test covers various scenarios:

    1. A polygon completely inside the cube
    2. A polygon completely outside the cube
    3. A polygon intersecting the cube
    4. A polygon on the edge of the cube
    5. A polygon very close to but not touching the cube (within epsilon)
    """

    # Test case 1: Polygon completely inside the cube
    pts1 = np.array([(0.5, 0.5, 0.5), (0.7, 0.5, 0.5), (0.6, 0.7, 0.5)])
    tri1 = np.array([(0, 1, 2)])
    min_xyz1 = (0, 0, 0)
    max_xyz1 = (1, 1, 1)
    assert is_polygon_crossing_cube(pts1, tri1, min_xyz1, max_xyz1) == True

    # Test case 2: Polygon completely outside the cube
    pts2 = np.array([(1.5, 1.5, 1.5), (1.7, 1.5, 1.5), (1.6, 1.7, 1.5)])
    tri2 = np.array([(0, 1, 2)])
    min_xyz2 = (0, 0, 0)
    max_xyz2 = (1, 1, 1)
    assert is_polygon_crossing_cube(pts2, tri2, min_xyz2, max_xyz2) == False

    # Test case 3: Polygon intersecting the cube
    pts3 = np.array([(0.5, 0.5, 0.5), (1.5, 0.5, 0.5), (1.0, 1.5, 0.5)])
    tri3 = np.array([(0, 1, 2)])
    min_xyz3 = (0, 0, 0)
    max_xyz3 = (1, 1, 1)
    assert is_polygon_crossing_cube(pts3, tri3, min_xyz3, max_xyz3) == True

    # Test case 4: Polygon on the edge of the cube
    pts4 = np.array([(0, 0, 0), (1, 0, 0), (0.5, 0, 1)])
    tri4 = np.array([(0, 1, 2)])
    min_xyz4 = (0, 0, 0)
    max_xyz4 = (1, 1, 1)
    assert is_polygon_crossing_cube(pts4, tri4, min_xyz4, max_xyz4) == True

    # Test case 5: Polygon very close to but not touching the cube (within epsilon)
    eps = 1e-6
    pts5 = np.array(
        [
            (-eps / 2, -eps / 2, -eps / 2),
            (1 + eps / 2, -eps / 2, -eps / 2),
            (0.5, 1 + eps / 2, -eps / 2),
        ]
    )
    tri5 = np.array([(0, 1, 2)])
    min_xyz5 = (0, 0, 0)
    max_xyz5 = (1, 1, 1)
    assert is_polygon_crossing_cube(pts5, tri5, min_xyz5, max_xyz5) == True
