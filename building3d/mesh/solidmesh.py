from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
from building3d.geom.tetrahedron import tetrahedron_volume
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

        stats = {
            "num_of_vertices": len(self.mesh_vertices),
            "num_of_tetrahedra": len(self.mesh_elements),
            "max_tetrahedron_volume": 0,
            "avg_tetrahedron_volume": 0,
            "min_tetrahedron_volume": np.inf,
        }

        for tetra in self.mesh_elements:
            p0 = self.mesh_vertices[tetra[0]]
            p1 = self.mesh_vertices[tetra[1]]
            p2 = self.mesh_vertices[tetra[2]]
            p3 = self.mesh_vertices[tetra[3]]
            vol = tetrahedron_volume(p0, p1, p2, p3)
            if vol > stats["max_tetrahedron_volume"]:
                stats["max_tetrahedron_volume"] = vol
            elif vol < stats["min_tetrahedron_volume"]:
                stats["min_tetrahedron_volume"] = vol
            stats["avg_tetrahedron_volume"] += vol

        stats["avg_tetrahedron_volume"] /= stats["num_of_tetrahedra"]

        if show is True:
            print("SolidMesh statistics:")
            print(f"\tnum_of_vertices={stats['num_of_vertices']}")
            print(f"\tnum_of_tetrahedra={stats['num_of_tetrahedra']}")
            print(f"\tmax_tetrahedron_volume={stats['max_tetrahedron_volume']}")
            print(f"\tavg_tetrahedron_volume={stats['avg_tetraedron_volume']}")
            print(f"\tmin_tetrahedron_volume={stats['min_tetraedron_volume']}")

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


    def collapse_points(self):  # TODO
        """Merge overlapping points (between solids).
        """
        pass

