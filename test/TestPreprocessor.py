import os
import unittest
import numpy as np
import folium

from src import HelperFunctions as hf
from src.HelperFunctions import extract_osm_statistics
from src.Preprocessor import print_to_console


class TestPreprocessor(unittest.TestCase):

    path_to_raw = '..\\src\\resources\\raw\\'
    path_to_buffer = 'resources\\buffer'
    path_to_preprocessed = '..\\src\\resources\\preprocessed'
    path_to_osm_convert = '.\\..\\src\\resources\\osmconvert64-0.8.8p.exe'

    def test_amount_of_raw_files(self):

        path = os.path.join('..', 'src', self.path_to_raw)
        self.assertTrue(len(path) == 8)

    def test_preprocessed_files(self):

        for file in os.listdir(self.path_to_raw):

            path_raw_file = os.path.join(self.path_to_raw, file)
            raw_statistics_dict = hf.extract_osm_statistics(self.path_to_osm_convert, path_raw_file)

            # Create array from min to max with stepsize
            step = 0.0001
            lat_vals = np.arange(float(raw_statistics_dict['lat min']), float(raw_statistics_dict['lat max']) + step, step)
            lon_vals = np.arange(float(raw_statistics_dict['lon min']), float(raw_statistics_dict['lon max']) + step, step)

            # Create grid as convert to set
            LAT, LON = np.meshgrid(lat_vals, lon_vals)
            all_points = set(zip(LAT.ravel(), LON.ravel()))

            def get_covered_points_by_subfile(min_lat, max_lat, min_lon, max_lon):

                #
                sub_lat_vals = lat_vals[(lat_vals >= min_lat) & (lat_vals <= max_lat)]
                sub_lon_vals = lon_vals[(lon_vals >= min_lon) & (lon_vals <= max_lon)]

                # Gitter für die Subdatei erzeugen
                sub_LAT, sub_LON = np.meshgrid(sub_lat_vals, sub_lon_vals)

                # Punkte als Set von (lat, lon) Paaren zurückgeben
                return set(zip(sub_LAT.ravel(), sub_LON.ravel()))
            filename = file.split('.')[0]
            print("Filename: " + filename)
            print("Name: " + file)

            # Beispiel: zwei Teilbereiche
            subfiles_bounds = [
                (48.0, 48.001, 11.0, 11.001),
                (48.001, 48.002, 11.001, 11.002),
            ]

            for bounds in subfiles_bounds:
                covered = get_covered_points_by_subfile(bounds)
                all_points -= covered

            # 4. Ergebnis prüfen
            if all_points:
                print(f"{len(all_points)} Punkte wurden NICHT abgedeckt!")
            else:
                print("Alle Punkte wurden erfolgreich abgedeckt.")


    def test_availability(self):

        # Initialize map
        m = folium.Map(location=[0, 0], zoom_start=2)

        file_list = os.listdir(os.path.join(self.path_to_preprocessed))
        amount_of_files = len(file_list)

        file_counter = 0
        for file in file_list:
            file_counter += 1

            print_to_console(f"Processing file {file_counter} of {amount_of_files}")
            statistics = extract_osm_statistics(self.path_to_osm_convert, os.path.join(self.path_to_preprocessed + file))

            polygon_points = [
                [float(statistics['lat min']), float(statistics['lon min'])],
                [float(statistics['lat min']), float(statistics['lon max'])],
                [float(statistics['lat max']), float(statistics['lon max'])],
                [float(statistics['lat max']), float(statistics['lon min'])],
                [float(statistics['lat min']), float(statistics['lon min'])]
            ]

            folium.Polygon(
                locations=polygon_points,
                color='blue',
                weight=2,
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

        m.save("availability_map.html")


if __name__ == '__main__':
    unittest.main()
