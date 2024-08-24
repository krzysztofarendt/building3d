from __future__ import annotations
import logging
from typing import Sequence

from building3d import random_id
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.paths import PATH_SEP
from building3d.geom.numba.points import bounding_box
from building3d.geom.numba.zone import Zone
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.numba.building.get_mesh import get_mesh_from_zones
from building3d.geom.numba.solid.stitch import stitch_solids


logger = logging.getLogger(__name__)


class Building:
    """Building is a collection of zones.

    Zones do not have to be adjacent. They can even be separate buildings.
    """
    def __init__(
        self,
        zones: Sequence[Zone] = (),
        name: str | None = None,
        uid: str | None = None,
    ):
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
        self.graph = {}
        self.adj_solids = {}

        for zn in zones:
            self.add_zone(zn)

        logger.info(f"Building created: {self}")

    @property
    def children(self) -> dict[str, Zone]:
        return self.zones

    @property
    def parent(self) -> None:
        return None

    def add_zone(self, zone: Zone) -> None:
        """Add a Zone instance."""
        self.zones[zone.name] = zone
        logger.info(f"Zone {zone.name} added: {self}")

    def get_zone_names(self) -> list[str]:
        """Get list of zone names."""
        return list(self.zones.keys())

    def get_zones(self) -> list[Zone]:
        """Get list of zones."""
        return list(self.zones.values())

    def get_object(self, path: str) -> Zone | Solid | Wall | Polygon:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        zone_name = names.pop(0)

        if zone_name not in self.get_zone_names():
            raise ValueError(f"Zone {zone_name} not found")
        elif len(names) == 0:
            return self.zones[zone_name]
        else:
            return self.zones[zone_name].get_object("/".join(names))

    def get_graph(self, recalc=False) -> dict[str, str | None]:
        """Return graph matching adjacent polygons.

        Each polygon can have only 0 or 1 adjacent polygons. (TODO -> NOT TRUE? Why list then?)
        Polygons that are partially overlapping are considered non-adjacent.

        Expect return value in the following format:
        ```
        graph["zone0/solid0/wall0/polygon0"] = "zone1/solid1/wall1/polygon1"
        ```
        """
        if len(self.graph) > 0 and recalc is False:
            return self.graph
        else:
            graph = {}
            adjacent_solids = self.find_adjacent_solids()

            # TODO: DON'T LOVE BELOW CODE
            # For each polygon find the adjacent polygon (there can be only 1)
            for zone in self.get_zones():
                for solid in zone.get_solids():
                    for wall in solid.get_walls():
                        for poly in wall.get_polygons():
                            found = False
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
        # TODO: Add unit test
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
        """Find adjacent solids and stitch them.
        """
        logger.info(f"Stitching solids in building {self}")

        adj_solids = self.find_adjacent_solids()
        done = []

        for s_path in adj_solids.keys():
            for adj_s_path in adj_solids[s_path]:
                z1_name, s_name = s_path.split(PATH_SEP)
                z2_name, adj_s_name = adj_s_path.split(PATH_SEP)

                if set([s_name, adj_s_name]) not in done:
                    stitch_solids(
                        s1=self.zones[z1_name].solids[s_name],
                        s2=self.zones[z2_name].solids[adj_s_name],
                    )
                    done.append(set([s_name, adj_s_name]))

    def volume(self) -> float:
        """Calculate building volume as the sum of zone volumes."""
        volume = 0.0
        for z in self.get_zones():
            volume += z.volume()
        return volume

    def bbox(self) -> tuple[PointType, PointType]:
        pts, _ = self.get_mesh()
        return bounding_box(pts)

    def get_mesh(self) -> tuple[PointType, IndexType]:
        """Get vertices and faces of this building's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Return:
            tuple of vertices and faces
        """
        return get_mesh_from_zones(self.get_zones())

    def __str__(self):
        s = f"Building(name={self.name}, "
        s += f"zones={self.get_zone_names()}, "
        s += f"id={hex(id(self))})"
        return s

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key) -> Zone:
        return self.zones[key]
