"""
PSD content extraction module for the Multi-Format Document Engine.

This module provides functionality to extract content from PSD files
and convert it to the Universal IDM format.
"""

import hashlib
import logging
import os
from typing import Any

# Import psd-tools conditionally to handle cases where it's not installed
try:
    from psd_tools import PSDImage

    HAS_PSD_TOOLS = True
except ImportError:
    HAS_PSD_TOOLS = False

from pdfrebuilder.models.universal_idm import (
    BlendMode,
    BoundingBox,
    CanvasUnit,
    Color,
    DocumentMetadata,
    DrawingCommand,
    DrawingElement,
    FontDetails,
    ImageElement,
    Layer,
    LayerType,
    TextElement,
    UniversalDocument,
)

logger = logging.getLogger(__name__)


class PSDExtractionError(Exception):
    """Raised when PSD extraction fails"""


def _get_blend_mode(psd_blend_mode: str) -> BlendMode:
    """Convert PSD blend mode to Universal IDM blend mode"""
    blend_mode_map = {
        "normal": BlendMode.NORMAL,
        "multiply": BlendMode.MULTIPLY,
        "screen": BlendMode.SCREEN,
        "overlay": BlendMode.OVERLAY,
        "soft_light": BlendMode.SOFT_LIGHT,
        "hard_light": BlendMode.HARD_LIGHT,
        "color_dodge": BlendMode.COLOR_DODGE,
        "color_burn": BlendMode.COLOR_BURN,
        "darken": BlendMode.DARKEN,
        "lighten": BlendMode.LIGHTEN,
        "difference": BlendMode.DIFFERENCE,
        "exclusion": BlendMode.EXCLUSION,
        # These don't have direct equivalents in the Universal IDM
        "hue": BlendMode.NORMAL,
        "saturation": BlendMode.NORMAL,
        "color": BlendMode.NORMAL,
        "luminosity": BlendMode.NORMAL,
    }

    return blend_mode_map.get(psd_blend_mode, BlendMode.NORMAL)


def _get_layer_type(psd_layer: Any) -> LayerType:
    """Determine the layer type from a PSD layer"""
    if psd_layer.is_group():
        return LayerType.GROUP
    elif hasattr(psd_layer, "text_data") and psd_layer.text_data is not None:
        return LayerType.TEXT
    elif hasattr(psd_layer, "has_vector_mask") and psd_layer.has_vector_mask():
        return LayerType.SHAPE
    elif hasattr(psd_layer, "is_adjustment_layer") and psd_layer.is_adjustment_layer():
        return LayerType.ADJUSTMENT
    elif hasattr(psd_layer, "smart_object") and psd_layer.smart_object is not None:
        return LayerType.SMART_OBJECT
    else:
        return LayerType.PIXEL


def _extract_text_element(psd_layer: Any, element_id: str) -> TextElement:
    """Extract text element from a PSD text layer"""
    # Get text content
    text_data = psd_layer.text_data
    text = text_data.get("text", "") if text_data else ""

    # Get font details
    font_info = text_data.get("font", {}) if text_data else {}
    font_name = font_info.get("name", "Arial")
    font_size = font_info.get("size", 12)

    # Get color
    color_data = text_data.get("color", {}) if text_data else {}
    r = color_data.get("r", 0) / 255.0
    g = color_data.get("g", 0) / 255.0
    b = color_data.get("b", 0) / 255.0

    # Create font details
    font_details: FontDetails = FontDetails(
        name=font_name,
        size=font_size,
        color=Color(r, g, b),
        is_bold=font_info.get("bold", False),
        is_italic=font_info.get("italic", False),
    )

    # Get bounding box
    bbox = BoundingBox(psd_layer.left, psd_layer.top, psd_layer.right, psd_layer.bottom)

    # Create text element
    layer_index = getattr(psd_layer, "index", getattr(psd_layer, "_index", 0))
    return TextElement(
        id=element_id,
        bbox=bbox,
        raw_text=text,
        text=text,
        font_details=font_details,
        z_index=layer_index,
    )


def _extract_image_element(psd_layer: Any, element_id: str, image_dir: str) -> ImageElement:
    """Extract image element from a PSD pixel layer"""
    # Get image data
    image = psd_layer.composite()

    # Save image to file
    img_bytes = image.tobytes()
    # Replace MD5 with SHA-256 for more secure hashing
    img_hash = hashlib.sha256(img_bytes).hexdigest()
    path = os.path.join(image_dir, f"img_{img_hash[:8]}.png")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    image.save(path)

    # Get bounding box
    bbox = BoundingBox(psd_layer.left, psd_layer.top, psd_layer.right, psd_layer.bottom)

    # Create image element
    layer_index = getattr(psd_layer, "index", getattr(psd_layer, "_index", 0))
    return ImageElement(
        id=element_id,
        bbox=bbox,
        image_file=path,
        original_format="png",
        has_transparency=image.mode == "RGBA",
        z_index=layer_index,
    )


def _extract_shape_element(psd_layer: Any, element_id: str) -> DrawingElement:
    """Extract shape element from a PSD vector layer"""
    # Get vector mask
    vector_mask = psd_layer.vector_mask

    # Extract path data
    drawing_commands = []
    if vector_mask:
        for path in vector_mask.paths:
            # Convert path to drawing commands
            for i, point in enumerate(path):
                if i == 0:
                    # Move to first point
                    drawing_commands.append(DrawingCommand(cmd="M", pts=[point.anchor[0], point.anchor[1]]))
                else:
                    # Bezier curve to next point
                    drawing_commands.append(
                        DrawingCommand(
                            cmd="C",
                            pts=[
                                path[i - 1].leaving[0],
                                path[i - 1].leaving[1],
                                point.preceding[0],
                                point.preceding[1],
                                point.anchor[0],
                                point.anchor[1],
                            ],
                        )
                    )

            # Close path if it's closed
            if getattr(path, "is_closed", False):
                drawing_commands.append(DrawingCommand(cmd="H"))

    # Get fill and stroke
    fill_color = None
    stroke_color = None
    stroke_width = 0

    # Try to extract fill and stroke from layer effects
    if hasattr(psd_layer, "effects") and psd_layer.effects:
        for effect in psd_layer.effects:
            if effect.__class__.__name__ == "ColorOverlay":
                # Extract fill color
                if hasattr(effect, "color") and effect.color:
                    r, g, b = effect.color.rgb
                    fill_color = Color(r / 255.0, g / 255.0, b / 255.0)
            elif effect.__class__.__name__ == "Stroke":
                # Extract stroke
                if hasattr(effect, "color") and effect.color:
                    r, g, b = effect.color.rgb
                    stroke_color = Color(r / 255.0, g / 255.0, b / 255.0)
                if hasattr(effect, "size"):
                    stroke_width = effect.size

    # Get bounding box
    bbox = BoundingBox(psd_layer.left, psd_layer.top, psd_layer.right, psd_layer.bottom)

    # Create drawing element
    layer_index = getattr(psd_layer, "index", getattr(psd_layer, "_index", 0))
    return DrawingElement(
        id=element_id,
        bbox=bbox,
        color=stroke_color,
        fill=fill_color,
        width=stroke_width,
        drawing_commands=drawing_commands,
        z_index=layer_index,
    )


def _process_layer(psd_layer: Any, parent_id: str, element_counter: dict[str, int], image_dir: str) -> Layer:
    """Process a PSD layer and convert it to a Universal IDM layer"""
    # Generate layer ID
    layer_index = getattr(psd_layer, "index", getattr(psd_layer, "_index", 0))
    layer_id = f"{parent_id}_{psd_layer.name.replace(' ', '_')}_{layer_index}"

    # Determine layer type
    layer_type = _get_layer_type(psd_layer)

    # Get layer properties
    bbox = BoundingBox(psd_layer.left, psd_layer.top, psd_layer.right, psd_layer.bottom)

    # Create layer
    layer = Layer(
        layer_id=layer_id,
        layer_name=psd_layer.name,
        layer_type=layer_type,
        bbox=bbox,
        visibility=psd_layer.visible,
        opacity=psd_layer.opacity / 255.0,
        blend_mode=_get_blend_mode(psd_layer.blend_mode),
        children=[],
        content=[],
        clipping_mask=getattr(psd_layer, "clipping", False),
    )

    # Process children for group layers
    if layer_type == LayerType.GROUP:
        for child_layer in psd_layer:
            child = _process_layer(child_layer, layer_id, element_counter, image_dir)
            layer.children.append(child)
    else:
        # Process content based on layer type
        if layer_type == LayerType.TEXT:
            # Extract text element
            element_id = f"text_{element_counter['text']}"
            element_counter["text"] += 1
            text_element = _extract_text_element(psd_layer, element_id)
            layer.content.append(text_element)

        elif layer_type == LayerType.SHAPE:
            # Extract shape element
            element_id = f"drawing_{element_counter['drawing']}"
            element_counter["drawing"] += 1
            shape_element = _extract_shape_element(psd_layer, element_id)
            layer.content.append(shape_element)

        elif layer_type == LayerType.PIXEL:
            # Extract image element
            element_id = f"image_{element_counter['image']}"
            element_counter["image"] += 1
            image_element = _extract_image_element(psd_layer, element_id, image_dir)
            layer.content.append(image_element)

    return layer


def extract_psd_content(psd_path: str, extraction_flags: dict[str, bool] | None = None) -> UniversalDocument:
    """
    Extract content from a PSD file and convert it to the Universal IDM format

    Args:
        psd_path: Path to the PSD file
        extraction_flags: Optional flags to control extraction behavior

    Returns:
        UniversalDocument: Extracted document content

    Raises:
        PSDExtractionError: If extraction fails
    """
    if not HAS_PSD_TOOLS:
        raise PSDExtractionError("psd-tools is not installed. Please install it with 'pip install psd-tools'")

    if extraction_flags is None:
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
            "include_effects": True,
        }

    try:
        # Open PSD file
        psd = PSDImage.open(psd_path)

        # Create engine info dictionary (temporary solution until proper engine abstraction is implemented)
        engine_info = {
            "version": "1.0",
            "engine": "psd-tools",
            "engine_version": "1.0",  # TODO: Get actual version from psd-tools
        }

        # Create metadata
        metadata: DocumentMetadata = DocumentMetadata(
            format=f"PSD {psd.version}",
            creator="Adobe Photoshop",
            custom_properties={
                "color_mode": psd.color_mode.name,
                "channels": psd.channels,  # Store the int directly
                "depth": psd.depth,
            },
        )

        # Create document
        document = UniversalDocument(
            version=engine_info["version"],
            engine=engine_info["engine"],
            engine_version=engine_info["engine_version"],
            metadata=metadata,
            document_structure=[],
        )

        # Create canvas unit
        canvas = CanvasUnit(
            size=(psd.width, psd.height),
            canvas_name=os.path.basename(psd_path),
            background_color=None,  # Will be set if background layer is found
            layers=[],
        )

        # Element counter for generating unique IDs
        element_counter = {
            "text": 0,
            "image": 0,
            "drawing": 0,
        }

        # Process layers
        for psd_layer in psd:
            from pdfrebuilder.settings import get_config_value

            layer = _process_layer(
                psd_layer,
                "canvas",
                element_counter,
                get_config_value("image_dir") or "images",
            )
            canvas.layers.append(layer)

        # Add canvas to document
        document.document_structure.append(canvas)

        logger.info(f"✅ Extraction complete: PSD with {len(canvas.layers)} top-level layers processed")
        return document

    except Exception as e:
        raise PSDExtractionError(f"Failed to extract PSD content: {e!s}")


def check_psd_tools_availability() -> bool:
    """Check if psd-tools is available"""
    return HAS_PSD_TOOLS
