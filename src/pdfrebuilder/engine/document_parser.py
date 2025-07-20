"""
Universal document parser interface for the Multi-Format Document Engine.
This module provides a unified interface for parsing different document formats.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from pdfrebuilder.engine.extract_pdf_content_fitz import extract_pdf_content
from pdfrebuilder.models.universal_idm import UniversalDocument
from pdfrebuilder.tools import detect_file_format

logger = logging.getLogger(__name__)


class DocumentParsingError(Exception):
    """Exception raised when document parsing fails"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class AssetManifest:
    """Tracks extracted assets from a document"""

    def __init__(self):
        self.images = []
        self.fonts = []
        self.other_assets = []

    def add_image(
        self,
        path: str,
        original_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Add an image to the manifest"""
        self.images.append({"path": path, "original_name": original_name, "metadata": metadata or {}})

    def add_font(self, path: str, font_name: str, metadata: dict[str, Any] | None = None):
        """Add a font to the manifest"""
        self.fonts.append({"path": path, "font_name": font_name, "metadata": metadata or {}})

    def add_asset(self, path: str, asset_type: str, metadata: dict[str, Any] | None = None):
        """Add another type of asset to the manifest"""
        self.other_assets.append({"path": path, "asset_type": asset_type, "metadata": metadata or {}})

    def to_dict(self) -> dict[str, Any]:
        """Convert manifest to dictionary"""
        return {
            "images": self.images,
            "fonts": self.fonts,
            "other_assets": self.other_assets,
        }


class DocumentParser(ABC):
    """Abstract base class for document parsers"""

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""

    @abstractmethod
    def parse(self, file_path: str, extraction_flags: dict[str, bool] | None = None) -> UniversalDocument:
        """Parse document into Universal IDM"""

    @abstractmethod
    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        """Extract and save images, fonts, and other assets"""


class PDFParser(DocumentParser):
    """PDF document parser using PyMuPDF (fitz)"""

    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        if not os.path.exists(file_path):
            return False

        file_format = detect_file_format(file_path)
        return file_format == "pdf"

    def parse(self, file_path: str, extraction_flags: dict[str, bool] | None = None) -> UniversalDocument:
        """Parse PDF document into Universal IDM"""
        logger.info(f"Parsing PDF document: {file_path}")
        return extract_pdf_content(file_path, extraction_flags)

    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        """Extract and save images, fonts, and other assets from PDF"""
        # Note: For PDFs, asset extraction is currently handled within extract_pdf_content
        # This method is a placeholder for future enhancements
        manifest = AssetManifest()
        logger.info(f"Asset extraction for PDF is handled during parsing: {file_path}")
        return manifest


class PSDParser(DocumentParser):
    """PSD document parser using psd-tools"""

    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        if not os.path.exists(file_path):
            return False

        file_format = detect_file_format(file_path)
        return file_format == "psd"

    def parse(self, file_path: str, extraction_flags: dict[str, bool] | None = None) -> UniversalDocument:
        """Parse PSD document into Universal IDM"""
        try:
            # Import here to avoid dependency issues if psd-tools is not installed
            from pdfrebuilder.engine.extract_psd_content import check_psd_tools_availability, extract_psd_content

            # Check if psd-tools is available
            if not check_psd_tools_availability():
                raise NotImplementedError("psd-tools is not installed. Please install it with 'pip install psd-tools'")

            logger.info(f"Parsing PSD document: {file_path}")
            return extract_psd_content(file_path, extraction_flags)

        except ImportError:
            logger.error("Failed to import psd-tools or extract_psd_content module")
            raise NotImplementedError("PSD parsing is not available. Please ensure psd-tools is installed.")

    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        """Extract and save images, fonts, and other assets from PSD"""
        try:
            # Import here to avoid dependency issues if psd-tools is not installed
            from pdfrebuilder.engine.extract_psd_content import check_psd_tools_availability
            from pdfrebuilder.models.psd_validator import check_psd_compatibility

            # Check if psd-tools is available
            if not check_psd_tools_availability():
                raise NotImplementedError("psd-tools is not installed. Please install it with 'pip install psd-tools'")

            # Check PSD compatibility
            is_compatible, compatibility_info = check_psd_compatibility(file_path)
            if not is_compatible:
                issues = compatibility_info.get("issues", [])
                raise NotImplementedError(f"PSD file is not compatible: {', '.join(issues)}")

            # Create asset manifest
            manifest = AssetManifest()

            # For now, we'll extract assets during parsing
            # This method is a placeholder for future enhancements
            logger.info(f"Asset extraction for PSD is handled during parsing: {file_path}")

            return manifest

        except ImportError:
            logger.error("Failed to import psd-tools or related modules")
            raise NotImplementedError("PSD asset extraction is not available. Please ensure psd-tools is installed.")


class WandParser(DocumentParser):
    """Document parser using Python-Wand (ImageMagick binding) for PSD and layered image formats"""

    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        if not os.path.exists(file_path):
            return False

        file_format = detect_file_format(file_path)

        # Supported formats for Wand engine
        supported_formats = ["psd", "psb", "tiff", "tif", "xcf", "ai"]

        # Also support common image formats that might have layers
        image_formats = ["png", "jpg", "jpeg", "gif", "bmp", "svg"]

        return file_format.lower() in supported_formats + image_formats

    def parse(self, file_path: str, extraction_flags: dict[str, bool] | None = None) -> UniversalDocument:
        """Parse document into Universal IDM using Wand"""
        try:
            # Import here to avoid dependency issues if Wand is not installed
            from pdfrebuilder.engine.extract_wand_content import check_wand_availability, extract_wand_content

            # Check if Wand is available
            is_available, availability_info = check_wand_availability()
            if not is_available:
                error_msg = availability_info.get("error", "Wand is not available")
                install_info = availability_info.get("install_command", "pip install Wand")
                raise NotImplementedError(f"{error_msg}. Install with: {install_info}")

            logger.info(f"Parsing document with Wand: {file_path}")
            return extract_wand_content(file_path, extraction_flags)

        except ImportError:
            logger.error("Failed to import Wand or extract_wand_content module")
            raise NotImplementedError("Wand parsing is not available. Please ensure Python-Wand is installed.")

    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        """Extract and save images, fonts, and other assets using Wand"""
        try:
            # Import here to avoid dependency issues if Wand is not installed
            from pdfrebuilder.engine.extract_wand_content import check_wand_availability

            # Check if Wand is available
            is_available, availability_info = check_wand_availability()
            if not is_available:
                error_msg = availability_info.get("error", "Wand is not available")
                install_info = availability_info.get("install_command", "pip install Wand")
                raise NotImplementedError(f"{error_msg}. Install with: {install_info}")

            # Create asset manifest
            manifest = AssetManifest()

            # For now, we'll extract assets during parsing
            # This method is a placeholder for future enhancements
            logger.info(f"Asset extraction for Wand is handled during parsing: {file_path}")

            return manifest

        except ImportError:
            logger.error("Failed to import Wand or related modules")
            raise NotImplementedError("Wand asset extraction is not available. Please ensure Python-Wand is installed.")


# Registry of available parsers
_PARSERS = [
    PDFParser(),
    PSDParser(),
    WandParser(),
]


def get_parser_for_file(file_path: str) -> DocumentParser | None:
    """Get the appropriate parser for the given file"""
    for parser in _PARSERS:
        if parser.can_parse(file_path):
            return parser
    return None


def get_parser_by_engine(engine_name: str, file_path: str) -> DocumentParser | None:
    """
    Get a specific parser by engine name for the given file.

    Args:
        engine_name: Name of the engine ('fitz', 'psd-tools', 'wand', or 'auto')
        file_path: Path to the document file

    Returns:
        DocumentParser: The requested parser if available and compatible

    Raises:
        ValueError: If engine is not supported or not compatible with file
    """
    if engine_name == "auto":
        return get_parser_for_file(file_path)

    # Map engine names to parser classes
    engine_map: dict[str, type[PDFParser] | type[PSDParser] | type[WandParser]] = {
        "fitz": PDFParser,
        "psd-tools": PSDParser,
        "wand": WandParser,
    }

    if engine_name not in engine_map:
        available_engines = [*list(engine_map.keys()), "auto"]
        raise ValueError(f"Unsupported engine: {engine_name}. Available engines: {available_engines}")

    parser_class = engine_map[engine_name]
    parser = parser_class()

    # Check if the parser can handle this file
    if not parser.can_parse(file_path):
        file_format = detect_file_format(file_path)
        raise ValueError(f"Engine '{engine_name}' cannot parse file format '{file_format}': {file_path}")

    return parser


def parse_document(
    file_path: str,
    extraction_flags: dict[str, bool] | None = None,
    engine: str = "auto",
) -> UniversalDocument:
    """
    Parse a document using the specified or appropriate parser based on file format

    Args:
        file_path: Path to the document file
        extraction_flags: Optional flags to control extraction behavior
        engine: Engine to use ('auto', 'fitz', 'psd-tools', 'wand')

    Returns:
        UniversalDocument: Parsed document structure

    Raises:
        DocumentParsingError: If parsing fails or file is not found
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise DocumentParsingError(f"File not found: {file_path}")

    try:
        parser = get_parser_by_engine(engine, file_path)
        if parser is None:
            file_format = detect_file_format(file_path)
            if engine == "auto":
                raise DocumentParsingError(
                    f"Unsupported file format: {file_format}. Supported formats: PDF, PSD, and various image formats (via Wand)"
                )
            else:
                raise DocumentParsingError(f"No parser available for engine '{engine}' and file format '{file_format}'")

        return parser.parse(file_path, extraction_flags)

    except Exception as e:
        if isinstance(e, DocumentParsingError):
            raise
        raise DocumentParsingError(f"Failed to parse document: {e!s}", {"original_error": str(e)})
