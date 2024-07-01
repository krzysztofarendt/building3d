from building3d.geom.building import Building
from building3d.geom.predefined.solids.box import box
from building3d.geom.zone import Zone
from building3d.io.dotbim import read_dotbim
from building3d.io.dotbim import write_dotbim

if __name__ == "__main__":
    file_path = "building.bim"

    solid_1 = box(1, 1, 1, (0, 0, 0), name="Zone_1")
    zone_1 = Zone(name="Zone_1")
    zone_1.add_solid(solid_1)

    solid_2 = box(1, 1, 1, (1, 0, 0), name="Zone_2")
    zone_2 = Zone(name="Zone_2")
    zone_2.add_solid(solid_2)

    zones = [zone_1, zone_2]
    building = Building(name="building")
    for z in zones:
        building.add_zone(z)

    write_dotbim(file_path, building)
    building_copy = read_dotbim(file_path)
