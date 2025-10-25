# tests/test_utils.py
import os
import re
import platform

import pytest
from matplotlib.streamplot import OutOfBounds

from src.common.Utilities import print_to_console, extract_osm_statistics, osm_statistics_to_dict, get_min_max_lon_lat, \
    delete_file, bbox_content_check, calc_file_size_gb

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


def test_osm_statistics_to_dict():

    input_example = ("timestamp min: 2009-03-11T03:07:51Z\n"
             "timestamp max: 2025-07-06T23:11:24Z\n"
             "lon min: 93.4123727\n"
             "lon max: 107.9912119\n"
             "lat min: -15.5588126\n"
             "lat max: -9.0077748\n"
             "nodes: 74903\n"
             "ways: 3455\n"
             "relations: 130\n"
             "node id min: 276254213\n"
             "node id max: 12984403735\n"
             "way id min: 25348921\n"
             "way id max: 1412901663\n"
             "relation id min: 80500\n"
             "relation id max: 19269193\n"
             "keyval pairs max: 460\n"
             "keyval pairs max object: relation 80500\n"
             "noderefs max: 1998\n"
             "noderefs max object: way 854995446\n"
             "relrefs max: 425\n"
             "relrefs max object: relation 19269193\n")

    statistics_dict = osm_statistics_to_dict(input_example)
    assert type(statistics_dict) == dict
    assert statistics_dict is not None
    assert statistics_dict['lon min'] == ' 93.4123727'
    assert statistics_dict['lon max'] == ' 107.9912119'
    assert statistics_dict['lat min'] == ' -15.5588126'
    assert statistics_dict['lat max'] == ' -9.0077748'


def test_get_min_max_lon_lat():

    osm_statistics = extract_osm_statistics(osm_convert_path, osm_test_file_path)

    lon_min = float(osm_statistics['lon min'])
    lon_max = float(osm_statistics['lon max'])
    lat_min = float(osm_statistics['lat min'])
    lat_max = float(osm_statistics['lat max'])

    longitudinal_min, longitudinal_max, latitude_min, latitude_max = get_min_max_lon_lat(osm_statistics)

    assert longitudinal_min == lon_min
    assert longitudinal_max == lon_max
    assert latitude_min == lat_min
    assert latitude_max == lat_max
    assert type(longitudinal_min) == float
    assert type(longitudinal_max) == float
    assert type(latitude_min) == float
    assert type(latitude_max) == float


def test_delete_file():

    # Create file
    with open(os.path.join(ROOT_DIR, 'test', 'common', 'first_file.osm.pbf'), 'w'):
        pass

    # Check file is present
    assert os.path.exists(os.path.join(ROOT_DIR, 'test', 'common', 'first_file.osm.pbf'))

    # Try to delete of raw file (should not be deleted)
    delete_file(True, os.path.join(ROOT_DIR, 'test', 'common', 'first_file.osm.pbf'))

    # File should still exist
    assert os.path.exists(os.path.join(ROOT_DIR, 'test', 'common', 'first_file.osm.pbf'))

    # Try to delete not raw file (should be deleted)
    delete_file(False, os.path.join(ROOT_DIR, 'test', 'common', 'first_file.osm.pbf'))

    # File should not exist
    assert not os.path.exists(os.path.join(ROOT_DIR, 'test', 'common', 'first_file.osm.pbf'))


def test_calc_file_size_gb():

    # Successfully
    assert calc_file_size_gb(osm_test_file_path) == 0.000504993

    # Not valid input path
    with pytest.raises(OSError):
        calc_file_size_gb('NotExistingPath')


def test_bbox_content_check_missing_values():

    bbox_dict_first = {
        "lon min": -279.5,
        "lon max": -179.0,
        "lat min": -84.0,
    }

    with pytest.raises(ValueError):
        bbox_content_check(bbox_dict_first)


def test_bbox_content_check_out_of_bound_longitudinal():

    bbox_dict_first = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_second = {
        "lon min": 170.0,
        "lon max": 180.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    assert bbox_content_check(bbox_dict_first)
    assert bbox_content_check(bbox_dict_second)

    bbox_dict_first = {
        "lon min": -590.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_second = {
        "lon min": 590.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_third = {
        "lon min": 160.0,
        "lon max": -590.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_fourth = {
        "lon min": 160.0,
        "lon max": 590.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_first)
    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_second)
    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_third)
    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_fourth)


def test_bbox_content_check_out_of_bound_lateral():

    bbox_dict_first = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_second = {
        "lon min": 170.0,
        "lon max": 180.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    assert bbox_content_check(bbox_dict_first)
    assert bbox_content_check(bbox_dict_second)

    bbox_dict_first = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -584.0,
        "lat max": -73.0,
    }

    bbox_dict_second = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": 584.0,
        "lat max": -73.0,
    }

    bbox_dict_third = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -573.0,
    }

    bbox_dict_fourth = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": 573.0,
    }

    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_first)
    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_second)
    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_third)
    with pytest.raises(OutOfBounds):
        bbox_content_check(bbox_dict_fourth)


def test_bbox_content_check_float():

    bbox_dict_first = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_second = {
        "lon min": -180.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    assert bbox_content_check(bbox_dict_first)
    assert bbox_content_check(bbox_dict_second)

    bbox_dict_first = {
        "lon min": -180,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    bbox_dict_second = {
        "lon min": '-180.0',
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    with pytest.raises(TypeError):
        bbox_content_check(bbox_dict_first)
    with pytest.raises(TypeError):
        bbox_content_check(bbox_dict_second)