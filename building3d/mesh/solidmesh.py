from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
from building3d.geom.point import Point
from .tetrahedralization import delaunay_tetrahedralization


class SolidMesh:

    def __init__(self, delta: float = 0.5):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.solids = {}

        # Attributes filled with data by self.generate()
        self.mesh_vertices = []
        self.mesh_vertex_owners = []  # solid names
        self.mesh_elements = []
        self.mesh_element_owners = []  # solid names

    def add_solid(self, sld: building3d.geom.solid.Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are also added (if they were not already added manually).
        """
        self.solids[sld.name] = sld

    def mesh_statistics(self, show=False) -> dict:
        """Print and return info about mesh quality."""
        # TODO
        stats = {
            "num_of_vertices": None,
            "num_of_faces": None,
            "max_face_area": None,
            "avg_face_area": None,
            "min_face_area": None,
            "max_edge_len": None,
            "avg_edge_len": None,
            "min_edge_len": None,
        }
        return stats

    def generate(self, boundary_vertices: dict[str, list[Point]] = {}):  # TODO
        """Generate mesh for all added polygons and solids."""

        # Solids
        for sld_name, sld in self.solids.items():
            vertices, tetrahedra = delaunay_tetrahedralization(
                sld=sld,
                boundary_vertices=boundary_vertices,
                delta=self.delta
            )
            self.mesh_vertices.extend(vertices)
            self.mesh_vertex_owners.extend([sld_name for _ in vertices])
            self.mesh_elements.extend(tetrahedra)
            self.mesh_element_owners.extend([sld_name for _ in tetrahedra])


    def collapse_points(self):  # TODO: Add solid mesh. Currently works on polygon meshes only.
        """Merge overlapping points.

        Checks if there are points which are equal to one another.
        Point equality is defined in the Point class. In general,
        points are equal if the difference between their coordinates is below
        the defined epsilon.

        Subsequently, overlapping points are merged.

        Overlapping points typically exist on the edges of adjacent polygons,
        because the polygon meshes are generated independently.
        """
        pass

    def fix_short_edges(self, min_length: float):  # TODO
        """Delete vertices connected to short edges."""
        pass

