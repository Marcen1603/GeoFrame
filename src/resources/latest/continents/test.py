import json
import os
import subprocess
import sys
import time
import traceback


# Create cache file
cache_file_path = os.path.join('src', 'resources', 'latest', 'continents', f'cache_file_continents.json')
with open(os.path.join(cache_file_path), 'w') as f:
    json.dump({}, f)

for test in os.listdir(os.path.join('src', 'resources', 'latest', 'continents')):
    
    if test.endswith('osm.pbf'):
    
        command = [
            os.path.join('src', 'resources', 'osmconvert', 'osmconvert64-0.8.8p.exe'),
            os.path.join('src', 'resources', 'latest', 'continents', test),
            '--out-statistics'
        ]

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            statistics = result.stdout.decode('utf-8')
        except FileNotFoundError as e:
            print(f'Error: Executable not found: {e}')
            sys.exit(-1)
        except subprocess.CalledProcessError as e:
            print(f'Error: Subprocess failed: {e.stderr.decode()}')
            sys.exit(-1)
            

        statistics_dict = {}
        for statistic in statistics.split("\n"):

            if statistic != '':
                split = statistic.split(":", 1)
                statistics_dict[split[0]] = split[1]

        coordinates = {
                        'lon min': statistics_dict['lon min'],
                        'lon max': statistics_dict['lon max'],
                        'lat min': statistics_dict['lat min'],
                        'lat max': statistics_dict['lat max']
        }

        try:
            with open(os.path.join(cache_file_path), "r", encoding="utf-8") as f:

                data = json.load(f)
                data[test] = coordinates
                with open(os.path.join(cache_file_path), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except ValueError as e:
            print(f'Error while trying to write to the cache file! Error: {traceback.format_exc()}. {e}')
            sys.exit(-1)