# font_utils

Font utilities for PDF processing.

This module provides font management functionality including:

- Font registration and caching
- Font file scanning and discovery
- Glyph coverage analysis
- Google Fonts integration
- Font substitution tracking

## Functions

### set_font_validator(font_validator)

Set the global font validator instance for tracking substitutions

### _track_font_substitution(original_font, substituted_font, reason, text_content, element_id, page_number)

Track a font substitution if validator is available

### scan_available_fonts(fonts_dir)

Scan the fonts_dir for .ttf and .otf files and cache their paths.
Also scans manual_fonts_dir if available.
Returns a dict: {font_name: font_path}

### font_covers_text(font_path, text)

Returns True if the font at font_path covers all characters in text.

### ensure_font_registered(page, font_name, verbose, text)

Ensure the font is registered on the given page. Only registers once per page.
Always use the original font_name string for rendering.
Returns the font name actually registered (may be a fallback).
If 'text' is provided, will check glyph coverage and select a fallback if needed.
