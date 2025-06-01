import math

import pyrosm
from pyrosm import OSM
from src.ColorMapping import ColorMapping

import matplotlib.pyplot as plt


def clip_world_map():

    # ./osmconvert64-0.8.8p.exe planet-250505.osm.pbf -b="8.5505,52.8584,8.6505,52.9584" -o="clipped.osm.pbf"

    pass


def plot_roads(osm: pyrosm, ax):

    roads = osm.get_network(network_type="all")

    # Plot Roads
    if roads is not None:
        print("Roads plotted!")
        roads.plot(ax=ax, linewidth=0.3, color=colorMapping.get_color("roads"), alpha=0.7)
    else:
        print("Roads not plotted!")


def plot_natural(osm: pyrosm, ax):

    natural = osm.get_data_by_custom_criteria(custom_filter={"natural": True})

    if natural is not None:
        if "natural" in natural.columns:
            natural_wood = natural[natural["natural"] == "wood"]
            natural_water = natural[natural["natural"] == "water"]
            grassland = natural[natural["natural"] == "grassland"]
            natural = natural[natural["natural"] == "natural"]

            if not natural_wood.empty:
                print("Natural wood plotted!")
                natural_wood.plot(ax=ax, color=colorMapping.get_color("natural_wood"), alpha=0.5)
            else:
                print("Natural wood not plotted!")
            if not natural_water.empty:
                print("Natural water plotted!")
                natural_water.plot(ax=ax, color=colorMapping.get_color("natural_water"), alpha=0.5)
            else:
                print("Natural water not plotted!")
            if not grassland.empty:
                print("Grassland plotted!")
                grassland.plot(ax=ax, color=colorMapping.get_color("grassland"), alpha=0.5)
            else:
                print("Grassland not plotted!")
            if not natural.empty:
                print("Natural plotted!")
                natural.plot(ax=ax, color=colorMapping.get_color("natural"), alpha=0.5)
            else:
                print("Natural not plotted!")


def plot_landuse(osm: pyrosm, ax):

    landuse = osm.get_data_by_custom_criteria(custom_filter={"landuse": True})

    if landuse is not None:

        if "landuse" in landuse.columns:

            for value in ["allotments", "brownfield", "basin", "cemetery", "commercial", "construction", "farmland",
                          "forest", "farmyard", "flowerbed", "garages", "grass", "greenhouse_horticulture", "greenfield",
                          "landfill", "salt_pond", "industrial", "orchard", "residential", "retail", "landfill", "meadow",
                          "military", "plant_nursery", "quarry", "railway", "religious", "recreation_ground",
                          "village_green", "vineyard"]:
                area = landuse[landuse["landuse"] == value]
                if not area.empty:
                    print(f"{value} plotted!")
                    area.plot(ax=ax, color=colorMapping.get_color(value), alpha=0.3)
                else:
                    print(f"{value} not platted!")


def plot_aeroway(osm:pyrosm, ax):

    aeroway = osm.get_data_by_custom_criteria(custom_filter={"aeroway": True})

    if aeroway is not None:
        if "aeroway" in aeroway.columns:

            apron = aeroway[aeroway["aeroway"] == "apron"]
            terminal = aeroway[aeroway["aeroway"] == "terminal"]

            if not apron.empty:
                print("Farmland plotted!")
                apron.plot(ax=ax, color=colorMapping.get_color("apron"), alpha=0.3)
            else:
                print("Apron not plotted!")

            if not terminal.empty:
                print("Terminal plotted!")
                terminal.plot(ax=ax, color=colorMapping.get_color("terminal"), alpha=0.5)


def plot_buildings(osm:pyrosm, ax):

    buildings = osm.get_buildings()

    if buildings is not None:
        print("Buildings plotted!")
        buildings.plot(ax=ax, color=colorMapping.get_color("buildings"), alpha=0.5)
    else:
        print("Buildings not plotted!")


def bounding_box(lat, lon, distance_m):
    """
    Calculates a bounding box around a geographic point for a given distance in all directions.

    :param lat: Latitude of the center point in decimal degrees
    :param lon: Longitude of the center point in decimal degrees
    :param distance_m: Distance in meters to extend in all directions (north, south, east, west)
    :return: List in the format [west, south, east, north]
    """
    # Approximate length of one degree of latitude in meters
    meters_per_degree_lat = 111320

    # Approximate length of one degree of longitude in meters (varies by latitude)
    meters_per_degree_lon = 111320 * math.cos(math.radians(lat))

    delta_lat = distance_m / meters_per_degree_lat
    delta_lon = distance_m / meters_per_degree_lon

    south = lat - delta_lat
    north = lat + delta_lat
    west = lon - delta_lon
    east = lon + delta_lon

    return [west, south, east, north]


if __name__ == "__main__":

    # Definition of location
    latitude = 22.317380521068817# 52.90837464776529
    longitude = 114.16983034197081 # 8.60048609236055
    distance = 1000

    # [west, south, east, north]
    bbox = bounding_box(latitude, longitude, distance)

    print(bbox)


    colorMapping = ColorMapping()

    # Path to the clipped.osm.pbf file
    pbf_path = "resources/planet-250505.osm.pbf"

    # Load pdf file and with bounding box
    clipped_osm = OSM(pbf_path, bounding_box=bounding_box(latitude, longitude, distance))

    fig, axes = plt.subplots(figsize=(12, 12))
    background_color = "white"
    fig.patch.set_facecolor(background_color)

    available_tags = pyrosm.pyrosm.Conf.tags.available
    print("Available tags:")
    print(available_tags)

    for value in available_tags:
        tag_values = clipped_osm.get_data_by_custom_criteria(custom_filter={value: True})
        if tag_values is not None:
            print("Found " + value)
            print(tag_values)
        else:
            print(value + " was not found!")

    print("--------------------")

    plot_roads(clipped_osm, axes)
    plot_natural(clipped_osm, axes)
    plot_landuse(clipped_osm, axes)
    plot_buildings(clipped_osm, axes)

    # Kartenlimits setzen
    axes.set_xlim(bbox[0], bbox[2])
    axes.set_ylim(bbox[1], bbox[3])
    axes.set_facecolor(background_color)
    axes.axis('off')
    plt.tight_layout()
    plt.savefig("map.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.show()
