from __future__ import annotations
import logging

import numpy as np

from building3d.geom.polygon import Polygon
from building3d.geom.point import Point
from building3d.geom.triangle import triangle_area
from building3d.mesh.triangulation import delaunay_triangulation
from building3d.config import MESH_DELTA


logger = logging.getLogger(__name__)


class PolyMesh:
    def __init__(self, delta: float = MESH_DELTA):
        logger.debug(f"PolyMesh(delta={delta})")

        # Mesh settings
        self.delta = delta

        # Polygons to be meshed
        self.polygons = {}

        # Attributes filled with data by self.generate()
        self.vertices: list[Point] = []
        self.vertex_owners = {}
        self.faces = []
        self.face_owners = {}
        self.areas = []  # TODO: Will have to calculate if mesh is read from B3D file

    def reinit(
        self,
        vertices: list[Point] | None = None,
        vertex_owners: dict | None = None,
        faces: list[list[int]] | None = None,
        face_owners: dict | None = None,
    ):
        logger.debug("Reinitializing PolyMesh")
        if vertices and vertex_owners and faces and face_owners:
            self.vertices = vertices
            self.vertex_owners = vertex_owners
            self.faces = faces
            self.face_owners = face_owners
            self._recalc_areas()
        else:
            self.vertices = []
            self.vertex_owners = {}
            self.faces = []
            self.face_owners = {}

    def add_polygon(self, poly: Polygon):
        logger.debug(f"Adding polygon: {poly}")
        self.polygons[poly.name] = poly

    def get_vertices_per_polygon(self) -> dict[str, list[Point]]:
        """Return list of vertices for each polygon name."""
        logger.debug("Getting the list of Points per polygon")
        vertices = {}
        for name in self.polygons.keys():
            vertices[name] = [self.vertices[i] for i in self.vertex_owners[name]]
        log_return = {k: len(v) for (k, v) in vertices.items()}
        logger.debug(f"Number of Points per polygon: {log_return}")
        return vertices

    def generate(
        self,
        fixed_points: dict[str, list[Point]] = {},
    ):
        """Generate mesh for all added polygons and solids."""
        logger.debug(f"Generating mesh...")
        self.reinit()

        # Find matching faces, because they should share vertices
        matching_pairs = {}
        for poly_name_1, poly_1 in self.polygons.items():
            for poly_name_2, poly_2 in self.polygons.items():
                if poly_name_1 != poly_name_2:
                    if poly_1.is_facing_polygon(poly_2):
                        matching_pairs[poly_name_1] = poly_name_2

        # Polygons
        poly_vertices = {}

        for poly_name, poly in self.polygons.items():
            logger.debug(f"Processing {poly_name}")

            fixed = []
            if poly_name in fixed_points.keys():
                logger.debug(f"Adding {len(fixed_points[poly_name])} init. vert. for {poly_name}")
                fixed = fixed_points[poly_name]

            # Check if matching polygon was already meshed and add its points if yes
            if poly_name in matching_pairs.keys():
                match_name = matching_pairs[poly_name]
                if match_name in poly_vertices.keys():
                    fixed.extend(poly_vertices[match_name])

            vertices, faces = delaunay_triangulation(
                poly=poly,
                delta=self.delta,
                fixed_points=fixed,
            )
            poly_vertices[poly_name] = vertices
            self._add_vertices(poly_name, vertices, faces)

        # Calculate face areas
        self._recalc_areas()

    def _add_vertices(self, owner: str, vertices: list[Point], faces: list[list[int]]):
        # Increase face counter to include previously added vertices
        _faces = np.array(faces)
        _faces += len(self.vertices)
        faces = _faces.tolist()

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

    def _recalc_areas(self):
        self.areas = []
        for f in self.faces:
            p0 = self.vertices[f[0]]
            p1 = self.vertices[f[1]]
            p2 = self.vertices[f[2]]
            self.areas.append(triangle_area(p0, p1, p2))
