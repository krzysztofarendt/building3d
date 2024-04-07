from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
import building3d.geom.point
from building3d.mesh.polymesh import PolyMesh
from building3d.mesh.solidmesh import SolidMesh


class Mesh:

    def __init__(self, delta: float = 0.5):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.polymesh = PolyMesh(delta)
        self.solidmesh = SolidMesh(delta)

    def add_polygon(self, poly: building3d.geom.polygon.Polygon):
        self.polymesh.add_polygon(poly)

    def add_solid(self, sld: building3d.geom.solid.Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are also added (if they were not already added manually).
        """
        self.solidmesh.add_solid(sld)
        for poly in sld.boundary:
            self.add_polygon(poly)

    def generate(self):
        """Generate mesh for all added polygons and solids."""
        self.polymesh.generate()
        boundary_vertices = self.polymesh.get_vertices_per_polygon()
        self.solidmesh.generate(boundary_vertices)
