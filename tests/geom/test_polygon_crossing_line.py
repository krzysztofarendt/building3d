import numpy as np
from building3d.geom.polygon.crossing import is_line_segment_crossing_polygon
from building3d.geom.types import INT, FLOAT


def test_line_segment_crosses_polygon():
    # Define a simple square polygon in the XY plane
    pts = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0]
    ], dtype=FLOAT)

    # Define the triangulation of the square
    tri = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ], dtype=INT)

    # Test cases
    test_cases = [
        # Segment crosses the polygon
        (np.array([0.5, -1.0, 1.0]), np.array([0.5, 2.0, -1.0]), True),
        # Segment doesn't cross (perpendicular, within the projection, but doesn't touch)
        (np.array([0.5, 0.5, 1.0]), np.array([0.5, 0.5, 2.0]), False),
        # Segment doesn't cross (outside the polygon)
        (np.array([2.0, 2.0, 1.0]), np.array([2.0, 2.0, -1.0]), False),
        # Segment touches the edge of the polygon
        (np.array([0.0, 0.5, 1.0]), np.array([0.0, 0.5, -1.0]), True),
        # Segment touches a vertex of the polygon
        (np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, -1.0]), True),
        # Segment goes over one edge (parallel to the polygon)
        (np.array([0.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]), False),
        # Segment goes over one edge (parallel to the polygon)
        (np.array([0.0, -1.0, 0.0]), np.array([0.0, 2.0, 0.0]), False),
    ]

    for seg_start, seg_end, expected in test_cases:
        result = is_line_segment_crossing_polygon(seg_start, seg_end, pts, tri)
        assert result == expected, f"Failed for segment {seg_start} to {seg_end}"

    # Test with a very small epsilon
    small_epsilon_result = is_line_segment_crossing_polygon(
        np.array([0.5, -1.0, 1e-10]), np.array([0.5, 2.0, -1e-10]), pts, tri, epsilon=1e-12
    )
    assert small_epsilon_result == True, "Failed for small epsilon test"
