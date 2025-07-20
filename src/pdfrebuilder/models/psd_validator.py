"""
PSD validation utilities for the Multi-Format Document Engine.

This module provides utilities for validating PSD files and their structure.
"""

import logging
import os
from typing import Any, BinaryIO

logger = logging.getLogger(__name__)


class PSDValidationError(Exception):
    """Raised when PSD validation fails"""


def validate_psd_header(file_obj: BinaryIO) -> bool:
    """
    Validate that a file has a valid PSD header

    Args:
        file_obj: File object opened in binary mode

    Returns:
        True if the file has a valid PSD header, False otherwise
    """
    # Save current position
    current_pos = file_obj.tell()

    # Go to beginning of file
    file_obj.seek(0)

    # Read signature (8BPS)
    signature = file_obj.read(4)

    # Read version (1 or 2)
    version = int.from_bytes(file_obj.read(2), byteorder="big")

    # Restore position
    file_obj.seek(current_pos)

    # Check signature and version
    return signature == b"8BPS" and version in [1, 2]


def validate_psd_file(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate a PSD file

    Args:
        file_path: Path to the PSD file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check if file exists
    if not os.path.exists(file_path):
        errors.append(f"File not found: {file_path}")
        return False, errors

    try:
        # Open file in binary mode
        with open(file_path, "rb") as f:
            # Check header
            if not validate_psd_header(f):
                errors.append(f"Invalid PSD header: {file_path}")
                return False, errors

            # Additional validation could be added here
            # For now, we just check the header

    except Exception as e:
        errors.append(f"Error validating PSD file: {e!s}")
        return False, errors

    return len(errors) == 0, errors


def check_psd_compatibility(file_path: str) -> tuple[bool, dict[str, Any]]:
    """
    Check if a PSD file is compatible with the Multi-Format Document Engine

    Args:
        file_path: Path to the PSD file

    Returns:
        Tuple of (is_compatible, compatibility_info)
    """
    compatibility_info: dict[str, Any] = {
        "is_compatible": False,
        "issues": [],
        "warnings": [],
        "features": [],
    }

    # First validate the file
    is_valid, errors = validate_psd_file(file_path)
    if not is_valid:
        compatibility_info["issues"].extend(errors)
        return False, compatibility_info

    try:
        # This is a placeholder for more detailed compatibility checking
        # In a full implementation, we would use psd-tools to check:
        # - Layer structure complexity
        # - Text layer encoding
        # - Smart objects
        # - Layer effects
        # - Color modes
        # - etc.

        # For now, we assume it's compatible if it's a valid PSD
        compatibility_info["is_compatible"] = True
        compatibility_info["features"].append("basic_layer_support")

        # Add a warning about experimental support
        compatibility_info["warnings"].append(
            "PSD support is experimental and may not handle all PSD features correctly."
        )

    except Exception as e:
        compatibility_info["issues"].append(f"Error checking compatibility: {e!s}")
        return False, compatibility_info

    return compatibility_info["is_compatible"], compatibility_info


def get_psd_metadata(file_path: str) -> dict[str, Any]:
    """
    Extract metadata from a PSD file

    Args:
        file_path: Path to the PSD file

    Returns:
        Dictionary of metadata

    Raises:
        PSDValidationError: If metadata extraction fails
    """
    # This is a placeholder for metadata extraction
    # In a full implementation, we would use psd-tools to extract:
    # - Image dimensions
    # - Color mode
    # - Number of layers
    # - Creation date
    # - etc.

    try:
        # Basic metadata that we can extract without psd-tools
        metadata = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "format": "PSD",
        }

        return metadata

    except Exception as e:
        raise PSDValidationError(f"Error extracting PSD metadata: {e!s}")


def validate_psd_layer_structure(layer_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate PSD layer structure for compatibility with Universal IDM

    Args:
        layer_data: Layer data from psd-tools

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    # This is a placeholder for layer structure validation
    # In a full implementation, we would check:
    # - Layer types
    # - Text encoding
    # - Layer effects
    # - etc.

    return True, []


# Then update all type annotations:
# - Replace Tuple[bool, List[str]] with tuple[bool, list[str]]
# - Replace Tuple[bool, Dict[str, Any]] with tuple[bool, dict[str, Any]]
# - Replace Dict[str, Any] with dict[str, Any]
