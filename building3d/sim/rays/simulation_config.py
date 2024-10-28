class SimulationConfig:

    def __init__(self):

        # Verbosity (turns on prints in the JIT-compiled code)
        self.verbose = True

        # Simulation engine parameters
        self.engine = {
            "buffer_size": 200,
            "time_step": 1e-4,
            "num_steps": 100,
            "voxel_size": 0.1,
            "search_transparent": True,
        }

        # Ray configuration
        self.rays = {
            "num_rays": 100,
            "ray_speed": 343.0,
            "source": (0.0, 0.0, 0.0),
            "absorbers": [],  # list of tuples, shape (num_absorbers, 3)
            "absorber_radius": 0.1,
        }

        # Surface parameters
        self.surfaces = {
            "absorption": {
                "default": 0.2,
                # Examples overwriting the default value for specific polygons
                # "bname/zname": 0.1,
                # "bname/zname/sname/wname/pname": 0.5,
            },
        }

        # Visualization parameters (plots, movies)
        self.visualization = {
            "ray_opacity": 0.5,
            "ray_trail_length": 16,
            "ray_trail_opacity": 0.3,
            "ray_point_size": 3.0,
            "building_opacity": 0.1,
            "building_color": (0.8, 0.8, 0.8),
            "movie_fps": 30,
            "movie_colormap": "RdPu",
        }

        # Path templates
        # (all paths relative to the project output directory)
        self.paths = {
            "energy_file": "energy_<step>.npy",
            "position_file": "position_<step>.npy",
            "velocity_file": "velocity_<step>.npy",
            "hits_file": "hits_<step>.npy",
            "state_dir": "state",
            "main_log_file": "main.log",
            "movie_file": "simulation.mp4",
            "b3d_file": "building.b3d",
        }
