"""
Wand-based document content extraction for PSD and layered image formats.

This module provides content extraction capabilities using Python-Wand (ImageMagick binding)
for processing PSD files and other layered image formats. It implements the Universal Document
Structure Schema (v1.0) for consistent output across different input engines.

Key Features:
- PSD layer extraction and hierarchy preservation
- Image processing with color profile management
- Optional OCR text extraction for rasterized text
- Memory-efficient processing for large documents
- Comprehensive error handling and dependency checking

Dependencies:
- Python-Wand: pip install Wand
- ImageMagick: System-level installation required
- Optional: Tesseract OCR for text extraction

Example:
    from pdfrebuilder.engine.extract_wand_content import extract_wand_content, check_wand_availability

    # Check if Wand is available
    is_available, info = check_wand_availability()
    if is_available:
        # Extract content from PSD file
        document = extract_wand_content("document.psd")
"""

import datetime
import hashlib
import logging
import os
from typing import Any

from pdfrebuilder.models.universal_idm import (
    BlendMode,
    BoundingBox,
    CanvasUnit,
    DocumentMetadata,
    ImageElement,
    Layer,
    LayerType,
    PageUnit,
    UniversalDocument,
)

logger = logging.getLogger(__name__)


def check_wand_availability() -> tuple[bool, dict[str, Any]]:
    """
    Check if Python-Wand and ImageMagick are available and return version information.

    Returns:
        Tuple[bool, Dict[str, Any]]: (is_available, info_dict)
            - is_available: True if both Wand and ImageMagick are working
            - info_dict: Contains version info on success, error info on failure

    Example:
        >>> is_available, info = check_wand_availability()
        >>> if is_available:
        ...     print(f"Wand version: {info['wand_version']}")
        >>> else:
        ...     print(f"Error: {info['error']}")
    """
    try:
        # Try to import Wand modules
        from wand.image import Image
        from wand.version import MAGICK_VERSION, VERSION

        # Test basic ImageMagick functionality
        with Image(width=1, height=1, background="white") as test_img:
            # Test basic operations to ensure ImageMagick is working
            test_img.format = "png"
            _ = test_img.quantum_range  # Access a property to verify functionality

        return True, {
            "wand_version": VERSION,
            "imagemagick_version": MAGICK_VERSION,
            "status": "available",
        }

    except ImportError as e:
        return False, {
            "error": "Python-Wand is not installed",
            "install_command": "pip install Wand",
            "additional_info": "You also need to install ImageMagick on your system.",
            "import_error": str(e),
            "installation_guide": {
                "windows": "https://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows",
                "macos": "brew install imagemagick",
                "ubuntu": "apt-get install libmagickwand-dev",
                "centos": "yum install ImageMagick-devel",
                "general": "https://imagemagick.org/script/download.php",
            },
        }

    except Exception as e:
        return False, {
            "error": str(e),
            "possible_cause": "ImageMagick may not be properly installed or configured",
            "installation_guide": {
                "windows": "https://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows",
                "macos": "brew install imagemagick",
                "ubuntu": "apt-get install libmagickwand-dev",
                "centos": "yum install ImageMagick-devel",
                "general": "https://imagemagick.org/script/download.php",
            },
            "troubleshooting": [
                "Verify ImageMagick is installed: 'magick -version' or 'convert -version'",
                "Check MAGICK_HOME environment variable",
                "Ensure ImageMagick libraries are in system PATH",
                "Try reinstalling both ImageMagick and Wand",
            ],
        }


def check_tesseract_availability() -> tuple[bool, dict[str, Any]]:
    """
    Check if Tesseract OCR is available for text extraction.

    Returns:
        Tuple[bool, Dict[str, Any]]: (is_available, info_dict)
    """
    try:
        import pytesseract

        # Try to get tesseract version using pytesseract
        version_info = pytesseract.get_tesseract_version()
        version_line = f"tesseract {version_info}"

        return True, {
            "tesseract_version": version_line,
            "status": "available",
        }

    except ImportError:
        return False, {
            "error": "pytesseract is not installed",
            "install_command": "pip install pytesseract",
            "additional_info": "You also need to install Tesseract OCR on your system.",
        }
    except Exception as e:
        return False, {
            "error": f"Tesseract OCR is not available: {e!s}",
            "install_command": {
                "windows": "Download from https://github.com/UB-Mannheim/tesseract/wiki",
                "macos": "brew install tesseract",
                "ubuntu": "apt-get install tesseract-ocr",
                "centos": "yum install tesseract",
            },
        }


def extract_wand_content(file_path: str, extraction_flags: dict[str, bool] | None = None) -> UniversalDocument:
    """
    Extract content from a PSD or layered image file using Python-Wand.

    Args:
        file_path: Path to the image file (PSD, PSB, TIFF, etc.)
        extraction_flags: Optional flags to control extraction behavior
            - include_text: Extract text layers (default: True)
            - include_images: Extract image layers (default: True)
            - include_drawings_non_background: Extract vector graphics (default: True)
            - include_raw_background_drawings: Extract background elements (default: False)

    Returns:
        UniversalDocument: Extracted document structure following Universal IDM schema

    Raises:
        ImportError: If Wand is not available
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is not supported
        RuntimeError: If extraction fails

    Example:
        >>> document = extract_wand_content("design.psd")
        >>> print(f"Extracted {len(document.document_structure)} canvas(es)")
    """
    # Check dependencies
    is_available, availability_info = check_wand_availability()
    if not is_available:
        error_msg = availability_info.get("error", "Wand is not available")
        install_info = availability_info.get("install_command", "pip install Wand")
        raise ImportError(f"{error_msg}. Install with: {install_info}")

    # Validate input file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Set default extraction flags
    if extraction_flags is None:
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings_non_background": True,
            "include_raw_background_drawings": False,
        }

    logger.info(f"Starting Wand extraction for: {file_path}")
    logger.debug(f"Extraction flags: {extraction_flags}")

    try:
        from wand.image import Image

        # Detect file format for format-specific handling
        file_format = _detect_image_format(file_path)
        logger.info(f"Detected format: {file_format}")

        # Extract document metadata and structure
        with Image(filename=file_path) as img:
            # Get basic document information
            metadata = _extract_document_metadata(img, file_path)

            # Create document structure based on format
            document_structure: list[PageUnit | CanvasUnit]
            if file_format.lower() == "tiff" and _is_multi_page_tiff(img):
                # Handle multi-page TIFF as separate pages
                _tiff_canvases: list[CanvasUnit] = _extract_multi_page_tiff(img, extraction_flags)
                document_structure = list(_tiff_canvases)
            else:
                # Handle as single canvas (PSD, single images, etc.)
                canvas = _create_canvas_structure(img, extraction_flags, file_format)
                document_structure = [canvas]

            # Create Universal Document
            document = UniversalDocument(
                version="1.0",
                engine="wand",
                engine_version=availability_info.get("wand_version", "unknown"),
                metadata=metadata,
                document_structure=document_structure,
            )

            logger.info(f"Successfully extracted content from {file_path}")
            return document

    except Exception as e:
        logger.error(f"Failed to extract content from {file_path}: {e!s}")
        raise RuntimeError(f"Wand extraction failed: {e!s}") from e


def _extract_document_metadata(img, file_path: str) -> DocumentMetadata:
    """Extract document metadata from Wand image object."""
    try:
        # Get basic image properties
        width, height = img.size
        format_name = img.format or "Unknown"

        # Initialize metadata dictionary with defaults
        metadata_dict = {
            "format": f"{format_name} (via Wand)",
            "title": os.path.splitext(os.path.basename(file_path))[0],
            "author": "",
            "subject": "",
            "keywords": "",
            "creator": "",
            "producer": "Python-Wand",
            "creation_date": "",
            "modification_date": "",
        }

        # Try to get file system metadata
        try:
            stat = os.stat(file_path)
            import datetime

            # Convert timestamps to PDF date format
            creation_time = datetime.datetime.fromtimestamp(stat.st_ctime)
            modification_time = datetime.datetime.fromtimestamp(stat.st_mtime)

            metadata_dict.update(
                {
                    "creation_date": creation_time.strftime("D:%Y%m%d%H%M%S+00'00'"),
                    "modification_date": modification_time.strftime("D:%Y%m%d%H%M%S+00'00'"),
                }
            )
        except Exception as e:
            logger.debug(f"Could not extract file system metadata: {e}")

        # Try to get image-specific metadata
        try:
            # Get image properties and artifacts
            if hasattr(img, "artifacts") and img.artifacts:
                artifacts = img.artifacts

                # Extract EXIF metadata if available
                metadata_dict.update(
                    {
                        "author": artifacts.get("exif:Artist", artifacts.get("exif:Copyright", "")),
                        "creator": artifacts.get("exif:Software", ""),
                        "subject": artifacts.get("exif:ImageDescription", ""),
                    }
                )

                # Try to get creation date from EXIF
                exif_date = artifacts.get("exif:DateTime", artifacts.get("exif:DateTimeOriginal", ""))
                if exif_date:
                    try:
                        # Convert EXIF date format to PDF date format
                        dt = datetime.datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")
                        metadata_dict["creation_date"] = dt.strftime("D:%Y%m%d%H%M%S+00'00'")
                    except ValueError:
                        logger.debug(f"Could not parse EXIF date: {exif_date}")

            # Try to get PSD-specific metadata if available
            if format_name.upper() in ["PSD", "PSB"]:
                metadata_dict = _extract_psd_specific_metadata(img, metadata_dict)

        except Exception as e:
            logger.debug(f"Could not extract extended metadata: {e}")

        # Try to get color profile information
        try:
            if hasattr(img, "color_profile") and img.color_profile:
                profile_info = f"Color Profile: {len(img.color_profile)} bytes"
                if metadata_dict["keywords"]:
                    metadata_dict["keywords"] += f", {profile_info}"
                else:
                    metadata_dict["keywords"] = profile_info
        except Exception as e:
            logger.debug(f"Could not extract color profile info: {e}")

        # Add image dimensions to keywords
        dimensions_info = f"Dimensions: {width}x{height}"
        if metadata_dict["keywords"]:
            metadata_dict["keywords"] += f", {dimensions_info}"
        else:
            metadata_dict["keywords"] = dimensions_info

        return DocumentMetadata.from_dict(metadata_dict)

    except Exception as e:
        logger.warning(f"Error extracting metadata: {e}")
        # Return minimal metadata
        return DocumentMetadata(
            format="Unknown",
            title=os.path.splitext(os.path.basename(file_path))[0],
            author="",
            subject="",
            keywords="",
            creator="",
            producer="Python-Wand",
            creation_date="",
            modification_date="",
        )


def _extract_psd_specific_metadata(img, metadata_dict: dict[str, Any]) -> dict[str, Any]:
    """Extract PSD-specific metadata from Wand image object."""
    try:
        # Try to get PSD-specific properties
        if hasattr(img, "artifacts") and img.artifacts:
            artifacts = img.artifacts

            # Look for Photoshop-specific metadata
            psd_keys = [
                "photoshop:AuthorsPosition",
                "photoshop:CaptionWriter",
                "photoshop:Category",
                "photoshop:City",
                "photoshop:Country",
                "photoshop:Credit",
                "photoshop:DateCreated",
                "photoshop:Headline",
                "photoshop:Instructions",
                "photoshop:Source",
                "photoshop:State",
                "photoshop:TransmissionReference",
                "photoshop:Urgency",
            ]

            psd_metadata = {}
            for key in psd_keys:
                if key in artifacts:
                    psd_metadata[key] = artifacts[key]

            # Update metadata with PSD-specific information
            if "photoshop:DateCreated" in psd_metadata:
                try:
                    # Try to parse Photoshop date format
                    date_str = psd_metadata["photoshop:DateCreated"]
                    # This might be in various formats, try common ones
                    for fmt in ["%Y-%m-%d", "%Y:%m:%d", "%m/%d/%Y"]:
                        try:
                            dt = datetime.datetime.strptime(date_str, fmt)
                            metadata_dict["creation_date"] = dt.strftime("D:%Y%m%d%H%M%S+00'00'")
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logger.debug(f"Could not parse Photoshop date: {e}")

            # Update other fields
            if "photoshop:Credit" in psd_metadata:
                metadata_dict["author"] = psd_metadata["photoshop:Credit"]
            if "photoshop:Headline" in psd_metadata:
                metadata_dict["subject"] = psd_metadata["photoshop:Headline"]

            # Add PSD-specific keywords
            psd_keywords = []
            for key, value in psd_metadata.items():
                if value and key not in [
                    "photoshop:DateCreated",
                    "photoshop:Credit",
                    "photoshop:Headline",
                ]:
                    clean_key = key.replace("photoshop:", "")
                    psd_keywords.append(f"{clean_key}: {value}")

            if psd_keywords:
                if metadata_dict["keywords"]:
                    metadata_dict["keywords"] += f", {', '.join(psd_keywords)}"
                else:
                    metadata_dict["keywords"] = ", ".join(psd_keywords)

        # Try to get layer count for PSD files
        try:
            if hasattr(img, "iterator_reset") and hasattr(img, "iterator_next"):
                img.iterator_reset()
                layer_count = 0
                while img.iterator_next():
                    layer_count += 1
                img.iterator_reset()  # Reset for future use

                if layer_count > 1:
                    layer_info = f"Layers: {layer_count}"
                    if metadata_dict["keywords"]:
                        metadata_dict["keywords"] += f", {layer_info}"
                    else:
                        metadata_dict["keywords"] = layer_info
        except Exception as e:
            logger.debug(f"Could not count layers: {e}")

    except Exception as e:
        logger.debug(f"Error extracting PSD-specific metadata: {e}")

    return metadata_dict


def _detect_image_format(file_path: str) -> str:
    """Detect the image format from file extension and content."""
    try:
        # Get format from file extension
        _, ext = os.path.splitext(file_path.lower())
        ext = ext.lstrip(".")

        # Map common extensions to formats
        format_map = {
            "jpg": "jpeg",
            "jpeg": "jpeg",
            "png": "png",
            "gif": "gif",
            "tif": "tiff",
            "tiff": "tiff",
            "psd": "psd",
            "psb": "psb",
            "bmp": "bmp",
            "svg": "svg",
            "xcf": "xcf",
            "ai": "ai",
        }

        return format_map.get(ext, ext or "unknown")

    except Exception as e:
        logger.debug(f"Error detecting format: {e}")
        return "unknown"


def _is_multi_page_tiff(img) -> bool:
    """Check if the TIFF image has multiple pages."""
    try:
        # Check if image has multiple frames/pages
        if hasattr(img, "iterator_reset") and hasattr(img, "iterator_next"):
            img.iterator_reset()
            page_count = 0

            while True:
                try:
                    current_page = img.iterator_next()
                    if not current_page:
                        break
                    page_count += 1
                    if page_count > 1:
                        img.iterator_reset()  # Reset for future use
                        return True
                except Exception:
                    break

            img.iterator_reset()  # Reset for future use

        return False

    except Exception as e:
        logger.debug(f"Error checking multi-page TIFF: {e}")
        return False


def _extract_multi_page_tiff(img, extraction_flags: dict[str, bool]) -> list[CanvasUnit]:
    """Extract multi-page TIFF as separate canvas units."""
    pages = []

    try:
        if hasattr(img, "iterator_reset") and hasattr(img, "iterator_next"):
            img.iterator_reset()
            page_index = 0

            while True:
                try:
                    current_page = img.iterator_next()
                    if not current_page:
                        break

                    # Create canvas for this page
                    width, height = img.size

                    # Create a single layer with the page content
                    bbox_obj = BoundingBox(0, 0, float(width), float(height))
                    page_layer = Layer(
                        layer_id=f"tiff_page_{page_index}_layer",
                        layer_name=f"TIFF Page {page_index + 1}",
                        layer_type=LayerType.BASE,
                        bbox=bbox_obj,
                        visibility=True,
                        opacity=1.0,
                        blend_mode=BlendMode.NORMAL,
                        children=[],
                        content=[],
                    )

                    # Extract the page as an image if requested
                    if extraction_flags.get("include_images", True):
                        image_element = _extract_tiff_page_as_image(img, page_index, bbox_obj.to_list())
                        if image_element:
                            page_layer.content.append(image_element)

                    # Create canvas for this page
                    canvas = CanvasUnit(
                        size=(float(width), float(height)),
                        layers=[page_layer],
                        canvas_name=f"TIFF Page {page_index + 1}",
                    )

                    pages.append(canvas)
                    page_index += 1

                except Exception as e:
                    logger.debug(f"Error processing TIFF page {page_index}: {e}")
                    break

            img.iterator_reset()  # Reset for future use

        logger.info(f"Extracted {len(pages)} pages from multi-page TIFF")
        return pages

    except Exception as e:
        logger.debug(f"Error extracting multi-page TIFF: {e}")
        return []


def _extract_tiff_page_as_image(img, page_index: int, bbox: list[float]) -> ImageElement | None:
    """Extract a TIFF page as an image element."""
    try:
        from pdfrebuilder.settings import get_config_value

        # Get configuration
        config = get_wand_config()
        image_format = config.get("image_format", "png")

        # Create output directory for images
        image_dir = get_config_value("image_dir")
        os.makedirs(image_dir, exist_ok=True)

        # Generate filename for this page
        import hashlib

        page_hash = hashlib.md5(f"tiff_page_{page_index}".encode(), usedforsecurity=False).hexdigest()[:8]
        image_filename = f"tiff_page_{page_index:03d}_{page_hash}.{image_format}"
        image_path = os.path.join(image_dir, image_filename)

        # Extract the current page as an image
        with img.clone() as page_img:
            # Set format and quality
            page_img.format = image_format
            if image_format.lower() in ["jpg", "jpeg"]:
                page_img.compression_quality = 90

            # Apply enhancements and optimizations
            _apply_image_enhancements(page_img, config)
            _apply_color_profile_management(page_img, config)
            _optimize_image_for_output(page_img, config)

            # Save the page image
            page_img.save(filename=image_path)

            # Get image properties
            width, height = page_img.size
            has_transparency = page_img.alpha_channel
            color_space = str(page_img.colorspace).upper()

            # Create image element
            image_element = ImageElement(
                id=f"tiff_page_{page_index}_{page_hash}",
                bbox=BoundingBox.from_list(bbox),
                image_file=os.path.relpath(image_path, "."),
                original_format=image_format.upper(),
                dpi=int(get_wand_config().get("density", 300)),
                color_space=color_space,
                has_transparency=bool(has_transparency),
                z_index=0,
            )

            logger.debug(f"Extracted TIFF page {page_index} as image: {image_path}")
            return image_element

    except Exception as e:
        logger.debug(f"Error extracting TIFF page {page_index} as image: {e}")
        return None


def _create_canvas_structure(img, extraction_flags: dict[str, bool], file_format: str = "unknown") -> CanvasUnit:
    """Create canvas structure from Wand image object."""
    width, height = img.size

    # Handle different formats differently
    if file_format.lower() in ["jpeg", "png", "gif", "bmp"]:
        # For single-layer image formats, create a simple structure
        layers = _create_single_image_structure(img, width, height, extraction_flags, file_format)
    else:
        # For layered formats (PSD, etc.), extract layers
        layers = _extract_layers_from_image(img, width, height, extraction_flags)

        # If no layers were extracted, create a base layer with the flattened image
        if not layers:
            base_layer = _create_base_layer_from_image(img, width, height, extraction_flags)
            layers = [base_layer]

    # Create canvas object
    canvas_name = f"Extracted {file_format.upper()}" if file_format != "unknown" else "Extracted Canvas"
    canvas = CanvasUnit(
        size=(float(width), float(height)),
        layers=layers,
        canvas_name=canvas_name,
    )

    logger.info(f"Created canvas structure: {width}x{height} with {len(layers)} layer(s)")
    return canvas


def _create_single_image_structure(
    img, width: int, height: int, extraction_flags: dict[str, bool], file_format: str
) -> list[Layer]:
    """Create a simple layer structure for single-layer image formats (JPEG, PNG, GIF, BMP)."""
    try:
        # Create a single base layer
        bbox_obj = BoundingBox(0, 0, float(width), float(height))
        base_layer = Layer(
            layer_id=f"{file_format.lower()}_base_layer",
            layer_name=f"{file_format.upper()} Image",
            layer_type=LayerType.BASE,
            bbox=bbox_obj,
            visibility=True,
            opacity=1.0,
            blend_mode=BlendMode.NORMAL,
            children=[],
            content=[],
        )

        # Extract the image content if requested
        if extraction_flags.get("include_images", True):
            image_element = _extract_single_image_content(img, file_format, bbox_obj.to_list())
            if image_element:
                base_layer.content.append(image_element)

        logger.debug(f"Created single image structure for {file_format}")
        return [base_layer]

    except Exception as e:
        logger.debug(f"Error creating single image structure: {e}")
        return []


def _extract_single_image_content(img, file_format: str, bbox: list[float]) -> ImageElement | None:
    """Extract content from a single-layer image format."""
    try:
        from pdfrebuilder.settings import get_config_value

        # Get configuration
        config = get_wand_config()
        output_format = config.get("image_format", "png")

        # Create output directory for images
        image_dir = get_config_value("image_dir")
        os.makedirs(image_dir, exist_ok=True)

        # Generate filename for the image
        import hashlib

        img_hash = hashlib.md5(f"{file_format}_image".encode(), usedforsecurity=False).hexdigest()[:8]
        image_filename = f"{file_format.lower()}_image_{img_hash}.{output_format}"
        image_path = os.path.join(image_dir, image_filename)

        # Extract the image
        with img.clone() as extracted_img:
            # Set output format and quality
            extracted_img.format = output_format
            if output_format.lower() in ["jpg", "jpeg"]:
                extracted_img.compression_quality = 90

            # Apply enhancements and optimizations
            _apply_image_enhancements(extracted_img, config)
            _apply_color_profile_management(extracted_img, config)
            _optimize_image_for_output(extracted_img, config)

            # Save the image
            extracted_img.save(filename=image_path)

            # Get image properties
            width, height = extracted_img.size
            has_transparency = extracted_img.alpha_channel
            color_space = str(extracted_img.colorspace).upper()

            # Create image element
            image_element = ImageElement(
                id=f"{file_format.lower()}_image_{img_hash}",
                bbox=BoundingBox.from_list(bbox),
                image_file=os.path.relpath(image_path, "."),
                original_format=file_format.upper(),
                dpi=int(get_wand_config().get("density", 300)),
                color_space=color_space,
                has_transparency=bool(has_transparency),
                z_index=0,
            )

            logger.debug(f"Extracted {file_format} image: {image_path}")
            return image_element

    except Exception as e:
        logger.debug(f"Error extracting {file_format} image: {e}")
        return None


def _extract_layers_from_image(img, width: int, height: int, extraction_flags: dict[str, bool]) -> list[Layer]:
    """Extract individual layers from a Wand image object."""
    layers = []

    try:
        # First, try to get layer information from image properties
        layer_info = _analyze_layer_structure(img)

        # Check if the image has multiple layers/frames
        if hasattr(img, "iterator_reset") and hasattr(img, "iterator_next"):
            img.iterator_reset()
            layer_index = 0

            # Iterate through all layers/frames
            while True:
                try:
                    current_layer = img.iterator_next()
                    if not current_layer:
                        break

                    # Get layer info for this specific layer
                    current_layer_info = layer_info.get(layer_index, {})

                    # Create layer object for this layer
                    layer = _create_layer_from_wand_layer(
                        img,
                        layer_index,
                        width,
                        height,
                        extraction_flags,
                        current_layer_info,
                    )
                    if layer:
                        layers.append(layer)

                    layer_index += 1

                except Exception as e:
                    logger.debug(f"Error processing layer {layer_index}: {e}")
                    break

            # Reset iterator
            img.iterator_reset()

        # If we found layers, organize them into hierarchy
        if layers:
            layers = _organize_layer_hierarchy(layers, layer_info)

    except Exception as e:
        logger.debug(f"Could not extract individual layers: {e}")

    return layers


def _analyze_layer_structure(img) -> dict[int, dict[str, Any]]:
    """Analyze the layer structure of the image to extract hierarchy information."""
    layer_info: dict[int, dict[str, Any]] = {}
    global_info: dict[str, Any] = {}

    try:
        # Try to get layer count and basic information
        if hasattr(img, "artifacts") and img.artifacts:
            artifacts = img.artifacts

            # Look for layer-related metadata with various formats
            layer_patterns = [
                "layer:",  # Standard format: layer:0:name
                "layer[",  # Bracket format: layer[0]:name
                "psd:layer:",  # PSD-specific: psd:layer:0:name
                "photoshop:layer:",  # Photoshop format
            ]

            for key, value in artifacts.items():
                for pattern in layer_patterns:
                    if key.startswith(pattern):
                        try:
                            # Extract layer index and property name
                            remainder = key[len(pattern) :]

                            if pattern == "layer[":
                                # Handle bracket format: layer[0]:name
                                if "]:" in remainder:
                                    layer_idx_str, property_name = remainder.split("]:")
                                    layer_idx = int(layer_idx_str)
                                else:
                                    continue
                            else:
                                # Handle colon format: layer:0:name
                                parts = remainder.split(":", 1)
                                if len(parts) >= 2:
                                    layer_idx = int(parts[0])
                                    property_name = parts[1]
                                else:
                                    continue

                            if layer_idx not in layer_info:
                                layer_info[layer_idx] = {}

                            layer_info[layer_idx][property_name] = value

                        except (ValueError, IndexError):
                            continue

            # Look for additional Photoshop-specific metadata
            photoshop_keys = [
                "photoshop:LayerCount",
                "photoshop:LayerNames",
                "photoshop:LayerOpacities",
                "photoshop:LayerVisibilities",
                "photoshop:LayerBlendModes",
            ]

            for key in photoshop_keys:
                if key in artifacts:
                    global_info[key] = artifacts[key]

        # Process global layer information if available
        if global_info:
            # Parse layer names if available as a list
            if "photoshop:LayerNames" in global_info:
                try:
                    names = global_info["photoshop:LayerNames"]
                    if isinstance(names, str):
                        # Try to parse as comma-separated or other formats
                        name_list = [name.strip() for name in names.split(",")]
                        for i, name in enumerate(name_list):
                            if i not in layer_info:
                                layer_info[i] = {}
                            layer_info[i]["name"] = name
                except Exception as e:
                    logger.debug(f"Error parsing layer names: {e}")

            # Parse layer opacities if available
            if "photoshop:LayerOpacities" in global_info:
                try:
                    opacities = global_info["photoshop:LayerOpacities"]
                    if isinstance(opacities, str):
                        opacity_list = [float(op.strip()) for op in opacities.split(",")]
                        for i, opacity in enumerate(opacity_list):
                            if i not in layer_info:
                                layer_info[i] = {}
                            layer_info[i]["opacity"] = opacity
                except Exception as e:
                    logger.debug(f"Error parsing layer opacities: {e}")

        # Enhance layer information with additional properties
        for layer_idx, info in layer_info.items():
            if isinstance(layer_idx, int):
                # Determine layer type based on available information
                layer_name = info.get("name", f"Layer {layer_idx + 1}")

                # Check for group indicators
                if any(keyword in layer_name.lower() for keyword in ["group", "folder", "set"]):
                    info["is_group"] = True
                    info["layer_type"] = "group"
                elif any(keyword in layer_name.lower() for keyword in ["text", "type"]):
                    info["is_group"] = False
                    info["layer_type"] = "text"
                elif any(keyword in layer_name.lower() for keyword in ["shape", "vector"]):
                    info["is_group"] = False
                    info["layer_type"] = "shape"
                else:
                    info["is_group"] = False
                    info["layer_type"] = "pixel"

                # Extract layer masks and clipping paths information
                if "mask" in info or any("mask" in key.lower() for key in info.keys()):
                    info["has_mask"] = True
                else:
                    info["has_mask"] = False

                if "clip" in info or any("clip" in key.lower() for key in info.keys()):
                    info["has_clipping_path"] = True
                else:
                    info["has_clipping_path"] = False

                # Extract layer effects information
                info["effects"] = _extract_layer_effects_from_info(info, artifacts)

                # Try to determine parent-child relationships
                if "parent" in info or "group" in info:
                    try:
                        parent_id = info.get("parent", info.get("group"))
                        if parent_id:
                            info["parent_layer"] = int(parent_id)
                    except (ValueError, TypeError):
                        pass

                # Extract positioning information if available
                position_keys = [
                    "x",
                    "y",
                    "left",
                    "top",
                    "right",
                    "bottom",
                    "width",
                    "height",
                ]
                position_info = {}
                for pos_key in position_keys:
                    if pos_key in info:
                        try:
                            position_info[pos_key] = float(info[pos_key])
                        except (ValueError, TypeError):
                            pass

                if position_info:
                    # Calculate bounding box if we have position information
                    if all(key in position_info for key in ["left", "top", "right", "bottom"]):
                        info["bounds"] = [
                            position_info["left"],
                            position_info["top"],
                            position_info["right"],
                            position_info["bottom"],
                        ]
                    elif all(key in position_info for key in ["x", "y", "width", "height"]):
                        info["bounds"] = [
                            position_info["x"],
                            position_info["y"],
                            position_info["x"] + position_info["width"],
                            position_info["y"] + position_info["height"],
                        ]

    except Exception as e:
        logger.debug(f"Error analyzing layer structure: {e}")

    return layer_info


def _extract_layer_effects_from_info(layer_info: dict[str, Any], artifacts: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract layer effects from layer information and image artifacts."""
    effects = []

    try:
        # Look for effect-related keys in layer info
        effect_keywords = [
            "dropshadow",
            "drop_shadow",
            "shadow",
            "innershadow",
            "inner_shadow",
            "outerglow",
            "outer_glow",
            "glow",
            "innerglow",
            "inner_glow",
            "bevel",
            "emboss",
            "stroke",
            "border",
            "coloroverlay",
            "color_overlay",
            "overlay",
            "gradientoverlay",
            "gradient_overlay",
            "patternoverlay",
            "pattern_overlay",
        ]

        # Check for effects in layer info
        for key, value in layer_info.items():
            key_lower = key.lower()

            for effect_keyword in effect_keywords:
                if effect_keyword in key_lower:
                    effect = _parse_effect_from_key_value(key, value, effect_keyword)
                    if effect:
                        effects.append(effect)
                    break

        # Look for Photoshop-specific effect metadata in artifacts
        if artifacts:
            for artifact_key, artifact_value in artifacts.items():
                if "effect" in artifact_key.lower() or "style" in artifact_key.lower():
                    effect = _parse_effect_from_artifact(artifact_key, artifact_value)
                    if effect:
                        effects.append(effect)

        # Remove duplicates based on effect type
        unique_effects = []
        seen_types = set()
        for effect in effects:
            effect_type = effect.get("type")
            if effect_type and effect_type not in seen_types:
                unique_effects.append(effect)
                seen_types.add(effect_type)

        return unique_effects

    except Exception as e:
        logger.debug(f"Error extracting layer effects: {e}")
        return []


def _parse_effect_from_key_value(key: str, value: Any, effect_keyword: str) -> dict[str, Any] | None:
    """Parse a layer effect from a key-value pair."""
    try:
        # Determine effect type based on keyword
        if "dropshadow" in effect_keyword or "drop_shadow" in effect_keyword:
            effect_type = "dropShadow"
        elif "innershadow" in effect_keyword or "inner_shadow" in effect_keyword:
            effect_type = "innerShadow"
        elif "outerglow" in effect_keyword or "outer_glow" in effect_keyword:
            effect_type = "outerGlow"
        elif "innerglow" in effect_keyword or "inner_glow" in effect_keyword:
            effect_type = "innerGlow"
        elif "bevel" in effect_keyword or "emboss" in effect_keyword:
            effect_type = "bevel"
        elif "stroke" in effect_keyword or "border" in effect_keyword:
            effect_type = "stroke"
        elif "coloroverlay" in effect_keyword or "color_overlay" in effect_keyword:
            effect_type = "colorOverlay"
        elif "gradientoverlay" in effect_keyword or "gradient_overlay" in effect_keyword:
            effect_type = "gradientOverlay"
        elif "patternoverlay" in effect_keyword or "pattern_overlay" in effect_keyword:
            effect_type = "patternOverlay"
        else:
            return None

        # Create basic effect structure
        effect = {
            "type": effect_type,
            "enabled": True,
            "blend_mode": "Normal",
            "opacity": 1.0,
        }

        # Try to parse value for additional properties
        if isinstance(value, str):
            # Try to parse structured data from string
            if value.lower() in ["true", "1", "yes", "on"]:
                effect["enabled"] = True
            elif value.lower() in ["false", "0", "no", "off"]:
                effect["enabled"] = False
            else:
                # Try to parse as JSON or structured format
                try:
                    import json

                    parsed_value = json.loads(value)
                    if isinstance(parsed_value, dict):
                        effect.update(parsed_value)
                except (json.JSONDecodeError, ValueError):
                    # Try to parse as comma-separated values
                    if "," in value:
                        parts = [part.strip() for part in value.split(",")]
                        # Common format: "enabled,opacity,color,size"
                        if len(parts) >= 2:
                            try:
                                effect["enabled"] = parts[0].lower() in [
                                    "true",
                                    "1",
                                    "yes",
                                    "on",
                                ]
                                effect["opacity"] = float(parts[1]) / 100.0 if float(parts[1]) > 1 else float(parts[1])
                            except (ValueError, IndexError):
                                pass
        elif isinstance(value, int | float):
            # Numeric value might be opacity or size
            if 0 <= value <= 1:
                effect["opacity"] = float(value)
            elif 0 <= value <= 100:
                effect["opacity"] = float(value) / 100.0
            else:
                effect["size"] = float(value)
        elif isinstance(value, dict):
            # Direct dictionary update
            effect.update(value)

        # Add effect-specific default properties
        if effect_type in ["dropShadow", "innerShadow"]:
            effect.setdefault("color", [0, 0, 0, 1])  # Black
            effect.setdefault("angle", 120.0)
            effect.setdefault("distance", 5.0)
            effect.setdefault("size", 5.0)
        elif effect_type in ["outerGlow", "innerGlow"]:
            effect.setdefault("color", [1, 1, 0, 1])  # Yellow
            effect.setdefault("size", 5.0)
        elif effect_type == "bevel":
            effect.setdefault("style", "outer_bevel")
            effect.setdefault("depth", 100.0)
            effect.setdefault("size", 5.0)
            effect.setdefault("angle", 120.0)
        elif effect_type == "stroke":
            effect.setdefault("color", [0, 0, 0, 1])  # Black
            effect.setdefault("size", 3.0)
            effect.setdefault("position", "outside")
        elif effect_type == "colorOverlay":
            effect.setdefault("color", [1, 0, 0, 1])  # Red

        return effect

    except Exception as e:
        logger.debug(f"Error parsing effect from key-value: {e}")
        return None


def _parse_effect_from_artifact(artifact_key: str, artifact_value: Any) -> dict[str, Any] | None:
    """Parse a layer effect from an image artifact."""
    try:
        # This is a simplified parser for Photoshop-style effect metadata
        # In practice, this would need to handle the complex binary format
        # of Photoshop layer effects

        key_lower = artifact_key.lower()

        # Look for common effect patterns in artifact keys
        if "dropshadow" in key_lower:
            return {
                "type": "dropShadow",
                "enabled": True,
                "blend_mode": "Multiply",
                "color": [0, 0, 0, 1],
                "opacity": 0.75,
                "angle": 120.0,
                "distance": 5.0,
                "size": 5.0,
            }
        elif "innershadow" in key_lower:
            return {
                "type": "innerShadow",
                "enabled": True,
                "blend_mode": "Multiply",
                "color": [0, 0, 0, 1],
                "opacity": 0.75,
                "angle": 120.0,
                "distance": 5.0,
                "size": 5.0,
            }
        elif "glow" in key_lower:
            glow_type = "outerGlow" if "outer" in key_lower else "innerGlow"
            return {
                "type": glow_type,
                "enabled": True,
                "blend_mode": "Screen",
                "color": [1, 1, 0, 1],
                "opacity": 0.75,
                "size": 5.0,
            }
        elif "bevel" in key_lower or "emboss" in key_lower:
            return {
                "type": "bevel",
                "enabled": True,
                "style": "outer_bevel",
                "depth": 100.0,
                "size": 5.0,
                "angle": 120.0,
                "highlight_mode": "Screen",
                "shadow_mode": "Multiply",
            }
        elif "stroke" in key_lower:
            return {
                "type": "stroke",
                "enabled": True,
                "blend_mode": "Normal",
                "color": [0, 0, 0, 1],
                "opacity": 1.0,
                "size": 3.0,
                "position": "outside",
            }

        return None

    except Exception as e:
        logger.debug(f"Error parsing effect from artifact: {e}")
        return None


def _extract_layer_as_image(
    img,
    layer_index: int,
    layer_id: str,
    layer_bbox: list[float],
    layer_info: dict[str, Any] | None = None,
) -> ImageElement | None:
    """Extract a layer as an image element."""
    try:
        from pdfrebuilder.settings import get_config_value

        if layer_info is None:
            layer_info = {}

        # Get configuration
        config = get_wand_config()
        image_format = config.get("image_format", "png")

        # Create output directory for images
        image_dir = get_config_value("image_dir")
        os.makedirs(image_dir, exist_ok=True)

        # Generate consistent filename for this layer
        image_filename = _generate_consistent_image_filename(layer_id, layer_index, image_format, "layer")
        image_path = os.path.join(image_dir, image_filename)

        # Try to extract the current layer as an image
        try:
            # Create a copy of the current layer
            with img.clone() as layer_img:
                # Set format and quality
                layer_img.format = image_format
                if image_format.lower() in ["jpg", "jpeg"]:
                    layer_img.compression_quality = 90

                # Apply image enhancements and color management
                _apply_image_enhancements(layer_img, config)
                _apply_color_profile_management(layer_img, config)
                _optimize_image_for_output(layer_img, config)

                # Save the layer image
                layer_img.save(filename=image_path)

                # Get image properties
                width, height = layer_img.size
                has_transparency = layer_img.alpha_channel
                color_space = str(layer_img.colorspace).upper()

                # Create image element
                image_element = ImageElement(
                    id=f"image_{layer_index}_{os.path.splitext(image_filename)[0]}",
                    bbox=BoundingBox.from_list(layer_bbox),
                    image_file=os.path.relpath(image_path, "."),
                    original_format=image_format.upper(),
                    dpi=int(get_wand_config().get("density", 300)),
                    color_space=color_space,
                    has_transparency=bool(has_transparency),
                    z_index=layer_index,
                )

                # Add transformation matrix if available
                if "transform" in layer_info or "transformation" in layer_info:
                    transform_data = layer_info.get("transform", layer_info.get("transformation"))
                    if transform_data and isinstance(transform_data, list | tuple) and len(transform_data) >= 6:
                        image_element.transformation_matrix = list(transform_data)

                logger.debug(f"Extracted layer {layer_index} as image: {image_path}")
                return image_element

        except Exception as e:
            logger.debug(f"Could not extract layer {layer_index} as image: {e}")

            # Fallback: try to extract the entire image and crop to layer bounds
            try:
                with img.clone() as fallback_img:
                    # Crop to layer bounds if they're reasonable
                    img_width, img_height = fallback_img.size
                    x1, y1, x2, y2 = layer_bbox

                    # Validate bounds
                    if 0 <= x1 < x2 <= img_width and 0 <= y1 < y2 <= img_height and x2 - x1 > 1 and y2 - y1 > 1:
                        # Crop to layer bounds
                        fallback_img.crop(int(x1), int(y1), int(x2), int(y2))

                    # Set format and save
                    fallback_img.format = image_format
                    if image_format.lower() in ["jpg", "jpeg"]:
                        fallback_img.compression_quality = 90

                    fallback_img.save(filename=image_path)

                    # Get properties
                    width, height = fallback_img.size
                    has_transparency = fallback_img.alpha_channel
                    color_space = str(fallback_img.colorspace).upper()

                    # Create image element
                    # Generate a simple hash for the layer (not for security purposes)
                    layer_hash = hashlib.md5(
                        f"layer_{layer_index}_{layer_bbox}".encode(),
                        usedforsecurity=False,
                    ).hexdigest()[:8]

                    image_element = ImageElement(
                        id=f"image_{layer_index}_{layer_hash}",
                        bbox=BoundingBox.from_list(layer_bbox),
                        image_file=os.path.relpath(image_path, "."),
                        original_format=image_format.upper(),
                        dpi=int(get_wand_config().get("density", 300)),
                        color_space=color_space,
                        has_transparency=bool(has_transparency),
                        z_index=layer_index,
                    )

                    logger.debug(f"Extracted layer {layer_index} as fallback image: {image_path}")
                    return image_element

            except Exception as fallback_error:
                logger.debug(f"Fallback image extraction also failed for layer {layer_index}: {fallback_error}")

        return None

    except Exception as e:
        logger.debug(f"Error extracting layer {layer_index} as image: {e}")
        return None


def _organize_layer_hierarchy(layers: list[Layer], layer_info: dict[int, dict[str, Any]]) -> list[Layer]:
    """Organize layers into a proper hierarchy based on parent-child relationships."""
    try:
        # Create a mapping of layer index to layer object
        layer_map = dict(enumerate(layers))
        root_layers = []

        # Process each layer to establish hierarchy
        for i, layer in enumerate(layers):
            layer_data = layer_info.get(i, {})
            parent_idx = layer_data.get("parent_layer")

            if parent_idx is not None and parent_idx in layer_map:
                # This layer has a parent, add it as a child
                parent_layer = layer_map[parent_idx]
                parent_layer.children.append(layer)

                # Update parent layer type if it has children
                if parent_layer.layer_type != LayerType.GROUP:
                    parent_layer.layer_type = LayerType.GROUP
            else:
                # This is a root layer
                root_layers.append(layer)

        return root_layers if root_layers else layers

    except Exception as e:
        logger.debug(f"Error organizing layer hierarchy: {e}")
        return layers


def _create_layer_from_wand_layer(
    img,
    layer_index: int,
    width: int,
    height: int,
    extraction_flags: dict[str, bool],
    layer_info: dict[str, Any] | None = None,
) -> Layer | None:
    """Create a LayerObject from a Wand image layer."""
    try:
        if layer_info is None:
            layer_info = {}

        # Get layer properties from layer_info or defaults
        layer_id = f"layer_{layer_index}"
        layer_name = layer_info.get("name", f"Layer {layer_index + 1}")
        layer_type = layer_info.get("layer_type", "pixel")

        # Extract layer properties
        opacity = 1.0
        visibility = True
        blend_mode = "Normal"

        # Get opacity
        if "opacity" in layer_info:
            try:
                opacity_val = layer_info["opacity"]
                if isinstance(opacity_val, str) and opacity_val.endswith("%"):
                    opacity = float(opacity_val[:-1]) / 100.0
                else:
                    opacity = float(opacity_val) / 100.0 if float(opacity_val) > 1 else float(opacity_val)
                opacity = max(0.0, min(1.0, opacity))  # Clamp to 0-1 range
            except (ValueError, TypeError):
                pass

        # Get visibility
        if "visible" in layer_info:
            visibility = str(layer_info["visible"]).lower() in [
                "true",
                "1",
                "yes",
                "on",
            ]
        elif "visibility" in layer_info:
            visibility = str(layer_info["visibility"]).lower() in [
                "true",
                "1",
                "yes",
                "on",
            ]

        # Get blend mode
        if "blend" in layer_info:
            blend_mode = str(layer_info["blend"])
        elif "blend_mode" in layer_info:
            blend_mode = str(layer_info["blend_mode"])

        # Try to get layer bounds if available
        layer_bbox = [0, 0, float(width), float(height)]
        if "bounds" in layer_info:
            try:
                bounds = layer_info["bounds"]
                if isinstance(bounds, list | tuple) and len(bounds) == 4:
                    layer_bbox = [float(x) for x in bounds]
            except (ValueError, TypeError):
                pass

        # Try to extract additional layer properties from image artifacts
        try:
            if hasattr(img, "artifacts") and img.artifacts:
                artifacts = img.artifacts

                # Look for layer-specific metadata with various key formats
                possible_keys = [
                    f"layer:{layer_index}:",
                    f"layer[{layer_index}]:",
                    f"psd:layer:{layer_index}:",
                ]

                for key_prefix in possible_keys:
                    for artifact_key, artifact_value in artifacts.items():
                        if artifact_key.startswith(key_prefix):
                            property_name = artifact_key[len(key_prefix) :]

                            if property_name == "opacity" and "opacity" not in layer_info:
                                try:
                                    opacity = float(artifact_value) / 100.0
                                    opacity = max(0.0, min(1.0, opacity))
                                except (ValueError, TypeError):
                                    pass
                            elif property_name in ["visible", "visibility"] and "visible" not in layer_info:
                                visibility = str(artifact_value).lower() in [
                                    "true",
                                    "1",
                                    "yes",
                                    "on",
                                ]
                            elif property_name in ["blend", "blend_mode"] and "blend" not in layer_info:
                                blend_mode = str(artifact_value)
                            elif property_name == "name" and "name" not in layer_info:
                                layer_name = str(artifact_value)
        except Exception as e:
            logger.debug(f"Could not extract additional layer properties for layer {layer_index}: {e}")

        # Convert layer_type string to LayerType enum
        if layer_type == "pixel":
            layer_type_enum = LayerType.PIXEL
        elif layer_type == "text":
            layer_type_enum = LayerType.TEXT
        elif layer_type == "shape":
            layer_type_enum = LayerType.SHAPE
        elif layer_type == "group":
            layer_type_enum = LayerType.GROUP
        else:
            layer_type_enum = LayerType.PIXEL  # Default

        # Convert blend_mode string to BlendMode enum
        try:
            blend_mode_enum = BlendMode(blend_mode)
        except ValueError:
            blend_mode_enum = BlendMode.NORMAL  # Default

        # Create bounding box object
        bbox_obj = BoundingBox(layer_bbox[0], layer_bbox[1], layer_bbox[2], layer_bbox[3])

        # Create layer object
        layer = Layer(
            layer_id=layer_id,
            layer_name=layer_name,
            layer_type=layer_type_enum,
            bbox=bbox_obj,
            visibility=visibility,
            opacity=opacity,
            blend_mode=blend_mode_enum,
            children=[],
            content=[],  # Will be populated with extracted elements
        )

        # Add layer effects if available
        if layer_info.get("effects"):
            # Store effects as layer effects
            layer.layer_effects = layer_info["effects"]

        # Extract content from this layer if requested
        if extraction_flags.get("include_images", True):
            # Extract the layer as a raster image
            image_element = _extract_layer_as_image(img, layer_index, layer_id, layer_bbox, layer_info)
            if image_element:
                layer.content.append(image_element)

        logger.debug(f"Created layer: {layer_name} (type: {layer_type}, opacity: {opacity}, visible: {visibility})")
        return layer

    except Exception as e:
        logger.debug(f"Error creating layer object for layer {layer_index}: {e}")
        return None


def _create_base_layer_from_image(img, width: int, height: int, extraction_flags: dict[str, bool]) -> Layer:
    """Create a base layer from the flattened image."""
    # Create base layer for the canvas
    bbox_obj = BoundingBox(0, 0, float(width), float(height))
    base_layer = Layer(
        layer_id="canvas_base_layer",
        layer_name="Canvas Content",
        layer_type=LayerType.BASE,
        bbox=bbox_obj,
        visibility=True,
        opacity=1.0,
        blend_mode=BlendMode.NORMAL,
        children=[],
        content=[],  # Will be populated with extracted elements
    )

    # Extract content from the flattened image if requested
    if extraction_flags.get("include_images", True):
        # Extract the entire image as a single element
        image_element = _extract_base_image(img, width, height)
        if image_element:
            base_layer.content.append(image_element)

    return base_layer


def get_wand_config() -> dict[str, Any]:
    """
    Get Wand-specific configuration from settings.

    Returns:
        Dict[str, Any]: Wand configuration dictionary

    Example:
        >>> config = get_wand_config()
        >>> print(f"Density: {config['density']} DPI")
    """
    from pdfrebuilder.settings import get_nested_config_value

    return {
        "density": get_nested_config_value("engines.input.wand.density", 300),
        "use_ocr": get_nested_config_value("engines.input.wand.use_ocr", False),
        "tesseract_lang": get_nested_config_value("engines.input.wand.tesseract_lang", "eng"),
        "image_format": get_nested_config_value("engines.input.wand.image_format", "png"),
        "color_management": get_nested_config_value("engines.input.wand.color_management", True),
        "memory_limit_mb": get_nested_config_value("engines.input.wand.memory_limit_mb", 1024),
        "enhance_images": get_nested_config_value("engines.input.wand.enhance_images", False),
        "auto_level": get_nested_config_value("engines.input.wand.auto_level", False),
        "auto_gamma": get_nested_config_value("engines.input.wand.auto_gamma", False),
        "sharpen": get_nested_config_value("engines.input.wand.sharpen", False),
        "noise_reduction": get_nested_config_value("engines.input.wand.noise_reduction", False),
    }


def validate_wand_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate Wand configuration parameters.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)

    Example:
        >>> config = get_wand_config()
        >>> is_valid, errors = validate_wand_config(config)
        >>> if not is_valid:
        ...     print("Configuration errors:", errors)
    """
    errors = []

    # Validate density
    density = config.get("density", 300)
    if not isinstance(density, int | float) or density <= 0:
        errors.append(f"Invalid density: {density}. Must be a positive number.")

    # Validate memory limit
    memory_limit = config.get("memory_limit_mb", 1024)
    if not isinstance(memory_limit, int | float) or memory_limit <= 0:
        errors.append(f"Invalid memory_limit_mb: {memory_limit}. Must be a positive number.")

    # Validate image format
    image_format = config.get("image_format", "png")
    valid_formats = ["png", "jpg", "jpeg", "tiff", "bmp", "gif"]
    if image_format.lower() not in valid_formats:
        errors.append(f"Invalid image_format: {image_format}. Must be one of: {valid_formats}")

    # Validate tesseract language if OCR is enabled
    if config.get("use_ocr", False):
        tesseract_lang = config.get("tesseract_lang", "eng")
        if not isinstance(tesseract_lang, str) or not tesseract_lang.strip():
            errors.append("Invalid tesseract_lang: Must be a non-empty string when OCR is enabled.")

    return len(errors) == 0, errors


def _extract_base_image(img, width: int, height: int) -> ImageElement | None:
    """Extract the base/flattened image as an image element."""
    try:
        from pdfrebuilder.settings import get_config_value

        # Get configuration
        config = get_wand_config()
        image_format = config.get("image_format", "png")

        # Create output directory for images
        image_dir = get_config_value("image_dir")
        os.makedirs(image_dir, exist_ok=True)

        # Generate consistent filename for the base image
        image_filename = _generate_consistent_image_filename("base_canvas", 0, image_format, "base")
        image_path = os.path.join(image_dir, image_filename)

        # Extract the flattened image
        with img.clone() as base_img:
            # Flatten all layers into a single image
            try:
                base_img.flatten()
            except Exception as e:
                logger.debug(f"Could not flatten image, using as-is: {e}")

            # Set format and quality
            base_img.format = image_format
            if image_format.lower() in ["jpg", "jpeg"]:
                base_img.compression_quality = 90

            # Apply image enhancements and color management
            _apply_image_enhancements(base_img, config)
            _apply_color_profile_management(base_img, config)
            _optimize_image_for_output(base_img, config)

            # Save the base image
            base_img.save(filename=image_path)

            # Get image properties
            has_transparency = base_img.alpha_channel
            color_space = str(base_img.colorspace).upper()

            # Prepare image properties for metadata
            img_properties = {
                "width": width,
                "height": height,
                "format": image_format.upper(),
                "color_space": color_space,
                "has_transparency": has_transparency,
                "dpi": config.get("density", 300),
            }

            # Record comprehensive metadata for base image
            base_layer_info = {
                "name": "Base Canvas",
                "layer_type": "base",
                "opacity": 1.0,
                "visible": True,
                "blend_mode": "Normal",
                "has_mask": False,
                "has_clipping_path": False,
                "effects": [],
            }
            _record_image_metadata(image_path, base_layer_info, img_properties, config)

            # Create image element
            image_element = ImageElement(
                id=f"base_image_{width}x{height}",
                bbox=BoundingBox.from_list([0.0, 0.0, float(width), float(height)]),
                image_file=os.path.relpath(image_path, "."),
                original_format=image_format.upper(),
                dpi=int(get_wand_config().get("density", 300)),
                color_space=str(base_img.colorspace).upper(),
                has_transparency=bool(has_transparency),
                z_index=0,
            )
            return image_element

    except Exception as e:
        logger.debug(f"Error extracting base image: {e}")
        return None


def _apply_image_enhancements(img, config: dict[str, Any]) -> None:
    """Apply optional image enhancements to a Wand image object."""
    try:
        if not config.get("enhance_images", False):
            return

        logger.debug("Applying image enhancements")

        # Auto-level: Automatically adjust levels for better contrast
        if config.get("auto_level", False):
            try:
                img.auto_level()
                logger.debug("Applied auto-level enhancement")
            except Exception as e:
                logger.debug(f"Could not apply auto-level: {e}")

        # Auto-gamma: Automatically adjust gamma correction
        if config.get("auto_gamma", False):
            try:
                img.auto_gamma()
                logger.debug("Applied auto-gamma enhancement")
            except Exception as e:
                logger.debug(f"Could not apply auto-gamma: {e}")

        # Sharpen: Apply sharpening filter
        if config.get("sharpen", False):
            try:
                # Apply moderate sharpening (radius=0, sigma=1.0)
                img.sharpen(radius=0, sigma=1.0)
                logger.debug("Applied sharpening enhancement")
            except Exception as e:
                logger.debug(f"Could not apply sharpening: {e}")

        # Noise reduction: Apply noise reduction filter
        if config.get("noise_reduction", False):
            try:
                # Apply moderate noise reduction
                img.noise("gaussian", attenuate=0.5)
                logger.debug("Applied noise reduction enhancement")
            except Exception as e:
                logger.debug(f"Could not apply noise reduction: {e}")

        # Additional enhancement: Normalize colors if requested
        if config.get("normalize_colors", False):
            try:
                img.normalize()
                logger.debug("Applied color normalization")
            except Exception as e:
                logger.debug(f"Could not apply color normalization: {e}")

        # Additional enhancement: Enhance contrast if requested
        if config.get("enhance_contrast", False):
            try:
                img.contrast_stretch(black_point=0.1, white_point=0.9)
                logger.debug("Applied contrast enhancement")
            except Exception as e:
                logger.debug(f"Could not apply contrast enhancement: {e}")

    except Exception as e:
        logger.debug(f"Error applying image enhancements: {e}")


def _apply_color_profile_management(img, config: dict[str, Any]) -> None:
    """Apply color profile management to ensure consistent color reproduction."""
    try:
        if not config.get("color_management", True):
            return

        logger.debug("Applying color profile management")

        # Get current color profile
        current_profile = None
        try:
            if hasattr(img, "color_profile") and img.color_profile:
                current_profile = img.color_profile
                logger.debug(f"Found embedded color profile: {len(current_profile)} bytes")
        except Exception as e:
            logger.debug(f"Could not read color profile: {e}")

        # Ensure consistent color space
        try:
            target_colorspace = "srgb"  # Standard RGB for web/display
            if img.colorspace != target_colorspace:
                logger.debug(f"Converting from {img.colorspace} to {target_colorspace}")
                img.colorspace = target_colorspace
        except Exception as e:
            logger.debug(f"Could not convert color space: {e}")

        # Apply standard sRGB profile if no profile exists
        if not current_profile:
            try:
                # This would require having an sRGB profile file
                # For now, we'll just ensure the colorspace is set correctly
                img.colorspace = "srgb"
                logger.debug("Applied standard sRGB color space")
            except Exception as e:
                logger.debug(f"Could not apply standard color profile: {e}")

    except Exception as e:
        logger.debug(f"Error applying color profile management: {e}")


def _optimize_image_for_output(img, config: dict[str, Any]) -> None:
    """Optimize image for output based on format and quality settings."""
    try:
        image_format = config.get("image_format", "png").lower()

        # Format-specific optimizations
        if image_format in ["jpg", "jpeg"]:
            # JPEG optimizations
            img.compression_quality = config.get("jpeg_quality", 90)
            img.interlace_scheme = "jpeg"  # Progressive JPEG

            # Remove alpha channel for JPEG (not supported)
            if img.alpha_channel:
                img.alpha_channel = "remove"
                logger.debug("Removed alpha channel for JPEG output")

        elif image_format == "png":
            # PNG optimizations
            img.compression_quality = config.get("png_compression", 95)

            # Optimize PNG compression
            if hasattr(img, "options"):
                img.options["png:compression-level"] = "9"  # Maximum compression
                img.options["png:compression-strategy"] = "1"  # Filtered compression

        elif image_format == "webp":
            # WebP optimizations
            img.compression_quality = config.get("webp_quality", 85)
            if hasattr(img, "options"):
                img.options["webp:lossless"] = "false"
                img.options["webp:alpha-quality"] = "100"

        # General optimizations
        # Strip metadata to reduce file size (optional)
        if config.get("strip_metadata", False):
            try:
                img.strip()
                logger.debug("Stripped image metadata")
            except Exception as e:
                logger.debug(f"Could not strip metadata: {e}")

        # Set density/DPI
        density = config.get("density", 300)
        try:
            img.resolution = (density, density)
            logger.debug(f"Set image resolution to {density} DPI")
        except Exception as e:
            logger.debug(f"Could not set image resolution: {e}")

    except Exception as e:
        logger.debug(f"Error optimizing image for output: {e}")


def _generate_consistent_image_filename(
    layer_id: str, layer_index: int, image_format: str, prefix: str = "layer"
) -> str:
    """Generate a consistent filename for extracted images."""
    import hashlib
    import re

    # Clean layer_id for filename use
    clean_layer_id = re.sub(r"[^\w\-_]", "_", layer_id)

    # Create hash for uniqueness
    hash_input = f"{clean_layer_id}_{layer_index}_{prefix}"
    layer_hash = hashlib.md5(hash_input.encode(), usedforsecurity=False).hexdigest()[:8]

    # Generate filename with consistent format
    filename = f"{prefix}_{layer_index:03d}_{layer_hash}.{image_format.lower()}"

    return filename


def extract_text_with_ocr(image_path: str, language: str = "eng") -> str | None:
    """
    Extract text from an image using pytesseract OCR.

    Args:
        image_path: Path to the image file
        language: Tesseract language code (default: "eng")

    Returns:
        Extracted text or None if OCR fails
    """
    try:
        import pytesseract
        from PIL import Image

        # Open image and extract text
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img, lang=language)
            return text.strip() if text else None

    except ImportError:
        logger.debug("pytesseract not available for OCR")
        return None
    except Exception as e:
        logger.debug(f"OCR extraction failed: {e}")
        return None


def _record_image_metadata(
    image_path: str,
    layer_info: dict[str, Any],
    img_properties: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Record comprehensive metadata for extracted images."""
    try:
        import os
        from datetime import datetime

        # Get file information
        file_stat = os.stat(image_path)
        file_size = file_stat.st_size

        # Create comprehensive metadata record
        metadata = {
            # File information
            "file_path": os.path.relpath(image_path, "."),
            "file_size_bytes": file_size,
            "extraction_timestamp": datetime.now().isoformat(),
            # Image properties
            "width": img_properties.get("width", 0),
            "height": img_properties.get("height", 0),
            "format": img_properties.get("format", "unknown"),
            "color_space": img_properties.get("color_space", "unknown"),
            "has_transparency": img_properties.get("has_transparency", False),
            "dpi": img_properties.get("dpi", config.get("density", 300)),
            # Layer information
            "layer_name": layer_info.get("name", "Unknown Layer"),
            "layer_type": layer_info.get("layer_type", "pixel"),
            "layer_opacity": layer_info.get("opacity", 1.0),
            "layer_visibility": layer_info.get("visible", True),
            "layer_blend_mode": layer_info.get("blend_mode", "Normal"),
            # Processing information
            "extraction_engine": "wand",
            "enhancements_applied": config.get("enhance_images", False),
            "color_management_applied": config.get("color_management", True),
            # Additional metadata
            "has_mask": layer_info.get("has_mask", False),
            "has_clipping_path": layer_info.get("has_clipping_path", False),
            "effects_count": len(layer_info.get("effects", [])),
        }

        # Add transformation matrix if available
        if "transformation_matrix" in img_properties:
            metadata["transformation_matrix"] = img_properties["transformation_matrix"]

        # Add layer bounds if available
        if "bounds" in layer_info:
            metadata["layer_bounds"] = layer_info["bounds"]

        # Add effects information if available
        if layer_info.get("effects"):
            metadata["effects"] = [
                {
                    "type": effect.get("type", "unknown"),
                    "enabled": effect.get("enabled", False),
                }
                for effect in layer_info["effects"]
            ]

        # Add OCR text if enabled
        if config.get("use_ocr", False):
            ocr_text = extract_text_with_ocr(image_path, config.get("tesseract_lang", "eng"))
            if ocr_text:
                metadata["ocr_text"] = ocr_text

        return metadata

    except Exception as e:
        logger.debug(f"Error recording image metadata: {e}")
        return {
            "file_path": os.path.relpath(image_path, "."),
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_engine": "wand",
            "error": str(e),
        }


def _create_image_manifest_entry(image_element: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    """Create a manifest entry for an extracted image."""
    return {
        "id": image_element["id"],
        "type": "image",
        "file_path": image_element["image_file"],
        "bbox": image_element["bbox"],
        "z_index": image_element.get("z_index", 0),
        "metadata": metadata,
        "extraction_info": {
            "engine": "wand",
            "format": image_element.get("original_format", "unknown"),
            "dpi": image_element.get("dpi", 300),
            "color_space": image_element.get("color_space", "unknown"),
            "has_transparency": image_element.get("has_transparency", False),
        },
    }
