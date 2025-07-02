import os
import subprocess
import sys


def extract_osm_statistics(osm_convert_path: str, file_path: str) -> dict:

    print(os.path.dirname(os.path.abspath(sys.argv[0])))
    command = f'{osm_convert_path} {file_path} --out-statistics'
    statistics = None

    try:
        statistics = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
    except FileNotFoundError:
        print('Error while executing subprocess: ' + command)
        sys.exit(-1)

    return osm_statistics_to_dict(statistics)


def osm_statistics_to_dict(oms_statistics: str) -> dict:

    statistics_dict = {}
    for statistic in oms_statistics.split("\n"):

        if statistic != '':
            split = statistic.split(":", 1)
            statistics_dict[split[0]] = split[1]

    return statistics_dict