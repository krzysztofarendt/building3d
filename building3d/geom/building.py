"""Building class"""
from __future__ import annotations

import numpy as np

from building3d import random_id
from building3d.geom.operations.stitch_solids import stitch_solids
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.paths import PATH_SEP
from building3d.geom.point import Point
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
import building3d.mesh.mesh as mesh
from building3d.config import MESH_DELTA


class Building:
    """Building is a collection of zones.

    Zones do not have to be adjacent. They can even be separate buildings.
    """
    def __init__(self, name: str | None = None, uid: str | None = None):
        """Initialize the building.

        Args:
            name: name of the building
            uid: unique id of the building, random if None
        """
        if name is None:
            name = random_id()
        self.name = validate_name(name)
        if uid is not None:
            self.uid = uid
        else:
            self.uid = random_id()
        self.zones: dict[str, Zone] = {}  # {Zone.name: Zone}
        self.mesh = mesh.Mesh()
        self.graph = {}
        self.adj_solids = {}

    def add_zone(self, zone: Zone) -> None:
        """Add a Zone instance."""
        self.zones[zone.name] = zone

    def get_zone_names(self) -> list[str]:
        """Get list of zone names."""
        return list(self.zones.keys())

    def get_zones(self) -> list[Zone]:
        """Get list of zones."""
        return list(self.zones.values())

    def get_object(self, path: str) -> Zone | Solid | Wall | Polygon | None:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        zone_name = names.pop(0)

        if zone_name not in self.get_zone_names():
            raise ValueError(f"Zone {zone_name} not found")
        elif len(names) == 0:
            return self.zones[zone_name]
        else:
            return self.zones[zone_name].get_object("/".join(names))

    def get_graph(self, recalc=False) -> dict:
        """Return graph matching adjacent polygons.

        Each polygon can have only 0 or 1 adjacent polygons.
        Polygons that are partially overlapping are considered non-adjacent.

        Expect return value in the following format:
        ```
        graph["zone0/solid0/wall0/polygon0"] = ["zone1/solid1/wall1/polygon1", ...]
        ```
        """
        if len(self.graph) > 0 and recalc is False:
            return self.graph
        else:
            graph = {}
            adjacent_solids = self.find_adjacent_solids()
            found = False

            # For each polygon find the adjacent polygon (there can be only 1)
            for zone in self.get_zones():
                for solid in zone.get_solids():
                    for wall in solid.get_walls():
                        for poly in wall.get_polygons():
                            poly_path = PATH_SEP.join([zone.name, solid.name, wall.name, poly.name])
                            graph[poly_path] = None
                            # Find adjacent polygon (look only at the adjacent solids)
                            solid_path = PATH_SEP.join([zone.name, solid.name])
                            for a_solid_path in adjacent_solids[solid_path]:
                                z, s = a_solid_path.split(PATH_SEP)  # Adjacent zone and solid names
                                for w in self.zones[z].solids[s].get_wall_names():
                                    for p in self.zones[z].solids[s].walls[w].get_polygon_names():
                                        adj_poly_path = PATH_SEP.join([z, s, w, p])
                                        adj_poly = self.get_object(adj_poly_path)
                                        if poly.is_facing_polygon(adj_poly):
                                            graph[poly_path] = adj_poly_path
                                            found = True
                                        if found:
                                            break
                                    if found:
                                        break
                                if found:
                                    break
            self.graph = graph
            return graph

    def find_adjacent_solids(self, recalc=False) -> dict[str, list[str]]:
        """Return a dict mapping adjacent solids.

        The keys of the returned dict are solid paths, i.e. "zone_name/solid_name".
        The values are lists of adjacent solid paths.
        """
        if len(self.adj_solids) > 0 and recalc is False:
            return self.adj_solids
        else:
            zones = self.get_zones()
            adjacent = {}
            for i in range(len(zones)):
                for j in range(i, len(zones)):
                    solids_i = zones[i].get_solids()
                    solids_j = zones[j].get_solids()
                    for si in solids_i:
                        for sj in solids_j:
                            path_to_si = object_path(zones[i], si)
                            path_to_sj = object_path(zones[j], sj)
                            if path_to_si not in adjacent:
                                adjacent[path_to_si] = []
                            if si.is_adjacent_to_solid(sj, exact=False):
                                adjacent[path_to_si].append(path_to_sj)
            self.adj_solids = adjacent
            return adjacent

    def stitch_solids(self):
        """Find adjacent solids and stitch them."""
        adj_solids = self.find_adjacent_solids()
        done = []

        for sld_path in adj_solids.keys():
            for adj_sld_path in adj_solids[sld_path]:
                z1_name, sld_name = sld_path.split(PATH_SEP)
                z2_name, adj_sld_name = adj_sld_path.split(PATH_SEP)

                if set([sld_name, adj_sld_name]) not in done:
                    new_sld, new_adj_sld = stitch_solids(
                        sld1=self.zones[z1_name].solids[sld_name],
                        sld2=self.zones[z2_name].solids[adj_sld_name],
                    )

                    self.zones[z1_name].solids[sld_name] = new_sld
                    self.zones[z2_name].solids[adj_sld_name] = new_adj_sld

                    done.append(set([sld_name, adj_sld_name]))

    def volume(self) -> float:
        """Calculate building volume as the sum of zone volumes."""
        volume = 0.0
        for z in self.zones.values():
            volume += z.volume()
        return volume

    def get_mesh(
        self,
        children: bool = True,
    ) -> tuple[list[Point], list[list[int]]]:
        """Get vertices and faces of this building's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Args:
            children: if True, will include subpolygons

        Return:
            tuple of vertices and faces
        """
        verts = []
        faces = []

        for z in self.zones.values():
            offset = len(verts)
            v, f = z.get_mesh(children)
            verts.extend(v)
            f = np.array(f) + offset
            f = [list(x) for x in f]
            faces.extend(f)

        return verts, faces

    def generate_simulation_mesh(
        self,
        delta: float | None = None,
        include_volumes: bool = False,
    ) -> None:
        """Generate mesh suitable for numerical simulations.

        Generates surface mesh by default (`PolyMesh`).
        If `include_volumes` is `True`, generates also the volume mesh (`SolidMesh`).

        Args:
            delta: approximate element size, will use default is `None`
            include_volumes: if True, will generate surface and volume meshes
        """
        if delta is None:
            delta = MESH_DELTA

        self.mesh = mesh.Mesh(delta=delta)

        for zone in self.get_zones():
            self.mesh.add_zone(zone)

        self.mesh.generate(solidmesh=include_volumes)

    def __eq__(self, other) -> bool:
        """Returns True if all zones of this and other are equal."""
        if len(self.zones.values()) != len(other.zones.values()):
            return False
        else:
            num_matches = 0
            for this_zone in self.zones.values():
                for other_zone in other.zones.values():
                    if this_zone == other_zone:
                        num_matches += 1
                        break
            if num_matches != len(self.zones.values()):
                return False
            return True
