from building3d.display.plot_building import plot_building
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.io.b3d import write_b3d
from building3d.mesh.quality.mesh_stats import mesh_stats

if __name__ == "__main__":
    zone = box(2.0, 5.0, 3.0)

    # Save to B3D
    building = Building(name="example_3")
    building.add_zone_instance(zone)
    building.generate_simulation_mesh(delta=0.5, include_volumes=True)

    print(mesh_stats(building.mesh.polymesh.vertices, building.mesh.polymesh.faces))
    print(
        mesh_stats(building.mesh.solidmesh.vertices, building.mesh.solidmesh.elements)
    )

    # Plot
    plot_building(building)
    plot_mesh(building.mesh)

    # The below line is needed because the mesh instance was created
    # outside the building instance
    write_b3d("example_3.b3d", building)
