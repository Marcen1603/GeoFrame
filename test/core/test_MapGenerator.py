# ---------- Tests für Konstruktor ----------
import pytest

from src.core.MapGenerator import Generator


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



# ---------- Tests für Static-Methoden ----------