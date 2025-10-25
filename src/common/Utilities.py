import math
import multiprocessing
import os
import subprocess
import sys
import datetime
import time
import traceback

from matplotlib.streamplot import OutOfBounds


def print_to_console(message:str):

    current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_datetime} (Thread: {multiprocessing.current_process().name}): {message}')


def extract_osm_statistics(osm_convert_path: str, file_path: str) -> dict:

    command = [
        osm_convert_path,
        file_path,
        '--out-statistics'
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        statistics = result.stdout.decode('utf-8')
    except FileNotFoundError as e:
        print_to_console(f'Error: Executable not found: {e}')
        sys.exit(-1)
    except subprocess.CalledProcessError as e:
        print_to_console(f'Error: Subprocess failed: {e.stderr.decode()}')
        sys.exit(-1)

    return osm_statistics_to_dict(statistics)


def osm_statistics_to_dict(oms_statistics: str) -> dict:

    statistics_dict = {}
    for statistic in oms_statistics.split("\n"):

        if statistic != '':
            split = statistic.split(":", 1)
            statistics_dict[split[0]] = split[1]

    return statistics_dict


def get_min_max_lon_lat(statistics_dict: dict):
    
    longitudinal_min = float(statistics_dict['lon min'])
    longitudinal_max = float(statistics_dict['lon max'])
    latitude_min = float(statistics_dict['lat min'])
    latitude_max = float(statistics_dict['lat max'])
    
    return longitudinal_min, longitudinal_max, latitude_min, latitude_max


def delete_file(raw_file: bool, raw_file_path: str):
    # Delete original file
    if not raw_file:
        try:
            os.remove(raw_file_path)
            print_to_console(f'Successfully removed file: {raw_file_path}')
        except IOError as e:
            print_to_console(f'Error while trying to remove file: {traceback.format_exc()}. {e}')
        finally:
            print_to_console(f"File '{raw_file_path}' deleted successfully.")


def calc_file_size_gb(file_path: str) -> float:

    # Get file size
    file_size = os.path.getsize(file_path)
    file_size_gb = file_size / math.pow(10, 9)
    print_to_console(f'Size in GB: {file_size_gb}')

    return file_size_gb


def bbox_content_check(bbox_dict: dict) -> bool:

    expected_values = ['lon min', 'lon max', 'lat min', 'lat max']

    missing = [k for k in expected_values if k not in bbox_dict]
    if len(missing) > 0:
        raise ValueError(f'{missing} are missing in the bbox_dict!')

    if not -180.0 <= bbox_dict['lon min'] <= 180.0:
        raise OutOfBounds(f'Longitudinal min value {bbox_dict['lon min']} out of bound -180/180!')
    if not -180.0 <= bbox_dict['lon max'] <= 180.0:
        raise OutOfBounds(f'Longitudinal max value {bbox_dict['lon max']} out of bound -180/180!')
    if not -90.0 <= bbox_dict['lat min'] <= 90.0:
        raise OutOfBounds(f'Latitude min value {bbox_dict['lat min']} out of bound -90/90!')
    if not -90.0 <= bbox_dict['lat max'] <= 90.0:
        raise OutOfBounds(f'Latitude max value {bbox_dict['lat max']} out of bound -90/90!')

    if type(bbox_dict['lon min']) != float:
        raise TypeError(f'Longitudinal min value {type(bbox_dict['lon min'])} is not equal to float!')
    if type(bbox_dict['lon max']) != float:
        raise TypeError(f'Longitudinal max value {type(bbox_dict['lon max'])} is not equal to float!')
    if type(bbox_dict['lat min']) != float:
        raise TypeError(f'Lateral min value {type(bbox_dict['lat min'])} is not equal to float!')
    if type(bbox_dict['lat max']) != float:
        raise TypeError(f'Lateral max value {type(bbox_dict['lat max'])} is not equal to float!')

    return True