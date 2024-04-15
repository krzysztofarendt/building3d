from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.point import Point
from building3d.mesh.tetrahedralization import delaunay_tetrahedralization
from building3d.config import MESH_DELTA


class SolidMesh:

    def __init__(self, delta: float = MESH_DELTA):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.solids = {}

        # Attributes filled with data by self.generate()
        self.vertices = []
        self.vertex_owners = []  # solid names
        self.elements = []
        self.element_owners = []  # solid names
        self.volumes = []

    def add_solid(self, sld: building3d.geom.solid.Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are also added (if they were not already added manually).
        """
        self.solids[sld.name] = sld

    def mesh_statistics(self, show=False) -> dict:
        """Print and return info about mesh quality."""

        vol_hist, bin_edges = np.histogram(self.volumes, bins=10)

        stats = {
            "num_of_vertices": len(self.vertices),
            "num_of_elements": len(self.elements),
            "max_element_volume": max(self.volumes),
            "avg_element_volume": np.mean(self.volumes),
            "min_element_volume": min(self.volumes),
        }

        if show is True:
            print("SolidMesh statistics:")
            print("=====================")
            print(f"\tnum_of_vertices={stats['num_of_vertices']}")
            print(f"\tnum_of_elements={stats['num_of_elements']}")
            print(f"\tmax_element_volume={stats['max_element_volume']}")
            print(f"\tavg_element_volume={stats['avg_element_volume']}")
            print(f"\tmin_element_volume={stats['min_element_volume']}")
            print("\tVolume distribution:")
            for i in range(len(vol_hist)):
                bracket = ")" if i < len(vol_hist) - 1 else "]"
                print(f"\t- [{bin_edges[i]:.3f}, {bin_edges[i+1]:.3f}{bracket} = {vol_hist[i]}")

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
            self.vertices.extend(vertices)
            self.vertex_owners.extend([sld_name for _ in vertices])
            self.elements.extend(tetrahedra)
            self.element_owners.extend([sld_name for _ in tetrahedra])

        # Calculate volumes
        for el in self.elements:
            p0 = self.vertices[el[0]]
            p1 = self.vertices[el[1]]
            p2 = self.vertices[el[2]]
            p3 = self.vertices[el[3]]
            vol = tetrahedron_volume(p0, p1, p2, p3)
            self.volumes.append(vol)

    def copy(self,
             elements: None | list = None,
             max_vol: None | float = None,
    ) -> SolidMesh:
        """Create a filtered copy of itself."""
        mesh = SolidMesh(delta=self.delta)
        mesh.solids = self.solids

        if elements is not None:
            # Filtered copy
            # TODO: Reorder vertices, because now all of them are copied even if they are not in `elements`
            mesh.vertices = self.vertices
            mesh.vertex_owners = self.vertex_owners
            mesh.elements = elements
            mesh.element_owners = [owner for i, owner in enumerate(self.element_owners) if i in elements]
            mesh.volumes = [vol for i, vol in enumerate(self.volumes) if i in elements]
        elif max_vol is not None:
            # Filtered copy
            # TODO: Reorder vertices, because now all of them are copied even if they are not in `elements`
            mesh.vertices = self.vertices
            mesh.vertex_owners = self.vertex_owners
            mesh.elements = [el for el, vol in zip(self.elements, self.volumes) if vol < max_vol]
            mesh.element_owners = [
                own for own, vol in zip(self.element_owners, self.volumes) if vol < max_vol
            ]
            mesh.volumes = [vol for vol in self.volumes if vol < max_vol]
        else:
            # Full copy
            mesh.vertices = self.vertices
            mesh.vertex_owners = self.vertex_owners
            mesh.elements = self.elements
            mesh.element_owners = self.element_owners
            mesh.volumes = self.volumes

        return mesh
