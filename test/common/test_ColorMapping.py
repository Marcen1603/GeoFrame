import pytest
import matplotlib.colors

from src.common.ColorMapping import darken, lighten, HEX_PATTERN


@pytest.mark.parametrize("hex_color", ["#ffcc00", "#000000", "#ffffff", "#336699"])
@pytest.mark.parametrize("percent", [0, 10, 50, 100])
def test_darken_valid_output(hex_color, percent):
    """darken sollte gültige Hex-Werte zurückgeben."""
    result = darken(hex_color, percent)
    assert isinstance(result, str)
    assert HEX_PATTERN.match(result), f"Ungültiges Hex-Format: {result}"


@pytest.mark.parametrize("hex_color", ["#ffcc00", "#000000", "#ffffff", "#336699"])
@pytest.mark.parametrize("percent", [0, 10, 50, 100])
def test_lighten_valid_output(hex_color, percent):
    """lighten sollte gültige Hex-Werte zurückgeben."""
    result = lighten(hex_color, percent)
    assert isinstance(result, str)
    assert HEX_PATTERN.match(result), f"Ungültiges Hex-Format: {result}"


def test_darken_0_percent_returns_same_color():
    """Bei 0 % Abdunkelung bleibt die Farbe gleich."""
    color = "#ffcc00"
    assert darken(color, 0) == matplotlib.colors.to_hex(matplotlib.colors.to_rgb(color))


def test_lighten_0_percent_returns_same_color():
    """Bei 0 % Aufhellung bleibt die Farbe gleich."""
    color = "#ffcc00"
    assert lighten(color, 0) == matplotlib.colors.to_hex(matplotlib.colors.to_rgb(color))


def test_darken_100_percent_returns_black():
    """100 % Abdunkelung ergibt Schwarz (#000000)."""
    result = darken("#ffcc00", 100)
    assert result == "#000000"


def test_lighten_100_percent_returns_white():
    """100 % Aufhellung ergibt Weiß (#ffffff)."""
    result = lighten("#336699", 100)
    assert result == "#ffffff"


def test_darken_then_lighten_approx_original():
    """Erst abdunkeln, dann aufhellen sollte ungefähr die Ursprungsfarbe ergeben."""
    original = "#6699cc"
    dark = darken(original, 40)
    restored = lighten(dark, 40)

    rgb_orig = matplotlib.colors.to_rgb(original)
    rgb_restored = matplotlib.colors.to_rgb(restored)

    # Toleranz, da Rundungsfehler auftreten
    assert all(abs(o - r) < 0.05 for o, r in zip(rgb_orig, rgb_restored))


@pytest.mark.parametrize("invalid_color", ["#xyz123", "123456", "red", None, 123])
def test_invalid_hex_color_raises(invalid_color):
    """Ungültige Farben sollten eine Exception auslösen."""
    with pytest.raises(Exception):
        darken(invalid_color, 20)
    with pytest.raises(Exception):
        lighten(invalid_color, 20)


@pytest.mark.parametrize("invalid_percent", [-10, 200, "abc", None])
def test_invalid_percent_handling(invalid_percent):
    """Ungültige Prozentwerte sollten eine Exception auslösen."""
    with pytest.raises(Exception):
        darken("#ffcc00", invalid_percent)
    with pytest.raises(Exception):
        lighten("#ffcc00", invalid_percent)
