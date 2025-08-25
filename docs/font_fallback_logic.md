# Font Fallback Logic

This document outlines the logic used by the `pdfrebuilder` for font substitution and fallback when a requested font is not available or does not meet the requirements for rendering a given text element.

## Overview

The font fallback system is primarily managed by the `ensure_font_registered` function in `pdfrebuilder.font.utils`, which in turn uses the `FallbackFontManager` and `FontValidator` classes. The goal is to find a suitable font to render the text with the highest possible fidelity, even if the originally specified font is not available.

## Fallback Priority

The system follows a clear priority order when attempting to find a font:

1.  **Exact Font Match (Cached):** The system first checks if the requested font has already been registered for the current page. If so, it uses the cached font reference.

2.  **Standard PDF Fonts:** If the requested font is one of the 14 standard PDF fonts (e.g., "helv", "cour"), it is used directly without further validation, as these are assumed to be available in any PDF viewer.

3.  **Local Font Files:** The system searches for a font file matching the requested font name in the configured `manual_fonts_dir` and `downloaded_fonts_dir`. It looks for `.ttf`, `.otf`, `.woff`, and `.woff2` files.

4.  **Google Fonts Download:** If the font is not found locally, the system attempts to download it from Google Fonts.

5.  **Glyph Coverage-Based Substitution:** If text content is provided, and the originally specified font is not available or does not cover all the characters in the text, the system will scan all available local fonts to find one that *does* cover the text. This is the "intelligent substitution" part of the logic.

6.  **Priority List Fallback:** If no font with full glyph coverage is found, the system iterates through a predefined list of common fallback fonts (`FallbackFontManager.FALLBACK_FONTS`). The first font in this list that can be successfully registered is used.

7.  **Guaranteed Fallback:** If all other methods fail, the system falls back to a "guaranteed" font, which is typically "Helvetica" or another standard PDF font.

## Key Classes and Functions

-   **`ensure_font_registered(page, font_name, text=None)`:** This is the main entry point for the font fallback logic. It orchestrates the entire process of finding and registering a font.

-   **`FallbackFontManager`:** This class manages the fallback process.
    -   `FALLBACK_FONTS`: A class variable that defines the prioritized list of fallback fonts.
    -   `select_fallback_font()`: The main method that selects a fallback font. It first tries to find a font with full glyph coverage and then falls back to the priority list.
    -   `_score_fallback_font()`: A (currently complex) method that attempts to score fallback fonts based on glyph coverage, font characteristics, and reliability.
    -   `validate_fallback_font()`: Checks if a given fallback font can be successfully registered on a page.

-   **`scan_available_fonts(fonts_dir)`:** Scans a directory for font files and extracts their family names.

-   **`font_covers_text(font_path, text)`:** Checks if a font file at a given path contains all the necessary glyphs to render the given text.

## Analysis of Test Failures

The current test failures in `tests/font/test_font_substitution.py` are caused by a mismatch between the expected and actual behavior of this fallback logic.

-   **Incorrect Font Name:** The test `test_font_substitution_by_coverage` was failing because the name extracted from the Noto Sans CJK font file is `'Noto Sans JP Thin'`, not `'Noto Sans CJK JP'` or `'Noto Sans JP'`. This is an issue with the font's metadata, not necessarily the code.

-   **Unpredictable Fallback Order:** The other failing tests are asserting a specific fallback font (e.g., 'helv'), but the system is choosing a different one (e.g., 'Courier' or 'Public_Sans'). This is happening because:
    -   The refactored tests now include real fonts in the test directory, and the fallback logic correctly finds and uses them before it gets to the standard PDF fonts.
    -   The `FALLBACK_FONTS` list has a specific order, and the tests were not written to account for this order. For example, 'tiro' comes before 'cour', so the fallback will be 'tiro'.

## Recommendations

1.  **Fix Test Assertions:** The tests should be updated to reflect the actual, correct behavior of the fallback logic. For example, if the system correctly falls back to `Public Sans` because it's available, the test should assert that, not `helv`.

2.  **Simplify Fallback Logic (Future Work):** The scoring mechanism in `_score_fallback_font` is complex and might not be necessary. A simpler approach of just finding the first available font that covers the text might be more robust and easier to test.

3.  **Improve Font Name Extraction:** The logic in `scan_available_fonts` for extracting the font family name could be improved to better handle different name record formats and platforms, which might resolve the `'Noto Sans JP Thin'` vs. `'Noto Sans JP'` issue. Using `getBestFamilyName()` from `fontTools` might be a better approach.
