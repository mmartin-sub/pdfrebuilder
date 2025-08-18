"""
Document rendering module for the Multi-Format Document Engine
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import fitz  # Only for Matrix and types; all I/O should use FitzPDFEngine
from PIL import Image
from psd_tools import PSDImage

logger = logging.getLogger(__name__)


class RenderingError(Exception):
    """Exception raised when document rendering fails"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class RenderConfig:
    """Configuration for document rendering"""

    def __init__(
        self,
        output_dpi: int = 300,
        output_format: str = "png",
        color_space: str = "RGB",
        compression_quality: int = 95,
        transparent_background: bool = False,
        page_numbers: list[int] | None = None,
    ):
        self.output_dpi = output_dpi
        self.output_format = output_format.lower()
        self.color_space = color_space
        self.compression_quality = compression_quality
        self.transparent_background = transparent_background
        self.page_numbers = page_numbers  # If None, render all pages


class RenderResult:
    """Result of a document rendering operation"""

    def __init__(
        self,
        success: bool,
        output_paths: list[str],
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.success = success
        self.output_paths = output_paths
        self.error_message = error_message
        self.metadata = metadata or {}


class DocumentRenderer(ABC):
    """Abstract base class for document renderers"""

    @abstractmethod
    def can_render(self, file_path: str) -> bool:
        """
        Check if this renderer can handle the given file

        Args:
            file_path: Path to the file to check

        Returns:
            True if this renderer can handle the file, False otherwise
        """

    @abstractmethod
    def render(
        self,
        file_path: str,
        output_dir: str,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """
        Render a document to high-resolution images

        Args:
            file_path: Path to the file to render
            output_dir: Directory to save rendered images to
            config: Optional rendering configuration

        Returns:
            RenderResult object containing rendering results
        """


class PDFRenderer(DocumentRenderer):
    """PDF document renderer using PyMuPDF (fitz)"""

    def can_render(self, file_path: str) -> bool:
        """Check if this renderer can handle the given file"""
        try:
            # Check file extension
            if file_path.lower().endswith(".pdf"):
                return True

            # Check magic bytes
            with open(file_path, "rb") as f:
                header = f.read(4)
                return header == b"%PDF"
        except Exception:
            return False

    def render(
        self,
        file_path: str,
        output_dir: str,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """Render a PDF document to high-resolution images"""
        if config is None:
            config = RenderConfig()

        output_paths = []

        try:
            # Open the PDF
            doc = fitz.open(file_path)

            # Determine which pages to render
            if config.page_numbers is None:
                page_numbers = list(range(len(doc)))
            else:
                page_numbers = [p for p in config.page_numbers if 0 <= p < len(doc)]

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Calculate zoom factor based on DPI (default PDF is 72 DPI)
            zoom = config.output_dpi / 72.0

            # Render each page
            for page_num in page_numbers:
                page: fitz.Page = doc.load_page(page_num)

                # Create a pixmap with appropriate colorspace
                if config.transparent_background and config.color_space == "RGBA":
                    # RGBA pixmap with transparent background
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=True)
                else:
                    # RGB pixmap with white background
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)

                # Determine output format and file extension
                if config.output_format == "png":
                    file_ext = "png"
                    save_args = {}
                elif config.output_format == "jpg" or config.output_format == "jpeg":
                    file_ext = "jpg"
                    save_args = {"jpg_quality": config.compression_quality}
                else:
                    file_ext = config.output_format
                    save_args = {}

                # Create output path
                output_path = os.path.join(output_dir, f"page_{page_num}.{file_ext}")

                # Save the pixmap
                pix.save(output_path, **save_args)
                output_paths.append(output_path)

                logger.info(f"Rendered page {page_num + 1}/{len(page_numbers)} to {output_path}")

            # Close the document
            doc.close()

            return RenderResult(
                success=True,
                output_paths=output_paths,
                metadata={
                    "page_count": len(page_numbers),
                    "dpi": config.output_dpi,
                    "format": config.output_format,
                },
            )

        except Exception as e:
            logger.error(f"Error rendering PDF: {e}")
            import traceback

            traceback.print_exc()

            return RenderResult(success=False, output_paths=output_paths, error_message=str(e))


class PSDRenderer(DocumentRenderer):
    """PSD document renderer using psd-tools and Pillow"""

    def can_render(self, file_path: str) -> bool:
        """Check if this renderer can handle the given file"""
        try:
            # Check file extension
            if file_path.lower().endswith(".psd"):
                return True

            # Check magic bytes
            with open(file_path, "rb") as f:
                header = f.read(4)
                return header == b"8BPS"
        except Exception:
            return False

    def render(
        self,
        file_path: str,
        output_dir: str,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """Render a PSD document to high-resolution images"""
        if config is None:
            config = RenderConfig()

        output_paths = []

        try:
            # Open the PSD
            psd = PSDImage.open(file_path)

            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Calculate scaling factor based on DPI
            # PSD files typically have a resolution defined in the file
            psd_dpi = getattr(psd, "resolution", 72)
            if isinstance(psd_dpi, tuple):
                psd_dpi = psd_dpi[0]  # Use horizontal DPI if it's a tuple

            scale = config.output_dpi / psd_dpi if psd_dpi > 0 else config.output_dpi / 72.0

            # Composite the PSD (flatten all visible layers)
            image = psd.composite()

            if image is None:
                logger.warning(f"PSD file has no visible layers to render: {file_path}")
                return RenderResult(success=True, output_paths=[], error_message="No visible layers to render.")

            # Resize if needed
            if scale != 1.0:
                new_width = int(image.width * scale)
                new_height = int(image.height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert color space if needed
            if image.mode != config.color_space:
                if config.color_space == "RGBA" and image.mode == "RGB":
                    # Add alpha channel
                    image = image.convert("RGBA")
                elif config.color_space == "RGB" and image.mode == "RGBA":
                    # Remove alpha channel
                    image = image.convert("RGB")
                else:
                    # General conversion
                    image = image.convert(config.color_space)

            # Determine output format and file extension
            if config.output_format == "png":
                file_ext = "png"
            elif config.output_format in ("jpg", "jpeg"):
                file_ext = "jpg"
            else:
                file_ext = config.output_format

            # Create output path
            output_path = os.path.join(output_dir, f"canvas.{file_ext}")

            # Save the image
            if config.output_format in ("jpg", "jpeg"):
                image.save(output_path, quality=config.compression_quality)
            else:
                image.save(output_path)
            output_paths.append(output_path)

            logger.info(f"Rendered PSD to {output_path}")

            return RenderResult(
                success=True,
                output_paths=output_paths,
                metadata={
                    "page_count": 1,  # PSD files are single-page
                    "dpi": config.output_dpi,
                    "format": config.output_format,
                    "original_size": (psd.width, psd.height),
                    "rendered_size": (image.width, image.height),
                },
            )

        except Exception as e:
            logger.error(f"Error rendering PSD: {e}")
            import traceback

            traceback.print_exc()

            return RenderResult(success=False, output_paths=output_paths, error_message=str(e))


class RendererRegistry:
    """Registry of document renderers"""

    def __init__(self):
        self.renderers = []

    def register(self, renderer: DocumentRenderer):
        """Register a renderer"""
        self.renderers.append(renderer)

    def get_renderer(self, file_path: str) -> DocumentRenderer | None:
        """Get a renderer that can handle the given file"""
        for renderer in self.renderers:
            if renderer.can_render(file_path):
                return renderer
        return None

    def render(
        self,
        file_path: str,
        output_dir: str,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """Render a document using an appropriate renderer"""
        renderer = self.get_renderer(file_path)
        if renderer:
            return renderer.render(file_path, output_dir, config)
        else:
            return RenderResult(
                success=False,
                output_paths=[],
                error_message=f"No renderer found for file: {file_path}",
            )


# Create and configure the renderer registry
def create_renderer_registry() -> RendererRegistry:
    """Create and configure the renderer registry"""
    registry = RendererRegistry()
    registry.register(PDFRenderer())
    registry.register(PSDRenderer())
    return registry


# Global renderer registry instance
renderer_registry = create_renderer_registry()


def render_document(
    document_structure: dict[str, Any],
    output_path: str,
    config: RenderConfig | None = None,
) -> RenderResult:
    """
    Render a document from its structure using an appropriate renderer

    Args:
        document_structure: Document structure dictionary
        output_path: Path to save the rendered document
        config: Optional rendering configuration

    Returns:
        RenderResult object containing rendering results

    Raises:
        RenderingError: If rendering fails or document structure is invalid
    """
    # Validate document structure
    if not isinstance(document_structure, dict):
        raise RenderingError("Invalid document structure: must be a dictionary")

    if "document_structure" not in document_structure:
        raise RenderingError("Invalid document structure: missing 'document_structure' field")

    try:
        # For now, we'll use a simple approach - this would be expanded based on the engine
        # specified in the document structure
        engine = document_structure.get("engine", "reportlab")

        if engine == "reportlab":
            # Use ReportLab renderer (placeholder)
            result = RenderResult(success=True, output_paths=[output_path], metadata={"engine": engine})
        elif engine == "fitz":
            # Use Fitz renderer (placeholder)
            result = RenderResult(success=True, output_paths=[output_path], metadata={"engine": engine})
        else:
            raise RenderingError(f"Unsupported rendering engine: {engine}")

        return result

    except Exception as e:
        if isinstance(e, RenderingError):
            raise
        raise RenderingError(f"Failed to render document: {e!s}", {"original_error": str(e)})
