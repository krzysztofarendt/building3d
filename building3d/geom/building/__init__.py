from __future__ import annotations

import logging
from typing import Sequence

from building3d.random import random_id
from building3d.geom.building.get_mesh import get_mesh_from_zones
from building3d.geom.building.graph import graph_polygon
from building3d.geom.building.graph import graph_solid
from building3d.geom.building.graph import graph_wall
from building3d.geom.building.graph import graph_zone
from building3d.geom.exceptions import GeometryError
from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.bboxes import bounding_box
from building3d.geom.solid.stitch import stitch_solids
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.zone import Zone

logger = logging.getLogger(__name__)


class Building:
    """Building is a collection of zones.

    Zones do not need to touch one another.
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
        self.adj_solids = {}

        for zn in zones:
            self.add_zone(zn)

        self.graph = {}
        self.graph_wall = {}
        self.graph_solid = {}
        self.graph_zone = {}

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
        """Get object by the absolute path.

        Args:
            abspath: absolute path to an object, starting with the building name.

        Returns:
            object (Building, Zone, Solid, Wall, or Polygon).

        Raises:
            ValueError: If the path does not point to any existing object.
        """
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

    def get_polygon_paths(self) -> list[str]:
        """Returns a list of all paths to polygons belonging to this building."""
        poly_paths = []
        bn = self.name

        for zn, z in self.zones.items():
            for sn, s in z.solids.items():
                for wn, w in s.walls.items():
                    for pn, _ in w.polygons.items():
                        path = PATH_SEP.join([bn, zn, sn, wn, pn])
                        poly_paths.append(path)
        return poly_paths

    def get_graph(
        self,
        new: bool = False,
        level: str = "polygon",
        facing: bool = True,
        overlapping: bool = False,
        touching: bool = False,
    ) -> dict[str, list[str]]:
        """Returns the graph of this building. Uses cached dict or makes new if requested.

        By default, assumes that connections are only when polygons are:
        - facing
        - not overlapping
        - not touching

        Args:
            new: if True, recalculates the graph
            level: "polygon" | "wall" | "solid" | "zone"

        Returns:
            dict with connections at a specified level
        """
        if len(self.graph) == 0:
            new = True

        if new is True:
            self.graph = graph_polygon(self, facing, overlapping, touching)
            self.graph_wall = graph_wall(
                self, facing, overlapping, touching, self.graph
            )
            self.graph_solid = graph_solid(
                self, facing, overlapping, touching, self.graph
            )
            self.graph_zone = graph_zone(
                self, facing, overlapping, touching, self.graph
            )

        if level == "polygon":
            return self.graph
        elif level == "wall":
            return self.graph_wall
        elif level == "solid":
            return self.graph_solid
        elif level == "zone":
            return self.graph_zone
        else:
            raise ValueError(f"Level not recognized: {level}")

    def stitch_solids(self):
        """Find adjacent solids and stitch them."""
        logger.info(f"Stitching solids in building {self}")

        # Find adjacent solids
        adj_solids = self.get_graph(new=False, level="solid", facing=True, overlapping=True)
        done = []

        for s_path in adj_solids.keys():
            for adj_s_path in adj_solids[s_path]:
                _, z1_name, s_name = s_path.split(PATH_SEP)
                _, z2_name, adj_s_name = adj_s_path.split(PATH_SEP)

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
