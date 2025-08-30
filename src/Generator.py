import glob
import json
import math
import os
import platform
import sys
import pyrosm

from pyrosm import OSM
from src.Utilities import print_to_console
from src.preprocessor.Preprocessor import OS
from src.ColorMapping import ColorMapping

import matplotlib.pyplot as plt


class Generator:

    def __init__(self, lat: float, lon: float, dis: int):

        # Paths
        self.path_to_latest = os.path.join('src', 'resources', 'latest')
        self.path_to_latest_continents = os.path.join(
            self.path_to_latest, 'continents')
        self.path_to_latest_preprocessed = os.path.join(
            self.path_to_latest, 'preprocessed')
        self.path_to_latest_planet = os.path.join(
            'src', 'preprocessed', 'resources', 'raw', 'planet-250707.osm.pbf')
        self.path_to_osm_convert = os.path.join(
            './', 'src', 'resources', 'osmconvert', 'osmconvert64-0.8.8p.exe')
        self.path_to_osm_convert_linux = os.path.join(
            'src', 'resources', 'osmconvert', 'osmconvert')
        osmconvert_path = self.path_to_osm_convert_linux if OS.from_str(
            platform.system()) == OS.LINUX else self.path_to_osm_convert

        # Values
        self.latitude = lat
        self.longitude = lon
        self.distance = dis

        # Coloring
        self.colorMapping = ColorMapping()

    def bounding_box(self):
        """
        Calculates a bounding box around a geographic point for a given distance in all directions.

        :return: List in the format [west, south, east, north]
        """
        # Approximate length of one degree of latitude in meters
        meters_per_degree_lat = 111320

        # Approximate length of one degree of longitude in meters (varies by latitude)
        meters_per_degree_lon = 111320 * math.cos(math.radians(self.latitude))

        delta_lat = self.distance / meters_per_degree_lat
        delta_lon = self.distance / meters_per_degree_lon

        lon_min = self.longitude - delta_lon
        lon_max = self.longitude + delta_lon
        lat_min = self.latitude - delta_lat
        lat_max = self.latitude + delta_lat

        bbox_dict = {
            'lon min': lon_min,
            'lon max': lon_max,
            'lat min': lat_min,
            'lat max': lat_max,
        }

        return [lon_min, lon_max, lat_min, lat_max], bbox_dict

    def select_pbf_file(self, bbox_dict: dict) -> str:

        path_to_preprocessed_cache_file = os.path.join(
            self.path_to_latest_preprocessed, 'cache_file*.json')
        # path_to_continent_cache_file = os.path.join(
        #     self.path_to_latest_continents, 'cache_file*.json')

        found = None
        for cache_file in [path_to_preprocessed_cache_file]:

            cache_files = glob.glob(cache_file)
            if len(cache_files) == 1:

                with open(cache_files.pop(), "r", encoding="utf-8") as f:

                    data = json.load(f)
                    for key in data:

                        file_statistics = data[key]
                        if float(file_statistics['lon min']) <= float(bbox_dict['lon min']) <= float(file_statistics['lon max']) and float(file_statistics['lon min']) <= float(bbox_dict['lon max']) <= float(file_statistics['lon max']) and float(file_statistics['lat min']) <= float(bbox_dict['lat min']) <= float(file_statistics['lat max']) and float(file_statistics['lat min']) <= float(bbox_dict['lat max']) <= float(file_statistics['lat max']):
                            print(data[key])
                            found = os.path.basename(key)
                            break

                    if found is not None:
                        break
            else:
                raise ValueError(
                    f'Found no or multiple cache files in: {path_to_preprocessed_cache_file}')

        if found is None:
            print_to_console(
                'No preprocessed file can be used, planet file will be returned!')
            return self.path_to_latest_planet

        print_to_console(f'Preprocessed file was found: {found}')
        return found

    def plot_roads(self, osm: pyrosm, ax):

        roads = osm.get_network(network_type="all")

        # Plot Roads
        if roads is not None:
            print("Roads plotted!")
            roads.plot(ax=ax, linewidth=0.3,
                       color=self.colorMapping.get_color("roads"), alpha=0.7)
        else:
            print("Roads not plotted!")

    def plot_natural(self, osm: pyrosm, ax):

        natural = osm.get_data_by_custom_criteria(
            custom_filter={"natural": True})

        if natural is not None:
            if "natural" in natural.columns:
                natural_wood = natural[natural["natural"] == "wood"]
                natural_water = natural[natural["natural"] == "water"]
                grassland = natural[natural["natural"] == "grassland"]
                natural = natural[natural["natural"] == "natural"]

                if not natural_wood.empty:
                    print("Natural wood plotted!")
                    natural_wood.plot(ax=ax, color=self.colorMapping.get_color(
                        "natural_wood"), alpha=0.5)
                else:
                    print("Natural wood not plotted!")
                if not natural_water.empty:
                    print("Natural water plotted!")
                    natural_water.plot(ax=ax, color=self.colorMapping.get_color(
                        "natural_water"), alpha=0.5)
                else:
                    print("Natural water not plotted!")
                if not grassland.empty:
                    print("Grassland plotted!")
                    grassland.plot(ax=ax, color=self.colorMapping.get_color(
                        "grassland"), alpha=0.5)
                else:
                    print("Grassland not plotted!")
                if not natural.empty:
                    print("Natural plotted!")
                    natural.plot(ax=ax, color=self.colorMapping.get_color(
                        "natural"), alpha=0.5)
                else:
                    print("Natural not plotted!")

    def plot_landuse(self, osm: pyrosm, ax):

        landuse = osm.get_data_by_custom_criteria(
            custom_filter={"landuse": True})

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
                        area.plot(ax=ax, color=self.colorMapping.get_color(
                            value), alpha=0.3)
                    else:
                        print(f"{value} not platted!")

    def plot_aeroway(self, osm: pyrosm, ax):

        aeroway = osm.get_data_by_custom_criteria(
            custom_filter={"aeroway": True})

        if aeroway is not None:
            if "aeroway" in aeroway.columns:

                apron = aeroway[aeroway["aeroway"] == "apron"]
                terminal = aeroway[aeroway["aeroway"] == "terminal"]

                if not apron.empty:
                    print("Farmland plotted!")
                    apron.plot(ax=ax, color=self.colorMapping.get_color(
                        "apron"), alpha=0.3)
                else:
                    print("Apron not plotted!")

                if not terminal.empty:
                    print("Terminal plotted!")
                    terminal.plot(ax=ax, color=self.colorMapping.get_color(
                        "terminal"), alpha=0.5)

    def plot_buildings(self, osm: pyrosm, ax):
        buildings = osm.get_buildings()
        if buildings is not None:
            print("Buildings plotted!")
            buildings.plot(ax=ax, color=self.colorMapping.get_color(
                "buildings"), alpha=0.5)
        else:
            print("Buildings not plotted!")

    def main(self):
        """Main executin method for the Generator
        """
        print_to_console("etst")
        # [west, south, east, north]
        bbox, bbox_dict = self.bounding_box()

        print_to_console(f'Generate GeoFrame for Bounding-Box: {bbox}')

        # Get correct file
        pbf_file_path = self.select_pbf_file(bbox_dict)

        # Bbox must be parsed to a list of style: minx, miny, maxx, maxy
        bbox_list = [bbox_dict['lon min'], bbox_dict['lat min'],
                     bbox_dict['lon max'], bbox_dict['lat max']]

        # Load pdf file and with bounding box
        clipped_osm = OSM(os.path.join(self.path_to_latest_preprocessed, pbf_file_path),
                          bounding_box=bbox_list)

        fig, axes = plt.subplots(figsize=(12, 12))
        background_color = "white"
        fig.patch.set_facecolor(background_color)

        available_tags = pyrosm.pyrosm.Conf.tags.available
        print_to_console(f'Available tags: {available_tags}')

        for value in available_tags:
            tag_values = None
            try:
                tag_values = clipped_osm.get_data_by_custom_criteria(
                    custom_filter={value: True})
            except Exception as e:
                print(f'While executing {value}, this error occur: {e}')
            if tag_values is not None:
                print_to_console(f'Found {value}')
                print_to_console(tag_values)
            else:
                print_to_console(f'{value} was not found!')

        print("--------------------")

        self.plot_roads(clipped_osm, axes)
        self.plot_natural(clipped_osm, axes)
        self.plot_landuse(clipped_osm, axes)
        self.plot_buildings(clipped_osm, axes)

        buildings = clipped_osm.get_buildings()
        print("Buildings shape:", buildings.shape)
        print("Buildings CRS:", buildings.crs)
        print("Buildings bounds:", buildings.total_bounds)

        print(f'bbox[0]: {bbox[0]}, bbox[2]: {bbox[2]}')
        print(f'bbox[1]: {bbox[1]}, bbox[3]: {bbox[3]}')

        # Kartenlimits setzen
        axes.set_xlim(bbox[0], bbox[2])
        axes.set_ylim(bbox[1], bbox[3])
        axes.set_facecolor(background_color)
        axes.axis('off')
        plt.tight_layout()
        plt.savefig("map.png", dpi=300, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.show()


# def clip_world_map():

#     # ./osmconvert64-0.8.8p.exe planet-250505.osm.pbf -b="8.5505,52.8584,8.6505,52.9584" -o="clipped.osm.pbf"

#     pass


# def bounding_box(lat, lon, distance_m):
#     """
#     Calculates a bounding box around a geographic point for a given distance in all directions.
#     :param lat: Latitude of the center point in decimal degrees
    # :param lon: Longitude of the center point in decimal degrees
    # :param distance_m: Distance in meters to extend in all directions (north, south, east, west)
    # :return: List in the format [west, south, east, north]
    # """
    # # Approximate length of one degree of latitude in meters
    # meters_per_degree_lat = 111320
    # # Approximate length of one degree of longitude in meters (varies by latitude)
    # meters_per_degree_lon = 111320 * math.cos(math.radians(lat))
    # delta_lat = distance_m / meters_per_degree_lat
    # delta_lon = distance_m / meters_per_degree_lon
    # south = lat - delta_lat
    # north = lat + delta_lat
    # west = lon - delta_lon
    # east = lon + delta_lon
    # return [west, south, east, north]
if __name__ == "__main__":

    # lat 53.126419385868196,
    # lon 8.648156683716197

    lat = 6.923406087268815
    lon = 79.98969066499438
    dis = 10000
    generator = Generator(lat, lon, dis)
    generator.main()
