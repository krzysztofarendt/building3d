from __future__ import annotations
import logging
from typing import Sequence

from building3d import random_id
from building3d.geom.exceptions import GeometryError
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.paths import PATH_SEP
from building3d.geom.numba.points import bounding_box
from building3d.geom.numba.zone import Zone
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

    @property
    def path(self) -> str:
        return self.name

    def add_zone(self, zone: Zone) -> None:
        """Add a Zone instance."""
        if zone.name in self.children.keys():
            raise GeometryError(f"Zone {zone.name} already exists in {self.name}")

        zone.parent = self
        self.zones[zone.name] = zone
        logger.info(f"Zone {zone.name} added: {self}")

    def get(self, abspath: str):
        """Get object by the absolute path."""
        obj = abspath.split(PATH_SEP)
        assert len(obj) >= 1
        building = obj[0]
        assert building == self.name

        if len(obj) == 1:
            return self
        elif len(obj) == 2:
            zone = obj[1]
            return self[zone]
        elif len(obj) == 3:
            zone = obj[1]
            solid = obj[2]
            return self[zone][solid]
        elif len(obj) == 4:
            zone = obj[1]
            solid = obj[2]
            wall = obj[3]
            return self[zone][solid][wall]
        elif len(obj) == 5:
            zone = obj[1]
            solid = obj[2]
            wall = obj[3]
            polygon = obj[4]
            return self[zone][solid][wall][polygon]
        elif len(obj) == 6:
            zone = obj[1]
            solid = obj[2]
            wall = obj[3]
            polygon = obj[4]
            index = int(obj[5])
            return self[zone][solid][wall][polygon][index]
        else:
            raise ValueError(f"Incorrect absolute path: {abspath}")

    def find_adjacent_solids(self, recalc=False) -> dict[str, list[str]]:
        """Return a dict mapping adjacent solids.

        The keys of the returned dict are solid paths, i.e. "zone_name/solid_name".
        The values are lists of adjacent solid paths.
        """
        # TODO: Add unit test
        if len(self.adj_solids) > 0 and recalc is False:
            return self.adj_solids
        else:
            zones = self.children.values()
            adjacent = {}
            for zi in zones:
                for zj in zones:
                    solids_i = zi.children.values()
                    solids_j = zj.children.values()
                    for si in solids_i:
                        for sj in solids_j:
                            if si.path not in adjacent:
                                adjacent[si.path] = []
                            if si.is_adjacent_to_solid(sj, exact=False):
                                adjacent[si.path].append(sj.path)
            self.adj_solids = adjacent
            return adjacent

    def stitch_solids(self):
        """Find adjacent solids and stitch them."""
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
        for z in self.children.values():
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
        return get_mesh_from_zones(list(self.children.values()))

    def __str__(self):
        s = f"Building(name={self.name}, "
        s += f"zones={list(self.children.keys())}, "
        s += f"id={hex(id(self))})"
        return s

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key) -> Zone:
        return self.zones[key]
