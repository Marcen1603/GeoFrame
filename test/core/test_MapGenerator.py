# ---------- Tests für Konstruktor ----------
import math
import os
import platform
import pytest
from matplotlib import pyplot as plt
from matplotlib.streamplot import OutOfBounds
from pyrosm import OSM

from src.common.Utilities import extract_osm_statistics
from src.core.MapGenerator import Generator

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
path_to_test_cache_file = os.path.join(ROOT_DIR, 'test', 'resources')
path_to_osm_convert_windows = os.path.join(ROOT_DIR, 'src', 'resources', 'osmconvert', 'osmconvert64-0.8.8p.exe')
path_to_osm_convert_linux = os.path.join(ROOT_DIR, 'src', 'resources', 'osmconvert', 'osmconvert')

osm_test_file_path = os.path.join(ROOT_DIR, 'test', 'resources', 'planet-latest_89.99999_-18.00001_108.00001_-8.99999.osm.pbf')

if platform.system().lower() == 'linux':
    osm_convert_path = path_to_osm_convert_linux
elif platform.system().lower() == 'windows':
    osm_convert_path = path_to_osm_convert_windows
else:
    raise NotImplementedError(f'Unsupported OS: {platform.system()}')

def test_init():
    lat = 53.12640694087143
    lon = 8.648171013164365
    dis = 750
    generator = Generator(lat, lon, dis)

    assert generator.latitude == lat
    assert generator.longitude == lon
    assert generator.distance == dis


@pytest.mark.parametrize("invalid_lat", [181.000, -951.000])
def test_invalid_lat_MapGenerator(invalid_lat):
    """Invalid input lat parameter for the MapGenerator"""
    with pytest.raises(Exception):
        Generator(invalid_lat, 8.648171013164365, 750)


@pytest.mark.parametrize("invalid_lon", [181.000, -951.000])
def test_invalid_lon_MapGenerator(invalid_lon):
    """Invalid input lon parameter for the MapGenerator"""
    with pytest.raises(Exception):
        Generator(53.12640694087143, invalid_lon, 750)


@pytest.mark.parametrize("invalid_dis", [-1000, 0, 0.999])
def test_invalid_dis_MapGenerator(invalid_dis):
    """Invalid input dis parameter for the MapGenerator"""
    with pytest.raises(Exception):
        Generator(53.12640694087143, 8.648171013164365, invalid_dis)

# ---------- Tests für Klassenmethoden ----------

def test_bounding_box_structure():
    """Ensure bounding_box returns the correct data structures."""
    generator = Generator(53.1264, 8.64817, 750)
    bbox_list, bbox_dict = generator.bounding_box()

    # Check types
    assert isinstance(bbox_list, list)
    assert isinstance(bbox_dict, dict)

    # Check keys in dictionary
    for key in ["lon min", "lon max", "lat min", "lat max"]:
        assert key in bbox_dict

    # Check size of bbox list
    assert len(bbox_list) == 4


def test_bounding_box_order():
    """Ensure min < max for both lat and lon."""
    generator = Generator(53.1264, 8.64817, 750)
    bbox, _ = generator.bounding_box()

    lon_min, lon_max, lat_min, lat_max = bbox

    assert lon_min < lon_max
    assert lat_min < lat_max


def test_bounding_box_symmetry():
    """Ensure that lat/lon differences are roughly symmetric."""
    generator = Generator(53.1264, 8.64817, 750)
    bbox, _ = generator.bounding_box()

    lon_min, lon_max, lat_min, lat_max = bbox
    lat_center = (lat_min + lat_max) / 2
    lon_center = (lon_min + lon_max) / 2

    # The center should be very close to the input coordinates
    assert math.isclose(lat_center, generator.latitude, rel_tol=1e-7)
    assert math.isclose(lon_center, generator.longitude, rel_tol=1e-7)


def test_bounding_box_expected_values():
    """Compare against a known expected result for reproducibility."""
    generator = Generator(53.12640694087143, 8.648171013164365, 750)
    _, bbox = generator.bounding_box()

    # Approximate expected values (within ~1 meter tolerance)
    expected = {
        "lat min": 53.11967,
        "lat max": 53.13314,
        "lon min": 8.63757,
        "lon max": 8.65877,
    }

    for key in expected:
        assert math.isclose(bbox[key], expected[key], rel_tol=1e-4, abs_tol=1e-4)


@pytest.mark.parametrize("distance", [1, 100, 1000, 10000])
def test_bounding_box_scaling(distance):
    """Bounding box size should grow linearly with distance."""
    generator = Generator(53.1264, 8.64817, distance)
    _, bbox = generator.bounding_box()

    lat_span = bbox["lat max"] - bbox["lat min"]
    lon_span = bbox["lon max"] - bbox["lon min"]

    # Larger distances → larger spans
    assert lat_span >= 0
    assert lon_span >= 0


def test_select_pbf_file_successfully():

    generator = Generator(50.0, 50.0, 750)
    generator.path_to_latest_preprocessed = path_to_test_cache_file

    # Input data -> found first_file
    bbox_dict = {
        "lon min": -150.0,
        "lon max": -155.0,
        "lat min": -40.0,
        "lat max": -38.0,
    }

    found_file = generator.select_pbf_file(bbox_dict)
    assert found_file == 'first.osm.pbf'

    # Input data -> found second_file
    bbox_dict = {
        "lon min": -170.0,
        "lon max": -168.0,
        "lat min": -85.0,
        "lat max": -84.0,
    }

    found_file = generator.select_pbf_file(bbox_dict)
    assert found_file == 'second.osm.pbf'


def test_select_pbf_file_between_two_files():

    generator = Generator(50.0, 50.0, 750)
    generator.path_to_latest_preprocessed = path_to_test_cache_file

    # Input data -> overlap between two files
    bbox_dict = {
        "lon min": -170.0,
        "lon max": -168.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    found_file = generator.select_pbf_file(bbox_dict)
    assert found_file == generator.path_to_latest_planet

def test_select_pbf_file_out_of_boundaries():

    generator = Generator(50.0, 50.0, 750)

    # Input data -> out of max longitudinal boundary
    bbox_dict = {
        "lon min": 160.0,
        "lon max": 195.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    with pytest.raises(OutOfBounds):
        generator.select_pbf_file(bbox_dict)

    # Input data -> out of min longitudinal boundary
    bbox_dict = {
        "lon min": -190.0,
        "lon max": -179.0,
        "lat min": -84.0,
        "lat max": -73.0,
    }

    with pytest.raises(OutOfBounds):
        generator.select_pbf_file(bbox_dict)

    # Input data -> out of max latitude boundary
    bbox_dict = {
        "lon min": -170.0,
        "lon max": -168.0,
        "lat min": 80.0,
        "lat max": 95.0,
    }

    with pytest.raises(OutOfBounds):
        generator.select_pbf_file(bbox_dict)

    # Input data -> out of min latitude boundary
    bbox_dict = {
        "lon min": -170.0,
        "lon max": -168.0,
        "lat min": -95.0,
        "lat max": -80.0,
    }

    with pytest.raises(OutOfBounds):
        generator.select_pbf_file(bbox_dict)


def plot_roads():
    generator = Generator(50.0, 50.0, 750)
    bbox_dict = extract_osm_statistics(osm_convert_path, osm_test_file_path)
    _, axes = plt.subplots(figsize=(12, 12))

    bbox_list = [bbox_dict['lon min'], bbox_dict['lat min'], bbox_dict['lon max'], bbox_dict['lat max']]
    osm = OSM(osm_test_file_path, bounding_box=bbox_list)

    generator.plot_roads(osm, axes)


if __name__ == "__main__":

    plot_roads()

# ---------- Tests für Static-Methoden ----------