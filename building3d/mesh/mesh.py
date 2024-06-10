from __future__ import annotations
import logging
import time

import building3d.geom.building
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.zone import Zone
from building3d.mesh.polymesh import PolyMesh
from building3d.mesh.solidmesh import SolidMesh
from building3d.config import MESH_DELTA


logger = logging.getLogger(__name__)


class Mesh:

    def __init__(self, delta: float = MESH_DELTA):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.polymesh = PolyMesh(delta)
        self.solidmesh = SolidMesh(delta)

    def add_polygon(self, poly: Polygon):
        """Add polygon instance to the list of polygons for this mesh.

        This is not required if this polygon is part of a solid added to this mesh.
        """
        self.polymesh.add_polygon(poly)

    def add_solid(self, sld: Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are added automatically.
        """
        self.solidmesh.add_solid(sld)
        for wall in sld.get_walls():
            for poly in wall.get_polygons(children=False):
                self.add_polygon(poly)

    def add_zone(self, zone: Zone):
        """Add zone. It will add all solids and polygons of the zone."""
        for _, solid in zone.solids.items():
            self.add_solid(solid)

    def add_building(self, building: building3d.geom.building.Building):
        """Add building and all its zones, solids, polygons.

        Additionally, the mesh is assigned to the building.mesh.
        This method changes the building mesh attribute in-place.

        Args:
            building: Building instance

        Return:
            None
        """
        for _, zone in building.zones.items():
            self.add_zone(zone)
        building.mesh = self  # NOTE: Changes building in-place!

    def generate(self, solidmesh=False):
        """Generate mesh for all added polygons and solids."""
        t0 = time.time()

        self.polymesh.generate()
        t_polymesh = time.time()

        boundary_vertices = self.polymesh.get_vertices_per_polygon()
        t_boundary_vertices = time.time()

        if solidmesh is True:
            self.solidmesh.generate(boundary_vertices)
        t_solidmesh = time.time()

        time_poly = t_polymesh - t0
        time_boundary = t_boundary_vertices - t_polymesh
        time_solid = t_solidmesh - t_boundary_vertices
        logger.info(
            f"Mesh generation time: poly mesh = {time_poly:.2f}s, " + \
            f"collect boundary vertices = {time_boundary:.2f}s, " + \
            f"solid mesh = {time_solid:.2f}s"
        )
