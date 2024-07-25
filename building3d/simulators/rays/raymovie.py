from pathlib import Path

import numpy as np
import pyvista as pv

from building3d.geom.building import Building
from building3d.geom.cloud import points_to_array
from .manyrays import ManyRays


class RayMovie:
    ray_opacity = 0.7
    ray_trail_opacity = 0.7
    ray_color = [1.0, 0.0, 0.0]  # red
    ray_point_size = 4  # default 3, looks good if many rays
    building_opacity = 0.5
    building_color = [0.8, 0.8, 0.8]  # gray
    fps = 30

    def __init__(self, filename: str, building: Building, rays: ManyRays):
        self.rays = rays

        # Initialize plotter
        self.plotter = pv.Plotter(
            notebook=False,
            off_screen=True,
            window_size=(1280, 1024),
        )

        # Draw building
        bdg_verts, bdg_faces = building.get_mesh(children=True)
        bdg_varr = points_to_array(bdg_verts)
        bdg_farr = []
        for f in bdg_faces:
            bdg_farr.extend([3, f[0], f[1], f[2]])
        bdg_mesh = pv.PolyData(bdg_varr, faces=bdg_farr)
        self.plotter.add_mesh(
            bdg_mesh,
            show_edges=True,
            opacity=RayMovie.building_opacity,
            color=RayMovie.building_color,
        )

        # Draw rays (first frame)
        # Points
        verts = self.rays.get_points()
        varr = points_to_array(verts)
        self.point_mesh = pv.PolyData(varr)
        self.plotter.add_mesh(
            self.point_mesh,
            opacity=RayMovie.ray_opacity,
            point_size=RayMovie.ray_point_size,
            color=RayMovie.ray_color,
        )

        # Trailing lines
        line_verts, lines = self.rays.get_lines()
        line_varr = points_to_array(line_verts)
        larr = []
        for l in lines:
            larr.extend([len(l)])
            larr.extend(l)
        self.line_mesh = pv.PolyData(line_varr, lines=larr)
        self.plotter.add_mesh(
            self.line_mesh,
            opacity=RayMovie.ray_trail_opacity,
            color=RayMovie.ray_color,
        )

        # Start movie
        ext = Path(filename).suffix.lower()
        if ext == ".gif":
            self.plotter.open_gif(filename, fps=RayMovie.fps)
        elif ext == ".mp4":
            self.plotter.open_movie(filename, framerate=RayMovie.fps, quality=5)
        else:
            raise ValueError(f"Movie extension not supported: {ext}")

    def update(self):
        # Update points
        verts = self.rays.get_points()
        varr = points_to_array(verts)
        self.point_mesh.points = varr
        # Update trailing lines
        line_verts, _ = self.rays.get_lines()
        line_varr = points_to_array(line_verts)
        self.line_mesh.points = line_varr
        # Write next frame
        self.plotter.write_frame()

    def save(self):
        self.plotter.close()
