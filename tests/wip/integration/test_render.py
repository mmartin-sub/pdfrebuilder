# tests/test_render.py
import pytest

from pdfrebuilder.engine.tool_fritz import _convert_color_to_rgb


def test_convert_color_to_rgb_int():
    assert _convert_color_to_rgb(0xFF0000) == (1.0, 0.0, 0.0)
    assert _convert_color_to_rgb(0x00FF00) == (0.0, 1.0, 0.0)
    assert _convert_color_to_rgb(0x0000FF) == (0.0, 0.0, 1.0)


def test_convert_color_to_rgb_tuple():
    assert _convert_color_to_rgb([255, 128, 0]) == pytest.approx((1.0, 128 / 255.0, 0.0))
    assert _convert_color_to_rgb((1.0, 0.5, 0.0)) == (1.0, 0.5, 0.0)


def test_convert_color_to_rgb_invalid():
    assert _convert_color_to_rgb(None) is None
    assert _convert_color_to_rgb("not a color") is None


def test_convert_color_to_rgb_range():
    # All outputs should be in [0.0, 1.0]
    for val in [0x123456, [255, 255, 255], (0.0, 0.0, 0.0)]:
        rgb = _convert_color_to_rgb(val)
        if rgb is not None:
            assert all(0.0 <= c <= 1.0 for c in rgb)
