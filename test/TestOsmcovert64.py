import datetime
import json
import os
import subprocess
import sys
import time
import unittest
from multiprocessing import Pool
from typing import Tuple

from preprocessor.Utilities import extract_osm_statistics


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

def osmconvert_execute(args: Tuple[str, str]):
    path_to_osmconvert64, test_file = args
    start = time.time()

    statistics = extract_osm_statistics(path_to_osmconvert64, test_file)
    longitudinal_min = float(statistics['lon min'])
    longitudinal_max = float(statistics['lon max'])
    latitude_min = float(statistics['lat min'])
    latitude_max = float(statistics['lat max'])

    create_sub_file(test_file, longitudinal_min, latitude_min, longitudinal_max, latitude_max)
    end = time.time()
    print(f"Task dauerte: {end - start:.2f} Sekunden")


class TestOsmconvert64(unittest.TestCase):

    test_file = 'resources\\south-america-latest.osm.pbf'
    path_to_osmconvert64 = '.\\..\\src\\resources\\osmconvert64-0.8.8p.exe'
    path_to_results = 'results'

    offset = 0.00001
    lon_min_bound = -127.5000007
    lon_max_bound = -22.5000000
    lat_min_bound = -76.6199935
    lat_max_bound = 65.1925988

    bounding_box_parameter = f'-b="{lon_min_bound}, {lat_min_bound}, {lon_max_bound}, {lat_max_bound}"'

    def test_osm_convert_options(self):

        test_results = {}

        # Test hash memory size from 500MB up to 4000MB (maximum)
        # --hash-memory=1500

        bound = 500
        while bound <= 4000:

            start_time = time.time()

            test_out_file_name = f'-o="{os.path.join(self.path_to_results, f'hash_memory_{bound}.osm.pbf')}"'
            os.system(f'{self.path_to_osmconvert64} {self.test_file} --hash-memory={bound} {self.bounding_box_parameter} {test_out_file_name}')
            test_results[f'test_memory_size_{bound}'] = time.time() - start_time

            bound += 500

        current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        file_name = f'test_osm_convert_options_{current_datetime}.json'
        with open(os.path.join(self.path_to_results, file_name), "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)


    def test_multiprocessing(self):

        cpu_test_size = 24
        results = {}

        for cpu_usage in range(1, cpu_test_size + 1, 1):
            print(f'CPU usage: {cpu_usage}')

            start_time = time.time()

            execute_value = []
            for i in range(cpu_test_size):
                execute_value.append(i)

            with Pool(cpu_usage) as pool:
                pool.map(osmconvert_execute, [(self.path_to_osmconvert64, self.test_file)] * cpu_test_size)

            results[cpu_usage] = time.time() - start_time

        current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        file_name = f'test_multiprocessing_results_{current_datetime}.json'
        with open(os.path.join(self.path_to_results, file_name), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    unittest.main()