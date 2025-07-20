"""
PyMuPDF (fitz) PDF Engine Implementation

This module provides a PyMuPDF-based PDF rendering engine with fast rendering,
excellent vector graphics support, and good image handling capabilities.
"""

import logging
import os
import sys
from typing import Any

from pdfrebuilder.engine.pdf_rendering_engine import PDFRenderingEngine, RenderingError
from pdfrebuilder.models.universal_idm import Color

logger = logging.getLogger(__name__)


class PyMuPDFEngine(PDFRenderingEngine):
    """PyMuPDF-based PDF engine with fast rendering and vector graphics support."""

    engine_name = "pymupdf"
    engine_version = "unknown"  # Will be set during initialization
    supported_features = {
        "rotation": True,
        "images": True,
        "drawings": True,
        "text": True,
        "font_embedding": True,
        "transparency": True,
        "vector_graphics": True,
        "annotations": True,
        "overlay_mode": True,
    }

    def __init__(self):
        """Initialize the PyMuPDF engine."""
        super().__init__()
        self._current_doc = None
        self._font_cache = {}

    def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the engine with configuration."""
        # Import fitz here to avoid module-level import
        try:
            import fitz

            # Set version after successful import
            self.engine_version = fitz.version[0] if hasattr(fitz, "version") else fitz.__version__
        except ImportError as e:
            from pdfrebuilder.engine.engine_logger import EngineLogger

            EngineLogger.log_engine_error(self.engine_name, e, show_version=False)
            raise

        self._config = config
        self._initialized = True

        # Apply PyMuPDF-specific configuration
        self.overlay_mode = config.get("overlay_mode", False)
        self.annotation_mode = config.get("annotation_mode", "ignore")
        self.compression = config.get("compression", "flate")
        self.image_quality = config.get("image_quality", 85)
        self.text_rendering_mode = config.get("text_rendering_mode", "fill")
        self.anti_aliasing = config.get("anti_aliasing", True)
        self.optimize_for_web = config.get("optimize_for_web", False)

        # Log initialization using the new logging system
        self.log_initialization()

    def create_document(self, metadata: dict[str, Any]) -> Any:
        """Create a new PyMuPDF document."""
        try:
            import fitz

            doc = fitz.open()

            # Set metadata if provided
            if metadata:
                doc_metadata = {}
                for key, value in metadata.items():
                    if key in [
                        "title",
                        "author",
                        "subject",
                        "keywords",
                        "creator",
                        "producer",
                    ]:
                        doc_metadata[key] = str(value)

                if doc_metadata:
                    doc.set_metadata(doc_metadata)

            self._current_doc = doc
            return doc

        except Exception as e:
            raise RenderingError(f"Failed to create PyMuPDF document: {e!s}")

    def add_page(
        self,
        document: Any,
        size: tuple[float, float],
        background_color: Any | None = None,
    ) -> Any:
        """Add a new page to the document."""
        try:
            width, height = size
            page = document.new_page(width=width, height=height)

            # Set background color if provided
            if background_color is not None:
                color = self._convert_color(background_color)
                if color:
                    page.draw_rect(page.rect, fill=color)

            return page

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
                self._render_text_element(page, element, resources, result)
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
            # Apply optimization settings
            if self.optimize_for_web:
                document.save(output_path, garbage=4, deflate=True, clean=True)
            else:
                document.save(output_path)

            document.close()
            logger.info(f"PyMuPDF document saved to: {output_path}")

        except Exception as e:
            raise RenderingError(f"Failed to finalize document: {e!s}")

    def _render_text_element(
        self,
        page: Any,
        element: dict[str, Any],
        resources: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """Render a text element."""
        try:
            import fitz

            # Extract text properties
            text_content = element.get("text", "")
            font_details = element.get("font_details", {})
            bbox = element.get("bbox", [0, 0, 100, 20])

            # Convert bbox to fitz.Rect
            rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])

            # Get font properties
            font_name = font_details.get("name", "helv")
            font_size = font_details.get("size", 12)
            color = self._convert_color(font_details.get("color", [0, 0, 0]))

            # Map font name to PyMuPDF font
            fitz_font = self._get_fitz_font(font_name)

            # Render text
            page.insert_text(
                rect.tl,  # Top-left point
                text_content,
                fontname=fitz_font,
                fontsize=font_size,
                color=color,
            )

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
            import fitz

            image_file = element.get("image_file", "")
            bbox = element.get("bbox", [0, 0, 100, 100])

            if not image_file or not os.path.exists(image_file):
                result["warnings"].append(f"Image file not found: {image_file}")
                return

            # Convert bbox to fitz.Rect
            rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])

            # Insert image
            page.insert_image(rect, filename=image_file)

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
            import fitz

            drawing_commands = element.get("drawing_commands", [])
            bbox = element.get("bbox", [0, 0, 100, 100])
            stroke_color = self._convert_color(element.get("color"))
            fill_color = self._convert_color(element.get("fill"))
            width = element.get("width", 1.0)

            # Process drawing commands
            path = []
            for cmd in drawing_commands:
                cmd_type = cmd.get("cmd", "")
                pts = cmd.get("pts", [])

                if cmd_type == "M" and len(pts) >= 2:
                    # Move to
                    path.append(fitz.Point(pts[0], pts[1]))
                elif cmd_type == "L" and len(pts) >= 2:
                    # Line to
                    if path:
                        page.draw_line(
                            path[-1],
                            fitz.Point(pts[0], pts[1]),
                            color=stroke_color,
                            width=width,
                        )
                    path.append(fitz.Point(pts[0], pts[1]))
                elif cmd_type == "C" and len(pts) >= 6:
                    # Cubic Bezier curve - PyMuPDF doesn't have direct support
                    # We'll approximate with a line for now
                    if path:
                        page.draw_line(
                            path[-1],
                            fitz.Point(pts[4], pts[5]),
                            color=stroke_color,
                            width=width,
                        )
                    path.append(fitz.Point(pts[4], pts[5]))
                elif cmd_type == "rect":
                    # Rectangle
                    rect_bbox = cmd.get("bbox", bbox)
                    rect = fitz.Rect(rect_bbox[0], rect_bbox[1], rect_bbox[2], rect_bbox[3])
                    page.draw_rect(rect, color=stroke_color, fill=fill_color, width=width)
                elif cmd_type == "ellipse":
                    # Ellipse
                    ellipse_bbox = cmd.get("bbox", bbox)
                    rect = fitz.Rect(
                        ellipse_bbox[0],
                        ellipse_bbox[1],
                        ellipse_bbox[2],
                        ellipse_bbox[3],
                    )
                    page.draw_oval(rect, color=stroke_color, fill=fill_color, width=width)

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

    def _convert_color(self, color: Color | dict | list | int | None) -> tuple[float, float, float] | None:
        """Convert various color formats to PyMuPDF color tuple."""
        if color is None:
            return None

        if isinstance(color, Color):
            return (color.r, color.g, color.b)
        elif isinstance(color, dict):
            return (color.get("r", 0), color.get("g", 0), color.get("b", 0))
        elif isinstance(color, list) and len(color) >= 3:
            return (color[0], color[1], color[2])
        elif isinstance(color, int):
            # Convert integer color to RGB
            r = ((color >> 16) & 0xFF) / 255.0
            g = ((color >> 8) & 0xFF) / 255.0
            b = (color & 0xFF) / 255.0
            return (r, g, b)
        else:
            return (0, 0, 0)  # Default to black

    def _get_fitz_font(self, font_name: str) -> str:
        """Map font name to PyMuPDF font identifier."""
        # Cache font mappings
        if font_name in self._font_cache:
            return self._font_cache[font_name]

        # Common font mappings
        font_mappings = {
            "Arial": "helv",
            "Arial-Bold": "hebo",
            "Arial-Italic": "heit",
            "Arial-BoldItalic": "hebi",
            "Helvetica": "helv",
            "Helvetica-Bold": "hebo",
            "Helvetica-Oblique": "heit",
            "Helvetica-BoldOblique": "hebi",
            "Times-Roman": "tiro",
            "Times-Bold": "tibo",
            "Times-Italic": "tiit",
            "Times-BoldItalic": "tibi",
            "Courier": "cour",
            "Courier-Bold": "cobo",
            "Courier-Oblique": "coit",
            "Courier-BoldOblique": "cobi",
        }

        # Try exact match first
        if font_name in font_mappings:
            fitz_font = font_mappings[font_name]
        else:
            # Try to find a close match
            font_lower = font_name.lower()
            if "arial" in font_lower or "helvetica" in font_lower:
                if "bold" in font_lower and "italic" in font_lower:
                    fitz_font = "hebi"
                elif "bold" in font_lower:
                    fitz_font = "hebo"
                elif "italic" in font_lower or "oblique" in font_lower:
                    fitz_font = "heit"
                else:
                    fitz_font = "helv"
            elif "times" in font_lower:
                if "bold" in font_lower and "italic" in font_lower:
                    fitz_font = "tibi"
                elif "bold" in font_lower:
                    fitz_font = "tibo"
                elif "italic" in font_lower:
                    fitz_font = "tiit"
                else:
                    fitz_font = "tiro"
            elif "courier" in font_lower:
                if "bold" in font_lower and ("italic" in font_lower or "oblique" in font_lower):
                    fitz_font = "cobi"
                elif "bold" in font_lower:
                    fitz_font = "cobo"
                elif "italic" in font_lower or "oblique" in font_lower:
                    fitz_font = "coit"
                else:
                    fitz_font = "cour"
            else:
                # Default to Helvetica
                fitz_font = "helv"

        # Cache the result
        self._font_cache[font_name] = fitz_font
        return fitz_font

    def get_version_info(self) -> dict[str, Any]:
        """Get comprehensive version information for PyMuPDF engine."""
        try:
            import fitz

            return {
                "engine_name": self.engine_name,
                "engine_version": self.engine_version,
                "load_path": os.path.dirname(fitz.__file__),
                "python_executable": sys.executable,
                "fitz_version": (str(fitz.version) if hasattr(fitz, "version") else fitz.__version__),
            }
        except ImportError:
            return {
                "engine_name": self.engine_name,
                "engine_version": self.engine_version,
                "load_path": None,
                "python_executable": sys.executable,
                "fitz_version": "not available",
            }

    def get_engine_info(self) -> dict[str, Any]:
        """Get information about the PyMuPDF engine."""
        try:
            import fitz

            fitz_version = fitz.version
        except ImportError:
            fitz_version = "not available"

        return {
            "engine": self.engine_name,
            "version": self.engine_version,
            "supported_features": self.supported_features,
            "fitz_version": fitz_version,
            "config": self._config,
        }

    def extract(self, input_pdf_path: str) -> dict[str, Any]:
        """Extract content from PDF using PyMuPDF."""
        # This delegates to the existing extraction functionality
        from pdfrebuilder.engine.extract_pdf_content_fitz import extract_pdf_content

        return extract_pdf_content(input_pdf_path)

    def generate(
        self,
        config: dict[str, Any],
        output_pdf_path: str,
        original_pdf_for_template: str | None = None,
    ) -> None:
        """Generate PDF from universal JSON config using PyMuPDF."""
        from pdfrebuilder.engine.performance_metrics import measure_engine_performance

        with measure_engine_performance(self.engine_name, self.engine_version) as metrics:
            try:
                # Import fitz here for conditional usage
                import fitz

                # Create document
                metadata = config.get("metadata", {})
                document = self.create_document(metadata)

                # Process document structure
                document_structure = config.get("document_structure", [])

                page_count = 0
                element_count = 0

                for doc_unit in document_structure:
                    if doc_unit.get("type") != "page":
                        continue

                    page_count += 1

                    # Get page properties
                    page_size = doc_unit.get("size", [612, 792])  # Default letter size
                    background_color = doc_unit.get("page_background_color")

                    # Add page
                    page = self.add_page(document, page_size, background_color)

                    # Handle template overlay
                    if original_pdf_for_template and os.path.exists(original_pdf_for_template):
                        try:
                            template_doc = fitz.open(original_pdf_for_template)
                            page_idx = doc_unit.get("page_number", 0)
                            if page_idx < template_doc.page_count:
                                page.show_pdf_page(page.rect, template_doc, page_idx)
                            template_doc.close()
                        except Exception as e:
                            logger.warning(f"Could not apply template: {e}")
                            metrics["warnings"].append(f"Template error: {e}")

                    # Process layers
                    layers = doc_unit.get("layers", [])
                    for layer in layers:
                        if not layer.get("visibility", True):
                            continue

                        # Process layer content
                        content = layer.get("content", [])
                        element_count += len(content)
                        for element in content:
                            result = self.render_element(page, element, {})
                            if result.get("warnings"):
                                metrics["warnings"].extend(result["warnings"])

                # Update metrics
                metrics["page_count"] = page_count
                metrics["element_count"] = element_count

                # Finalize document
                self.finalize_document(document, output_pdf_path)

            except Exception as e:
                logger.error(f"Error generating PDF with PyMuPDF: {e}")
                raise RenderingError(f"PDF generation failed: {e!s}")

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate PyMuPDF-specific configuration."""
        result = super().validate_config(config)

        # Additional PyMuPDF-specific validations
        if "image_quality" in config:
            quality = config["image_quality"]
            if not isinstance(quality, int) or quality < 1 or quality > 100:
                result["valid"] = False
                result["errors"].append("image_quality must be an integer between 1 and 100")

        if "annotation_mode" in config:
            mode = config["annotation_mode"]
            if mode not in ["preserve", "ignore", "remove"]:
                result["valid"] = False
                result["errors"].append("annotation_mode must be 'preserve', 'ignore', or 'remove'")

        return result
