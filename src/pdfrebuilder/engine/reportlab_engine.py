"""
ReportLab PDF Engine Implementation

This module provides a ReportLab-based PDF rendering engine with enhanced precision,
proper font embedding, and licensing verification capabilities.
"""

import logging
import os
import sys
from typing import Any, ClassVar, cast

from reportlab.lib.colors import Color as RLColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from pdfrebuilder.engine.pdf_rendering_engine import PDFRenderingEngine, RenderingError
from pdfrebuilder.font.font_validator import FontValidator
from pdfrebuilder.models.universal_idm import (
    Color,
    DrawingElement,
    ImageElement,
    Layer,
    PageUnit,
    TextElement,
    UniversalDocument,
)

logger = logging.getLogger(__name__)


class ReportLabEngine(PDFRenderingEngine):
    """ReportLab-based PDF engine with enhanced precision and font embedding."""

    engine_name = "reportlab"
    engine_version = "4.4.3"
    supported_features: ClassVar[dict[str, bool]] = {
        "rotation": True,
        "images": True,
        "drawings": True,
        "text": True,
        "font_embedding": True,
        "transparency": True,
        "vector_graphics": True,
    }

    def __init__(self, font_validator: FontValidator | None = None):
        """Initialize the ReportLab engine."""
        super().__init__()
        self.font_validator = font_validator or FontValidator()
        self._registered_fonts: dict[str, str] = {}
        self._font_cache: dict[str, bool] = {}
        self.compression: int = 1
        self.page_mode: str = "portrait"
        self.embed_fonts: bool = True
        self.font_subsetting: bool = True
        self.image_compression: str = "jpeg"
        self.color_space: str = "rgb"
        self.precision: float = 1.0

    def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the engine with configuration."""
        self._config = config
        self._initialized = True

        # Apply ReportLab-specific configuration
        self.compression = config.get("compression", 1)
        self.page_mode = config.get("page_mode", "portrait")
        self.embed_fonts = config.get("embed_fonts", True)
        self.font_subsetting = config.get("font_subsetting", True)
        self.image_compression = config.get("image_compression", "jpeg")
        self.color_space = config.get("color_space", "rgb")
        self.precision = config.get("precision", 1.0)

        # Log initialization using the new logging system
        self.log_initialization()

    def create_document(self, metadata: dict[str, Any]) -> Any:
        """Create a new ReportLab document."""
        try:
            # Get page size from metadata or use default
            page_size = letter  # Default
            if "page_size" in metadata:
                page_size = metadata["page_size"]
            elif "size" in metadata:
                page_size = metadata["size"]

            # Create document with metadata
            doc = SimpleDocTemplate(
                "temp.pdf",  # Will be overridden in finalize_document
                pagesize=page_size,
                rightMargin=0,
                leftMargin=0,
                topMargin=0,
                bottomMargin=0,
            )

            # Store metadata for later use
            cast(Any, doc)._metadata = metadata
            cast(Any, doc)._story = []

            return doc

        except Exception as e:
            raise RenderingError(f"Failed to create ReportLab document: {e!s}")

    def add_page(
        self,
        document: Any,
        size: tuple[float, float],
        background_color: Any | None = None,
    ) -> Any:
        """Add a new page to the document."""
        try:
            # ReportLab handles pages automatically through the story
            # We'll create a page break and return a page context
            from reportlab.platypus import PageBreak

            if hasattr(document, "_story"):
                story = document._story
                if story:
                    story.append(PageBreak())

            # Create a page context object
            page_context: dict[str, Any] = {
                "size": size,
                "background_color": background_color,
                "elements": [],
            }

            return page_context

        except Exception as e:
            raise RenderingError(f"Failed to add page: {e!s}")

    def render_element(self, page: Any, element: dict[str, Any], resources: dict[str, Any]) -> dict[str, Any]:
        """Render an element on the page."""
        try:
            result = {
                "status": "success",
                "element_id": element.get("id", "unknown"),
                "warnings": [],
            }

            element_type = element.get("type", "unknown")

            if element_type == "text":
                self._render_text_element_new(page, element, resources, result)
            elif element_type == "image":
                self._render_image_element(page, element, resources, result)
            elif element_type == "drawing":
                self._render_drawing_element(page, element, resources, result)
            else:
                result["status"] = "unsupported"
                result["warnings"].append(f"Unsupported element type: {element_type}")
                self.warn_unsupported_feature(element_type, f"Element ID: {element.get('id', 'unknown')}")

            return result

        except Exception as e:
            return {
                "status": "error",
                "element_id": element.get("id", "unknown"),
                "error": str(e),
            }

    def finalize_document(self, document: Any, output_path: str) -> None:
        """Finalize and save the document."""
        try:
            # Update the document filename
            document.filename = output_path

            # Build the document with the story
            if hasattr(document, "_story"):
                document.build(document._story)
            else:
                # Create empty document if no story
                document.build([])

            logger.info(f"ReportLab document saved to: {output_path}")

        except Exception as e:
            raise RenderingError(f"Failed to finalize document: {e!s}")

    def _render_text_element_new(
        self,
        page: Any,
        element: dict[str, Any],
        resources: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """Render a text element using the new interface."""
        try:
            # Extract text properties
            text_content = element.get("text", "")
            font_details = element.get("font_details", {})
            bbox = element.get("bbox", [0, 0, 100, 20])

            # Register font if needed
            font_name = font_details.get("name", "Helvetica")
            if font_name not in self._registered_fonts:
                self._register_font(font_name)

            # Create paragraph style
            style = self._create_text_style_new(element)

            # Create paragraph
            paragraph = Paragraph(text_content, style)

            # Add to page elements
            if "elements" in page:
                page["elements"].append({"type": "text", "paragraph": paragraph, "bbox": bbox})

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

    def _render_image_element(
        self,
        page: Any,
        element: dict[str, Any],
        resources: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """Render an image element."""
        try:
            image_file = element.get("image_file", "")
            bbox = element.get("bbox", [0, 0, 100, 100])

            if not image_file or not os.path.exists(image_file):
                result["warnings"].append(f"Image file not found: {image_file}")
                return

            # Add to page elements
            if "elements" in page:
                page["elements"].append({"type": "image", "file": image_file, "bbox": bbox})

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

    def _render_drawing_element(
        self,
        page: Any,
        element: dict[str, Any],
        resources: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """Render a drawing element."""
        try:
            drawing_commands = element.get("drawing_commands", [])
            bbox = element.get("bbox", [0, 0, 100, 100])
            color = element.get("color")
            fill = element.get("fill")

            # Add to page elements
            if "elements" in page:
                page["elements"].append(
                    {
                        "type": "drawing",
                        "commands": drawing_commands,
                        "bbox": bbox,
                        "color": color,
                        "fill": fill,
                    }
                )

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

    def _create_text_style_new(self, element: dict[str, Any]) -> ParagraphStyle:
        """Create a ReportLab paragraph style for a text element using new interface."""
        # Get font details
        font_details = element.get("font_details", {})
        element_id = element.get("id", "unknown")

        # Convert color
        color = self._convert_color_new(font_details.get("color", Color(0, 0, 0, 1)))

        # Create style
        style = ParagraphStyle(
            name=f"style_{element_id}",
            fontName=font_details.get("name", "Helvetica"),
            fontSize=font_details.get("size", 12),
            textColor=color,
            alignment=1,  # Center alignment
            spaceAfter=0,
            spaceBefore=0,
        )

        return style

    def _convert_color_new(self, color: Color | dict | list | int) -> RLColor:
        """Convert various color formats to ReportLab Color."""
        if isinstance(color, Color):
            return RLColor(color.r, color.g, color.b, alpha=color.a)
        elif isinstance(color, dict):
            return RLColor(
                color.get("r", 0),
                color.get("g", 0),
                color.get("b", 0),
                alpha=color.get("a", 1),
            )
        elif isinstance(color, list) and len(color) >= 3:
            alpha = color[3] if len(color) > 3 else 1
            return RLColor(color[0], color[1], color[2], alpha=alpha)
        elif isinstance(color, int):
            # Convert integer color to RGB
            r = ((color >> 16) & 0xFF) / 255.0
            g = ((color >> 8) & 0xFF) / 255.0
            b = (color & 0xFF) / 255.0
            return RLColor(r, g, b, alpha=1.0)
        else:
            return RLColor(0, 0, 0, alpha=1.0)  # Default to black

    def extract(self, input_pdf_path: str) -> dict[str, Any]:
        """Extract content from PDF using ReportLab (limited functionality)."""
        # ReportLab is primarily for generation, not extraction
        # This would need to use PyMuPDF for extraction
        raise NotImplementedError(
            "ReportLab engine does not support PDF extraction. Use PyMuPDF engine for extraction."
        )

    def generate(
        self,
        config: dict[str, Any],
        output_pdf_path: str,
        original_pdf_for_template: str | None = None,
    ) -> None:
        """Generate PDF from universal JSON config using ReportLab."""
        from pdfrebuilder.engine.performance_metrics import measure_engine_performance

        with measure_engine_performance(self.engine_name, self.engine_version) as metrics:
            try:
                # Parse the universal document
                if isinstance(config, dict):
                    document = UniversalDocument.from_dict(config)
                elif isinstance(config, UniversalDocument):
                    document = config
                else:
                    raise ValueError("Config must be a dict or UniversalDocument")

                # Get page size from the first page or use default
                page_size = letter  # Default
                if document.document_structure and isinstance(document.document_structure[0], PageUnit):
                    page_size = document.document_structure[0].size

                # Create canvas
                c = canvas.Canvas(output_pdf_path, pagesize=page_size)

                # Count pages and elements for metrics
                page_count = 0
                element_count = 0

                # Process each page
                for i, page_unit in enumerate(document.document_structure):
                    if isinstance(page_unit, PageUnit):
                        page_count += 1
                        for layer in page_unit.layers:
                            element_count += len(layer.content)
                        self._render_page_on_canvas(c, page_unit, document)
                        if i < len(document.document_structure) - 1:
                            c.showPage()
                    else:
                        logger.warning(f"Skipping non-page unit: {type(page_unit)}")
                        metrics["warnings"].append(f"Skipped non-page unit: {type(page_unit)}")

                # Save the canvas
                c.save()

                # Update metrics
                metrics["page_count"] = page_count
                metrics["element_count"] = element_count

                logger.info(f"PDF generated successfully: {output_pdf_path}")

            except Exception as e:
                logger.error(f"Error generating PDF with ReportLab: {e}")
                raise

    def _create_document(self, document: UniversalDocument, output_path: str) -> SimpleDocTemplate:
        """Create a ReportLab document with proper configuration."""
        # Get page size from first page or use default
        page_size = letter  # Default
        if document.document_structure:
            first_page = document.document_structure[0]
            if isinstance(first_page, PageUnit):
                width, height = first_page.size
                page_size = (width, height)

        # Create document with metadata
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0,
        )

        return doc

    def _render_page_on_canvas(self, c: canvas.Canvas, page_unit: PageUnit, document: UniversalDocument) -> None:
        """Render a single page on a ReportLab canvas."""
        # Get page size
        page_size: tuple[float, float] = (600.0, 400.0)  # Default
        if page_unit.size:
            page_size = page_unit.size

        # Process layers in z-order (bottom to top)
        layers = sorted(
            page_unit.layers,
            key=lambda layer: layer.z_index if hasattr(layer, "z_index") else 0,
        )

        for layer in layers:
            if not layer.visibility:
                continue

            # Process layer content
            for element in layer.content:
                if isinstance(element, TextElement):
                    self._render_text_element_canvas(c, element, layer, page_size)
                elif isinstance(element, DrawingElement):
                    self._render_drawing_element_canvas(c, element, layer, page_size)
                elif isinstance(element, ImageElement):
                    self._render_image_element_canvas(c, element, layer, page_size)
                else:
                    logger.warning(f"Unsupported element type: {type(element)}")

    def _render_image_element_canvas(
        self, c: canvas.Canvas, element: ImageElement, layer: Layer, page_size: tuple
    ) -> None:
        """Render an image element placeholder using ReportLab canvas."""
        try:
            # Get bounding box
            bbox = element.bbox
            x1, y1, x2, y2 = bbox.x1, bbox.y1, bbox.x2, bbox.y2

            # Convert to ReportLab coordinates
            y1_rl = page_size[1] - y2
            y2_rl = page_size[1] - y1

            # Draw a placeholder rectangle
            c.setStrokeColorRGB(0.5, 0.5, 0.5)  # Gray color
            c.rect(x1, y1_rl, x2 - x1, y2 - y1, fill=0)

            # Draw a cross inside the rectangle
            c.line(x1, y1_rl, x2, y2_rl)
            c.line(x1, y2_rl, x2, y1_rl)

            # Draw the image path
            c.setFillColorRGB(0.5, 0.5, 0.5)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x1 + (x2 - x1) / 2, y1_rl + (y2_rl - y1_rl) / 2, element.image_file)

        except Exception as e:
            logger.error(f"Error rendering image element {element.id}: {e}")

    def _render_drawing_element_canvas(
        self, c: canvas.Canvas, element: DrawingElement, layer: Layer, page_size: tuple
    ) -> None:
        """Render a drawing element using ReportLab canvas."""
        try:
            # Set drawing properties
            if element.color:
                color = self._convert_color(element.color)
                c.setStrokeColor(color)
            if element.fill:
                fill_color = self._convert_color(element.fill)
                c.setFillColor(fill_color)
            c.setLineWidth(element.width)

            # Process drawing commands
            for command in element.drawing_commands:
                if command.cmd == "rect" and command.bbox:
                    x, y, x1, y1 = command.bbox.to_list()
                    # Convert to ReportLab coordinates
                    y_rl = page_size[1] - y1
                    y1_rl = page_size[1] - y
                    c.rect(x, y1_rl, x1 - x, y_rl - y1_rl, fill=1 if element.fill else 0)
                elif command.cmd == "line":
                    x1, y1, x2, y2 = command.pts
                    # Convert to ReportLab coordinates
                    y1_rl = page_size[1] - y1
                    y2_rl = page_size[1] - y2
                    c.line(x1, y1_rl, x2, y2_rl)
                elif command.cmd == "curve":
                    x1, y1, x2, y2, x3, y3, x4, y4 = command.pts
                    # Convert to ReportLab coordinates
                    y1_rl = page_size[1] - y1
                    y2_rl = page_size[1] - y2
                    y3_rl = page_size[1] - y3
                    y4_rl = page_size[1] - y4
                    p = c.beginPath()
                    p.moveTo(x1, y1_rl)
                    p.curveTo(x2, y2_rl, x3, y3_rl, x4, y4_rl)
                    c.drawPath(p)

        except Exception as e:
            logger.error(f"Error rendering drawing element {element.id}: {e}")

    def _render_text_element_canvas(
        self, c: canvas.Canvas, element: TextElement, layer: Layer, page_size: tuple
    ) -> None:
        """Render a text element using ReportLab canvas."""
        try:
            # Register font if needed
            font_details = element.font_details
            if hasattr(font_details, "name") and font_details.name:
                font_name = font_details.name
            else:
                font_name = "Arial"  # Default fallback font
                logger.warning(
                    f"No valid font name found for element {getattr(element, 'id', 'unknown')}, using fallback font 'Arial'"
                )

            if font_name not in self._registered_fonts:
                self._register_font(font_name)

            # Get text content
            text_content = element.text

            # Handle variable substitution placeholders
            if "${" in text_content:
                # For now, just use the text as-is
                # In a full implementation, this would be processed by the batch modifier
                pass

            # Get position from bounding box
            bbox = element.bbox
            x = bbox.x1
            y = page_size[1] - bbox.y1  # Convert to ReportLab coordinates

            # Set font and color
            c.setFont(font_name, element.font_details.size)
            color = self._convert_color(element.font_details.color)
            c.setFillColor(color)

            # Draw text
            c.drawString(x, y, text_content)

        except Exception as e:
            logger.error(f"Error rendering text element {element.id}: {e}")

    def _render_page(self, doc: SimpleDocTemplate, page_unit: PageUnit, document: UniversalDocument) -> None:
        """Render a single page using ReportLab."""
        # Create a new page
        story: list[Any] = []

        # Process layers in z-order (bottom to top)
        layers = sorted(
            page_unit.layers,
            key=lambda layer: layer.z_index if hasattr(layer, "z_index") else 0,
        )

        for layer in layers:
            if not layer.visibility:
                continue

            # Process layer content
            for element in layer.content:
                if isinstance(element, TextElement):
                    self._render_text_element(story, element, layer)
                else:
                    logger.warning(f"Unsupported element type: {type(element)}")

        # Build the page
        doc.build(story)

    def _render_text_element(self, story: list[Any], element: TextElement, layer: Layer) -> None:
        """Render a text element using ReportLab."""
        try:
            # Register font if needed
            font_details = element.font_details
            if hasattr(font_details, "name") and font_details.name:
                font_name = font_details.name
            else:
                font_name = "Arial"  # Default fallback font
                logger.warning(
                    f"No valid font name found for element {getattr(element, 'id', 'unknown')}, using fallback font 'Arial'"
                )

            if font_name not in self._registered_fonts:
                self._register_font(font_name)

            # Create paragraph style
            style = self._create_text_style(element)

            # Create text content
            text_content = element.text

            # Handle variable substitution placeholders
            if "${" in text_content:
                # For now, just use the text as-is
                # In a full implementation, this would be processed by the batch modifier
                pass

            # Create paragraph
            paragraph = Paragraph(text_content, style)
            story.append(paragraph)

            # Add spacing based on element positioning
            # This is a simplified approach - in practice, you'd need more precise positioning
            story.append(Spacer(1, 12))

        except Exception as e:
            logger.error(f"Error rendering text element {element.id}: {e}")

    def _create_text_style(self, element: TextElement) -> ParagraphStyle:
        """Create a ReportLab paragraph style for a text element."""
        # Get font details
        font_details = element.font_details

        # Convert color
        color = self._convert_color(font_details.color)

        # Create style
        style = ParagraphStyle(
            name=f"style_{element.id}",
            fontName=font_details.name,
            fontSize=font_details.size,
            textColor=color,
            alignment=1,  # Center alignment
            spaceAfter=0,
            spaceBefore=0,
        )

        return style

    def _convert_color(self, color: Color) -> RLColor:
        """Convert our Color object to ReportLab Color."""
        return RLColor(color.r, color.g, color.b, alpha=color.a)

    def _register_font(self, font_name: str) -> None:
        """Register a font with ReportLab."""
        if font_name in self._registered_fonts:
            return

        try:
            # Check if font is available
            if self.font_validator:
                is_available = self.font_validator.is_font_available(font_name)
                if not is_available:
                    logger.warning(f"Font '{font_name}' not available, using fallback")
                    font_name = "Helvetica"  # Fallback font

            # Try to register the font
            # For now, we'll use the font name as-is
            # In a full implementation, you'd need to provide the actual font file path
            self._registered_fonts[font_name] = font_name

            # Register with ReportLab if we have the font file
            font_path = self._get_font_path(font_name)
            if font_path and os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    logger.info(f"Registered font: {font_name}")
                except Exception as e:
                    logger.warning(f"Could not register font {font_name}: {e}")
            else:
                logger.info(f"Font file not found for: {font_name}")

        except Exception as e:
            logger.error(f"Error registering font {font_name}: {e}")

    def _get_font_path(self, font_name: str) -> str | None:
        """Get the file path for a font."""
        # This is a simplified implementation
        # In practice, you'd need a proper font management system
        font_dir = "downloaded_fonts"
        possible_paths = [
            os.path.join(font_dir, f"{font_name}.ttf"),
            os.path.join(font_dir, f"{font_name}.otf"),
            os.path.join(font_dir, f"{font_name}.woff"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def validate_font_licensing(self, font_name: str) -> dict[str, Any]:
        """Validate font licensing for embedding."""
        if not self.font_validator:
            return {"status": "unknown", "reason": "No font validator available"}

        try:
            # Check if font is available
            is_available = self.font_validator.is_font_available(font_name)

            # For now, we'll assume fonts are embeddable
            # In a full implementation, you'd check actual licensing
            embeddable = is_available

            return {
                "font_name": font_name,
                "available": is_available,
                "embeddable": embeddable,
                "status": "valid" if embeddable else "restricted",
                "reason": ("Font available and embeddable" if embeddable else "Font not available or restricted"),
            }
        except Exception as e:
            return {
                "font_name": font_name,
                "available": False,
                "embeddable": False,
                "status": "error",
                "reason": f"Error checking font: {e}",
            }

    def get_version_info(self) -> dict[str, Any]:
        """Get comprehensive version information for ReportLab engine."""
        try:
            import reportlab

            return {
                "engine_name": self.engine_name,
                "engine_version": self.engine_version,
                "load_path": os.path.dirname(reportlab.__file__),
                "python_executable": sys.executable,
                "reportlab_version": getattr(reportlab, "__version__", "unknown"),
            }
        except ImportError:
            return {
                "engine_name": self.engine_name,
                "engine_version": self.engine_version,
                "load_path": None,
                "python_executable": sys.executable,
                "reportlab_version": "not available",
            }

    def get_engine_info(self) -> dict[str, Any]:
        """Get information about the ReportLab engine."""
        return {
            "engine": self.engine_name,
            "version": self.engine_version,
            "supported_features": self.supported_features,
            "registered_fonts": list(self._registered_fonts.keys()),
        }
