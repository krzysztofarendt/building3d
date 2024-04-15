from __future__ import annotations
import logging

import numpy as np

import building3d.geom.solid
import building3d.logger
from building3d.geom.collapse_points import collapse_points
import building3d.geom.polygon
from building3d.geom.point import Point
from building3d.geom.triangle import triangle_area
from building3d.geom.vector import length
from building3d.geom.vector import vector
from building3d.mesh.triangulation import delaunay_triangulation
from building3d.config import MESH_DELTA


logger = logging.getLogger(__name__)


class PolyMesh:
    def __init__(self, delta: float = MESH_DELTA):
        logger.debug(f"PolyMesh(delta={delta})")

        # Mesh settings
        self.delta = delta

        # Polygons to be meshed
        self.polygons = {}

        # Attributes filled with data by self.generate()
        self.vertices = []
        self.vertex_owners = []  # polygon names
        self.faces = []
        self.face_owners = []  # polygon names

    def reinit(self):
        logger.debug("Reinitializing PolyMesh")
        self.vertices = []
        self.vertex_owners = []  # polygon names
        self.faces = []
        self.face_owners = []  # polygon names

    def add_polygon(self, poly: building3d.geom.polygon.Polygon):
        logger.debug(f"Adding polygon: {poly}")
        self.polygons[poly.name] = poly

    def get_vertices_per_polygon(self) -> dict[str, list[Point]]:
        """Return list of vertices for each polygon name."""
        logger.debug("Getting the list of Points per polygon")
        vertices = {}
        for name in self.polygons.keys():
            vertices[name] = []
            for i in range(len(self.vertices)):
                if self.vertex_owners[i] == name:
                    v = self.vertices[i]
                    vertices[name].append(v)
        log_return = {k: len(v) for (k, v) in vertices.items()}
        logger.debug(f"Number of Points per polygon: {log_return}")
        return vertices

    def mesh_statistics(self, show=False) -> dict:
        """Print and return info about mesh quality."""
        num_of_vertices = len(self.vertices)
        num_of_faces = len(self.faces)

        face_areas = []
        edge_lengths = []
        for i in range(num_of_faces):
            p0 = self.vertices[self.faces[i][0]]
            p1 = self.vertices[self.faces[i][1]]
            p2 = self.vertices[self.faces[i][2]]
            face_areas.append(triangle_area(p0, p1, p2))
            edge_lengths.append(length(vector(p0, p1)))
            edge_lengths.append(length(vector(p1, p2)))
            edge_lengths.append(length(vector(p2, p0)))

        max_face_area = np.max(face_areas)
        avg_face_area = np.mean(face_areas)
        min_face_area = np.min(face_areas)
        max_edge_len = np.max(edge_lengths)
        avg_edge_len = np.mean(edge_lengths)
        min_edge_len = np.min(edge_lengths)

        area_hist, bin_edges = np.histogram(face_areas, bins=10)

        stats = {
            "num_of_vertices": num_of_vertices,
            "num_of_faces": num_of_faces,
            "max_face_area": max_face_area,
            "avg_face_area": avg_face_area,
            "min_face_area": min_face_area,
            "max_edge_len": max_edge_len,
            "avg_edge_len": avg_edge_len,
            "min_edge_len": min_edge_len,
        }

        if show is True:
            print("PolyMesh statistics:")
            print("====================")
            print(f"\t{num_of_vertices=}")
            print(f"\t{num_of_faces=}")
            print(f"\t{max_face_area=}")
            print(f"\t{avg_face_area=}")
            print(f"\t{min_face_area=}")
            print(f"\t{max_edge_len=}")
            print(f"\t{avg_edge_len=}")
            print(f"\t{min_edge_len=}")
            print("\tArea distribution:")
            for i in range(len(area_hist)):
                bracket = ")" if i < len(area_hist) - 1 else "]"
                print(f"\t- [{bin_edges[i]:.3f}, {bin_edges[i+1]:.3f}{bracket} = {area_hist[i]}")

        return stats

    def generate(self, initial_vertices: dict[str, list[Point]] = {}):
        """Generate mesh for all added polygons and solids."""
        use_init = True if len(initial_vertices) > 0 else False
        logger.debug(f"Generating mesh (using initial vertices: {use_init})")
        self.reinit()

        # Polygons
        for poly_name, poly in self.polygons.items():
            logger.debug(f"Processing {poly_name}")

            initial = []
            if poly_name in initial_vertices.keys():
                logger.debug(f"Adding {len(initial_vertices[poly_name])} init. vert. for {poly_name}")
                initial = initial_vertices[poly_name]

            vertices, faces = delaunay_triangulation(
                poly=poly,
                delta=self.delta,
                init_vertices=initial,
            )

            # Increase face counter to include previously added vertices
            faces = np.array(faces)
            faces += len(self.vertices)
            faces = faces.tolist()

            self.vertices.extend(vertices)
            self.vertex_owners.extend([poly_name for _ in vertices])

            self.faces.extend(faces)
            face_owners = [poly_name for _ in faces]
            self.face_owners.extend(face_owners)

        # TODO: info about ownership would be lost during collapsing points
        # self.vertices, self.faces = collapse_points(self.vertices, self.faces)
