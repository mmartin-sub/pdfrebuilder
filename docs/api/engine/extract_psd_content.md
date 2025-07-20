# extract_psd_content

PSD content extraction module for the Multi-Format Document Engine.

This module provides functionality to extract content from PSD files
and convert it to the Universal IDM format.

## Classes

### PSDExtractionError

Raised when PSD extraction fails

## Functions

### _get_blend_mode(psd_blend_mode)

Convert PSD blend mode to Universal IDM blend mode

### _get_layer_type(psd_layer)

Determine the layer type from a PSD layer

### _extract_text_element(psd_layer, element_id)

Extract text element from a PSD text layer

### _extract_image_element(psd_layer, element_id, image_dir)

Extract image element from a PSD pixel layer

### _extract_shape_element(psd_layer, element_id)

Extract shape element from a PSD vector layer

### _process_layer(psd_layer, parent_id, element_counter, image_dir)

Process a PSD layer and convert it to a Universal IDM layer

### extract_psd_content(psd_path, extraction_flags)

Extract content from a PSD file and convert it to the Universal IDM format

Args:
    psd_path: Path to the PSD file
    extraction_flags: Optional flags to control extraction behavior

Returns:
    UniversalDocument: Extracted document content

Raises:
    PSDExtractionError: If extraction fails

### check_psd_tools_availability()

Check if psd-tools is available
