# tests/test_utils.py
import re

from src.common.Utilities import print_to_console


def test_print_to_console_output(capsys):

    print_to_console("Hello World")


    captured = capsys.readouterr()
    output = captured.out.strip()

    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", output)
    assert "Hello World" in output
    assert "(Thread:" in output
