# generic

## Functions

### _rgb_to_hex(rgb_tuple)

Converts an RGB tuple (0.0-1.0) to a hex string #RRGGBB.

### _print_color_swatch(color_rgb_tuple, label_text, rich_console, HAS_RICH)

Prints a color swatch with a label to the console using rich, if available.
Otherwise, prints just the hex code and label.

### serialize_pdf_content_to_config(content, config_path)

Saves the extracted content dictionary to a JSON file, with statistics logging.

### normalize_text_spacing(text, space_density_threshold)

Removes extra spaces from text where spacing is unnaturally wide,
often an artifact of PDF text extraction.
Returns the cleaned text and a boolean indicating if a change was made.

### detect_file_format(file_path)

Detect the format of a file based on its magic bytes or extension.

Args:
    file_path: Path to the file

Returns:
    String indicating the file format: 'pdf', 'psd', or 'unknown'
