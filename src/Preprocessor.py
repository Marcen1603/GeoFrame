import datetime
import glob
import json
import math
import os
import shutil
import subprocess
import sys
import time
import traceback
from multiprocessing import Pool

from src.HelperFunctions import extract_osm_statistics, print_to_console, delete_original_files


class Preprocessor:

    def __init__(self):

        self.path_to_raw = 'resources\\raw'
        self.path_to_buffer = 'resources\\buffer'
        self.path_to_preprocessed = 'resources\\preprocessed'
        self.path_to_osm_covert = 'resources\\osmconvert64-0.8.8p.exe'
        self.path_to_cachefile = 'resources\\preprocessed\\cache_file*.json'
        self.path_to_cachefile_archive = 'resources\\preprocessed\\archive'

        self.offset = 0.00001
        self.lon_min_bound = -180.0
        self.lon_max_bound = 180.0
        self.lat_min_bound = -90.0
        self.lat_max_bound = 90.0

        # Init folders
        if not os.path.exists(self.path_to_preprocessed):
            os.makedirs(self.path_to_preprocessed)

        if not os.path.exists(self.path_to_buffer):
            os.makedirs(self.path_to_buffer)

        if not os.path.exists(self.path_to_cachefile_archive):
            os.makedirs(self.path_to_cachefile_archive)

        # Move cache files
        cache_files = glob.glob(self.path_to_cachefile)
        if len(cache_files) > 0:

            for cache_file in cache_files:
                basename = os.path.basename(cache_file)
                target_path = os.path.join(self.path_to_cachefile_archive, basename)
                shutil.move(cache_file, target_path)
                print_to_console(f"Moved {cache_file} to {target_path}")

        # Create cache file
        current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        with open(os.path.join(self.path_to_preprocessed, f'cache_file_{current_datetime}.json'), 'w') as f:
            json.dump({}, f)

        self.raw_files_statistics = {}
        self.preprocessed_files_statistics = {}


    def append_cache_file(self, key, value):

        cache_files = glob.glob(self.path_to_cachefile)
        if len(cache_files) > 1:
            try:
                raise ValueError(f'More than one file ({len(cache_files)}) in the folder {self.path_to_cachefile}. Files: {cache_files}')
            except ValueError as e:
                print_to_console(f'Error while trying to write to the cache file! Error: {traceback.format_exc()}. {e}')
                sys.exit(-1)

        cache_file = cache_files.pop()
        with open(cache_file, "r", encoding="utf-8") as f:

            data = json.load(f)
            data[key] = value
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)


    def create_sub_file(self, path_to_raw_file: str, min_lon: float, min_lat: float, max_lon:float, max_lat:float) -> str:

        basename = os.path.basename(path_to_raw_file).split('/')[-1].split("_")[0].replace('.osm.pbf', '')
        new_file_name = f'{self.path_to_buffer}\\{basename}_{min_lon}_{min_lat}_{max_lon}_{max_lat}.osm.pbf'
        new_file_name_parameter = f'-o="{new_file_name}"'
        bounding_box_parameter = f'-b="{min_lon}, {min_lat}, {max_lon}, {max_lat}"'

        try:
            subprocess.run(f'.\\resources\\osmconvert64-0.8.8p.exe resources\\raw\\{basename}.osm.pbf {bounding_box_parameter} {new_file_name_parameter}')
        except subprocess.CalledProcessError as processError:
            print_to_console(f"Error code: {processError.returncode}, {processError.output}")
            sys.exit(1)

        return new_file_name


    def calculate_min_max_longitude(self, x, longitudinal_min, longitudinal_split):

        new_lon_min = longitudinal_min + (x * longitudinal_split) - self.offset
        new_lon_max = longitudinal_min + ((x + 1) * longitudinal_split) + self.offset

        if new_lon_min < self.lon_min_bound:
            new_lon_min = self.lon_min_bound
        if new_lon_max > self.lon_max_bound:
            new_lon_max = self.lon_max_bound

        return new_lon_min, new_lon_max


    def calculate_min_max_latitude(self, y, latitude_min, latitude_split):

        new_lat_min = latitude_min + (y * latitude_split) - self.offset
        new_lat_max = latitude_min + ((y + 1) * latitude_split) + self.offset

        if new_lat_min < self.lat_min_bound:
            new_lat_min = self.lat_min_bound
        if new_lat_max > self.lat_max_bound:
            new_lat_max = self.lat_max_bound

        return new_lat_min, new_lat_max


    def process_tile(self, args):
        x, y, split_size, latitude_min, latitude_split, longitude_min, longitude_split, raw_file_path = args

        new_lon_min, new_lon_max = self.calculate_min_max_longitude(x, longitude_min, longitude_split)
        new_lat_min, new_lat_max = self.calculate_min_max_latitude(y, latitude_min, latitude_split)

        print_to_console(f'Range x: {x}/{split_size-1} | Range y: {y}/{split_size-1}')
        print_to_console("New values:")
        print_to_console(f"new_lon_min: {new_lon_min}")
        print_to_console(f"new_lon_max: {new_lon_max}")
        print_to_console(f"new_lat_min: {new_lat_min}")
        print_to_console(f"new_lat_max: {new_lat_max}")

        # Create sub-file
        path_to_new_file = self.create_sub_file(os.path.join(self.path_to_raw, raw_file_path), new_lon_min, new_lat_min, new_lon_max, new_lat_max)
        name_of_new_file = path_to_new_file.split("\\")[-1]
        print_to_console(name_of_new_file)
        print_to_console(f'New file: {path_to_new_file} from {raw_file_path}')

        file_size = os.path.getsize(path_to_new_file)
        file_size_gb = file_size / math.pow(10, 9)

        new_statistics_dict = extract_osm_statistics('.\\resources\\osmconvert64-0.8.8p.exe', path_to_new_file)

        if file_size_gb > 2.0:
            print_to_console("File is larger than 2 GB!" + str(file_size_gb))
            self.split_file(file_size_gb, new_statistics_dict, path_to_new_file)
        else:
            print_to_console("File is smaller than 2 GB!" + str(file_size_gb))
            if 'lon min' not in new_statistics_dict:
                delete_original_files(False, os.path.join(self.path_to_buffer, name_of_new_file))
            else:
                coordinates = {
                    'lon min': new_statistics_dict['lon min'],
                    'lon max': new_statistics_dict['lon max'],
                    'lat min': new_statistics_dict['lat min'],
                    'lat max': new_statistics_dict['lat max']
                }
                self.append_cache_file(os.path.join(self.path_to_preprocessed, name_of_new_file), coordinates)



    def split_file(self, file_size_gb:float, statistics_dict:dict, raw_file_path:str, raw_file=False):

        # Files larger than 2GB are cut into small pieces
        # Based on the file size in GB, the file is split into theoretical 1 GB files
        # The division is carried out at the latitude and longitude. For example, splitting into 4 files
        # divides the latitude once in the middle and the longitude once

        split_size = int(math.sqrt(file_size_gb)) + 1

        longitudinal_min = float(statistics_dict['lon min'])
        longitudinal_max = float(statistics_dict['lon max'])
        latitude_min = float(statistics_dict['lat min'])
        latitude_max = float(statistics_dict['lat max'])

        print_to_console("Split size: " + str(split_size))

        longitudinal_diff = abs(longitudinal_min - longitudinal_max)
        latitude_diff = abs(latitude_min - latitude_max)

        longitudinal_split = longitudinal_diff / split_size
        latitude_split = latitude_diff / split_size

        # Longitudinal
        for x in range(split_size):

            args_list = []

            for y in range(split_size):
                args_list.append((x, y, split_size, latitude_min, latitude_split, longitudinal_min, longitudinal_split, raw_file_path))

            with Pool(processes=split_size) as pool:
                pool.map(self._wrap_process_tile, args_list)

        delete_original_files(raw_file, raw_file_path)
        # Will also be executed if a split file is larger than 2GB and will be split again
        self.move_files()


    def move_files(self):
        # Move all buffer files to preprocessed
        for file in os.listdir(self.path_to_buffer):
            try:
                shutil.move(os.path.join(self.path_to_buffer, file), os.path.join(self.path_to_preprocessed, file))
            except Exception as e:
                print_to_console(f'Error while executing statement! Error: {traceback.format_exc()}. {e}')
                sys.exit(1)


    def main(self):

        for raw_file in os.listdir(self.path_to_raw):

            print_to_console(f'Processing Raw-File: {raw_file}')

            # Get file size
            file_size = os.path.getsize(os.path.join(self.path_to_raw, raw_file))
            file_size_gb = file_size / math.pow(10, 9)
            print_to_console(f'Size in GB: {file_size_gb}')

            # Get file statistics
            statistics_dict = extract_osm_statistics('.\\resources\\osmconvert64-0.8.8p.exe' ,os.path.join(self.path_to_raw, raw_file))

            # Save statistics of raw file
            self.raw_files_statistics[raw_file] = statistics_dict

            # Each file should be smaller than 2GB
            if file_size_gb > 2.0:

                print_to_console("File is larger than 2 GB!")
                self.split_file(file_size_gb, statistics_dict, raw_file, raw_file=True)

            else:

                print_to_console("File is smaller than 2 GB! No split needed!")
                try:
                    shutil.copy(os.path.join(self.path_to_raw, raw_file), os.path.join(self.path_to_preprocessed, raw_file))
                    coordinates = {
                        'lon min': statistics_dict['lon min'],
                        'lon max': statistics_dict['lon max'],
                        'lat min': statistics_dict['lat min'],
                        'lat max': statistics_dict['lat max']
                    }
                    self.append_cache_file(os.path.join(self.path_to_preprocessed, raw_file), coordinates)
                except Exception as e:
                    print_to_console(f'Error while executing copy statement! Error: {traceback.format_exc()}. {e}')
                    sys.exit(1)


    @staticmethod
    def _wrap_process_tile(args):
        # Hier musst du eine neue Instanz oder den Kontext übergeben
        # z. B. über functools.partial oder global
        # Oder einfach: Wenn der Code ohnehin in einer Klasse läuft, instanziere die Klasse vorher
        instance = Preprocessor()  # Hier deine Klasse mit den nötigen Parametern
        return instance.process_tile(args)


if __name__ == '__main__':

    preprocessor = Preprocessor()
    preprocessor.main()