import math
import multiprocessing
import os
import subprocess
import sys
import datetime
import time
import traceback


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


def delete_original_files(raw_file, raw_file_path):
    # Delete original file
    if not raw_file:
        try:
            os.remove(raw_file_path)
            print_to_console(f'Successfully removed file: {raw_file_path}')
        except IOError as e:
            print_to_console(f'Error while trying to remove file: {traceback.format_exc()}. {e}')
        finally:
            print_to_console(f"File '{raw_file_path}' deleted successfully.")


def print_to_console(message:str):

    current_datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(f'{current_datetime} (Thread: {multiprocessing.current_process().name}): {message}')


def calc_file_size_gb(file_path: str) -> float:

    # Get file size
    file_size = os.path.getsize(file_path)
    file_size_gb = file_size / math.pow(10, 9)
    print_to_console(f'Size in GB: {file_size_gb}')

    return file_size_gb