import datetime
import json
import multiprocessing
import os
import subprocess
import sys
import time
import unittest
from multiprocessing import Pool
from typing import Tuple

from src.HelperFunctions import print_to_console, extract_osm_statistics


# Ausgelagerte Hilfsfunktionen auf Modulebene
def create_sub_file(path_to_raw_file: str, min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:
    basename = os.path.basename(path_to_raw_file).split('/')[-1].split("_")[0].replace('.osm.pbf', '')
    new_file_name = f'results\\{basename}_{min_lon}_{min_lat}_{max_lon}_{max_lat}.osm.pbf'
    new_file_name_parameter = f'-o="{new_file_name}"'
    bounding_box_parameter = f'-b="{min_lon}, {min_lat}, {max_lon}, {max_lat}"'

    try:
        subprocess.run(f'.\\..\\src\\resources\\osmconvert64-0.8.8p.exe resources\\{basename}.osm.pbf {bounding_box_parameter} {new_file_name_parameter}')
    except subprocess.CalledProcessError as processError:
        print(f"Error code: {processError.returncode}, {processError.output}")
        sys.exit(1)

    return new_file_name

def execute(args: Tuple[str, str]):
    path_to_osmconvert64, test_file = args

    statistics = extract_osm_statistics(path_to_osmconvert64, test_file)
    longitudinal_min = float(statistics['lon min'])
    longitudinal_max = float(statistics['lon max'])
    latitude_min = float(statistics['lat min'])
    latitude_max = float(statistics['lat max'])

    create_sub_file(test_file, longitudinal_min, latitude_min, longitudinal_max, latitude_max)



class TestOsmconvert64(unittest.TestCase):

    test_file = 'resources\\south-america-latest.osm.pbf'
    path_to_osmconvert64 = '.\\..\\src\\resources\\osmconvert64-0.8.8p.exe'
    path_to_results = 'results'

    offset = 0.00001
    lon_min_bound = -180.0
    lon_max_bound = 180.0
    lat_min_bound = -90.0
    lat_max_bound = 90.0


    def test_osm_convert_options(self):

        test_results = {}

        # Test hash memory size from 500MB up to 4000MB (maximum)
        # --hash-memory=1500

        bound = 500
        while bound <= 4000:

            start_time = time.time()

            os.system(f'{self.path_to_osmconvert64} {self.test_file} --hash-memory={bound}')
            test_results[f'test_memory_size_{bound}'] = time.time() - start_time

            bound += 500

        # Test max objects from 15.000.000 up to 45.000.000 (maximum)
        bound = 15000000
        while bound <= 45000000:

            start_time = time.time()

            os.system(f'{self.path_to_osmconvert64} {self.test_file} --max-objects={bound}')
            test_results[f'test_max_objects_{bound}'] = time.time() - start_time

            bound += 10000000

        # Test max objects from 100.000 up to 500.000 (maximum)
        bound = 100000
        while bound <= 500000:

            start_time = time.time()

            os.system(f'{self.path_to_osmconvert64} {self.test_file} --max-objects={bound}')
            test_results[f'test_max_objects_{bound}'] = time.time() - start_time

            bound += 100000

        current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        file_name = f'TestOsmconvert64_results_{current_datetime}_{current_datetime}'
        with open(os.path.join(self.path_to_results, file_name), "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)


    def test_multiprocessing(self):

        # Test single processing
        #start_time_single = time.time()

        #for i in range(4):

        #    statistics = extract_osm_statistics(self.path_to_osmconvert64, self.test_file)
        #    longitudinal_min = float(statistics['lon min'])
        #    longitudinal_max = float(statistics['lon max'])
        #    latitude_min = float(statistics['lat min'])
        #    latitude_max = float(statistics['lat max'])

        #    create_sub_file(self.test_file, longitudinal_min, latitude_min, longitudinal_max, latitude_max)

        #print(f'Single time: {time.time() - start_time_single}')
        print(multiprocessing.cpu_count())
        # Test multi processing
        start_time_multi = time.time()

        execute_value = []
        for i in range(8):
            execute_value.append(i)

        with Pool(8) as pool:
            pool.map(execute, [(self.path_to_osmconvert64, self.test_file)] * 4)

        print(f'Multi time: {time.time() - start_time_multi}')


if __name__ == '__main__':
    unittest.main()