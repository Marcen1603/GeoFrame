# tests/test_utils.py
import os
import re
import platform

from src.common.Utilities import print_to_console, extract_osm_statistics

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

path_to_osm_convert_windows = os.path.join(ROOT_DIR, 'src', 'resources', 'osmconvert', 'osmconvert64-0.8.8p.exe')
path_to_osm_convert_linux = os.path.join(ROOT_DIR, 'src', 'resources', 'osmconvert', 'osmconvert')

osm_test_file_path = os.path.join(ROOT_DIR, 'test', 'resources', 'planet-latest_89.99999_-18.00001_108.00001_-8.99999.osm.pbf')

if platform.system().lower() == 'linux':
    osm_convert_path = path_to_osm_convert_linux
elif platform.system().lower() == 'windows':
    osm_convert_path = path_to_osm_convert_windows
else:
    raise NotImplementedError(f'Unsupported OS: {platform.system()}')

def test_print_to_console(capsys):

    print_to_console("Hello World")


    captured = capsys.readouterr()
    output = captured.out.strip()

    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", output)
    assert "Hello World" in output
    assert "(Thread:" in output


def test_extract_osm_statistics():

    osm_statistics = extract_osm_statistics(osm_convert_path, osm_test_file_path)
    assert 'lon min' in osm_statistics
    assert 'lon max' in osm_statistics
    assert 'lat min' in osm_statistics
    assert 'lat max' in osm_statistics
    assert osm_statistics is not None