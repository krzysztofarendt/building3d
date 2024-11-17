import logging
import os

import numpy as np

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.types import PointType, FloatDataType, FLOAT
from building3d.io.arrayformat import to_array_format
from building3d.io.arrayformat import get_polygon_points_and_faces

from .dump_buffers import dump_buffers
from .find_transparent import find_transparent
from .simulation_loop import simulation_loop
from .simulation_config import SimulationConfig
from .voxel_grid import make_voxel_grid

logger = logging.getLogger(__name__)


class Simulation:

    def __init__(
        self,
        building: Building,
        sim_cfg: SimulationConfig,
    ):
        # REPRESENT GEOMETRY IN A NUMBA-FRIENDLY WAY ==========================
        # Convert building to the array format
        logger.info("Converting the building to the array format")
        points, faces, polygons, walls, _, _ = to_array_format(building)
        self.points = points
        self.faces = faces
        self.polygons = polygons
        self.walls = walls

        # READ CONFIGURATION ==================================================
        self.sim_cfg = sim_cfg

        # Verbosity (turns on prints in the JIT-compiled code)
        self.verbose = sim_cfg.verbose

        # Paths
        self.project_dir: str = sim_cfg.paths["project_dir"]
        self.buffer_dir: str = sim_cfg.paths["buffer_dir"]

        # Engine parameters
        self.num_steps: int = sim_cfg.engine["num_steps"]
        self.time_step: float = sim_cfg.engine["time_step"]
        self.batch_size: int = sim_cfg.engine["batch_size"]
        self.voxel_size: float = sim_cfg.engine["voxel_size"]
        self.search_transparent: bool = sim_cfg.engine["search_transparent"]

        # Ray parameters
        self.num_rays: int = sim_cfg.rays["num_rays"]
        self.ray_speed: float = sim_cfg.rays["ray_speed"]
        self.source: PointType = np.array(sim_cfg.rays["source"], dtype=FLOAT)
        self.absorbers: PointType = np.array(sim_cfg.rays["absorbers"], dtype=FLOAT)
        self.absorber_radius: float = sim_cfg.rays["absorber_radius"]

        # Surface parameters
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

        # FIND TRANSPARENT POLYGONS ===========================================
        self.trans_poly_nums = set([-1])  # JIT function can't get an empty set
        if self.search_transparent:
            self.trans_poly_nums = self.get_transparent_polygon_numbers(building)

        # Sanitizers ==========================================================
        assert self.num_steps >= self.batch_size, "num_steps can't smaller than batch_size"
        assert self.num_steps % self.batch_size == 0, "num_steps must be a multiple of batch_size"

        # Prepare project directory ===========================================
        self.make_dirs()

    def make_dirs(self):
        # Create project directory
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)
        # Create buffer (state) directory, but raise error if it exists and is not empty
        # because that's a commmon source of errors when some states are overwritten
        if os.path.exists(self.buffer_dir) and len(os.listdir(self.buffer_dir)) > 0:
            raise RuntimeError(f"Buffer dir ({self.buffer_dir}) already exists and is non-empty!")
        else:
            os.makedirs(self.buffer_dir)

    @staticmethod
    def get_transparent_polygon_numbers(building):
        # Get transparent polygons
        logger.info("Finding transparent surfaces")
        # TODO: Very slow if many polygons
        # Complexity:
        # - worst case scenario -> O(n^2),
        # - best case scenario -> O(n),
        # where n is the number of polygons.
        trans_poly_paths = find_transparent(building)

        # Can't have an empty set because of Numba. Polygon -1 doesn't exist anyway.
        trans_poly_nums = set([-1])
        for poly_path in trans_poly_paths:
            poly = building.get(poly_path)
            assert isinstance(poly, Polygon)
            assert poly.num is not None
            trans_poly_nums.add(poly.num)

        return trans_poly_nums

    def run(self):
        logger.info("Starting the simulation")

        # Get initial position of rays
        position = np.zeros((self.num_rays, 3), dtype=FLOAT)
        for i in range(self.num_rays):
            position[i, :] = self.source

        # Get initial velocity of rays
        init_direction = np.random.rand(self.num_rays, 3) * 2.0 - 1.0
        for i in range(self.num_rays):
            init_direction[i] /= np.linalg.norm(init_direction[i])
        velocity = init_direction * self.ray_speed

        # Get initial energy and hits
        energy = np.ones(self.num_rays, dtype=FLOAT)
        num_absorbers = self.absorbers.shape[0]
        hits = np.zeros(num_absorbers, dtype=FLOAT)

        # Make voxel grid
        min_x = self.points[:, 0].min()
        min_y = self.points[:, 1].min()
        min_z = self.points[:, 2].min()
        max_x = self.points[:, 0].max()
        max_y = self.points[:, 1].max()
        max_z = self.points[:, 2].max()

        poly_pts = []
        poly_tri = []
        num_polys = len(self.walls)
        for pn in range(num_polys):
            pts, tri = get_polygon_points_and_faces(self.points, self.faces, self.polygons, pn)
            poly_pts.append(pts)
            poly_tri.append(tri)

        grid = make_voxel_grid(
            min_xyz=(min_x, min_y, min_z),
            max_xyz=(max_x, max_y, max_z),
            poly_pts=poly_pts,
            step=self.voxel_size,
            verbose=self.verbose,
        )

        # Run simulation loop (JIT compiled) in batches
        step = 0

        # Define buffers so that pyright doesn't complain that they may be unbound
        pos_buf = np.array([],  dtype=FLOAT)
        enr_buf = np.array([],  dtype=FLOAT)
        hit_buf = np.array([],  dtype=FLOAT)

        while step < self.num_steps:
            pos_buf, enr_buf, hit_buf = simulation_loop(
                init_step = step,
                num_steps = self.batch_size,
                num_rays = self.num_rays,
                ray_speed = self.ray_speed,
                time_step = self.time_step,
                grid_step = self.voxel_size,
                grid = grid,
                position = position,
                velocity = velocity,
                energy = energy,
                hits = hits,
                absorbers = self.absorbers,
                absorber_radius = self.absorber_radius,
                points = self.points,
                faces = self.faces,
                polygons = self.polygons,
                walls = self.walls,
                transparent_polygons = self.trans_poly_nums,
                surf_absorption = self.surf_absorption,
                verbose = self.verbose,
            )

            # Dump buffers for the current batch
            dump_buffers(pos_buf, enr_buf, hit_buf, self.buffer_dir, self.sim_cfg, step)
            logger.debug(f"Buffers saved ({step}-{step+self.batch_size})")

            # Update state
            position = pos_buf[-1]
            velocity = (pos_buf[-1] - pos_buf[-2]) / self.time_step
            energy = enr_buf[-1]
            hits = hit_buf[-1]

            # Increase step number
            step += self.batch_size

        logger.info("Simulation finished!")
        return pos_buf, enr_buf, hit_buf
