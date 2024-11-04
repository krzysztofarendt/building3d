import logging
from pathlib import Path

import numpy as np
import pyvista as pv

from building3d.geom.building import Building
from building3d.geom.types import FloatDataType
from building3d.geom.types import PointType

from .simulation_config import SimulationConfig
from .jit_print import jit_print

logger = logging.getLogger(__name__)


def make_movie_from_buffer(
    output_file: str,
    building: Building,
    pos_buf: PointType,
    enr_buf: FloatDataType,
    sim_cfg: SimulationConfig = SimulationConfig(),
    verbose: bool = True,
):
    """Generate movie from position and energy buffers.

    Args:
        output_file: path to the output file.
        building: Building instance.
        pos_buf: Ray position buffer.
        enr_buf: Ray energy buffer.
        sim_cfg (optional): Simulation configuration.
        verbose (optional): Prints progress if True.
    """
    logger.info(f"Making movie: {output_file}")
    jit_print(verbose, f"Making movie: {output_file}")

    # Graphics settings
    ray_opacity = sim_cfg.visualization["ray_opacity"]
    ray_trail_opacity = sim_cfg.visualization["ray_trail_opacity"]
    ray_trail_length = sim_cfg.visualization["ray_trail_length"]
    ray_point_size = sim_cfg.visualization["ray_point_size"]
    building_opacity = sim_cfg.visualization["building_opacity"]
    building_color = sim_cfg.visualization["building_color"]
    fps = sim_cfg.visualization["movie_fps"]
    cmap = sim_cfg.visualization["movie_colormap"]

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

    num_steps = pos_buf.shape[0]
    assert num_steps == enr_buf.shape[0]

    for i in range(1, num_steps):
        logger.info(f"Processing frame {i}")
        start = i - ray_trail_length
        if start < 0:
            start = 0
        end = i

        position = pos_buf[start:end, :, :]
        energy = enr_buf[start:end, :]

        if i == 1:

            # Draw building
            bdg_verts, bdg_faces = building.get_mesh()
            bdg_farr = []
            for f in bdg_faces:
                bdg_farr.extend([3, f[0], f[1], f[2]])
            bdg_mesh = pv.PolyData(bdg_verts, faces=bdg_farr)
            plotter.add_mesh(
                bdg_mesh,
                show_edges=True,
                opacity=building_opacity,
                color=building_color,
            )

            # Draw points
            varr = position[-1, :, :]
            point_mesh = pv.PolyData(varr)
            point_mesh["energy"] = energy[-1, :]
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
            line_varr, line_index = position_buffer_to_lines(position)
            line_mesh = pv.PolyData(line_varr, lines=line_index)
            line_mesh["energy"] = energy.flatten()
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
            point_mesh.points = position[-1, :, :]
            point_mesh["energy"] = energy[-1, :]

            # Update lines
            line_varr, line_index = position_buffer_to_lines(position)
            line_mesh.points = line_varr
            line_mesh.lines = line_index
            line_mesh["energy"] = energy.flatten()

            plotter.write_frame()

    plotter.close()
    logger.info(f"Movie saved: {output_file}")


def position_buffer_to_lines(pb: np.ndarray) -> tuple[np.ndarray, list[int]]:
    """Convert position buffer array to the format required by PyVista Plotter.

    The required format is as follows:
    - line points represented as a 2D array (num_points, 3),
    - line connectivity represented as a list indicating the number of points in a line segment
      followed by the point indices. For example, the two line segments [0, 1] and [1, 2, 3, 4]
      will be represented as [2, 0, 1, 4, 1, 2, 3, 4].

    Args:
        pb: position buffer returned by DumpReader

    Return:
        line points, line connectivity
    """
    num_rays = pb.shape[1]
    buf_len = pb.shape[0]
    line_varr = []
    line_index = []
    curr_index = 0
    for ray_i in range(num_rays):
        line_index.append(buf_len)
        for buf_i in range(buf_len):
            line_varr.append(pb[buf_i, ray_i, :])
            line_index.append(curr_index)
            curr_index += 1
    line_varr = np.array(line_varr)
    return line_varr, line_index
