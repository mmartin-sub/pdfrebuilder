# psd_text_processor

PSD text processing module for the Multi-Format Document Engine.

This module provides utilities for extracting and processing text from PSD files.

## Classes

### PSDTextExtractionError

Raised when PSD text extraction fails

## Functions

### extract_text_data(text_layer)

Extract text data from a PSD text layer

Args:
    text_layer: PSD text layer

Returns:
    Dictionary containing text data

Raises:
    PSDTextExtractionError: If text extraction fails

### create_font_details(text_data)

Create FontDetails object from PSD text data

Args:
    text_data: Text data extracted from PSD

Returns:
    FontDetails object

### get_text_alignment(text_data)

Get text alignment from PSD text data

Args:
    text_data: Text data extracted from PSD

Returns:
    Alignment value (0=left, 1=center, 2=right, 3=justify)

### extract_all_text_layers(psd_path)

Extract all text layers from a PSD file

Args:
    psd_path: Path to the PSD file

Returns:
    List of dictionaries containing text layer data

Raises:
    PSDTextExtractionError: If extraction fails

### check_psd_text_support()

Check if PSD text extraction is supported
