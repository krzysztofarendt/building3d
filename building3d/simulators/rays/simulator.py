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

        self.rays = ManyRays(
            building=building,
            source=source,
            speed=speed,
            time_step=time_step,
        )
        self.rays.add_rays(num_rays=num_rays)

        self.transparent_polys = set(self._find_transparent_polygons())
        print("Transparent surfaces:", self.transparent_polys)

        # Initialize rays: find enclosing solid, find next surface for each ray
        self.rays.init_location()

        print("Finding next surface for each ray...")
        for i in tqdm(range(len(self.rays))):
            self.rays[i].update_target_surface()

        # TODO:
        # - Decide if properties (transparency, absorption, scattering)
        #   should be stored here or in Wall
        # - Decide if subpolygons are of any use here
        ...

    def forward(self):
        # If distance below threshold, reflect (change direction)
        for i in range(len(self.rays)):
            if self.rays[i].get_distance() is None:
                self.rays[i].update_distance()

            d = self.rays[i].get_distance()
            if d is not None and d < self.min_distance:
                # TODO: Consider transparent surfaces
                #       - pass through
                #       - update location
                if self.rays[i].get_target_surface() in self.transparent_polys:
                    # NOTE: This may run multiple times (before/after passing through)
                    self.rays[i].update_location()
                else:
                    # Reflect
                    poly = self.building.get_object(self.rays[i].get_target_surface())
                    if isinstance(poly, Polygon):
                        self.rays[i].reflect(poly.normal)
                    else:
                        raise ValueError(f"Incorrect polygon type: {poly}")

                # For those that were reflected or let through a transparent surface
                # -> update next surface
                self.rays[i].update_target_surface()
                self.rays[i].update_distance()

        # Move rays forward
        self.rays.forward()

        # Update distance to next surface
        # TODO: OPTIMIZE! THIS DOES NOT HAVE TO BE RUN EVERY STEP FOR EVERY RAY!!!!!!!!!!!
        for i in range(len(self.rays)):
            self.rays[i].update_distance()

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

    def simulate(self, steps: int):
        print("Simulation...")
        for _ in tqdm(range(steps)):
            self.forward()

    def is_finished(self):
        return False
