"""Polygon class"""
import logging

import numpy as np

from building3d.geom.exceptions import GeometryError
from building3d.geom.exceptions import TriangulationError
from building3d.geom.point import Point
from building3d.geom.line import distance_point_to_edge
from building3d.geom.cloud import are_points_coplanar
from building3d.geom.cloud import points_to_array
from building3d.geom.vector import normal
from building3d.geom.vector import length
from building3d.geom.triangle import triangle_centroid
from building3d.geom.triangle import triangle_area
from building3d.geom.triangle import is_point_inside as is_point_inside_triangle
from building3d.geom.triangle import triangulate
from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.config import GEOM_EPSILON
from building3d.config import GEOM_RTOL
from building3d.util.roll_back import roll_back


logger = logging.getLogger(__name__)


class Polygon:
    """Polygon defined by its vertices (Point instances).

    Notes:
    - Initialization is faster if the first point lays in the convex corner
    - If used as a wall, the points should be ordered counter-clockwise
      w.r.t. the zone that this wall belongs to. Normal vector should point outwards.
    - If triangulation was done before (e.g. when reading from a file), `triangles` can
      be passed as an argument
    """
    def __init__(
        self,
        points: list[Point] = [],
        name: str | None = None,
        uid: str | None = None,
        triangles: list[tuple[int, ...]] = [],
    ):
        """Make polygon.

        If triangles are provided by the user, their correctness is not checked!

        Args:
            points: list of coplanar points, at least 3
            name: polygon name, will be random if `None`
            uid: polygon uid, will be random if `None`
            triangles: polygon faces (if known)

        Return:
            Polygon
        """
        if name is None:
            name = random_id()
        logger.debug(f"Creating polygon: {name}")

        self.name = validate_name(name)
        if uid is None:
            self.uid = random_id()
        else:
            self.uid = uid

        self.points: list[Point] = list(points)
        logger.debug(f"Points added: {self.points}")

        # Verify geometry (>= 3 coplanar points)
        self._verify()

        if len(triangles) > 0:
            # Take triangles from the user
            self.normal = self._normal()
            self.triangles = triangles
        else:
            # Calculate normal vector and triangulate
            # This works in the first iteration if the first point of the polygon
            # is located in the convex corner. If it's located in the non-convex corner
            # then the algorithm reorders the points until triangulation is successful
            triangulation_successful = False
            max_num_tries = len(self.points)
            n_try = 0
            while not triangulation_successful:
                if n_try > max_num_tries:
                    raise TriangulationError(f"Cannot triangulate {self}")
                try:
                    self.normal = self._normal()
                    self.triangles = self._triangulate()
                    triangulation_successful = True
                except TriangulationError as e:
                    logger.warning(self.name + ": " + str(e))
                    logger.warning("Will try to reorder vertices")
                    self.points = roll_back(self.points)
                n_try += 1

            if n_try > 1:
                logger.warning("Vertex reordering helped!")

        self.centroid = self._centroid()
        self.edges = self._edges()
        self.area = self._area()
        logger.info(f"Polygon created: {self}")

    def copy(self, new_name: str | None = None):
        """Return a copy of itself (with a new name).

        Args:
            new_name: polygon name (must be unique within a Wall)

        Return:
            Polygon
        """
        return Polygon([Point(p.x, p.y, p.z) for p in self.points], name=new_name)

    def flip(self, new_name: str | None = None):
        """Copy and flip the polygon. Changes the name.

        Args:
            new_name: polygon name (must be unique within a Wall)

        Return:
            Polygon
        """
        return Polygon(self.points[::-1], name=new_name)

    def slice(
        self,
        points: list[Point],
        name1: str | None = None,
        pt1: Point | None = None,
        name2: str | None = None,
        pt2: Point | None = None,
    ):
        """Slice a polygon into two parts.

        If `name1` and `name2` are given, at least one `pt1` or `pt2` must be provided.

        Slicing rules:
        - the first and the last slicing point must be touching a vertex or an edge
        - if more is touching vertex/edge at the beginning of the list, they are removed
          so that the list starts with a single vertex/edge touching point
        - the same applies to the end of the slicing points list

        Possible cases:
        1) slicing points start and end at two different edges
        2) slicing points start and end at the same edge
        3) slicing points start at a vertex and end at some edge (or vice versa)
        4) Slicing points start and end at two different vertices

        Args:
            points: list of points
            name1: name of the first part
            pt1: some point used to identify the first part
            name2: name of the second part
            pt2: some point used to identify the second part

        Return:
            (Polygon, Polygon)
        """
        # Make sure there is enough slicing points (at least 2)
        if len(points) < 2:
            raise GeometryError("Cannot slice the polygon using less than 2 points")

        # Make sure all slicing points are within this polygon
        for p in points:
            if not self.is_point_inside(p):
                raise GeometryError(
                    f"At least on of the points is not inside the polygon {self.name}: {p}"
                )

        if name1 is None:
            name1 = random_id()
        if name2 is None:
            name2 = random_id()

        # Clean slicing points: remove heading or trailing vertex/edge points
        points = self._remove_trailing_boundary_touching_points(points)

        # Find out which case is it
        sl_pt_loc = self._slicing_point_location(points)
        num_at_vertex = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_vertex"])
        num_at_edge = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_edge"])
        num_interior = sum([1 for loc, _ in sl_pt_loc.values() if loc == "interior"])
        sl_edges = set([index for loc, index in sl_pt_loc.values() if loc == "at_edge"])
        sl_vertices = set([index for loc, index in sl_pt_loc.values() if loc == "at_vertex"])

        assert num_at_vertex + num_at_edge + num_interior == len(points), \
            "Slicing point location counting must have a bug"

        # Make sure there is enough slicing points (at least 2)
        if len(points) < 2:
            raise GeometryError("Cannot slice the polygon using less than 2 points")

        case = None
        if num_at_edge == 2 and len(sl_edges) == 2 and num_at_vertex == 0:
            # 1) slicing points start and end at two different edges
            case = 1
        elif num_at_edge == 2 and len(sl_edges) == 1 and num_at_vertex == 0:
            # 2) slicing points start and end at the same edge
            case = 2
        elif num_at_edge == 1 and num_at_vertex == 1:
            # 3) slicing points start at a vertex and end at some edge (or vice versa)
            case = 3
        elif num_at_vertex == 2 and len(sl_vertices) == 2 and num_at_edge == 0:
            # 4) Slicing points start and end at two different vertices
            case = 4
        else:
            raise NotImplementedError(
                f"Algorithm not prepared for such a case ({case}):\n"
                f"- number of slicing points = {len(points)}\n"
                f"- number of slicing points touching edges = {num_at_edge}\n"
                f"- number of slicing points touching vertices = {num_at_vertex}\n"
                f"- edges to be used in the slice: {sl_edges}\n"
                f"- vertices to be used in the slice: {sl_vertices}\n"
            )

        # Create two polygons through slicing
        if case == 1:
            # 1) slicing points start and end at two different edges
            assert sl_pt_loc[0][0] == "at_edge"
            assert sl_pt_loc[len(points) - 1][0] == "at_edge"
            edge_num_1 = sl_pt_loc[0][1]
            edge_num_2 = sl_pt_loc[len(points) - 1][1]

            # Polygon 1 and Polygon 2
            points_1 = []
            points_1.extend(points)
            points_2 = []
            points_2.extend(points)

            next_1 = 0
            next_2 = 0
            last_1 = 0
            last_2 = 0

            for i in range(len(self.points)):
                if self.points[i] == self.edges[edge_num_2][0]:
                    next_1 = i
                if self.points[i] == self.edges[edge_num_2][1]:
                    next_2 = i
                if self.points[i] == self.edges[edge_num_1][1]:
                    last_1 = i
                if self.points[i] == self.edges[edge_num_1][0]:
                    last_2 = i

            if next_1 < next_2 or next_2 == 0:
                inc_1 = -1
            else:
                inc_1 = -1

            inc_2 = inc_1 * -1  # Polygon 2 goes the other way around

            while next_1 != last_1:
                points_1.append(self.points[next_1])
                next_1 += inc_1
                if next_1 < 0:
                    next_1 = len(self.points) - 1
                elif next_1 > len(self.points) - 1:
                    next_1 = 0
            points_1.append(self.points[next_1])

            while next_2 != last_2:
                points_2.append(self.points[next_2])
                next_2 += inc_2
                if next_2 < 0:
                    next_2 = len(self.points) - 1
                elif next_2 > len(self.points) - 1:
                    next_2 = 0
            points_2.append(self.points[next_2])

            poly_1 = Polygon(points_1, name=name1)
            poly_2 = Polygon(points_2, name=name2)

        elif case == 2:
            # 2) slicing points start and end at the same edge
            edge_num = sl_edges.pop()

            # Polygon 1 is composed of slice_points only
            poly_1 = Polygon(points, name=name1)

            # Polygon 2 is composed of both, own points and sliced points
            def make_poly_2(points):
                points_2 = []
                slice_points_included = False
                for p in self.points:
                    points_2.append(p)
                    if p in self.edges[edge_num]:
                        # Slicing ocurred at this edge - need to add slice_points
                        if not slice_points_included:
                            for sp in points:
                                points_2.append(sp)
                            slice_points_included = True
                poly_2 = Polygon(points_2, name=name2)
                return poly_2

            try:
                poly_2 = make_poly_2(points)
            except TriangulationError:
                # Probably points are given in the wrong order
                # The order of slicing points should be reversed w.r.t. input polygon
                points = points[::-1]
                poly_2 = make_poly_2(points)

        elif case == 3:
            # 3) slicing points start at a vertex and end at some edge (or vice versa)
            edge_num = sl_edges.pop()
            assert len(sl_edges) == 0, "Should be no edges left in this case"

            # Determine if first point starts at vertex or the last point ends at vertex
            if sl_pt_loc[0][0] == "at_vertex":
                start_at_vertex = True
                assert sl_pt_loc[len(points) - 1][0] == "at_edge"
            else:
                start_at_vertex = False
                assert sl_pt_loc[len(points) - 1][0] == "at_vertex"

            points_1 = []
            points_2 = []
            if start_at_vertex:
                points_1.extend(points)
                points_2.extend(points)
            else:
                points_1.extend(points[::-1])
                points_2.extend(points[::-1])

            next_1 = 0
            next_2 = 0
            last_1 = 0
            last_2 = 0

            for i in range(len(self.points)):
                if self.points[i] == self.edges[edge_num][0]:
                    next_1 = i
                if self.points[i] == self.edges[edge_num][1]:
                    next_2 = i
                if self.points[i] == points_1[0]:
                    last_1 = i
                if self.points[i] == points_2[0]:
                    last_2 = i

            assert last_1 == last_2, "They should both end up at the same vertex"

            if next_1 < next_2 or next_2 == 0:
                inc_1 = -1
            else:
                inc_1 = -1

            inc_2 = inc_1 * -1  # Polygon 2 goes the other way around

            while next_1 != last_1:
                points_1.append(self.points[next_1])
                next_1 += inc_1
                if next_1 < 0:
                    next_1 = len(self.points) - 1
                elif next_1 > len(self.points) - 1:
                    next_1 = 0

            while next_2 != last_2:
                points_2.append(self.points[next_2])
                next_2 += inc_2
                if next_2 < 0:
                    next_2 = len(self.points) - 1
                elif next_2 > len(self.points) - 1:
                    next_2 = 0

            poly_1 = Polygon(points_1, name=name1)
            poly_2 = Polygon(points_2, name=name2)

        elif case == 4:
            # 4) Slicing points start and end at two different vertices
            # Polygon 1
            pi_start = 0
            pi_end = 0
            for i in range(len(self.points)):
                if self.points[i] == points[0]:
                    pi_start = i
                if self.points[i] == points[-1]:
                    pi_end = i

            points_1 = []
            current = pi_start
            last = pi_end
            while current != last:
                points_1.append(self.points[current])
                current += 1
                if current > len(self.points) - 1:
                    current = 0

            for i in range(len(points) - 1, 0, -1):
                points_1.append(points[i])

            poly_1 = Polygon(points_1, name=name1)

            # Polygon 2 must go the other way around ####
            points_2 = []                               #
            current = pi_start                          #
            last = pi_end                               #
            while current != last:                      #
                points_2.append(self.points[current])   #
                current -= 1 # <------------------------#
                if current < 0:
                    current = len(self.points) - 1

            for i in range(len(points) - 1, 0, -1):
                points_2.append(points[i])

            poly_2 = Polygon(points_2, name=name2)

        else:
            raise NotImplementedError(f"Case {case} not implemented yet")

        # Determine which polygon is name1 and which name2, based on pt1 and pt2
        if pt1 is not None:
            pt1_in_poly1 = poly_1.is_point_inside(pt1)
            pt1_in_poly2 = poly_2.is_point_inside(pt1)
            if pt1_in_poly1 and pt1_in_poly2:
                raise GeometryError(
                    f"{pt1=} is inside both of the sliced polygons"
                )
            elif pt1_in_poly1:
                pass  # OK, no need to swap poly1 with poly2
            elif pt1_in_poly2:
                points_1 = poly_1.points
                points_2 = poly_2.points
                poly_1 = Polygon(points_2, name=name1)
                poly_2 = Polygon(points_1, name=name2)
            else:
                raise GeometryError(
                    f"{pt1=} is not inside any of the sliced polygons"
                )
        elif pt2 is not None:
            pt2_in_poly1 = poly_1.is_point_inside(pt2)
            pt2_in_poly2 = poly_2.is_point_inside(pt2)
            if pt2_in_poly1 and pt2_in_poly2:
                raise GeometryError(
                    f"{pt2=} is inside both of the sliced polygons"
                )
            elif pt2_in_poly2:
                pass  # OK, no need to swap poly1 with poly2
            elif pt2_in_poly1:
                points_1 = poly_1.points
                points_2 = poly_2.points
                poly_1 = Polygon(points_2, name=name1)
                poly_2 = Polygon(points_1, name=name2)
            else:
                raise GeometryError(
                    f"{pt2=} is not inside any of the sliced polygons"
                )
        else:
            pass

        # Check normals and flip polygons if different
        if not np.isclose(poly_1.normal, self.normal).all():
            poly_1 = poly_1.flip(poly_1.name)

        if not np.isclose(poly_2.normal, self.normal).all():
            poly_2 = poly_2.flip(poly_2.name)

        return (poly_1, poly_2)

    def _slicing_point_location(self, slicing_pts: list[Point]) -> dict:
        """Return the location of each slicing point.

        The returned dict has the following format:
        `{slicing_point_index: (location_string, location_index)}`.
        `location_index` is either vertex index or edge index.
        `location_string` is `at_vertex`, `at_edge`, or `interior`.
        """
        if len(slicing_pts) == 0:
            raise GeometryError("No slicing points passed")

        sl_pt_loc = {}
        for slp_i, slp in enumerate(slicing_pts):
            for p_i, p in enumerate(self.points):
                if p == slp:
                    sl_pt_loc[slp_i] = ("at_vertex", p_i)
                    break

            if slp_i in sl_pt_loc.keys():
                continue

            for edge_num, (ep1, ep2) in enumerate(self.edges):
                d_to_edge = distance_point_to_edge(ptest=slp, p1=ep1, p2=ep2)
                if np.isclose(d_to_edge, 0):
                    sl_pt_loc[slp_i] = ("at_edge", edge_num)

            if slp_i in sl_pt_loc.keys():
                continue
            else:
                sl_pt_loc[slp_i] = ("interior", None)

        if sl_pt_loc[0][0] == "interior":
            raise GeometryError("First slicing point must start at an edge or a vertex")
        if sl_pt_loc[len(slicing_pts) - 1][0] == "interior":
            raise GeometryError("Last slicing point must end at an edge or a vertex")


        return sl_pt_loc

    def _remove_trailing_boundary_touching_points(self, slicing_pts: list[Point]) -> list[Point]:
        """Remove all heading and trailing slicing points touching a vertex or an edge.

        The returned list of points starts with a single vertex touching polygon's
        vertex or edge and ends with a single vertex touching an edge or a vertex.
        """
        sl_pt_loc = self._slicing_point_location(slicing_pts)
        num_at_vertex = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_vertex"])
        num_at_edge = sum([1 for loc, _ in sl_pt_loc.values() if loc == "at_edge"])
        num_interior = sum([1 for loc, _ in sl_pt_loc.values() if loc == "interior"])

        new_points = []
        for i in range(len(slicing_pts)):
            # Collect point, location type, and location index for previous, this, and next point
            this_pt = slicing_pts[i]
            this_loc_type, this_loc_ix = sl_pt_loc[i]

            if i > 0:
                prev_loc_type, prev_loc_ix = sl_pt_loc[i - 1]
            else:
                prev_loc_type = None
                prev_loc_ix = None

            if i < len(slicing_pts) - 1:
                next_pt = slicing_pts[i + 1]
                next_loc_type, next_loc_ix = sl_pt_loc[i + 1]
            else:
                next_pt = None
                next_loc_type = None
                next_loc_ix = None

            neglect_subsequent = False

            # Check if this point should be kept or removed
            if neglect_subsequent is True:
                continue
            elif this_loc_type == "interior":
                new_points.append(this_pt)
            elif next_loc_type == "interior":
                new_points.append(this_pt)
            elif (
                prev_loc_type is not None
                and prev_loc_type == "interior"
                and this_loc_type in ("at_vertex", "at_edge")
            ):
                new_points.append(this_pt)
                neglect_subsequent = True
            elif this_loc_type == "at_vertex" and next_loc_type == "at_vertex":
                if num_at_vertex == 2:
                    # It means there are no interior points
                    assert num_interior == 0
                    new_points.append(this_pt)
                else:
                    continue
            elif this_loc_type == "at_vertex" and prev_loc_type == "at_vertex":
                if num_at_vertex == 2:
                    # It means there are no interior points
                    assert num_interior == 0
                    new_points.append(this_pt)
                else:
                    continue
            elif this_loc_type == "at_edge" and next_loc_type == "at_edge":
                if this_loc_ix != next_loc_ix:
                    # It means there are no interior points
                    assert num_interior == 0
                    new_points.append(this_pt)
                else:
                    continue
            elif (
                this_loc_type == "at_edge"
                and next_loc_type is None
                and prev_loc_type == "at_edge"
                and prev_loc_ix is not None
                and prev_loc_ix != this_loc_ix
            ):
                # It means there are no interior points
                # and this is the last slicing point
                assert num_interior == 0
                new_points.append(this_pt)
            elif (
                this_loc_type == "at_edge"
                and next_loc_type is None
                and prev_loc_type == "at_edge"
                and prev_loc_ix is not None
                and prev_loc_ix == this_loc_ix
            ):
                # It means there must be some interior points
                # and this is the last slicing point
                # and this and previous points lay on the same edge
                # so this one must be removed
                assert num_interior > 0
                continue
            elif (
                this_loc_type in ("at_vertex", "at_edge")
                and next_loc_type != "interior"
            ):
                continue
            elif (
                this_loc_type == "at_vertex"
                and next_loc_type == "at_edge"
                and next_loc_ix is not None
            ):
                d = distance_point_to_edge(
                    ptest = this_pt,
                    p1 = self.edges[next_loc_ix][0],
                    p2 = self.edges[next_loc_ix][1],
                )
                if np.isclose(d, 0):
                    continue
                else:
                    new_points.append(this_pt)
            elif (
                this_loc_type == "at_edge"
                and next_loc_type == "at_vertex"
                and next_pt is not None
            ):
                d = distance_point_to_edge(
                    ptest = next_pt,
                    p1 = self.edges[this_loc_ix][0],
                    p2 = self.edges[this_loc_ix][1],
                )
                if np.isclose(d, 0):
                    continue
                else:
                    new_points.append(this_pt)
            else:
                raise RuntimeError("This should never happen. Some case is not considered (bug!).")

        return new_points

    def points_as_array(self) -> np.ndarray:
        """Returns a copy of the points as a numpy array."""
        return points_to_array(self.points)

    def move_orthogonal(self, d: float) -> None:
        vec = self.normal * d
        for i in range(len(self.points)):
            self.points[i] += vec

    def plane_equation_coefficients(self) -> tuple:
        """Returns [a, b, c, d] from the equation ax + by + cz + d = 0.

        This equation describes the plane that this polygon is on.
        """
        return self.projection_coefficients(self.points[0])

    def projection_coefficients(self, p: Point) -> tuple:
        """Returns [a, b, c, d] from the equation ax + by + cz + d = 0.

        Uses the vector normal to this polygon and the point p
        to calculate the coefficients of the plane equation
        with the same slope as this polygon, but translated to the point p.
        """
        a = self.normal[0]
        b = self.normal[1]
        c = self.normal[2]

        d = -1 * (a * p.x + b * p.y + c * p.z)
        return (a, b, c, d)

    def distance_point_to_polygon(self, p: Point) -> float:
        """Return distance of point to the polygon.

        Note:
            For points not laying inside the orthogonal
            projection, the distance is calculated as the distance
            to the closest polygon vertex.
            TODO: Calculate distance to the nearest edge instead.
        """
        # Translate polygon's to the point p
        _, _, _, d = self.plane_equation_coefficients()
        _, _, _, dp = self.projection_coefficients(p)

        # Distance
        # Negative distance -> point behind the polygon
        # Positive distance -> point in front of the polygon
        dist = np.abs(d - dp)

        if self.is_point_inside_ortho_projection(p):
            return dist
        else:
            # Find the closest vertex
            return self.distance_point_to_polygon_points(p)

    def distance_point_to_polygon_points(self, p: Point) -> float:
        """Return minimum distance between test point and polygon points."""
        dist = np.inf
        for v in self.points:
            p_to_v = length(p.vector() - v.vector())
            if  p_to_v < dist:
                dist = p_to_v
        return dist

    def plane_normal_and_d(self) -> tuple[np.ndarray, float]:
        """Return the normal vector and coefficient d describing the plane."""
        _, _, _, d = self.plane_equation_coefficients()
        return (self.normal, d)

    def is_point_coplanar(self, p: Point) -> bool:
        """Checks whether the point p is coplanar with the polygon."""
        points = self.points + [p]
        is_coplanar = are_points_coplanar(*points)

        return is_coplanar

    def is_point_inside(self, p: Point) -> bool:
        """Checks whether a point lies on the surface of the polygon."""

        if not self.is_point_coplanar(p):
            return False

        for triangle_indices in self.triangles:
            tri = [self.points[i] for i in triangle_indices]

            if is_point_inside_triangle(p, tri[0], tri[1], tri[2]):
                return True

        return False

    def is_point_inside_margin(self, p: Point, margin: float) -> bool:
        """Checks whether a point lies within a polygon's inline.

        Returns `True` if:
        - point is inside the polygon and
        - distance from this point to the nearest edge is larger than `margin`

        Args:
            p: point to be checked
            margin: distance from the boundary to the inline

        Return:
            check result (bool)
        """
        inside = self.is_point_inside(p)
        if not inside:
            return False
        else:
            for edge in self.edges:
                d = distance_point_to_edge(p, edge[0], edge[1])
                if d < margin:
                    return False
        return True

    def is_point_inside_ortho_projection(self, p: Point) -> bool:
        """Checks whether an orthogonally projected point hits the surface.

        The point is projected orthogonally to the polygon's plane.
        If the projected point is inside the polygon, return True.
        """
        # Translate polygon's to the point p
        a, b, c, d = self.plane_equation_coefficients()
        ap, bp, cp, dp = self.projection_coefficients(p)

        assert np.isclose(a, ap), "If a and ap are not equal, d should be normalized"
        assert np.isclose(b, bp), "If b and bp are not equal, d should be normalized"
        assert np.isclose(c, cp), "If c and cp are not equal, d should be normalized"

        # Distance
        # Negative distance -> point behind the polygon
        # Positive distance -> point in front of the polygon
        dist = d - dp

        # Make a copy of the polygon and move it to the point p
        poly_at_p = self.copy(random_id())
        poly_at_p.move_orthogonal(dist)
        assert poly_at_p.is_point_coplanar(p)

        # Check if the point lays inside the polygon
        is_inside = poly_at_p.is_point_inside(p)

        del poly_at_p
        return is_inside

    def is_point_inside_projection(
        self,
        p: Point,
        vec: np.ndarray,
        fwd_only: bool = True
    ) -> bool:
        """Checks whether a projected point hits the surface.

        The point is projected along the vector vec.
        It is possible to consider both positive and negative directions of vec,
        or only the positive.

        Args:
            p: tested point
            vec: projection vector
            fwd_only: if True, only the forward (positive) direction of vec is considered

        Return:
            True if the projected point hits the surface
        """
        # Get coefficients of the plane equation
        a, b, c, d = self.plane_equation_coefficients()

        # Find the point projection along vec to the plane of the polygon
        denom = a * vec[0] + b * vec[1] + c * vec[2]

        if np.abs(denom) < GEOM_EPSILON:
            # Vector vec is colinear with the plane
            # The point lays inside this projection only if it is inside this polygon
            # logger.warning(f"Projection vector {vec} is colinear with the polygon {self.name}")
            return self.is_point_inside(p)
        else:
            # Projection crosses the surface of the plane
            s = (-d - a * p.x - b * p.y - c * p.z) / (a * vec[0] + b * vec[1] + c * vec[2])

            if fwd_only and s < 0:
                # The plane is in the other direction than the one pointed by vec
                return False

            p = p.copy()
            p += s * vec
            is_inside = self.is_point_inside(p)
            return is_inside

    def is_point_behind(self, p: Point) -> bool:
        """Checks if the point p is behind the polygon.

        A point is behind the polygon if the polygon's normal vector
        is directed in the opposite direction to the point.
        """
        # Translate polygon's to the point p
        _, _, _, d = self.plane_equation_coefficients()
        _, _, _, dp = self.projection_coefficients(p)

        # Distance
        # Negative distance -> point behind the polygon
        # Positive distance -> point in front of the polygon
        dist = d - dp

        if dist < 0:
            return True
        else:
            return False

    def is_facing_polygon(self, poly, exact: bool = True) -> bool:
        """Checks if this polygon is facing another polygon.

        Returns True if all points of two polygons are equal and their normals
        are pointing towards each other.

        If exact is True, all points of two polygons must be equal (order may be different).
        If exact is False, the method checks only if polygons are overlapping, points are coplanar
        and normal vectors are opposite.

        Args:
            poly: another polygon
            exact: if True, all points of adjacent polygons must be equal

        Return:
            True if the polygons are facing each other
        """
        if exact:
            this_points = set(self.points)
            other_points = set(poly.points)
            if this_points == other_points:
                if np.isclose(self.normal * -1, poly.normal).all():
                    return True
            return False
        else:
            this_points = self.points
            other_points = poly.points
            all_points = this_points + other_points
            # Condition 1: points must be  coplanar
            points_coplanar = are_points_coplanar(*all_points)
            # Condition 2: normal vectors must be opposite
            normals_opposite = np.isclose(self.normal, poly.normal * -1, rtol=GEOM_RTOL).all()
            # Condition 3: polygons must be overlapping
            this_in_other = np.array([self.is_point_inside(p) for p in other_points])
            other_in_this = np.array([poly.is_point_inside(p) for p in this_points])
            overlap = this_in_other.any() or other_in_this.any()

            if points_coplanar and normals_opposite and overlap:
                return True
            else:
                return False

    def _triangulate(self) -> list[tuple[int, ...]]:
        """Return a list of triangles (i, j, k) using the ear clipping algorithm.

        (i, j, k) are the indices of the points in self.points.
        """
        return triangulate(self.points, self.normal)

    def _normal(self) -> np.ndarray:
        """Calculate a unit normal vector for this wall.

        The normal vector is calculated using the cross product
        of two vectors A and B spanning between points:
        - A: 0 -> 1 (first and second point)
        - B: 0 -> -1 (first and last point)
        """
        return normal(self.points[-1], self.points[0], self.points[1])

    def _edges(self) -> list[tuple[Point, Point]]:
        """Return a list of edges of this wall."""
        wall_line_segments = []
        segment = []

        i = 0
        while i < len(self.points):
            segment.append(self.points[i])
            i += 1

            if len(segment) == 2:
                wall_line_segments.append(tuple(segment))
                segment = []
                i -= 1

        wall_line_segments.append((self.points[-1], self.points[0]))

        return wall_line_segments

    def _area(self) -> float:
        """Calculate the area of the wall.

        Calculated using the Stoke's theorem:
        https://en.wikipedia.org/wiki/Stokes%27_theorem

        Code based on:
        https://stackoverflow.com/questions/12642256/find-area-of-polygon-from-xyz-coordinates
        """
        poly = [(p.x, p.y, p.z) for p in self.points]

        if len(poly) < 3: # not a plane - no area
            return 0

        total = [0, 0, 0]
        N = len(poly)
        for i in range(N):
            vi1 = poly[i]
            if i == N - 1:
                vi2 = poly[0]
            else:
                vi2 = poly[i+1]
            prod = np.cross(vi1, vi2)
            total[0] += prod[0]
            total[1] += prod[1]
            total[2] += prod[2]

        result = float(np.dot(total, self.normal))

        return abs(result / 2)

    def _verify(self):
        """Verify geometry correctness."""
        # At least 3 points
        if len(self.points) < 3:
            raise GeometryError(f"Polygon has only {len(self.points)} points")

        # Check if all points are coplanar
        if not are_points_coplanar(*self.points):
            raise GeometryError(f"Points of polygon aren't coplanar")

    def some_interior_point(self) -> Point:
        """Return some point laying inside this polygon.

        Such point is sometimes needed to distuingish inside from outside.
        """
        p0 = self.points[self.triangles[0][0]]
        p1 = self.points[self.triangles[0][1]]
        p2 = self.points[self.triangles[0][2]]
        some_pt = triangle_centroid(p0, p1, p2)
        return some_pt

    def _centroid(self) -> Point:
        """Calculate the center of mass.

        The centroid is calculated using a weighted average of
        the triangle centroids. The weights are the triangle areas.

        Uses self.triangles (the output of self.triangulate()).
        """
        tri_ctr = []
        weights = []

        assert len(self.triangles) > 0, "No triangles after ear clipping?"

        for tri in self.triangles:
            tri_ctr.append(
                triangle_centroid(
                    self.points[tri[0]], self.points[tri[1]], self.points[tri[2]]
                )
            )
            weights.append(
                triangle_area(
                    self.points[tri[0]], self.points[tri[1]], self.points[tri[2]]
                )
            )
        tri_ctr_arr = np.array([(p.x, p.y, p.z) for p in tri_ctr])
        weights_arr = np.array(weights).reshape((-1, 1))

        weighted_centroids = tri_ctr_arr * weights_arr

        vec = weighted_centroids.sum(axis=0) / weights_arr.sum()
        ctr = Point(vec[0], vec[1], vec[2])

        return ctr

    def __str__(self):
        return f"Polygon(name={self.name}, points={[p for p in self.points]})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """Checks if all points of two polygons are equal."""
        if not np.isclose(self.normal, other.normal, atol=GEOM_EPSILON).all():
            return False
        elif len(self.points) == len(other.points):
            other_set = set(other.points)
            for p in self.points:
                # TODO: Below test is not sufficient; it does not test how points are connected.
                #       It may fail for some non-convex polygons, which can have same points
                #       connected differently.
                #       Convex polygons are covered, because there is only 1 way to connect
                #       points of a convex polygon.
                if p not in other_set:
                    return False
        else:
            return False
        return True
