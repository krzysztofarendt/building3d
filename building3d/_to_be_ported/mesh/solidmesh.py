from __future__ import annotations
import logging

import numpy as np

import building3d.geom.solid
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.point import Point
from building3d.mesh.tetrahedralization import delaunay_tetrahedralization
from building3d.mesh.quality.purge_mesh import purge_mesh
from building3d.config import MESH_DELTA
from building3d.config import GEOM_RTOL
from building3d.config import SOLID_MESH_MAX_TRIES
from building3d.mesh.quality.total_volume import total_volume
from building3d.mesh.exceptions import MeshError


logger = logging.getLogger(__name__)


class SolidMesh:

    def __init__(self, delta: float = MESH_DELTA):
        # Mesh settings
        self.delta = delta

        # Solids to be meshed
        self.solids = {}  # {Solid.uid: Solid}

        # Attributes filled with data by self.generate()
        self.vertices = []
        self.elements = []
        self.volumes = []  # TODO: Will have to recalculate if reading from B3D file

        self.vertex_owners = {}
        self.element_owners = {}

    def reinit(
        self,
        vertices: list[Point] | None = None,
        vertex_owners: dict | None = None,
        elements: list[list[int]] | None = None,
        element_owners: dict | None = None,
    ):
        logger.debug("Reinitializing SolidMesh")
        if vertices and vertex_owners and elements and element_owners:
            self.vertices = vertices
            self.vertex_owners = vertex_owners
            self.elements = elements
            self.element_owners = element_owners
            self._recalc_volumes()
        else:
            self.vertices = []
            self.vertex_owners = {}
            self.elements = []
            self.element_owners = {}

    def add_solid(self, sld: building3d.geom.solid.Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are also added (if they were not already added manually).
        """
        if sld.uid in self.solids.keys():
            raise MeshError(f"Solid {sld.uid} already exists")
        self.solids[sld.uid] = sld

    def generate(self, boundary_vertices: dict[str, list[Point]] = {}):
        """Generate mesh for all added polygons and solids."""
        # Solids
        for _, sld in self.solids.items():
            mesh_volume = -1
            vertices = []
            elements = []
            num_tries = 0
            error = 0
            while not np.isclose(mesh_volume, sld.volume, rtol=GEOM_RTOL):
                logger.debug(f"Trying to mesh a solid: {sld.name} (try #{num_tries})")

                if num_tries >= SOLID_MESH_MAX_TRIES:
                    msg = (
                        f"Meshing the solid failed after {num_tries} tries "
                        f"(volume error = {error * 100.:.4f}%). Try using smaller delta."
                    )
                    logger.warning(msg)
                    raise MeshError(msg)

                num_tries += 1

                vertices, elements = delaunay_tetrahedralization(
                    sld=sld, boundary_vmap=boundary_vertices, delta=self.delta
                )

                mesh_volume = total_volume(vertices, elements)
                error = np.abs(mesh_volume - sld.volume) / sld.volume
                logger.debug(
                    f"Mesh volume = {mesh_volume} vs. Geom. volume = {sld.volume} "
                    f"(error = {error * 100.:4f}%)"
                )

            self._add_vertices(sld.name, vertices, elements)
            logger.debug(f"Meshing finished. {len(vertices)=}, {len(elements)=}")

        # Calculate volumes
        self._recalc_volumes()

    def copy(
        self,
        elements: None | list = None,
        max_vol: None | float = None,
    ) -> SolidMesh:
        """Create a filtered copy of itself."""
        mesh = SolidMesh(delta=self.delta)
        mesh.solids = self.solids

        if elements is not None:
            # Filtered copy
            mesh.vertices = self.vertices
            mesh.elements = elements
            mesh.vertices, mesh.elements = purge_mesh(mesh.vertices, mesh.elements)
            mesh.volumes = [vol for i, vol in enumerate(self.volumes) if i in elements]
        elif max_vol is not None:
            # Filtered copy
            mesh.vertices = self.vertices
            mesh.elements = [
                el for el, vol in zip(self.elements, self.volumes) if vol < max_vol
            ]
            mesh.vertices, mesh.elements = purge_mesh(mesh.vertices, mesh.elements)
            mesh.volumes = [vol for vol in self.volumes if vol < max_vol]
        else:
            # Full copy
            mesh.vertices = self.vertices
            mesh.elements = self.elements
            mesh.volumes = self.volumes

        return mesh

    def _add_vertices(self, owner, vertices, elements):
        # Increase face counter to include previously added vertices
        elements = np.array(elements)
        elements += len(self.vertices)
        elements = elements.tolist()

        # Add vertices
        len_before = len(self.vertices)
        self.vertices.extend(vertices)
        len_after = len(self.vertices)
        self.vertex_owners[owner] = [x for x in range(len_before, len_after)]

        # Add faces
        len_before = len(self.elements)
        self.elements.extend(elements)
        len_after = len(self.elements)
        self.element_owners[owner] = [x for x in range(len_before, len_after)]

    def _recalc_volumes(self):
        """Recalculate tetrahedra volumes."""
        self.volumes = []
        for el in self.elements:
            p0 = self.vertices[el[0]]
            p1 = self.vertices[el[1]]
            p2 = self.vertices[el[2]]
            p3 = self.vertices[el[3]]
            vol = tetrahedron_volume(p0, p1, p2, p3)
            self.volumes.append(vol)
