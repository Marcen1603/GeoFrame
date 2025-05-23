import pyrosm
from pyrosm import OSM
from src.ColorMapping import ColorMapping

import matplotlib.pyplot as plt

# Path to the clipped file
pbf_path = "resources/clipped.osm.pbf"


def clip_world_map():

    # ./osmconvert64-0.8.8p.exe planet-250505.osm.pbf -b=8.5505,52.8584,8.6505,52.9584 -o=clipped.osm.pbf

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


if __name__ == "__main__":

    # Definition of location
    latitude = 52.90837464776529
    longitude = 8.60048609236055
    north = latitude + 0.05
    south = latitude - 0.05
    east = longitude + 0.05
    west = longitude - 0.05
    bbox = [west, south, east, north]

    colorMapping = ColorMapping()

    # Load pdf file and with bounding box
    osm = OSM(pbf_path, bounding_box=bbox)

    fig, ax = plt.subplots(figsize=(12, 12))
    bgcolor = "white"
    fig.patch.set_facecolor(bgcolor)

    plot_roads(osm, ax)
    plot_natural(osm, ax)
    plot_landuse(osm, ax)
    plot_buildings(osm, ax)


# Extrahiere Gebäude
buildings = osm.get_buildings()

# ----------------- Visualisierung --------------------

# Plot Buildings
if buildings is not None:
    print("Buildings plotted!")
    buildings.plot(ax=ax, color=colorMapping.get_color("buildings"), alpha=0.5)
else:
    print("Buildings not plotted!")

# Kartenlimits setzen
ax.set_xlim(west, east)
ax.set_ylim(south, north)
ax.set_facecolor(bgcolor)
ax.axis('off')
plt.tight_layout()
plt.savefig("map.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()
