from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
import building3d.geom.point
from building3d.geom.exceptions import GeometryError
from building3d.geom.triangle import triangle_area
from building3d.geom.vector import length
from building3d.geom.vector import vector
from .polygon_mesh import delaunay_triangulation
from .solid_mesh import delaunay_tetrahedralization


class Mesh:

    def __init__(self, delta: float = 0.5):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.polygons = {}
        self.solids = {}

        # Attributes filled with data by self.generate()
        self.poly_mesh_vertices = []
        self.poly_mesh_vertex_owners = []  # polygon names
        self.poly_mesh_faces = []
        self.poly_mesh_face_owners = []  # polygon names

        self.sld_mesh_vertices = []
        self.sld_mesh_vertex_owners = []  # solid names
        self.sld_mesh_elements = []
        self.sld_mesh_element_owners = []  # solid names

    def add_polygon(self, poly: building3d.geom.polygon.Polygon):
        self.polygons[poly.name] = poly

    def add_solid(self, sld: building3d.geom.solid.Solid):
        """Add solid instance to the list of solids for this mesh.

        All solid boundary polygons are also added (if they were not already added manually).
        """
        self.solids[sld.name] = sld
        for poly in sld.boundary:
            if poly.name not in self.polygons:
                self.polygons[poly.name] = poly

    def mesh_statistics(self, show=False) -> dict:
        """Print and return info about mesh quality."""
        num_of_vertices = len(self.poly_mesh_vertices)  # TODO: Add solid mesh
        num_of_faces = len(self.poly_mesh_faces)

        face_areas = []
        edge_lengths = []
        for i in range(num_of_faces):
            p0 = self.poly_mesh_vertices[self.poly_mesh_faces[i][0]]
            p1 = self.poly_mesh_vertices[self.poly_mesh_faces[i][1]]
            p2 = self.poly_mesh_vertices[self.poly_mesh_faces[i][2]]
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

    def generate(self):
        """Generate mesh for all added polygons and solids."""
        # Polygons
        for poly_name, poly in self.polygons.items():
            vertices, faces = delaunay_triangulation(poly, delta=self.delta)

            # Increase face counter to include previously added vertices
            faces = np.array(faces)
            faces += len(self.poly_mesh_vertices)
            faces = faces.tolist()

            self.poly_mesh_vertices.extend(vertices)
            self.poly_mesh_vertex_owners = [poly_name for _ in vertices]

            self.poly_mesh_faces.extend(faces)
            face_owners = [poly_name for _ in faces]
            self.poly_mesh_face_owners.extend(face_owners)

        # Solids (should connect to vertices at adjacent polygons)
        for sld_name, sld in self.solids.items():
            boundary_vertices = {}
            for poly in sld.boundary:
                boundary_vertices[poly.name] = \
                    [p for (p, owner) in \
                     zip(self.poly_mesh_vertices, self.poly_mesh_vertex_owners) \
                     if owner == poly.name]

            vertices, tetrahedra = delaunay_tetrahedralization(
                sld=sld,
                boundary_vertices=boundary_vertices,
                delta=self.delta
            )
            self.sld_mesh_vertices.extend(vertices)
            self.sld_mesh_vertex_owners.extend([sld_name for _ in vertices])
            self.sld_mesh_elements.extend(tetrahedra)
            self.sld_mesh_element_owners.extend([sld_name for _ in tetrahedra])

        # if len(self.solids) > 0:
        #     # Make sure all vertices are used in the solid mesh
        #     if np.array(self.sld_mesh_elements).max() < len(self.sld_mesh_vertices):
        #         # element_unique_vertices = np.unique(np.array(self.elements))
        #         # unused = []
        #         # for i, pt in enumerate(self.vertices):
        #         #     if i not in element_unique_vertices:
        #         #         unused.append(i)

        #         # print(f"{unused=}")
        #         raise GeometryError("solid mesh is broken")  # TODO: should be MeshError
        #         # import pdb; pdb.set_trace()

    def collapse_points(self):  # TODO: Add solid mesh. Currently works on polygon meshes only.
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
        for i, p in enumerate(self.poly_mesh_vertices):
            if p in same_points.keys():
                same_points[p].append(i)
            else:
                same_points[p] = [i]

        # Merge same points
        for_deletion = set()

        for i in range(len(self.poly_mesh_vertices)):
            p = self.poly_mesh_vertices[i]
            p_to_keep = same_points[p][0]
            for j in range(1, len(same_points[p])):
                p_to_delete = same_points[p][j]
                for_deletion.add(p_to_delete)

                # Replace point to be deleted with the one to keep in each face
                for k in range(len(self.poly_mesh_faces)):
                    if p_to_delete in self.poly_mesh_faces[k]:
                        self.poly_mesh_faces[k] = \
                            [x if x != p_to_delete else p_to_keep for x in self.poly_mesh_faces[k]]

        # Reindex
        for_deletion = sorted(list(for_deletion), reverse=True)
        for p_to_delete in for_deletion:
            for k in range(len(self.poly_mesh_faces)):
                self.poly_mesh_faces[k] = [x - 1 if x > p_to_delete else x for x in self.poly_mesh_faces[k]]
            self.poly_mesh_vertices.pop(p_to_delete)

    def fix_short_edges(self, min_length: float):  # TODO
        """Delete vertices connected to short edges."""
        pass
