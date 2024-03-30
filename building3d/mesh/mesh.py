from __future__ import annotations

import numpy as np

import building3d.geom.solid
import building3d.geom.polygon
import building3d.geom.point
from .polygon_mesh import delaunay_triangulation


class Mesh:

    def __init__(self, delta: float = 0.5):
        # Mesh settings
        self.delta = delta

        # Polygons and solid to be meshed
        self.polygons = {}
        self.solids = {}

        # Attributes filled with data by self.generate_mesh()
        self.vertices = []
        self.vertex_owners = []  # solid names

        self.faces = []
        self.face_owners = []  # polygon names

    def add_polygon(self, poly: building3d.geom.polygon.Polygon):
        self.polygons[poly.name] = poly

    def add_solid(self, sld: building3d.geom.solid.Solid):
        self.solids[sld.name] = sld

    def generate(self):
        """Generate mesh for all added polygons and solids."""
        # Polygons
        for poly_name, poly in self.polygons.items():
            vertices, faces = delaunay_triangulation(poly, self.delta)

            # Increase face counter to include previously added vertices
            faces = np.array(faces)
            faces += len(self.vertices)
            faces = faces.tolist()

            self.vertices.extend(vertices)
            vertex_owners = [None for _ in vertices]  # TODO: Should identify relevant solids

            self.faces.extend(faces)
            face_owners = [poly_name for _ in faces]
            self.face_owners.extend(face_owners)


        # Solids (should connect to vertices at adjacent polygons)
        pass  # TODO

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
                        self.faces[k] = [x if x != p_to_delete else p_to_keep for x in self.faces[k]]

        # Reindex
        for_deletion = sorted(list(for_deletion), reverse=True)
        for p_to_delete in for_deletion:
            for k in range(len(self.faces)):
                self.faces[k] = [x - 1 if x > p_to_delete else x for x in self.faces[k]]
            self.vertices.pop(p_to_delete)
