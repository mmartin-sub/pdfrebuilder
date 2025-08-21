"""
PSD text processing module for the Multi-Format Document Engine.

This module provides utilities for extracting and processing text from PSD files.
"""

import logging
from typing import Any, cast

# Import psd-tools conditionally to handle cases where it's not installed
try:
    from psd_tools import PSDImage

    HAS_PSD_TOOLS = True
except ImportError:
    HAS_PSD_TOOLS = False
    PSDImage = Any

from pdfrebuilder.models.universal_idm import Color, FontDetails

logger = logging.getLogger(__name__)


class PSDTextExtractionError(Exception):
    """Raised when PSD text extraction fails"""


def extract_text_data(text_layer: Any) -> dict[str, Any]:
    """
    Extract text data from a PSD text layer

    Args:
        text_layer: PSD text layer

    Returns:
        Dictionary containing text data

    Raises:
        PSDTextExtractionError: If text extraction fails
    """
    if not HAS_PSD_TOOLS:
        raise PSDTextExtractionError("psd-tools is not installed")

    if not hasattr(text_layer, "kind") or text_layer.kind != "type":
        raise PSDTextExtractionError("Layer is not a text layer")

    try:
        # Get text data
        text_data = text_layer.text_data
        if not text_data:
            return {"text": "", "font_details": {}}

        # Extract text content
        text = text_data.get("text", "")

        # Extract font details
        font_info = text_data.get("font", {})
        font_name = font_info.get("name", "Arial")
        font_size = font_info.get("size", 12)

        # Extract color
        color_data = text_data.get("color", {})
        r = color_data.get("r", 0) / 255.0
        g = color_data.get("g", 0) / 255.0
        b = color_data.get("b", 0) / 255.0

        # Extract paragraph info
        paragraph_info = text_data.get("paragraph", {})
        justification = paragraph_info.get("justification", 0)

        # Extract style info
        style_info = text_data.get("style_sheet", {})
        styles = style_info.get("styles", [])

        # Extract additional text properties
        text_properties = {
            "kerning": text_data.get("kerning", 0),
            "leading": text_data.get("leading", 0),
            "tracking": text_data.get("tracking", 0),
            "baseline_shift": text_data.get("baseline_shift", 0),
        }

        # Create font details
        font_details = {
            "name": font_name,
            "size": font_size,
            "color": (r, g, b),
            "is_bold": font_info.get("bold", False),
            "is_italic": font_info.get("italic", False),
            "kerning": text_properties["kerning"],
            "leading": text_properties["leading"],
            "tracking": text_properties["tracking"],
            "baseline_shift": text_properties["baseline_shift"],
        }

        return {
            "text": text,
            "font_details": font_details,
            "paragraph": {
                "justification": justification,
            },
            "styles": styles,
        }

    except Exception as e:
        raise PSDTextExtractionError(f"Failed to extract text data: {e!s}")


def create_font_details(text_data: dict[str, Any]) -> FontDetails:
    """
    Create FontDetails object from PSD text data

    Args:
        text_data: Text data extracted from PSD

    Returns:
        FontDetails object
    """
    font_info = text_data.get("font_details", {})

    # Get color
    color_tuple = font_info.get("color", (0, 0, 0))
    color = Color(*color_tuple) if len(color_tuple) >= 3 else Color(0, 0, 0)

    return FontDetails(
        name=font_info.get("name", "Arial"),
        size=font_info.get("size", 12),
        color=color,
        is_bold=font_info.get("is_bold", False),
        is_italic=font_info.get("is_italic", False),
        kerning=font_info.get("kerning"),
        leading=font_info.get("leading"),
        tracking=font_info.get("tracking"),
        baseline_shift=font_info.get("baseline_shift"),
    )


def get_text_alignment(text_data: dict[str, Any]) -> int:
    """
    Get text alignment from PSD text data

    Args:
        text_data: Text data extracted from PSD

    Returns:
        Alignment value (0=left, 1=center, 2=right, 3=justify)
    """
    paragraph = text_data.get("paragraph", {})
    justification = paragraph.get("justification", 0)

    # Map PSD justification to Universal IDM alignment
    # PSD: 0=left, 1=right, 2=center, 3=justify
    # Universal IDM: 0=left, 1=center, 2=right, 3=justify
    alignment_map = {
        0: 0,  # left
        1: 2,  # right
        2: 1,  # center
        3: 3,  # justify
    }

    return alignment_map.get(justification, 0)


def extract_all_text_layers(psd_path: str) -> list[dict[str, Any]]:
    """
    Extract all text layers from a PSD file

    Args:
        psd_path: Path to the PSD file

    Returns:
        List of dictionaries containing text layer data

    Raises:
        PSDTextExtractionError: If extraction fails
    """
    if not HAS_PSD_TOOLS:
        raise PSDTextExtractionError("psd-tools is not installed")

    try:
        # Open PSD file
        psd = cast(Any, PSDImage).open(psd_path)

        # Find all text layers
        text_layers: list[dict[str, Any]] = []

        def find_text_layers(layers, path=""):
            for layer in layers:
                layer_path = f"{path}/{layer.name}" if path else layer.name

                if hasattr(layer, "kind") and layer.kind == "type":
                    text_data = extract_text_data(layer)
                    text_layers.append(
                        {
                            "name": layer.name,
                            "path": layer_path,
                            "text": text_data["text"],
                            "font_details": text_data["font_details"],
                            "bbox": [layer.left, layer.top, layer.right, layer.bottom],
                        }
                    )

                if hasattr(layer, "layers"):
                    find_text_layers(layer.layers, layer_path)

        find_text_layers(psd)
        return text_layers

    except Exception as e:
        raise PSDTextExtractionError(f"Failed to extract text layers: {e!s}")


def check_psd_text_support() -> bool:
    """Check if PSD text extraction is supported"""
    return HAS_PSD_TOOLS
