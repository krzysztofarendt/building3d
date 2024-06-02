from building3d.display.plot_mesh import plot_mesh
from building3d.display.plot_zone import plot_zone
from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.io.b3d import write_b3d
from building3d.mesh.mesh import Mesh
from building3d.mesh.quality.mesh_stats import mesh_stats

if __name__ == "__main__":
    zone = box(2.0, 5.0, 3.0)

    mesh = Mesh(delta=0.5)
    mesh.add_zone(zone)
    mesh.generate(solidmesh=True)

    print(mesh_stats(mesh.polymesh.vertices, mesh.polymesh.faces))
    print(mesh_stats(mesh.solidmesh.vertices, mesh.solidmesh.elements))

    # Plot
    plot_zone(zone)
    plot_mesh(mesh)

    # Save to B3D
    building = Building(name="example_3")
    building.add_zone_instance(zone)

    # The below line is needed because the mesh instance was created
    # outside the building instance
    building.mesh = mesh
    write_b3d("example_3.b3d", building)
