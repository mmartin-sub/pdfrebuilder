# font_validator

Font validation module for the Multi-Format Document Engine.

This module provides font availability checking, substitution tracking,
and font-related validation reporting capabilities.

## Classes

### FontSubstitution

Information about a font substitution that occurred during processing

### FontValidationResult

Result of font validation for a document

#### Methods

##### add_substitution(substitution)

Add a font substitution to the result

##### add_coverage_issue(font_name, text, missing_chars, element_id)

Add a font coverage issue to the result

##### add_validation_message(message, level)

Add a validation message

### FontValidator

Font validation system for document processing

#### Methods

##### __init__(fonts_dir)

Initialize the font validator

Args:
    fonts_dir: Directory containing font files. If None, uses CONFIG setting.

##### _refresh_available_fonts()

Refresh the cache of available fonts

##### validate_document_fonts(layout_config)

Validate fonts used in a document layout configuration

Args:
    layout_config: Document layout configuration containing font information

Returns:
    FontValidationResult with validation details

##### _extract_fonts_from_config(layout_config)

Extract all fonts used in the document configuration

##### _extract_fonts_from_layer(layer, fonts_used)

Extract fonts from a layer and its content

##### _check_font_availability(fonts_used, result)

Check which fonts are available and which are missing

##### _is_font_available(font_name)

Check if a font is available (standard PDF font or local file)

##### is_font_available(font_name)

Public method to check if a font is available

##### _check_font_coverage(layout_config, result)

Check font glyph coverage for text elements

##### _check_layer_font_coverage(layer, result, page_number)

Check font coverage for elements in a layer

##### _check_element_font_coverage(element, result, page_number)

Check font coverage for a specific text element

##### _get_font_path(font_name)

Get the file path for a font

##### _find_missing_characters(font_path, text)

Find characters that are not covered by the font

##### _generate_validation_summary(result)

Generate a summary of the font validation results

##### track_font_substitution(original_font, substituted_font, reason, text_content, element_id, page_number)

Track a font substitution that occurred during processing

##### get_font_validation_report()

Get a comprehensive font validation report
