# tests/test_utils.py
import os
import re

from src.common.Utilities import print_to_console, extract_osm_statistics

path_to_osm_convert_linux = os.path.join(
    'src', 'resources', 'osmconvert', 'osmconvert')
osm_test_file_path = os.path.join(
    'test', 'resources', 'south-america-latest.osm.pbf')


def test_print_to_console(capsys):

    print_to_console("Hello World")


    captured = capsys.readouterr()
    output = captured.out.strip()

    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", output)
    assert "Hello World" in output
    assert "(Thread:" in output


def test_extract_osm_statistics():

    osm_statistics = extract_osm_statistics(path_to_osm_convert_linux, osm_test_file_path)

    assert osm_statistics is not None