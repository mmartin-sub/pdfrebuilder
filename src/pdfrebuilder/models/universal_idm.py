"""
Universal Intermediate Document Model (IDM) Schema v1.0

This module defines the comprehensive data structures for the Multi-Format Document Engine,
supporting both PDF and PSD formats with extensibility for future formats.
"""

import json
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, TypeVar, Union

# Schema version constant
UNIVERSAL_IDM_VERSION = "1.0"

# Type variables for better type hints
T = TypeVar("T")
ElementT = TypeVar("ElementT", bound="Element")


class DocumentType(Enum):
    """Document unit types for different formats"""

    PAGE = "page"  # PDF, Word, PowerPoint - discrete pages
    CANVAS = "canvas"  # PSD, Illustrator, Sketch - continuous design area


class LayerType(Enum):
    """Layer types for different content organization"""

    BASE = "base"  # PDF base layer containing all page content
    PIXEL = "pixel"  # PSD raster/bitmap layer
    TEXT = "text"  # PSD text layer
    SHAPE = "shape"  # PSD vector shape layer
    GROUP = "group"  # PSD group layer containing other layers
    ADJUSTMENT = "adjustment"  # PSD adjustment layer
    SMART_OBJECT = "smart_object"  # PSD smart object layer


class ElementType(Enum):
    """Element types for content within layers"""

    TEXT = "text"
    IMAGE = "image"
    DRAWING = "drawing"
    SHAPE = "shape"  # PSD-specific complex shapes


class BlendMode(Enum):
    """Standard blend modes supported across formats"""

    NORMAL = "Normal"
    MULTIPLY = "Multiply"
    SCREEN = "Screen"
    OVERLAY = "Overlay"
    SOFT_LIGHT = "Soft Light"
    HARD_LIGHT = "Hard Light"
    COLOR_DODGE = "Color Dodge"
    COLOR_BURN = "Color Burn"
    DARKEN = "Darken"
    LIGHTEN = "Lighten"
    DIFFERENCE = "Difference"
    EXCLUSION = "Exclusion"


@dataclass
class BoundingBox:
    """Standardized bounding box representation"""

    x1: float
    y1: float
    x2: float
    y2: float

    def to_list(self) -> list[float]:
        """Convert to list format for JSON serialization"""
        return [self.x1, self.y1, self.x2, self.y2]

    @classmethod
    def from_list(cls, bbox_list: list[float]) -> "BoundingBox":
        """Create from list format"""
        if len(bbox_list) != 4:
            raise ValueError(f"Bounding box must have exactly 4 values, got {len(bbox_list)}")
        return cls(*bbox_list)

    @property
    def width(self) -> float:
        return abs(self.x2 - self.x1)

    @property
    def height(self) -> float:
        return abs(self.y2 - self.y1)


@dataclass
class Color:
    """Universal color representation supporting multiple formats"""

    r: float
    g: float
    b: float
    a: float = 1.0

    def to_rgb_tuple(self) -> tuple[float, float, float]:
        """Convert to RGB tuple"""
        return (self.r, self.g, self.b)

    def to_rgba_tuple(self) -> tuple[float, float, float, float]:
        """Convert to RGBA tuple"""
        return (self.r, self.g, self.b, self.a)

    def to_hex(self) -> str:
        """Convert to hex string"""
        return f"#{int(self.r * 255):02x}{int(self.g * 255):02x}{int(self.b * 255):02x}"

    @classmethod
    def from_rgb_tuple(cls, rgb: tuple[float, float, float]) -> "Color":
        """Create from RGB tuple"""
        return cls(*rgb)

    @classmethod
    def from_rgba_tuple(cls, rgba: tuple[float, float, float, float]) -> "Color":
        """Create from RGBA tuple"""
        return cls(*rgba)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create from hex string"""
        hex_str = hex_str.lstrip("#")
        if len(hex_str) not in (3, 6, 8):
            raise ValueError(f"Invalid hex color: {hex_str}")

        # Expand shorthand notation
        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)

        # Parse RGB or RGBA
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            return cls(r, g, b)
        else:  # 8 characters (RGBA)
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            a = int(hex_str[6:8], 16) / 255.0
            return cls(r, g, b, a)

    @classmethod
    def from_int(cls, color_int: int) -> "Color":
        """Create from integer color value (RGB)"""
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return cls(r, g, b)


@dataclass
class FontDetails:
    """Comprehensive font information"""

    name: str
    size: float
    color: Color
    ascender: float = 0.0
    descender: float = 0.0
    is_superscript: bool = False
    is_italic: bool = False
    is_serif: bool = False
    is_monospaced: bool = False
    is_bold: bool = False
    original_flags: int = 0
    kerning: dict[str, float] | None = None
    leading: float | None = None
    tracking: float | None = None
    baseline_shift: float | None = None
    font_caps: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert FontDetails to a dictionary."""
        return {
            "name": self.name,
            "size": self.size,
            "color": self.color.to_rgba_tuple(),
            "ascender": self.ascender,
            "descender": self.descender,
            "is_superscript": self.is_superscript,
            "is_italic": self.is_italic,
            "is_serif": self.is_serif,
            "is_monospaced": self.is_monospaced,
            "is_bold": self.is_bold,
            "original_flags": self.original_flags,
            "kerning": self.kerning,
            "leading": self.leading,
            "tracking": self.tracking,
            "baseline_shift": self.baseline_shift,
            "font_caps": self.font_caps,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FontDetails":
        """Create FontDetails from a dictionary."""
        color_val = data.get("color")
        color_obj = Color(0, 0, 0)  # Default to black
        if isinstance(color_val, int):
            color_obj = Color.from_int(color_val)
        elif isinstance(color_val, list | tuple):
            if all(isinstance(c, int | float) for c in color_val):
                if len(color_val) == 4:
                    color_obj = Color.from_rgba_tuple(tuple(float(c) for c in color_val))
                elif len(color_val) == 3:
                    color_obj = Color.from_rgb_tuple(tuple(float(c) for c in color_val))

        return cls(
            name=data.get("name", "Arial"),
            size=data.get("size", 12),
            color=color_obj,
            ascender=data.get("ascender", 0.0),
            descender=data.get("descender", 0.0),
            is_superscript=data.get("is_superscript", False),
            is_italic=data.get("is_italic", False),
            is_serif=data.get("is_serif", False),
            is_monospaced=data.get("is_monospaced", False),
            is_bold=data.get("is_bold", False),
            original_flags=data.get("original_flags", 0),
            kerning=data.get("kerning"),
            leading=data.get("leading"),
            tracking=data.get("tracking"),
            baseline_shift=data.get("baseline_shift"),
            font_caps=data.get("font_caps"),
        )


@dataclass
class DrawingCommand:
    """Standardized drawing command"""

    cmd: str
    pts: list[float] = field(default_factory=list)
    bbox: Optional["BoundingBox"] = None


# Base Element Classes


class Element(ABC):
    """Base class for all document elements"""

    def __init__(self, id: str, bbox: Union["BoundingBox", list[float]], z_index: int = 0):
        self.id = id
        # Convert list to BoundingBox if needed
        if isinstance(bbox, list):
            self.bbox = BoundingBox.from_list(bbox)
        else:
            self.bbox = bbox
        self.z_index = z_index
        self.type: ElementType | None = None  # Will be set by subclasses

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert element to dictionary for serialization"""
        return {
            "id": self.id,
            "bbox": self.bbox.to_list() if hasattr(self.bbox, "to_list") else self.bbox,
            "z_index": self.z_index,
            "type": self.type.value if self.type else None,
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "Element":
        """Create element from dictionary"""


class TextElement(Element):
    """Text element with comprehensive formatting"""

    def __init__(
        self,
        id: str | None = None,
        bbox: BoundingBox | list[float] | None = None,
        raw_text: str | None = None,
        text: str | None = None,
        font_details: FontDetails | dict[str, Any] | None = None,
        z_index: int = 0,
        writing_mode: int = 0,
        writing_direction: tuple[float, float] = (1.0, 0.0),
        align: int = 0,
        adjust_spacing: bool = False,
        background_color: Color | None = None,
        element_id: str | None = None,
    ):
        # Handle backward compatibility for element_id parameter
        actual_id = element_id if element_id is not None else id
        if actual_id is None:
            raise ValueError("Either 'id' or 'element_id' parameter must be provided")

        # Handle bbox parameter - convert list to BoundingBox if needed
        if bbox is None:
            raise ValueError("bbox parameter is required")

        # Handle font_details - convert dict to FontDetails if needed
        if isinstance(font_details, dict):
            font_details = FontDetails.from_dict(font_details)
        elif font_details is None:
            # Create default font_details
            font_details = FontDetails(
                name="Arial",
                size=12,
                color=Color(0, 0, 0),
            )

        super().__init__(actual_id, bbox, z_index)
        self.type = ElementType.TEXT
        self.raw_text = raw_text or text or ""
        self.text = text or ""
        self.writing_mode = writing_mode
        self.writing_direction = writing_direction
        self.align = align
        self.adjust_spacing = adjust_spacing
        self.background_color = background_color
        self.element_id = actual_id  # For backward compatibility
        self._font_details = font_details

    @property
    def font_details(self) -> FontDetails:
        return self._font_details

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "text": self.text,
                "raw_text": self.raw_text,
                "writing_mode": self.writing_mode,
                "writing_direction": list(self.writing_direction),
                "align": self.align,
                "adjust_spacing": self.adjust_spacing,
                "background_color": (list(self.background_color.to_rgba_tuple()) if self.background_color else None),
                "font_details": self._font_details.to_dict(),
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TextElement":
        writing_direction_val = data.get("writing_direction", (1.0, 0.0))
        writing_direction_tuple = (
            (float(writing_direction_val[0]), float(writing_direction_val[1]))
            if isinstance(writing_direction_val, list | tuple) and len(writing_direction_val) == 2
            else (1.0, 0.0)
        )
        return cls(
            id=data["id"],
            bbox=data["bbox"],
            text=data.get("text", ""),
            raw_text=data.get("raw_text", ""),
            z_index=data.get("z_index", 0),
            writing_mode=data.get("writing_mode", 0),
            writing_direction=writing_direction_tuple,
            align=data.get("align", 0),
            adjust_spacing=data.get("adjust_spacing", False),
            background_color=(
                Color.from_rgba_tuple(tuple(data["background_color"])) if data.get("background_color") else None
            ),
            font_details=data.get("font_details"),
        )


class ImageElement(Element):
    """Image element with metadata"""

    def __init__(
        self,
        id: str | None = None,
        bbox: BoundingBox | list[float] | None = None,
        image_file: str | None = None,
        z_index: int = 0,
        original_format: str = "unknown",
        dpi: int = 72,
        color_space: str = "RGB",
        has_transparency: bool = False,
        transformation_matrix: list[float] | None = None,
        element_id: str | None = None,
    ):
        # Handle backward compatibility for element_id parameter
        actual_id = element_id if element_id is not None else id
        if actual_id is None:
            raise ValueError("Either 'id' or 'element_id' parameter must be provided")

        # Handle bbox parameter - convert list to BoundingBox if needed
        if bbox is None:
            raise ValueError("bbox parameter is required")

        if image_file is None:
            raise ValueError("image_file parameter is required")

        super().__init__(actual_id, bbox, z_index)
        self.type = ElementType.IMAGE
        self.image_file = image_file
        self.original_format = original_format
        self.dpi = dpi
        self.color_space = color_space
        self.has_transparency = has_transparency
        self.transformation_matrix = transformation_matrix
        self.element_id = actual_id  # For backward compatibility

        # Store the bbox list for backward compatibility
        self._bbox_list = self.bbox.to_list()

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        # Use the stored bbox list for serialization
        base_dict["bbox"] = self._bbox_list
        base_dict.update(
            {
                "image_file": self.image_file,
                "original_format": self.original_format,
                "dpi": self.dpi,
                "color_space": self.color_space,
                "has_transparency": self.has_transparency,
                "transformation_matrix": self.transformation_matrix,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImageElement":
        return cls(
            id=data["id"],
            bbox=data["bbox"],
            image_file=data["image_file"],
            z_index=data.get("z_index", 0),
            original_format=data.get("original_format", "unknown"),
            dpi=data.get("dpi", 72),
            color_space=data.get("color_space", "RGB"),
            has_transparency=data.get("has_transparency", False),
            transformation_matrix=data.get("transformation_matrix"),
        )


class DrawingElement(Element):
    """Drawing/vector element with comprehensive styling"""

    def __init__(
        self,
        id: str | None = None,
        bbox: BoundingBox | list[float] | None = None,
        z_index: int = 0,
        color: Color | list[float] | None = None,
        fill: Color | list[float] | None = None,
        width: float = 1.0,
        drawing_commands: list[DrawingCommand | dict[str, Any]] | None = None,
        original_shape_type: str | None = None,
        element_id: str | None = None,
    ):
        # Handle backward compatibility for element_id parameter
        actual_id = element_id if element_id is not None else id
        if actual_id is None:
            raise ValueError("Either 'id' or 'element_id' parameter must be provided")

        # Handle bbox parameter - convert list to BoundingBox if needed
        if bbox is None:
            raise ValueError("bbox parameter is required")

        # Handle color parameters - convert list to Color if needed
        if color is not None and isinstance(color, list | tuple):
            color_list = list(color[:3])
            # Ensure we have exactly 3 float values
            while len(color_list) < 3:
                color_list.append(0.0)
            color = Color.from_rgb_tuple((float(color_list[0]), float(color_list[1]), float(color_list[2])))

        if fill is not None and isinstance(fill, list | tuple):
            fill_list = list(fill[:3])
            # Ensure we have exactly 3 float values
            while len(fill_list) < 3:
                fill_list.append(0.0)
            fill = Color.from_rgb_tuple((float(fill_list[0]), float(fill_list[1]), float(fill_list[2])))

        # Process drawing commands
        processed_commands = []
        if drawing_commands:
            for cmd in drawing_commands:
                if isinstance(cmd, dict):
                    processed_commands.append(
                        DrawingCommand(
                            cmd=cmd["cmd"],
                            pts=cmd.get("pts", []),
                            bbox=(BoundingBox.from_list(cmd["bbox"]) if cmd.get("bbox") else None),
                        )
                    )
                else:
                    processed_commands.append(cmd)

        super().__init__(actual_id, bbox, z_index)
        self.type = ElementType.DRAWING
        self.color = color
        self.fill = fill
        self.width = width
        self.drawing_commands = processed_commands
        self.original_shape_type = original_shape_type
        self.element_id = actual_id  # For backward compatibility

        # Store the bbox list for backward compatibility
        self._bbox_list = self.bbox.to_list()

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        # Use the stored bbox list for serialization
        base_dict["bbox"] = self._bbox_list
        base_dict.update(
            {
                "color": list(self.color.to_rgb_tuple()) if self.color else None,
                "fill": list(self.fill.to_rgb_tuple()) if self.fill else None,
                "width": self.width,
                "drawing_commands": (
                    [
                        {
                            "cmd": cmd.cmd,
                            "pts": cmd.pts,
                            "bbox": cmd.bbox.to_list() if cmd.bbox else None,
                        }
                        for cmd in self.drawing_commands
                    ]
                    if self.drawing_commands
                    else []
                ),
                "original_shape_type": self.original_shape_type,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DrawingElement":
        return cls(
            id=data["id"],
            bbox=data["bbox"],
            z_index=data.get("z_index", 0),
            color=data.get("color"),
            fill=data.get("fill"),
            width=data.get("width", 1.0),
            drawing_commands=data.get("drawing_commands", []),
            original_shape_type=data.get("original_shape_type"),
        )


# Layer and Document Structure Classes


class Layer:
    """Universal layer representation"""

    def __init__(
        self,
        layer_id: str,
        layer_name: str,
        z_index: int = 0,
        bbox: BoundingBox | list[float] | None = None,
        layer_type: LayerType = LayerType.BASE,
        visibility: bool = True,
        opacity: float = 1.0,
        blend_mode: BlendMode = BlendMode.NORMAL,
        children: Sequence["Layer"] | None = None,
        content: Sequence[Element] | None = None,
        clipping_mask: bool = False,
        layer_effects: dict[str, Any] | None = None,
    ):
        # Handle bbox parameter - convert list to BoundingBox if needed
        if bbox is None:
            bbox = BoundingBox(0, 0, 0, 0)  # Default empty bbox
        elif isinstance(bbox, list):
            bbox = BoundingBox.from_list(bbox)

        self.layer_id = layer_id
        self.layer_name = layer_name
        self.z_index = z_index
        self.layer_type = layer_type
        self.bbox = bbox
        self.visibility = visibility
        self.opacity = opacity
        self.blend_mode = blend_mode
        self.children = list(children) if children is not None else []
        self.content: list[Element] = list(content) if content is not None else []
        self.clipping_mask = clipping_mask
        self.layer_effects = layer_effects or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_name": self.layer_name,
            "z_index": self.z_index,
            "layer_type": self.layer_type.value,
            "bbox": self.bbox.to_list() if hasattr(self.bbox, "to_list") else self.bbox,
            "visibility": self.visibility,
            "opacity": self.opacity,
            "blend_mode": self.blend_mode.value,
            "children": [child.to_dict() for child in self.children],
            "content": [item.to_dict() for item in self.content],
            "clipping_mask": self.clipping_mask,
            "layer_effects": self.layer_effects,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Layer":
        ELEMENT_TYPE_MAP: dict[str, type[Element]] = {
            "text": TextElement,
            "image": ImageElement,
            "drawing": DrawingElement,
        }
        content: list[Element] = []
        if "content" in data:
            for item_data in data["content"]:
                item_type = item_data.get("type")
                if item_type:
                    element_class = ELEMENT_TYPE_MAP.get(item_type)
                    if element_class:
                        content.append(element_class.from_dict(item_data))

        return cls(
            layer_id=data["layer_id"],
            layer_name=data["layer_name"],
            z_index=data.get("z_index", 0),
            bbox=data["bbox"],
            layer_type=LayerType(data["layer_type"]),
            visibility=data.get("visibility", True),
            opacity=data.get("opacity", 1.0),
            blend_mode=BlendMode(data.get("blend_mode", "Normal")),
            children=[Layer.from_dict(child) for child in data.get("children", [])],
            content=content,
            clipping_mask=data.get("clipping_mask", False),
            layer_effects=data.get("layer_effects"),
        )


class DocumentUnit(ABC):
    """Base class for document units (pages or canvas)"""

    def __init__(
        self,
        size: tuple[float, float],
        background_color: Color | None = None,
        layers: Sequence[Layer] | None = None,
    ):
        self.size = size
        self.background_color = background_color
        self.layers = list(layers) if layers is not None else []

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        return {
            "size": list(self.size),
            "background_color": (list(self.background_color.to_rgba_tuple()) if self.background_color else None),
            "layers": [layer.to_dict() for layer in self.layers],
        }


class PageUnit(DocumentUnit):
    """Page-based document unit (PDF, Word, etc.)"""

    def __init__(
        self,
        size: tuple[float, float],
        background_color: Color | None = None,
        layers: Sequence[Layer] | None = None,
        page_number: int = 0,
    ):
        super().__init__(size, background_color, layers)
        self.page_number = page_number

    @property
    def type(self) -> str:
        """Return the document type for this unit"""
        return DocumentType.PAGE.value

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "type": self.type,
                "page_number": self.page_number,
            }
        )
        return base_dict

    def add_layer(self, layer: Layer) -> None:
        """Add a layer to the page"""
        self.layers.append(layer)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PageUnit":
        size_val = data.get("size")
        size_tuple: tuple[float, float]
        if isinstance(size_val, list | tuple) and len(size_val) == 2:
            x, y = size_val
            size_tuple = (float(x), float(y))
        else:
            size_tuple = (612.0, 792.0)
        # This is a simplified version - you'll need to implement proper deserialization
        return cls(
            size=size_tuple,
            background_color=(
                Color.from_rgba_tuple(tuple(data["background_color"])) if data.get("background_color") else None
            ),
            layers=[Layer.from_dict(layer) for layer in data.get("layers", [])],
            page_number=data.get("page_number", 0),
        )


class CanvasUnit(DocumentUnit):
    """Canvas-based document unit (PSD, Illustrator, etc.)"""

    def __init__(
        self,
        size: tuple[float, float] | None = None,
        background_color: Color | None = None,
        layers: Sequence[Layer] | None = None,
        canvas_name: str = "Untitled",
        # Backward compatibility parameters
        canvas_size: tuple[float, float] | None = None,
    ):
        # Handle backward compatibility for canvas_size parameter
        actual_size = canvas_size if canvas_size is not None else size
        if actual_size is None:
            raise ValueError("Either 'size' or 'canvas_size' parameter must be provided")

        # Convert list to tuple if needed
        if isinstance(actual_size, list):
            actual_size = tuple(actual_size)

        super().__init__(actual_size, background_color, layers)
        self.canvas_name = canvas_name

        # Add canvas_size property for backward compatibility
        self.canvas_size = list(actual_size)

    @property
    def type(self) -> str:
        """Return the document type for this unit"""
        return DocumentType.CANVAS.value

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update(
            {
                "type": self.type,
                "canvas_name": self.canvas_name,
            }
        )
        return base_dict

    def add_layer(self, layer: Layer) -> None:
        """Add a layer to the canvas"""
        self.layers.append(layer)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanvasUnit":
        # This is a simplified version - you'll need to implement proper deserialization
        return cls(
            size=tuple(data["size"]) if "size" in data else None,
            canvas_size=(tuple(data["size"]) if "size" in data else None),  # For backward compatibility
            background_color=(
                Color.from_rgba_tuple(tuple(data["background_color"])) if data.get("background_color") else None
            ),
            layers=[Layer.from_dict(layer) for layer in data.get("layers", [])],
            canvas_name=data.get("canvas_name", "Untitled"),
        )


@dataclass
class DocumentMetadata:
    """Universal document metadata"""

    format: str = "unknown"
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    creation_date: str | None = None
    modification_date: str | None = None
    custom_properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "title": self.title,
            "author": self.author,
            "subject": self.subject,
            "keywords": self.keywords,
            "creator": self.creator,
            "producer": self.producer,
            "creation_date": self.creation_date,
            "modification_date": self.modification_date,
            "custom_properties": self.custom_properties,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        return cls(
            format=data.get("format", "unknown"),
            title=data.get("title"),
            author=data.get("author"),
            subject=data.get("subject"),
            keywords=data.get("keywords"),
            creator=data.get("creator"),
            producer=data.get("producer"),
            creation_date=data.get("creation_date"),
            modification_date=data.get("modification_date"),
            custom_properties=data.get("custom_properties", {}),
        )


class UniversalDocument:
    """Top-level Universal Document Model"""

    def __init__(
        self,
        version: str = UNIVERSAL_IDM_VERSION,
        engine: str = "unknown",
        engine_version: str = "unknown",
        metadata: DocumentMetadata | None = None,
        document_structure: Sequence[PageUnit | CanvasUnit] | None = None,
    ):
        self.version = version
        self.engine = engine
        self.engine_version = engine_version
        self.metadata = metadata or DocumentMetadata()
        self.document_structure: list[PageUnit | CanvasUnit] = (
            list(document_structure) if document_structure is not None else []
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the UniversalDocument to a dictionary representation for serialization."""
        return {
            "version": self.version,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "metadata": self.metadata.to_dict() if self.metadata else {},
            "document_structure": [unit.to_dict() for unit in self.document_structure],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UniversalDocument":
        doc_structure = []
        if "document_structure" in data:
            for unit_data in data["document_structure"]:
                unit_type = unit_data.get("type")
                if unit_type == DocumentType.PAGE.value:
                    doc_structure.append(PageUnit.from_dict(unit_data))
                elif unit_type == DocumentType.CANVAS.value:
                    doc_structure.append(CanvasUnit.from_dict(unit_data))

        return cls(
            version=data.get("version", UNIVERSAL_IDM_VERSION),
            engine=data.get("engine", "unknown"),
            engine_version=data.get("engine_version", "unknown"),
            metadata=DocumentMetadata.from_dict(data.get("metadata", {})),
            document_structure=doc_structure,
        )

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "UniversalDocument":
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))

    def add_document_unit(self, unit: PageUnit | CanvasUnit) -> None:
        """Add a document unit (page or canvas) to the document"""
        self.document_structure.append(unit)

    def get_pages(self) -> list[PageUnit]:
        """Get all page units from the document"""
        return [unit for unit in self.document_structure if isinstance(unit, PageUnit)]

    def get_canvases(self) -> list[CanvasUnit]:
        """Get all canvas units from the document"""
        return [unit for unit in self.document_structure if isinstance(unit, CanvasUnit)]


def validate_schema_version(data: dict[str, Any]) -> None:
    """Validate that the schema version is supported"""
    version = data.get("version", "1.0")
    if version != UNIVERSAL_IDM_VERSION:
        raise ValueError(f"Unsupported schema version: {version}")


def migrate_schema(data: dict[str, Any], target_version: str = UNIVERSAL_IDM_VERSION) -> dict[str, Any]:
    """Migrate schema to target version (placeholder for future migrations)"""
    # For now, just validate the version
    validate_schema_version(data)
    return data


# Aliases for backward compatibility with tests
Page = PageUnit
Canvas = CanvasUnit
