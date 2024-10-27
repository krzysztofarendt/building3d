import logging

import numpy as np

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.types import PointType, FloatDataType, FLOAT
from building3d.io.arrayformat import to_array_format

from .find_transparent import find_transparent
from .simulation_loop import simulation_loop
from .simulation_config import SimulationConfig

logger = logging.getLogger(__name__)


class Simulation:

    def __init__(
        self,
        building: Building,
        sim_cfg: SimulationConfig,
    ):
        self.building: Building = building

        # Convert building to the array format
        logger.info("Converting the building to the array format")
        points, faces, polygons, walls, _, _ = to_array_format(self.building)
        self.points = points
        self.faces = faces
        self.polygons = polygons
        self.walls = walls

        # Engine parameters
        self.buffer_size: int = sim_cfg.engine["buffer_size"]
        self.time_step: float = sim_cfg.engine["time_step"]
        self.num_steps: int = sim_cfg.engine["num_steps"]
        self.voxel_size: float = sim_cfg.engine["voxel_size"]
        self.search_transparent: bool = sim_cfg.engine["search_transparent"]

        # Ray parameters
        self.num_rays: int = sim_cfg.rays["num_rays"]
        self.ray_speed: float = sim_cfg.rays["ray_speed"]
        self.source: PointType = np.array(sim_cfg.rays["source"], dtype=FLOAT)
        self.absorbers: PointType = np.array(sim_cfg.rays["absorbers"], dtype=FLOAT)
        self.absorber_radius: float = sim_cfg.rays["absorber_radius"]

        # Surface parameters
        # TODO: surface absorption should be an array of floats, shape (num_polygons, )
        # TODO: Add a possibility to overwrite the default value for selected polygons
        default_absorption = sim_cfg.surfaces["absorption"]["default"]
        self.surf_absorption: FloatDataType = np.full(len(self.polygons), default_absorption)

        # Visualization parameters
        # TODO: Should these parameters be here? Plotting and movie rendering isn't here...
        self.ray_opacity: float = sim_cfg.visualization["ray_opacity"]
        self.ray_trail_length: float = sim_cfg.visualization["ray_trail_length"]
        self.ray_trail_opacity: float = sim_cfg.visualization["ray_trail_opacity"]
        self.ray_point_size: float = sim_cfg.visualization["ray_point_size"]
        self.building_opacity: float = sim_cfg.visualization["building_opacity"]
        self.building_color: tuple = sim_cfg.visualization["building_color"]
        self.movie_fps: int = sim_cfg.visualization["movie_fps"]
        self.movie_colormap: str = sim_cfg.visualization["movie_colormap"]

    def run(self):
        # Get transparent polygons
        logger.info("Finding transparent surfaces")
        if self.search_transparent:
            # TODO: Very slow if many polygons
            # Complexity:
            # - worst case scenario -> O(n^2),
            # - best case scenario -> O(n),
            # where n is the number of polygons.
            trans_poly_paths = find_transparent(self.building)
        else:
            trans_poly_paths = set()

        # Can't have an empty set because of Numba. Polygon -1 doesn't exist anyway.
        trans_poly_nums = set([-1])
        for poly_path in trans_poly_paths:
            poly = self.building.get(poly_path)
            assert isinstance(poly, Polygon)
            assert poly.num is not None
            trans_poly_nums.add(poly.num)

        # Run simulation loop (JIT compiled)
        logger.info("Starting the simulation")
        pos_buf, vel_buf, enr_buf, hit_buf = simulation_loop(
            num_steps = self.num_steps,
            num_rays = self.num_rays,
            ray_speed = self.ray_speed,
            time_step = self.time_step,
            grid_step = self.voxel_size,
            source = self.source,
            absorbers = self.absorbers,
            absorber_radius = self.absorber_radius,
            points = self.points,
            faces = self.faces,
            polygons = self.polygons,
            walls = self.walls,
            transparent_polygons = trans_poly_nums,
            surf_absorption = self.surf_absorption,
            buffer_size = self.buffer_size,
        )
        logger.info("Finished the simulation")
        return pos_buf, vel_buf, enr_buf, hit_buf
