import datetime
import math
import os
import subprocess
import time
import traceback

class Preprocessor:

    def __init__(self):

        self.path_to_raw = 'resources\\raw'
        self.path_to_buffer = 'resources\\buffer'
        self.path_to_preprocessed = 'resources\\preprocessed'
        self.path_to_osmcovert = 'resources\\osmconvert64-0.8.8p.exe'

        self.raw_files_statistics = {}
        self.preprocessed_files_statistics = {}


    def create_sub_file(self, path_to_raw_file: str, min_lat: float, min_lon: float, max_lat:float, max_lon:float) -> str:

        if not os.path.exists(self.path_to_buffer):
            os.makedirs(self.path_to_buffer)

        basename = os.path.basename(path_to_raw_file).split('/')[-1].split("_")[0].replace('.osm.pbf', '')
        new_file_name = f'{self.path_to_buffer}\\{basename}_{min_lat}_{min_lon}_{max_lat}_{max_lon}.osm.pbf'
        new_file_name_parameter = f'-o="{new_file_name}"'
        bounding_box_parameter = f'-b="{min_lat}, {min_lon}, {max_lat}, {max_lon}"'

        print_to_console("Command: " + os.path.join(f'.\\{self.path_to_osmcovert}', path_to_raw_file, bounding_box_parameter, new_file_name_parameter))
        test = subprocess.run(f'.\\resources\\osmconvert64-0.8.8p.exe resources\\raw\\africa-latest.osm.pbf -b="{min_lat}, {min_lon}, {max_lat}, {max_lon}" -o="resources\\buffer\\africa-latest_{min_lat}_{min_lon}_{max_lat}_{max_lon}.osm.pbf"')
        print_to_console("Returncode:")
        print_to_console(str(test.returncode))

        return new_file_name


    def get_osm_statistics(self, path_to_file):

        raw_statistic = subprocess.run(['.\\resources\\osmconvert64-0.8.8p.exe', path_to_file, '--out-statistics'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        return raw_statistic

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

        offset = 0.00001
        longitudinal_split = longitudinal_diff / split_size
        latitude_split = latitude_diff / split_size

        lon_min_bound = -180.0
        lon_max_bound = 180.0
        lat_min_bound = -90.0
        lat_max_bound = 90.0

        path_to_new_file = ''

        # Longitudinal
        for x in range(split_size):

            new_lon_min = longitudinal_min + (x * longitudinal_split) - offset
            new_lon_max = longitudinal_min + ((x + 1) * longitudinal_split) + offset

            if new_lon_min < lon_min_bound:
                new_lon_min = lon_min_bound
            if new_lon_max > lon_max_bound:
                new_lon_max = lon_max_bound

            # Latitude
            for y in range(split_size):

                new_lat_min = latitude_min + (y * latitude_split) - offset
                new_lat_max = latitude_min + ((y + 1) * latitude_split) + offset

                print_to_console(f'Range x: {x}/{split_size} | Range y: {y}/{split_size}')

                if new_lat_min < lat_min_bound:
                    new_lat_min = lat_min_bound
                if new_lat_max > lat_max_bound:
                    new_lat_max = lat_max_bound

                print_to_console("New values:")
                print_to_console("new_lon_min: " + str(new_lon_min))
                print_to_console("new_lon_max: " + str(new_lon_max))
                print_to_console("new_lat_min: " + str(new_lat_min))
                print_to_console("new_lat_max: " + str(new_lat_max))

                # Create sub-files
                path_to_new_file = self.create_sub_file(os.path.join(self.path_to_raw, raw_file_path), new_lat_min, new_lon_min, new_lat_max, new_lon_max)
                print_to_console(f'New file: {path_to_new_file} from {raw_file_path}')

                # Get file size
                file_size = os.path.getsize(path_to_new_file)
                file_size_gb = file_size / math.pow(10, 9)

                # Get file statistics
                new_file_statistics = self.get_osm_statistics(path_to_new_file)

                if file_size_gb > 2.0:

                    print_to_console("File is larger than 2 GB!" + str(file_size_gb))

                    # Create statistics dict
                    new_statistics_dict = {}
                    for statistic in new_file_statistics.split("\n"):

                        if statistic != '':
                            split = statistic.split(":", 1)
                            new_statistics_dict[split[0]] = split[1]

                    self.split_file(file_size_gb, new_statistics_dict, path_to_new_file)

                else:
                    print_to_console("File is smaller than 2 GB!" + str(file_size_gb))

                    self.preprocessed_files_statistics[os.path.basename(path_to_new_file).split('/')[-1]] = new_file_statistics

        # Delete original file
        if not raw_file:
            try:
                os.remove(path_to_new_file)
            except IOError:
                print_to_console(f'Error while trying to remove file: {traceback.format_exc()}')
            finally:
                print_to_console(f"File '{path_to_new_file}' deleted successfully.")


    def main(self):

        for raw_file in os.listdir(self.path_to_raw):

            print_to_console(f'Processing Raw-File: {raw_file}')

            # Get file size
            file_size = os.path.getsize(os.path.join(self.path_to_raw, raw_file))
            file_size_gb = file_size / math.pow(10, 9)
            print_to_console(f'Size in GB: {file_size_gb}')

            # Get file statistics
            file_statistics = self.get_osm_statistics(os.path.join(self.path_to_raw, raw_file))

            # Create statistics dict
            statistics_dict = {}
            for statistic in file_statistics.split("\n"):

                if statistic != '':
                    split = statistic.split(":", 1)
                    statistics_dict[split[0]] = split[1]

            # Save statistics of raw file
            self.raw_files_statistics[raw_file] = statistics_dict

            # Each file should be smaller than 2GB
            if file_size_gb > 2.0:

                print_to_console("File is larger than 2 GB!")

                self.split_file(file_size_gb, statistics_dict, raw_file, raw_file=True)


def print_to_console(message:str):

    current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    print(f'{current_datetime}: {message}')
    

if __name__ == '__main__':

    preprocessor = Preprocessor()
    preprocessor.main()