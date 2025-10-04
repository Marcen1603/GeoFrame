import datetime
import glob
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
from enum import Enum
from multiprocessing import Pool
from progress.bar import Bar

import requests

from src.common.Utilities import print_to_console, extract_osm_statistics, calc_file_size_gb, delete_file, \
    get_min_max_lon_lat


class OS(Enum):
    LINUX = 'linux'
    WINDOWS = 'windows'

    @classmethod
    def from_str(cls, value: str):
        for member in cls:
            if member.value == value.lower():
                return member
        raise ValueError(f"{value} is not a valid os!")


class Preprocessor:

    def __init__(self):

        self.used_os = OS.from_str(platform.system())
        self.cpu_count = 4
        self.use_multithreading = True

        print_to_console(
            f'Available processors: {self.cpu_count} | Multithreading: {self.use_multithreading}')

        # Download
        self.download_planet_file = False

        print_to_console(f'Download planet file: {self.download_planet_file}')

        self.path_to_raw = os.path.join(
            'src', 'preprocessor', 'resources', 'raw')
        self.path_to_done = os.path.join(
            'src', 'preprocessor', 'resources', 'done')
        self.path_to_buffer = os.path.join(
            'src', 'preprocessor', 'resources', 'buffer')
        self.path_to_preprocessed = os.path.join(
            'src', 'preprocessor', 'resources', 'preprocessed')
        self.path_to_osm_convert = os.path.join(
            './', 'src', 'resources', 'osmconvert', 'osmconvert64-0.8.8p.exe')
        self.path_to_osm_convert_linux = os.path.join(
            'src', 'resources', 'osmconvert', 'osmconvert')
        self.path_to_cachefile = os.path.join(
            'src', 'preprocessor', 'resources', 'preprocessed', 'cache_file*.json')
        self.path_to_cachefile_archive = os.path.join(
            'src', 'preprocessor', 'resources', 'preprocessed', 'archive')

        self.max_split_size = 1  # Defined as gigabyte
        self.split_multiplicator = 2  # Sqrt(file_size) * split_multiplicator
        self.offset = 0.00001
        self.lon_min_bound = -180.0
        self.lon_max_bound = 180.0
        self.lat_min_bound = -90.0
        self.lat_max_bound = 90.0

        # Init folders
        for path in [self.path_to_preprocessed, self.path_to_buffer, self.path_to_cachefile_archive, self.path_to_done, self.path_to_raw]:
            if not os.path.exists(path):
                os.makedirs(path)

        # Move cache files
        cache_files = glob.glob(self.path_to_cachefile)
        if len(cache_files) > 0:

            for cache_file in cache_files:
                basename = os.path.basename(cache_file)
                target_path = os.path.join(
                    self.path_to_cachefile_archive, basename)
                shutil.move(cache_file, target_path)
                print_to_console(f"Moved {cache_file} to {target_path}")

        # Create cache file
        current_datetime = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y%m%d%H%M%S')
        with open(os.path.join(self.path_to_preprocessed, f'cache_file_{current_datetime}.json'), 'w') as f:
            json.dump({}, f)

        self.preprocessed_files_statistics = {}

    def download_files(self):
        """The needed files from osm will be downloaded. Based on the gloabl set variables the planet file and the continent files will be downloaded.
        """

        def download_request(url, path):
            r = requests.get(url, stream=True)
            total_length = int(r.headers.get('content-length', 0)) // 1024 + 1

            with open(path, 'wb') as f:
                bar = Bar('Downloading', max=total_length)
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        bar.next()
                bar.finish()

        # Planet file
        if self.download_planet_file:

            for file in os.listdir(self.path_to_raw):
                os.remove(os.path.join(self.path_to_raw, file))

            print_to_console("Cleaned raw folder")

            url = 'https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf'
            filename = os.path.join(self.path_to_raw, 'planet-latest.osm.pbf')
            print_to_console(f'Downloading planet-latest.osm.pbf')
            download_request(url, filename)

    def append_cache_file(self, key, value):
        """Used to append the key value pairs to the cache file.

        Args:
            key (_type_): Key for the dict
            value (_type_): Value for the dict

        Raises:
            ValueError: If there are no or multiple cache files
        """

        cache_files = glob.glob(self.path_to_cachefile)
        if len(cache_files) > 1:
            raise ValueError(
                f'More than one file ({len(cache_files)}) in the folder {self.path_to_cachefile}. Files: {cache_files}')

        cache_file = cache_files.pop()
        with open(cache_file, "r", encoding="utf-8") as f:

            data = json.load(f)
            data[key] = value
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def create_sub_file(self, path_to_raw_file: str, min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:
        """Executing the osmconvert file via subprocess.

        Args:
            path_to_raw_file (str): The path to the file which should be splitted.
            min_lon (float): The new minimal longitudinal value.
            min_lat (float): The new minimal lateral value.
            max_lon (float): The new maximal longitudinal value.
            max_lat (float): The new maximal lateral valie.

        Returns:
            str: Name of the file
        """

        basename = os.path.basename(path_to_raw_file).split(
            '/')[-1].split("_")[0].replace('.osm.pbf', '')
        new_file_name = os.path.join(
            self.path_to_buffer, f'{basename}_{min_lon}_{min_lat}_{max_lon}_{max_lat}.osm.pbf')
        new_file_name_parameter = f'-o={new_file_name}'
        bounding_box_parameter = f'-b={min_lon}, {min_lat}, {max_lon}, {max_lat}'

        # Switch between windows and linux path of the osmconverter
        osmconvert_path = self.path_to_osm_convert_linux if self.used_os == OS.LINUX else self.path_to_osm_convert

        command = [
            osmconvert_path,
            path_to_raw_file,
            bounding_box_parameter,
            new_file_name_parameter
        ]

        try:
            subprocess.run(command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=True)
            print(command)
        except FileNotFoundError as e:
            print_to_console(
                f'Error: Executable not found: {e}. Command: {command}')
            sys.exit(-1)
        except subprocess.CalledProcessError as e:
            print_to_console(
                f'Error: Subprocess failed: {e.stderr.decode()}. Command: {command}')
            sys.exit(-1)

        return new_file_name

    def calculate_min_max_longitude(self, x, longitudinal_min, longitudinal_split):
        """Based on the given range of y, the min of longitudinal and the split range of longitudinal,
        the new values are generated.

        Args:
            longitudinal_min (_type_): The lower value of the longitudinal range.
            longitudinal_split (_type_): The value of longitudinal split range.

        Returns:
            _type_: A pair of the new lower and maximal longitudinal values.
        """

        new_lon_min = longitudinal_min + (x * longitudinal_split) - self.offset
        new_lon_max = longitudinal_min + \
            ((x + 1) * longitudinal_split) + self.offset

        if new_lon_min < self.lon_min_bound:
            new_lon_min = self.lon_min_bound
        if new_lon_max > self.lon_max_bound:
            new_lon_max = self.lon_max_bound

        return new_lon_min, new_lon_max

    def calculate_min_max_latitude(self, y, latitude_min, latitude_split):
        """Based on the given range of y, the min of latitide and the splitted range of latitiude,
        the new values are generated.

        Args:
            y (_type_): The iterate of the split, if split size is 2 than the range is up to 2.
            latitude_min (_type_): The lower value of the latitude range.
            latitude_split (_type_): The value of latitude split range.

        Returns:
            _type_: A pair of the new lower and maximal latitude values.
        """

        new_lat_min = latitude_min + (y * latitude_split) - self.offset
        new_lat_max = latitude_min + ((y + 1) * latitude_split) + self.offset

        if new_lat_min < self.lat_min_bound:
            new_lat_min = self.lat_min_bound
        if new_lat_max > self.lat_max_bound:
            new_lat_max = self.lat_max_bound

        return new_lat_min, new_lat_max

    def split_file(self, args):
        """In this method the split process based on the given arguments are executed.

        Args:
            args (_type_): A set of parameters which are used to create a sub file.
        """
        x, y, split_size, latitude_min, latitude_split, longitude_min, longitude_split, raw_file_path = args

        # Calculate bew min/max values for longitude and latitude of the sub files
        new_lon_min, new_lon_max = self.calculate_min_max_longitude(
            x, longitude_min, longitude_split)
        new_lat_min, new_lat_max = self.calculate_min_max_latitude(
            y, latitude_min, latitude_split)

        print_to_console(
            f'Range x: {x}/{split_size-1} | Range y: {y}/{split_size-1}')

        # Create sub-file
        path_to_new_file = self.create_sub_file(
            raw_file_path, new_lon_min, new_lat_min, new_lon_max, new_lat_max)
        name_of_new_file = os.path.basename(path_to_new_file)
        print_to_console(f'New file: {path_to_new_file} from {raw_file_path}')

        file_size_gb = calc_file_size_gb(path_to_new_file)
        osmconvert_path = self.path_to_osm_convert_linux if self.used_os == OS.LINUX else self.path_to_osm_convert
        new_statistics_dict = extract_osm_statistics(
            osmconvert_path, path_to_new_file)

        # If file again larger than the threshold, move to raw folder to process later
        if file_size_gb > self.max_split_size:
            print_to_console(
                f'File is larger than {self.max_split_size} GB! Moved to raw and processing later. ' + str(file_size_gb))
            shutil.move(os.path.join(self.path_to_buffer, name_of_new_file), os.path.join(
                self.path_to_raw, name_of_new_file))

        # Process file if it is smaller than the threshold
        else:

            print_to_console(
                f'File is smaller than {self.max_split_size} GB! ' + str(file_size_gb))

            # If file contains no data, than the file can be removed -> typically if it covers only parts of the ocean
            if 'lon min' not in new_statistics_dict:
                delete_file(False, os.path.join(
                    self.path_to_buffer, name_of_new_file))

            # If the file contains content, than append data to cache file and move to preprocessed
            else:
                coordinates = {
                    'lon min': new_statistics_dict['lon min'],
                    'lon max': new_statistics_dict['lon max'],
                    'lat min': new_statistics_dict['lat min'],
                    'lat max': new_statistics_dict['lat max']
                }
                try:
                    self.append_cache_file(os.path.join(
                        self.path_to_preprocessed, name_of_new_file), coordinates)
                except ValueError as e:
                    print_to_console(
                        f'Error while trying to write to the cache file! Error: {traceback.format_exc()}. {e}')
                    sys.exit(-1)
                try:
                    shutil.move(os.path.join(self.path_to_buffer, name_of_new_file), os.path.join(
                        self.path_to_preprocessed, name_of_new_file))
                except Exception as e:
                    print_to_console(
                        f'Error while moving file! Error: {traceback.format_exc()}. {e}')
                    sys.exit(1)

    def sub_files(self, file_size_gb: float, statistics_dict: dict, raw_file_path: str):
        """Split a given osm file into multiple smaller ones. 
        The split algorithm is based on the file size and the threshold. Assumption: Threshold 1GB and the file is 15GB.
        In the first step get the sqrt of the 15GB, which is 3.872 and this result is rounded up to 4. This result would 
        mean, that this 15GB file will be splitted into 4x4 files (longituidnal and lateral matrix - for each 4). The 
        theoretical result would be 1 GB files, but the threshold is also 1GB. Because the content of the osm files are
        not distributed equaliy, some files will have more than 1GB and other less. For that reason it will be aimed to
        the half size of the threadhold -> 0.5GB. If the threashold were 2GB than everything would be fine and if the
        threshold were 4GB than the split can be reduced to less splitted files.

        Args:
            file_size_gb (float): The size of the input file given in gigabyte.
            statistics_dict (dict): The statistics of the given file from osmcovert
            raw_file_path (str): The path of the raw file.
        """

        split_size = (int(math.sqrt(file_size_gb)) + 1) * \
            self.split_multiplicator
        print_to_console("Split size: " + str(split_size))

        lon_min, lon_max, lat_min, lat_max = get_min_max_lon_lat(
            statistics_dict)

        longitudinal_diff = abs(lon_min - lon_max)
        latitude_diff = abs(lat_min - lat_max)

        longitudinal_split = longitudinal_diff / split_size
        latitude_split = latitude_diff / split_size

        args_list = []
        # Create list of split variations
        for x in range(split_size):

            for y in range(split_size):
                args_list.append((x, y, split_size, lat_min, latitude_split,
                                 lon_min, longitudinal_split, raw_file_path))

        # Execute multi threading to create all split variations
        with Pool(processes=(self.cpu_count if self.use_multithreading else 1)) as pool:
            pool.map(self.split_file, args_list)

    def main(self):
        """
        The main method to execute the preprocessor
        """
        self.download_files()

        # Get all files from the raw folder
        process_files = os.listdir(self.path_to_raw)

        # Iterate through all files
        while len(process_files) > 0:
            for process_file in process_files:

                print_to_console(f'Processing Raw-File: {process_file}')

                path_to_process_file = os.path.join(
                    self.path_to_raw, process_file)
                file_size_gb = calc_file_size_gb(path_to_process_file)
                osmconvert_path = self.path_to_osm_convert_linux if self.used_os == OS.LINUX else self.path_to_osm_convert
                statistics_dict = extract_osm_statistics(
                    osmconvert_path, path_to_process_file)

                # If file is lager than the defined threshold, split it into multiple ones
                if file_size_gb > self.max_split_size:

                    print_to_console(
                        f'File is larger than {self.max_split_size} GB!')
                    self.sub_files(file_size_gb, statistics_dict,
                                   path_to_process_file)

                # If file is smaller than the defined threshold copy directly to preprocessed files
                else:

                    print_to_console(
                        f'File is smaller than {self.max_split_size} GB! No split needed!')
                    try:
                        shutil.copy(path_to_process_file, os.path.join(
                            self.path_to_preprocessed, process_file))
                        coordinates = {
                            'lon min': statistics_dict['lon min'],
                            'lon max': statistics_dict['lon max'],
                            'lat min': statistics_dict['lat min'],
                            'lat max': statistics_dict['lat max']
                        }
                        try:
                            self.append_cache_file(os.path.join(
                                self.path_to_preprocessed, process_file), coordinates)
                        except ValueError as e:
                            print_to_console(
                                f'Error while trying to write to the cache file! Error: {traceback.format_exc()}. {e}')
                            sys.exit(-1)
                    except Exception as e:
                        print_to_console(
                            f'Error while executing copy statement! Error: {traceback.format_exc()}. {e}')
                        sys.exit(1)

                # After processing the file, move it to the done folder
                shutil.move(os.path.join(self.path_to_raw, process_file),
                            os.path.join(self.path_to_done, process_file))

            # Files which are splited into smaller ones, can still be larger than the threshold. This process is done in
            # parallel execution and it is not possible to make the process of splitting recursive, so this files will be moved to
            # the raw folder. With this files will be continued at this point, thats why here a list of files of the raw folder
            # is created/replaced again.
            process_files = os.listdir(self.path_to_raw)


if __name__ == '__main__':

    preprocessor = Preprocessor()
    preprocessor.main()
