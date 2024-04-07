from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
from building3d.geom.point import Point
from building3d.geom.triangle import triangle_area
from building3d.geom.vector import length
from building3d.geom.vector import vector
from .triangulation import delaunay_triangulation


class PolyMesh:
    def __init__(self, delta: float = 0.5):
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
        self.vertices = []
        self.vertex_owners = []  # polygon names
        self.faces = []
        self.face_owners = []  # polygon names

    def add_polygon(self, poly: building3d.geom.polygon.Polygon):
        self.polygons[poly.name] = poly

    def get_vertices_per_polygon(self) -> dict[str, list[Point]]:
        """Return list of vertices for each polygon name."""
        vertices = {}
        for name in self.polygons.keys():
            vertices[name] = []
            for i in range(len(self.vertices)):
                if self.vertex_owners[i] == name:
                    v = self.vertices[i]
                    vertices[name].append(v)
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

        if show is True:
            print("MESH STATISTICS:")
            print(f"\t{num_of_vertices=}")
            print(f"\t{num_of_faces=}")
            print(f"\t{max_face_area=}")
            print(f"\t{avg_face_area=}")
            print(f"\t{min_face_area=}")
            print(f"\t{max_edge_len=}")
            print(f"\t{avg_edge_len=}")
            print(f"\t{min_edge_len=}")

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
        return stats

    def generate(self, initial_vertices: dict[str, list[Point]] = {}):
        """Generate mesh for all added polygons and solids."""

        self.reinit()

        # Polygons
        for poly_name, poly in self.polygons.items():

            initial = []
            if poly_name in initial_vertices.keys():
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

    def collapse_points(self):
        """Merge overlapping points.

        Checks if there are points which are equal to one another.
        Point equality is defined in the Point class. In general,
        points are equal if the difference between their coordinates is below
        the defined epsilon.

        Subsequently, overlapping points are merged.

        Overlapping points typically exist on the edges of adjacent polygons,
        because the polygon meshes are generated independently.
        """

        # Identify identical points
        same_points = {}
        for i, p in enumerate(self.vertices):
            if p in same_points.keys():
                same_points[p].append(i)
            else:
                same_points[p] = [i]

        # Merge same points
        for_deletion = set()

        for i in range(len(self.vertices)):
            p = self.vertices[i]
            p_to_keep = same_points[p][0]
            for j in range(1, len(same_points[p])):
                p_to_delete = same_points[p][j]
                for_deletion.add(p_to_delete)

                # Replace point to be deleted with the one to keep in each face
                for k in range(len(self.faces)):
                    if p_to_delete in self.faces[k]:
                        self.faces[k] = \
                            [x if x != p_to_delete else p_to_keep for x in self.faces[k]]

        # Reindex
        for_deletion = sorted(list(for_deletion), reverse=True)
        for p_to_delete in for_deletion:
            for k in range(len(self.faces)):
                self.faces[k] = [x - 1 if x > p_to_delete else x for x in self.faces[k]]
            self.vertices.pop(p_to_delete)

    def fix_short_edges(self, min_length: float):
        """Delete vertices connected to short edges and regenerate mesh."""

        initial_vertices = {}

        for polyname in self.polygons.keys():

            protected_points = self.polygons[polyname].points
            num_of_faces = len(self.faces)

            # Calculate edge lengths
            edge_lengths = {}
            for i in range(num_of_faces):
                p_index_0 = self.faces[i][0]
                p_index_1 = self.faces[i][1]
                p_index_2 = self.faces[i][2]
                p0 = self.vertices[p_index_0]
                p1 = self.vertices[p_index_1]
                p2 = self.vertices[p_index_2]
                edge_lengths[(p_index_0, p_index_1)] = length(vector(p0, p1))
                edge_lengths[(p_index_1, p_index_2)] = length(vector(p1, p2))
                edge_lengths[(p_index_2, p_index_0)] = length(vector(p2, p0))

            # Pick points designated for removal
            points_to_delete = set()
            for (p_index_a, p_index_b), elen in edge_lengths.items():
                pa = self.vertices[p_index_a]
                pb = self.vertices[p_index_b]
                if elen < min_length:
                    if pa not in protected_points:
                        points_to_delete.add(pa)
                    elif pb not in protected_points:
                        points_to_delete.add(pb)
                    else:
                        pass  # Both points are the polygon vertices

            # Re-generate mesh
            initial_vertices[polyname] = [
                p for p in self.vertices if p not in points_to_delete
            ]
        self.generate(initial_vertices)
