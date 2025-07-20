# tool_fritz

## Functions

### _convert_color_to_rgb(color_val)

Converts various color formats to a PyMuPDF-compatible RGB tuple (0.0-1.0).

Handles the following color formats:

- None: Returns None (indicating no color)
- Integer: Interpreted as RGB hex value (e.g., 0xFF0000 for red)
- List/Tuple: RGB values in range 0-255 or 0.0-1.0

Args:
    color_val: Color value in any of the supported formats

Returns:
    RGB tuple with values in range 0.0-1.0, or None if input is None
