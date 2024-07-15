from tqdm import tqdm

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d import random_between
from building3d.geom.point import Point
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.ray import Ray
from building3d.simulators.rays.manyrays import ManyRays
from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.object_path import split_path


class RaySimulator(BaseSimulator):
    """Simulator class for ray tracing.

    Controls:
    - time steps
    - source and receiver
    - reflections
    - absorption
    - when to finish
    """
    def __init__(
        self,
        building: Building,
        source: Point,
        receiver: Point,
        receiver_radius: float,
        num_rays: int = 1000,
        speed: float = 343.0,
        time_step: float = 1e-4,
    ):
        self.building = building
        self.building_adj_polygons = building.get_graph()
        self.building_adj_solids = building.find_adjacent_solids()

        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius
        self.speed = speed
        self.time_step = time_step
        self.min_distance = speed * time_step * 1.01

        self.rays = ManyRays(speed=speed, time_step=time_step)
        self.rays.add_rays(source=source, num_rays=num_rays)

        self.transparent_polys = set(self._find_transparent_polygons())
        print("Transparent surfaces:", self.transparent_polys)

        # Find the location of the rays inside the building (zone_name/solid_name)
        self.location = []
        path_to_solid = ""
        for z in building.get_zones():
            for s in z.get_solids():
                if s.is_point_inside(source):
                    path_to_solid = object_path(zone=z, solid=s)
                    self.location = [path_to_solid for _ in range(len(self.rays))]

        if len(self.location) == 0:
            raise RuntimeError("Ray source outside solid.")

        # Find the next blocking surface (polygon)
        # Directions of rays are already known, so we can look at all polygons in the current solid
        # This will enable to track only one polygon per ray until the ray hits the surface
        zname, sname = split_path(path_to_solid)
        z = building.zones[zname]
        s = z.solids[sname]

        # Initialize lists with next surfaces and respective distances
        self.next_surface = ["" for _ in range(len(self.rays))]
        self.dist = [0.0 for _ in range(len(self.rays))]
        self.delta_dist = [0.0 for _ in range(len(self.rays))]

        print("Finding next blocking surface for each ray...")  # TODO: Add logger
        for i in tqdm(range(len(self.rays))):
            self._update_next_surface(i)

        print(self.next_surface)
        print(self.dist)
        # TODO:
        # - Decide if properties (transparency, absorption, scattering)
        #   should be stored here or in Wall
        # - Decide if subpolygons are of any use here
        ...

    def forward(self):
        # If distance below threshold, reflect (change direction)
        for i in range(len(self.rays)):
            if self.dist[i] < self.min_distance:
                # TODO: Consider transparent surfaces
                #       - pass through
                #       - update location
                if self.next_surface[i] in self.transparent_polys:
                    # NOTE: This may run multiple times (before/after passing through)
                    self._update_location(i)
                else:
                    # Reflect
                    poly = self.building.get_object(self.next_surface[i])
                    if isinstance(poly, Polygon):
                        self.rays[i].reflect(poly.normal)
                    else:
                        raise ValueError(f"Incorrect polygon type: {poly}")

                # For those that were reflected or let through a transparent surface
                # -> update next surface
                self._update_next_surface(i)

        # Move rays forward
        self.rays.forward()

        # Update distance to next surface
        # TODO: OPTIMIZE! THIS DOES NOT HAVE TO BE RUN EVERY STEP FOR EVERY RAY!!!!!!!!!!!
        for i in range(len(self.rays)):
            poly = self.building.get_object(self.next_surface[i])
            if isinstance(poly, Polygon):
                self.dist[i] = poly.distance_point_to_polygon(self.rays[i].position)
            else:
                raise ValueError(f"Incorrect polygon type: {poly}")

        # print(self.dist)

    def _update_next_surface(self, ray_index) -> None:
        """Update self.next_surface and self.dist for self.rays[ray_index]."""
        assert self.location is not None
        path_to_solid = self.location[ray_index]
        zname, sname = split_path(path_to_solid)
        z = self.building.zones[zname]
        s = z.solids[sname]
        found = False

        for w in s.get_walls():
            for p in w.get_polygons():
                r = self.rays[ray_index]
                if p.is_point_inside_projection(r.position, r.velocity):
                    self.next_surface[ray_index] = object_path(zone=z, solid=s, wall=w, poly=p)
                    self.dist[ray_index] = p.distance_point_to_polygon(r.position)
                    found = True
                    break
            if found:
                break

        if not found:
            # This should not happen, because all rays are initilized inside a solid
            # and solids must be fully enclosed with polygons
            raise RuntimeError("Some ray is not going towards any surface... (?)")

    def _update_location(self, ray_index) -> None:
        """Update the solid that the ray is located in. Changes `self.location`."""
        curr_solid = self.location[ray_index]
        adjacent_solids = self.building_adj_solids[curr_solid]
        for path_to_solid in adjacent_solids:
            s = self.building.get_object(path_to_solid)
            if isinstance(s, Solid):
                if s.is_point_inside(self.rays[ray_index].position):
                    self.location[ray_index] = path_to_solid
            else:
                raise ValueError(f"Incorrect solid type: {s}")

    def _find_transparent_polygons(self) -> list[str]:
        """Find and return the list of transparent polygons in the building.

        A polygon is transparent if it separates two adjacent solids within a single zone.
        """
        graph = self.building_adj_polygons

        transparent_polys = []
        added = set()

        for k, v in graph.items():
            if k not in added or v not in added:
                z0, _, _, _ = k.split(PATH_SEP)
                if v is not None:
                    z1, _, _, _ = v.split(PATH_SEP)
                    # Doesn't have to check if p0 is facing p1,
                    # because if they are in the graph, they must be
                    if z0 == z1:
                        transparent_polys.extend([k, v])
                        added.add(k)
                        added.add(v)

        return transparent_polys

    def is_finished(self):
        return False
