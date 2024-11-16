import logging

import numpy as np

from building3d.geom.types import FloatDataType, FLOAT
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon

from .jit_print import jit_print


logger = logging.getLogger(__name__)


class SimulationConfig:

    def __init__(self, building: Building):

        self.building = building

        # Verbosity (turns on prints in the JIT-compiled code)
        self.verbose = True

        # Simulation engine parameters
        self.engine = {
            "time_step": 2.5e-5,  # Max. freq. = 1 / (2 * dt) = 20 kHz
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
                # To add custom values to each polygon use self.set_surface_param()
            },
        }
        self.set_default_surface_paths(self.building)

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
            "hits_file": "hits_<step>.npy",
        }

    def set_default_surface_paths(self, building: Building):
        """Add all polygon paths to surface parameters and fill them with default values."""
        poly_paths = building.get_polygon_paths()
        for key in self.surfaces.keys():
            for path in poly_paths:
                self.surfaces[key][path] = self.surfaces[key]["default"]

    def set_surface_param(
        self,
        param_name: str,
        surface_path: str,
        value: float,
        building: Building,
    ) -> None:
        """Sets the surface parameter value based on the surface path.

        The surface paths can be complete or partial.
        A complete path includes all objects from the building to the polygon, e.g.:
        `bname/zname/sname/wname/pname`.

        A partial path ends with a building, zone, solid, or wall.
        It is assumed that all children of a given parent get the same value.
        For example, if you set
        `sim_cfg.set_surface_param("absorption", "bname/zname/sname", 0.1, bdg)`,
        then all polygons within the solid `sname` will have `absoprtion` equal to 0.1.

        Args:
            param_name: Name of the parameter, e.g. "absorption".
            surace_path: Path to polygons, can be complete or partial (see description above).
            value: Value to assign.
            building: Building instance, used only to assert that the path exists.

        Returns:
            None
        """
        try:
            obj = building.get(surface_path)
        except (ValueError, KeyError) as e:
            err_msg = "Path does not point to any existing object in the building."
            jit_print(self.verbose, err_msg)
            logger.error(err_msg)
            logger.error(str(e))
            raise e

        if isinstance(obj, Polygon):
            self.surfaces[param_name][surface_path] = value
        elif isinstance(obj, (Building, Zone, Solid, Wall)):
            # Set the value to all polygons belonging to this object
            polygon_paths = obj.get_polygon_paths()
            for path in polygon_paths:
                self.surfaces[param_name][path] = value
        else:
            raise TypeError(f"Incorrect type of object: {type(obj)}")

    def surface_params_to_array(
        self,
        param_name: str,
        building: Building,
    ) -> FloatDataType:
        """Converts a dict with surface parameter values to an array.

        This array can be then passed to the `simulation_loop()` function,
        e.g. through the `surf_absorption` argument.

        Args:
            param_name: Name of the parameter, e.g. "absorption".
            building: Building instance, used to get the polygon numbers.

        Returns:
            Array shaped (len(polygons), ), each element's index corresponds to polygon.num.
            Polygon numbers are assigned to polygon instances during the conversion to
            the array format, so this method must be called when after the numbers are assigned.
        """
        # Get all polygon paths
        poly_paths = building.get_polygon_paths()

        # Create an array of surface parameter values for all polygons
        values = np.zeros(len(poly_paths), dtype=FLOAT)

        for pp in poly_paths:
            poly = building.get(pp)
            assert isinstance(poly, Polygon)
            if poly.num is None:
                raise RuntimeError("Polygon not numbered by the array format converter yet.")
            assert 0 <= poly.num < len(poly_paths), "The polygon is numbered incorrectly"

            # Assign values to the return array
            if pp in self.surfaces[param_name]:
                values[poly.num] = self.surfaces[param_name][pp]
            else:
                values[poly.num] = self.surfaces[param_name]["default"]

        return values
