import datetime
import glob
import json
import math
import os
import unittest
import folium

class TestPreprocessor(unittest.TestCase):

    path_to_raw = os.path.join('..', 'src', 'resources', 'raw')
    path_to_buffer = os.path.join('..', 'src', 'resources', 'buffer')
    path_to_preprocessed = os.path.join('..', 'src', 'resources', 'preprocessed')
    path_to_osm_convert = os.path.join('..', 'src', 'resources', 'osmconvert64-0.8.8p.exe')


    def test_amount_of_raw_files(self):

        path = os.path.join(self.path_to_raw)
        self.assertTrue(len(os.listdir(path)) == 8)


    def test_size_of_preprocessed_files(self):

        for preprocessed_file in os.listdir(self.path_to_preprocessed):

            # Get file size
            path_to_file = os.path.join(self.path_to_preprocessed, preprocessed_file)
            file_size_gb = os.path.getsize(path_to_file) / math.pow(10, 9)
            self.assertTrue(file_size_gb <= 2.0, f'File {path_to_file} is larger than 2GB!')


    def test_availability(self):

        # Initialize map
        m = folium.Map(location=[0, 0], zoom_start=2)

        cache_files = glob.glob(os.path.join('..', 'src', 'resources', 'preprocessed', 'cache_file*.json'))
        if len(cache_files) > 1:
            raise ValueError("Too much cache files!")

        else:
            with open(cache_files.pop(), "r", encoding="utf-8") as f:

                data = json.load(f)
                print(data)
                for key in data:

                    lat_min = min(float(data[key]['lat min']), float(data[key]['lat max']))
                    lat_max = max(float(data[key]['lat min']), float(data[key]['lat max']))
                    lon_min = min(float(data[key]['lon min']), float(data[key]['lon max']))
                    lon_max = max(float(data[key]['lon min']), float(data[key]['lon max']))

                    polygon_points = [
                        [lat_min, lon_min],  # SW
                        [lat_min, lon_max],  # SE
                        [lat_max, lon_max],  # NE
                        [lat_max, lon_min],  # NW
                        [lat_min, lon_min],  # zurück zum Anfang
                    ]

                    folium.Polygon(
                        locations=polygon_points,
                        color='blue',
                        weight=2,
                        fill=True,
                        fill_opacity=0.4
                    ).add_to(m)

                m.save(f'preprocessed_availability_map.html')


    # def test_original_availability(self):

    #     # Initialize map
    #     m = folium.Map(location=[0, 0], zoom_start=2)

    #     file_list = os.listdir(self.path_to_buffer)

    #     file_counter = 0
    #     for file in file_list:
    #         file_counter += 1

    #         print_to_console(f"Processing file {file_counter} of {len(file_list)}")
    #         statistics = extract_osm_statistics(self.path_to_osm_convert, os.path.join(self.path_to_buffer, file))

    #         if 'lat min' not in statistics:
    #             print_to_console(f'File {file} does not contain lat_min. Size: {calc_file_size_gb(os.path.join(self.path_to_buffer, file))}')

    #         else:

    #             polygon_points = [
    #                 [float(statistics['lat min']), float(statistics['lon min'])],
    #                 [float(statistics['lat min']), float(statistics['lon max'])],
    #                 [float(statistics['lat max']), float(statistics['lon max'])],
    #                 [float(statistics['lat max']), float(statistics['lon min'])],
    #             ]

    #             folium.Polygon(
    #                 locations=polygon_points,
    #                 color='blue',
    #                 weight=2,
    #                 fill=True,
    #                 fill_opacity=0.4
    #             ).add_to(m)

    #     m.save(f'preprocessed_availability_map.html')

if __name__ == '__main__':
    unittest.main()
