import logging
from pathlib import Path

import numpy as np
import pyvista as pv

from building3d.geom.cloud import points_to_array
from building3d.io.b3d import read_b3d
from .dumpreader import DumpReader


logger = logging.getLogger(__name__)


def make_movie(output_file: str, state_dump_dir: str, building_file: str, num_steps: int = 0):
    """Generate movie from the saved states and building file (b3d).

    Args:
        output_file: path to the output movie file
        state_dump_dir: path to the state dump directory
        building_file: path to the saved building file (b3d)
        num_steps: number of steps to use in the movie, take all if <= 0
    """
    logger.info(f"Start making movie: {output_file}")

    # Graphics settings
    ray_opacity = 0.5
    ray_trail_opacity = 0.25
    ray_point_size = 3  # default 3, looks good if many rays
    building_opacity = 0.5
    building_color = [0.8, 0.8, 0.8]  # gray
    fps = 30
    cmap = "RdPu"

    # Initialize plotter
    plotter = pv.Plotter(
        notebook=False,
        off_screen=True,
        window_size=(1280, 1024),
    )
    # Start movie
    ext = Path(output_file).suffix.lower()
    if ext == ".gif":
        plotter.open_gif(output_file, fps=fps)
    elif ext == ".mp4":
        plotter.open_movie(output_file, framerate=fps, quality=5)
    else:
        err_msg = f"Movie extension not supported: {ext}"
        logger.error(err_msg)
        raise ValueError(err_msg)

    point_mesh = pv.PolyData()
    line_mesh = pv.PolyData()
    building = read_b3d(building_file)

    for i, state in enumerate(DumpReader(state_dump_dir)):
        logger.debug(f"Processing frame {i}")
        position_buffer = state["position"]  # shape: (num_rays, 3, Ray.buffer_size)
        energy_buffer = state["energy"]  # shape: (num_rays, Ray.buffer_size)

        if num_steps > 0 and i == num_steps:
            break

        if i == 0:

            # Draw building
            bdg_verts, bdg_faces = building.get_mesh(children=True)
            bdg_varr = points_to_array(bdg_verts)
            bdg_farr = []
            for f in bdg_faces:
                bdg_farr.extend([3, f[0], f[1], f[2]])
            bdg_mesh = pv.PolyData(bdg_varr, faces=bdg_farr)
            plotter.add_mesh(
                bdg_mesh,
                show_edges=True,
                opacity=building_opacity,
                color=building_color,
            )

            # Draw points
            varr = position_buffer[:, :, 0]
            point_mesh = pv.PolyData(varr)
            point_mesh["energy"] = energy_buffer[:, 0]
            point_mesh.set_active_scalars("energy")
            plotter.add_mesh(
                point_mesh,
                opacity=ray_opacity,
                point_size=ray_point_size,
                color=None,
                cmap=cmap,
                show_scalar_bar=True,
                clim=(0, 1),
            )

            # Draw trailing lines
            line_varr, line_index = position_buffer_to_lines(position_buffer)
            line_mesh = pv.PolyData(line_varr, lines=line_index)
            line_mesh["energy"] = energy_buffer.flatten()
            line_mesh.set_active_scalars("energy")
            plotter.add_mesh(
                line_mesh,
                opacity=ray_trail_opacity,
                color=None,
                cmap=cmap,
                show_scalar_bar=False,
                clim=(0, 1),
            )

        else:
            # Draw next frame (update points and lines)
            # Update points
            point_mesh.points = position_buffer[:, :, 0]
            point_mesh["energy"] = energy_buffer[:, 0]

            # Update lines
            line_varr, _ = position_buffer_to_lines(position_buffer)
            line_mesh.points = line_varr
            line_mesh["energy"] = energy_buffer.flatten()

            plotter.write_frame()

    logger.info(f"Movie saved: {output_file}")
    plotter.close()


def position_buffer_to_lines(pb: np.ndarray):
    """Convert position buffer array to the format required by PyVista Plotter.

    The required format is as follows:
    - line points represented as a 2D array (num_points, 3),
    - line connectivity represented as a list indicating the number of points in a line segment
      followed by the point indices. For example, the two line segments [0, 1] and [1, 2, 3, 4]
      will be represented as [2, 0, 1, 4, 1, 2, 3, 4].
    """
    num_rays = pb.shape[0]
    buf_len = pb.shape[2]  # == Ray.buffer_size
    line_varr = []
    line_index = []
    for ray_i in range(num_rays):
        for buf_i in range(buf_len):
            line_varr.append(pb[ray_i, :, buf_i])
            line_index.append(buf_len)
            line_index.extend([ray_i * buf_len + k for k in range(buf_len)])
    line_varr = np.array(line_varr)
    return line_varr, line_index
