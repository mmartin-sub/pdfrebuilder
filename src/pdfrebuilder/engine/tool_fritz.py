import logging

# Set up logging
logger = logging.getLogger(__name__)


def _convert_color_to_rgb(color_val):
    """
    Converts various color formats to a PyMuPDF-compatible RGB tuple (0.0-1.0).

    Handles the following color formats:
    - None: Returns None (indicating no color)
    - Integer: Interpreted as RGB hex value (e.g., 0xFF0000 for red)
    - List/Tuple: RGB values in range 0-255 or 0.0-1.0

    Args:
        color_val: Color value in any of the supported formats

    Returns:
        RGB tuple with values in range 0.0-1.0, or None if input is None
    """
    if color_val is None:
        return None
    if isinstance(color_val, int):
        return (
            (color_val >> 16 & 0xFF) / 255.0,
            (color_val >> 8 & 0xFF) / 255.0,
            (color_val & 0xFF) / 255.0,
        )
    elif isinstance(color_val, list | tuple):
        if len(color_val) == 3:
            return tuple(c / 255.0 for c in color_val) if any(c > 1.0 for c in color_val) else tuple(color_val)
        elif len(color_val) == 4:
            # Accept RGBA, ignore alpha
            return (
                tuple(c / 255.0 for c in color_val[:3]) if any(c > 1.0 for c in color_val[:3]) else tuple(color_val[:3])
            )
    logger.warning(f"Invalid color format encountered: {color_val}")
    return None
