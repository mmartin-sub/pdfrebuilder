# psd_validator

PSD validation utilities for the Multi-Format Document Engine.

This module provides utilities for validating PSD files and their structure.

## Classes

### PSDValidationError

Raised when PSD validation fails

## Functions

### validate_psd_header(file_obj)

Validate that a file has a valid PSD header

Args:
    file_obj: File object opened in binary mode

Returns:
    True if the file has a valid PSD header, False otherwise

### validate_psd_file(file_path)

Validate a PSD file

Args:
    file_path: Path to the PSD file

Returns:
    Tuple of (is_valid, list_of_errors)

### check_psd_compatibility(file_path)

Check if a PSD file is compatible with the Multi-Format Document Engine

Args:
    file_path: Path to the PSD file

Returns:
    Tuple of (is_compatible, compatibility_info)

### get_psd_metadata(file_path)

Extract metadata from a PSD file

Args:
    file_path: Path to the PSD file

Returns:
    Dictionary of metadata

Raises:
    PSDValidationError: If metadata extraction fails

### validate_psd_layer_structure(layer_data)

Validate PSD layer structure for compatibility with Universal IDM

Args:
    layer_data: Layer data from psd-tools

Returns:
    Tuple of (is_valid, list_of_errors)
