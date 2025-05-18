from pyrosm import OSM, get_data
import matplotlib.pyplot as plt

from src.ColorMapping import ColorMapping

# Beispielpfad zu deiner PBF-Datei
pbf_path = "resources/clipped.osm.pbf"  # <--- hier dein Pfad

colorMapping = ColorMapping()

# Definiere deine Bounding Box
latitude = 52.90837464776529
longitude = 8.60048609236055
north = latitude + 0.05
south = latitude - 0.05
east = longitude + 0.05
west = longitude - 0.05
bbox = [west, south, east, north]

# ./osmconvert64-0.8.8p.exe planet-250505.osm.pbf -b=8.5505,52.8584,8.6505,52.9584 -o=clipped.osm.pbf

# Lade das PBF-File mit Bounding Box
osm = OSM(pbf_path, bounding_box=bbox)

# Jetzt funktioniert get_network ohne weiteres bbox-Argument
roads = osm.get_network(network_type="all")

# Extrahiere natürliche Flächen (z.B. Wälder, Wasserflächen)
natural = osm.get_data_by_custom_criteria(custom_filter={"natural": True})

# Extrahiere Landnutzung
landuse = osm.get_data_by_custom_criteria(custom_filter={"landuse": True})

aeroway = osm.get_data_by_custom_criteria(custom_filter={"aeroway": True})

# Extrahiere Gebäude
buildings = osm.get_buildings()

# ----------------- Visualisierung --------------------

fig, ax = plt.subplots(figsize=(12, 12))
bgcolor = "white"
fig.patch.set_facecolor(bgcolor)

# Plot Roads
if roads is not None:
    print("Roads plotted!")
    roads.plot(ax=ax, linewidth=0.3, color=colorMapping.get_color("roads"), alpha=0.7)
else:
    print("Roads not plotted!")

# Plot natural areas
if natural is not None:
    if "natural" in natural.columns:
        natural_wood = natural[natural["natural"] == "wood"]
        natural_water = natural[natural["natural"] == "water"]
        grassland = natural[natural["natural"] == "grassland"]

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

if aeroway is not None:
    if "landuse" in landuse.columns:

        apron = aeroway[aeroway["aeroway"] == "apron"]

        if not apron.empty:
            print("Farmland plotted!")
            apron.plot(ax=ax, color=colorMapping.get_color("apron"), alpha=0.3)
        else:
            print("Apron not plotted!")

# Plot Landuse
if landuse is not None:

    if "landuse" in landuse.columns:
        farmland = landuse[landuse["landuse"].isin(["farmland", "farmyard"])]
        residential = landuse[landuse["landuse"] == "residential"]
        mining = landuse[landuse["landuse"].isin(["mine", "landfill"])]

        if not farmland.empty:
            print("Farmland plotted!")
            farmland.plot(ax=ax, color=colorMapping.get_color("farmland"), alpha=0.3)
        else:
            print("Farmland not platted!")
        if not residential.empty:
            print("Residential plotted!")
            residential.plot(ax=ax, color=colorMapping.get_color("residential"), alpha=0.2)
        else:
            print("Residential not plotted!")
        if not mining.empty:
            print("Mining plotted!")
            mining.plot(ax=ax, color=colorMapping.get_color("mining"), alpha=0.5)
        else:
            print("Mining not plotted!")
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
