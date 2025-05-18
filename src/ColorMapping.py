import re
import sys

import matplotlib
import colorsys


def darken(hex_color, percent):
    """
    Dunkelt eine Hex-Farbe um den angegebenen Prozentsatz ab.
    :param hex_color: Farbe als Hex-String, z. B. "#ffcc00"
    :param percent: Prozentuale Abdunkelung (z. B. 30 für 30 %)
    :return: Abgedunkelte Hex-Farbe
    """
    rgb = matplotlib.colors.to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = max(0, l * (1 - percent / 100))
    dark_rgb = colorsys.hls_to_rgb(h, l, s)
    return matplotlib.colors.to_hex(dark_rgb)


def lighten(hex_color, percent):
    """
    Hellt eine Hex-Farbe um den angegebenen Prozentsatz auf.
    :param hex_color: Farbe als Hex-String, z. B. "#ffcc00"
    :param percent: Prozentuale Aufhellung (z. B. 30 für 30 %)
    :return: Aufgehellte Hex-Farbe
    """
    rgb = matplotlib.colors.to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = min(1, l + (1 - l) * (percent / 100))
    light_rgb = colorsys.hls_to_rgb(h, l, s)
    return matplotlib.colors.to_hex(light_rgb)


class ColorMapping:

    def __init__(self):

        self.roads = '#808080'
        self.buildings = self.roads

        self.grass = '#cdebb0'              # Lch(90,32,128)
        self.grassland = self.grass
        self.meadow = self.grass
        self.village_green = self.grass
        self.garden = self.grass
        self.allotments = self.grass
        self.natural_wood = "#9DCA8A"
        self.natural_water = "#AAD3DF"

        self.scrub = '#c8d7ab'              # Lch(84,24,122)
        self.forest = '#add19e'             # Lch(80,30,135)
        self.forest_text = '#46673b'        # Lch(40,30,135)
        self.park = '#c8facc'               # Lch(94,30,145)
        self.allotments= '#c9e1bf'          # Lch(87,20,135)
        self.orchard = '#aedfa3'
        self.vineyard = self.orchard
        self.plant_nursery = self.orchard
        self.hedge = self.forest            # Lch(80,30,135)

        # --- "Base" landuses ---

        self.built_up_lowzoom = '#d0d0d0'
        self.built_up_z12 = '#dddddd'
        self.residential = '#e0dfdf'        # Lch(89,0,0)
        self.residential_line = '#b9b9b9'   # Lch(75,0,0)
        self.retail = '#ffd6d1'             # Lch(89,16,30)
        self.retail_line = '#d99c95'        # Lch(70,25,30)
        self.commercial = '#f2dad9'         # Lch(89,8.5,25)
        self.commercial_line = '#d1b2b0'    # Lch(75,12,25)
        self.industrial = '#ebdbe8'         # Lch(89,9,330)
        self.railway = self.industrial
        self.wastewater_plant = self.industrial
        self.industrial_line = '#c6b3c3'    # Lch(75,11,330)
        self.railway_line = self.industrial_line
        self.wastewater_plant_line = self.industrial_line
        self.farmland = '#eef0d5'           # Lch(94,14,112)
        self.farmland_line = '#c7c9ae'      # Lch(80,14,112)
        self.farmyard = '#f5dcba'           # Lch(89,20,80)
        self.farmyard_line = '#d1b48c'      # Lch(75,25,80)

        # --- Transport ----

        self.transportation_area = '#e9e7e2'
        self.apron = '#dadae0'
        self.garages = '#dfddce'
        self.parking = '#eeeeee'
        #self.parking_outline = saturate(darken(self.parking, 40%), 20%);
        self.railway = self.industrial
        self.railway_line = self.industrial_line
        self.rest_area = '#efc8c8'
        self.services = self.rest_area

        # --- Other ----

        self.bare_ground = '#eee5dc'
        self.campsite = '#def6c0'
        self.caravan_site = self.campsite
        self.picnic_site = self.campsite
        self.cemetery = '#aacbaf'
        self.grave_yard = self.cemetery
        self.construction = '#c7c7b4'
        self.brownfield = self.construction
        self.heath = '#d6d99f'
        self.mud: matplotlib.colors.rgb2hex((203,177,154,0.3), keep_alpha=True) # produces #e6dcd1 over self.land
        self.place_of_worship = '#d0d0d0'
        self.landuse_religious = self.place_of_worship
        self.place_of_worship_outline = darken(self.place_of_worship, 30)
        self.leisure = lighten(self.park, 5)
        self.power = darken(self.industrial, 5)
        self.power_line = darken(self.industrial_line, 5)
        self.sand = '#f5e9c6'
        self.societal_amenities = '#ffffe5'   # Lch(99,13,109)
        self.tourism = '#660033'
        self.quarry = '#c5c3c3'
        self.military = '#F3E3DD'
        self.beach = '#fff1ba'
        self.wastewater_plant = self.industrial
        self.wastewater_plant_line = self.industrial_line
        self.water_works = self.industrial
        self.water_works_line = self.industrial_line

        # --- Sports ---

        self.pitch = '#88e0be'                # Lch(83,35,166)
        self.track = self.pitch
        self.stadium = self.leisure
        self.sports_centre = self.stadium
        self.golf_course = self.campsite


    def get_color(self, value: str) -> str | None:

        for k,v in self.__dict__.items():

            if re.sub('[-_]', "", k) == re.sub('[-_]', "", value):

                return v

        print(value + " was not found!")
        sys.exit(-1)
