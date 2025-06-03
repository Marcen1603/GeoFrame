import math
import os
import subprocess

class Preprocessor:

    def __init__(self):

        self.path_to_raw = 'resources\\raw'
        self.path_to_osmcovert = 'resources\\osmconvert64-0.8.8p.exe'


    def create_sub_file(self, path_to_raw_file: str,) -> str:

        # ./osmconvert64-0.8.8p.exe planet-250505.osm.pbf -b="8.5505,52.8584,8.6505,52.9584" -o="clipped.osm.pbf"

        result = subprocess.run([f'.\\{self.path_to_osmcovert}', path_to_raw_file, min_lat, min_lon, max_lat, max_lon])

        return ""


    def get_osm_statistics(self, raw_file):

        with open(os.path.join(self.path_to_raw, raw_file), 'r') as file:

            raw_statistic = subprocess.run(['.\\resources\\osmconvert64-0.8.8p.exe', os.path.join(self.path_to_raw, raw_file), '--out-statistics'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        return raw_statistic


    def main(self):

        raw_files_statistics = {}
        preprocessed_files_statistics = {}

        for raw_file in os.listdir(self.path_to_raw):

            print(f'Processing {raw_file}')

            # Get file size
            file_size = os.path.getsize(os.path.join(self.path_to_raw, raw_file))
            file_size_gb = file_size / math.pow(10, 9)
            print(f'Size in GB: {file_size_gb}')

            # Get file statistics
            file_statistics = self.get_osm_statistics(raw_file)

            # Create statistics dict
            statistics_dict = {}
            for statistic in file_statistics.split("\n"):

                if statistic != '':
                    split = statistic.split(":", 1)
                    statistics_dict[split[0]] = split[1]

            # Save statistics of raw file
            raw_files_statistics[raw_file] = statistics_dict

            # Each file should be smaller than 2GB
            if file_size_gb > 2.0:

                print("File is larger than 2 GB!")

                # Files larger than 2GB are cut into small pieces
                # Based on the file size in GB, the file is split into theoretical 1 GB files
                # The division is carried out at the latitude and longitude. For example, splitting into 4 files
                # divides the latitude once in the middle and the longitude once

                split_size = int(math.sqrt(file_size_gb)) + 1

                longitudinal_min = float(statistics_dict['lon min'])
                longitudinal_max = float(statistics_dict['lon max'])
                latitude_min = float(statistics_dict['lat min'])
                latitude_max = float(statistics_dict['lat max'])

                print("Split size: " + str(split_size))
                print("Lon min: " + str(longitudinal_min))
                print("Lon max: " + str(longitudinal_max))
                print("Lat min: " + str(latitude_min))
                print("Lat min: " + str(latitude_max))

                longitudinal_diff = abs(longitudinal_min - longitudinal_max)
                latitude_diff = abs(latitude_min - latitude_max)

                print("longitudinal_diff: " + str(longitudinal_diff))
                print("latitude_diff: " + str(latitude_diff))

                offset = 0.00001
                longitudinal_split = longitudinal_diff / split_size
                latitude_split = latitude_diff / split_size

                print("longitudinal_split: " + str(longitudinal_split))
                print("latitude_split: " + str(latitude_split))

                lon_min_bound = -180.0
                lon_max_bound = 180.0
                lat_min_bound = -90.0
                lat_max_bound = 90.0

                for i in range(split_size):

                    print("Range: " + str(i))

                    new_lon_min = longitudinal_min + (i * longitudinal_split) - offset
                    new_lon_max = longitudinal_min + ((i + 1) * longitudinal_split) + offset
                    new_lat_min = latitude_min + (i * latitude_split) - offset
                    new_lat_max = latitude_min + ((i + 1) * latitude_split) + offset

                    if new_lon_min < lon_min_bound:
                        new_lon_min = lon_min_bound
                    if new_lon_max > lon_max_bound:
                        new_lon_max = lon_max_bound
                    if new_lat_min < lat_min_bound:
                        new_lat_min = lat_min_bound
                    if new_lat_max > lat_max_bound:
                        new_lat_max = lat_max_bound

                    print("New values:")
                    print("new_lon_min: " + str(new_lon_min))
                    print("new_lon_max: " + str(new_lon_max))
                    print("new_lat_min: " + str(new_lat_min))
                    print("new_lat_max: " + str(new_lat_max))

                    # Create sub-files

if __name__ == '__main__':

    preprocessor = Preprocessor()
    preprocessor.main()