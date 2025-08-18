import json
import logging
import os

from pdfrebuilder.core.render import json_serializer

# from pdfrebuilder.settings import CONFIG, STANDARD_PDF_FONTS


# --- Helper Function for Color Formatting ---
def _rgb_to_hex(rgb_tuple):
    """Converts an RGB tuple (0.0-1.0) to a hex string #RRGGBB."""
    if rgb_tuple is None:
        return "None"
    r = int(rgb_tuple[0] * 255)
    g = int(rgb_tuple[1] * 255)
    b = int(rgb_tuple[2] * 255)
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def _print_color_swatch(color_rgb_tuple, label_text, rich_console=None, HAS_RICH=False):
    """
    Prints a color swatch with a label to the console using rich, if available.
    Otherwise, prints just the hex code and label.
    """
    hex_color = _rgb_to_hex(color_rgb_tuple)
    if HAS_RICH and color_rgb_tuple is not None and rich_console is not None:
        from rich.text import Text

        color_text = Text(f" {hex_color} ", style=f"bold white on {hex_color}")
        rich_console.print(f"{label_text}: ", color_text, end=" ", highlight=False)
    else:
        # This is user-facing, so print is acceptable
        print(f"{label_text}: {hex_color}", end=" ")


def serialize_pdf_content_to_config(content, config_path):
    """Saves the extracted content dictionary to a JSON file, with statistics logging."""
    os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)

    # --- Statistics logging ---
    if hasattr(content, "document_structure"):
        # Handle UniversalDocument object
        units = content.document_structure
        unit_types = [
            unit.type.value if hasattr(unit.type, "value") else unit.type for unit in units
        ]
        unit_type = (
            "pages"
            if "page" in unit_types
            else "canvases"
            if "canvas" in unit_types
            else "units"
        )
        print(
            f"[serialize_content_to_config] Config uses UniversalDocument object. Number of {unit_type}: {len(units)}"
        )
    elif "pages" in content:
        units = content["pages"]
        unit_type = "pages"
        print(f"[serialize_content_to_config] Config uses 'pages' key. Number of pages: {len(units)}")
    elif "document_structure" in content:
        units = content["document_structure"]
        unit_types = [unit.get("type", "unknown") for unit in units]
        unit_type = "pages" if "page" in unit_types else "canvases" if "canvas" in unit_types else "units"
        print(
            f"[serialize_content_to_config] Config uses 'document_structure' key. Number of {unit_type}: {len(units)}"
        )
    else:
        print(
            f"[serialize_content_to_config] WARNING: Unrecognized config structure. Top-level keys: {list(content.keys())}"
        )
        units = []
        unit_type = "units"

    # Count layers and elements
    total_layers = 0
    total_elements = 0

    if hasattr(content, "document_structure"):
        # Handle UniversalDocument object
        for unit in units:
            unit_layers = unit.layers
            total_layers += len(unit_layers)

            # Count elements in each layer
            for layer in unit_layers:
                total_elements += len(layer.content)

                # Count elements in child layers (for PSD group layers)
                child_layers = layer.children
                if child_layers:
                    total_layers += len(child_layers)
                    for child in child_layers:
                        total_elements += len(child.content)
    else:
        # Handle dictionary structure
        for unit in units:
            unit_layers = unit.get("layers", [])
            total_layers += len(unit_layers)

            # Count elements in each layer
            for layer in unit_layers:
                total_elements += len(layer.get("content", []))

                # Count elements in child layers (for PSD group layers)
                child_layers = layer.get("children", [])
                if child_layers:
                    total_layers += len(child_layers)
                    for child in child_layers:
                        total_elements += len(child.get("content", []))

    print(
        f"[serialize_content_to_config] Config statistics: {unit_type}={len(units)}, layers={total_layers}, elements={total_elements}"
    )

    # Serialize to JSON - convert UniversalDocument to dict if needed
    if hasattr(content, "to_dict"):
        content_dict = content.to_dict()
    else:
        content_dict = content

    with open(config_path, "w") as f:
        json.dump(content_dict, f, indent=2, default=json_serializer)


def normalize_text_spacing(text, space_density_threshold=0.3):
    """
    Removes extra spaces from text where spacing is unnaturally wide,
    often an artifact of PDF text extraction.
    Returns the cleaned text and a boolean indicating if a change was made.
    """
    if len(text) < 10:
        return text, False

    space_density = text.count(" ") / len(text)
    if space_density > space_density_threshold:
        return text.replace(" ", ""), True

    return text, False


def detect_file_format(file_path):
    """
    Detect the format of a file based on its magic bytes or extension.

    Args:
        file_path: Path to the file

    Returns:
        String indicating the file format: 'pdf', 'psd', or 'unknown'
    """
    try:
        with open(file_path, "rb") as f:
            # Read the first 8 bytes for magic number detection
            header = f.read(8)

            # Check for PDF signature (%PDF-)
            if header.startswith(b"%PDF-"):
                return "pdf"

            # Check for PSD signature (8BPS)
            if header.startswith(b"8BPS"):
                return "psd"

            # If magic bytes don't match, try file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext == ".pdf":
                return "pdf"
            elif ext == ".psd":
                return "psd"

            # Unknown format
            return "unknown"
    except Exception as e:
        logging.error(f"Error detecting file format: {e}")
        return "unknown"
