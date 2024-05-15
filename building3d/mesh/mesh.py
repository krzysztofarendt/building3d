from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.zone import Zone
from building3d.mesh.polymesh import PolyMesh
from building3d.mesh.solidmesh import SolidMesh
from building3d.config import MESH_DELTA


class Mesh:

    def __init__(self, delta: float = MESH_DELTA):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.polymesh = PolyMesh(delta)
        self.solidmesh = SolidMesh(delta)

    def add_polygon(self, poly: Polygon):
        """Add polygon insntance to the list of polygons for this mesh.

        This is not required if this polygon is part of a solid added to this mesh.
        """
        self.polymesh.add_polygon(poly)

    def add_solid(self, sld: Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are added automatically.
        """
        self.solidmesh.add_solid(sld)
        for poly in sld.polygons():
            self.add_polygon(poly)

    def add_zone(self, zone: Zone):
        """Add zone. It will add all solids and polygons of the zone."""
        for _, solid in zone.solids.items():
            self.add_solid(solid)

    def generate(self, solidmesh=False):
        """Generate mesh for all added polygons and solids."""
        self.polymesh.generate()
        boundary_vertices = self.polymesh.get_vertices_per_polygon()
        if solidmesh is True:
            self.solidmesh.generate(boundary_vertices)
