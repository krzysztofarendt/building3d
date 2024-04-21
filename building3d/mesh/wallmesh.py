from __future__ import annotations
import logging

import building3d.logger
from building3d.geom.polygon import Polygon
from building3d.geom.point import Point
from building3d.geom.triangle import triangle_area
from building3d.geom.vector import length
from building3d.geom.vector import vector
from building3d.geom.triangle import triangle_centroid
from building3d.geom.wall import Wall
from building3d.mesh.triangulation import delaunay_triangulation
from building3d.config import MESH_DELTA
from building3d.geom.line import create_points_between_2_points
from building3d.config import GEOM_EPSILON


logger = logging.getLogger(__name__)


class WallMesh:
    def __init__(self, delta: float = MESH_DELTA):
        logger.debug(f"WallMesh(delta={delta})")

        # Mesh settings
        self.delta = delta

        # Walls to be meshed
        self.walls = {}

        # Attributes filled with data by self.generate()
        self.vertices = []
        self.vertex_owners = {}
        self.faces = []
        self.face_owners = {}

    def reinit(self):
        logger.debug("Reinitializing WallMesh")
        self.vertices = []
        self.vertex_owners = {}
        self.faces = []
        self.face_owners = {}

    def add_wall(self, wall: Wall):
        logger.debug(f"Adding wall: {wall.name}")
        self.walls[wall.name] = wall

    def get_vertices_per_wall(self) -> dict[str, list[Point]]:
        pass # TODO: It will be needed in zone mesh

    def mesh_statistics(self, show=False) -> dict:
        """Print and return info about mesh quality."""
        pass # TODO

    def _add_vertices(self, owner, vertices, faces):
        # Reindex faces
        offset = len(self.vertices)
        faces_reindexed = []
        for f in faces:
            faces_reindexed.append([f[0] + offset, f[1] + offset, f[2] + offset])
        faces = faces_reindexed

        # Add vertices
        len_before = len(self.vertices)
        self.vertices.extend(vertices)
        len_after = len(self.vertices)
        self.vertex_owners[owner] = [x for x in range(len_before, len_after)]

        # Add faces
        len_before = len(self.faces)
        self.faces.extend(faces)
        len_after = len(self.faces)
        self.face_owners[owner] = [x for x in range(len_before, len_after)]

    def generate(
        self,
        fixed_points: dict[str, list[Point]] = {},
    ):
        logger.debug(f"Generating mesh...")
        self.reinit()


        for w_name, w in self.walls.items():

            # Global fixed points -> passed through `fixed_points`
            # Local fixed points -> vertices from subpolygons' meshes
            fixed = []

            for poly_name, poly in w.polygons.items():

                # Skip if subpolygon
                if poly_name not in w.get_parents():
                    continue

                subpolygons = w.get_subpolygons(poly_name)

                if len(subpolygons) > 0:
                    for sub in subpolygons:
                        fixed.extend(self.make_edge_points(sub, delta=self.delta / 3))  # TODO: 3

                # Global
                if poly_name in fixed_points.keys():
                    fixed.extend(fixed_points[poly_name])

                vertices, faces = delaunay_triangulation(
                    poly=poly,
                    delta=self.delta,
                    fixed_points=fixed,
                )

                # Re-assign owners # TODO
                for sub in subpolygons:
                    sub_vertices = []
                    sub_faces = []
                    for f in faces:
                        p0 = vertices[f[0]]
                        p1 = vertices[f[1]]
                        p2 = vertices[f[2]]
                        face_centroid = triangle_centroid(p0, p1, p2)
                        if sub.is_point_inside(face_centroid):
                            pass  # TODO

                # Add
                self._add_vertices(poly_name, vertices, faces)


    def make_edge_points(self, poly: Polygon, delta: float) -> list[Point]:

        points = poly.points
        edge_points = []
        for i in range(len(points)):
            cur = i
            nxt = i + 1 if i + 1 < len(points) else 0
            pt1 = points[cur]
            pt2 = points[nxt]
            edge_len = length(pt2.vector() - pt1.vector())
            num_segments = int(edge_len // (delta + GEOM_EPSILON))
            new_pts = create_points_between_2_points(pt1, pt2, num_segments)
            edge_points.extend(new_pts)

        return edge_points
