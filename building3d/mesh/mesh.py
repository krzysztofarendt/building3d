from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
import building3d.geom.point
from .polygon_mesh import delaunay_triangulation


class Mesh:
    def __init__(self, delta: float = 0.5):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.polygons = {}
        self.solids = {}

        # Attributes filled with data by self.generate_mesh()
        self.vertices = []
        self.vertex_owners = []  # solid names

        self.faces = []
        self.face_owners = []  # polygon names

    def add_polygon(self, poly: building3d.geom.polygon.Polygon):
        self.polygons[poly.name] = poly

    def add_solid(self, sld: building3d.geom.solid.Solid):
        self.solids[sld.name] = sld

    def generate(self):
        """Generate mesh for all added polygons and solids."""
        # Polygons
        for poly_name, poly in self.polygons.items():
            vertices, faces = delaunay_triangulation(poly, self.delta)

            # Increase face counter to include previously added vertices
            faces = np.array(faces)
            faces += len(self.vertices)
            faces = faces.tolist()

            self.vertices.extend(vertices)
            vertex_owners = [None for _ in vertices]  # TODO: Should identify relevant solids

            self.faces.extend(faces)
            face_owners = [poly_name for _ in faces]
            self.face_owners.extend(face_owners)


        # Solids (should connect to vertices at adjacent polygons)
        pass
