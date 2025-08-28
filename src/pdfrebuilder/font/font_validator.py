"""
Font validation module for the Multi-Format Document Engine.

This module provides font availability checking, substitution tracking,
and font-related validation reporting capabilities.
"""

# Add missing imports
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from pdfrebuilder.font.utils import font_covers_text, scan_available_fonts
from pdfrebuilder.settings import STANDARD_PDF_FONTS

logger = logging.getLogger(__name__)


@dataclass
class FontSubstitution:
    """Information about a font substitution that occurred during processing"""

    original_font: str
    substituted_font: str
    reason: str
    text_content: str | None = None
    element_id: str | None = None
    page_number: int | None = None


@dataclass
class FontValidationResult:
    """Result of font validation for a document"""

    fonts_required: set[str] = field(default_factory=set)
    fonts_available: set[str] = field(default_factory=set)
    fonts_missing: set[str] = field(default_factory=set)
    fonts_substituted: list[FontSubstitution] = field(default_factory=list)
    font_coverage_issues: list[dict[str, Any]] = field(default_factory=list)
    validation_passed: bool = True
    validation_messages: list[str] = field(default_factory=list)

    def add_substitution(self, substitution: FontSubstitution) -> None:
        """Add a font substitution to the result"""
        self.fonts_substituted.append(substitution)
        if substitution.original_font not in self.fonts_missing:
            self.fonts_missing.add(substitution.original_font)

    def add_coverage_issue(
        self,
        font_name: str,
        text: str,
        missing_chars: list[str],
        element_id: str | None = None,
    ) -> None:
        """Add a font coverage issue to the result"""
        issue = {
            "font_name": font_name,
            "text": text,
            "missing_characters": missing_chars,
            "element_id": element_id,
            "severity": "high" if len(missing_chars) > len(text) * 0.1 else "medium",
        }
        self.font_coverage_issues.append(issue)

    def add_validation_message(self, message: str, level: str = "info") -> None:
        """Add a validation message"""
        formatted_message = f"[{level.upper()}] {message}"
        self.validation_messages.append(formatted_message)

        if level in ["error", "critical"]:
            self.validation_passed = False


class FontValidator:
    """Font validation system for document processing"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, fonts_dir: str | None = None):
        """Initialize the font validator

        Args:
            fonts_dir: Directory containing font files. If None, uses settings.
        """
        if hasattr(self, '_initialized') and self._initialized and not fonts_dir:
            return

        from pdfrebuilder.settings import settings

        self.fonts_dir = fonts_dir or settings.font_management.downloaded_fonts_dir or "downloaded_fonts"
        self.available_fonts: dict[str, str] = {}
        self.substitution_tracker: list[FontSubstitution] = []
        self._refresh_available_fonts()
        self._initialized = True

    def _refresh_available_fonts(self) -> None:
        """Refresh the cache of available fonts"""
        try:
            if os.path.exists(str(self.fonts_dir)):
                self.available_fonts = scan_available_fonts(self.fonts_dir)
                logger.info(f"[FontValidator] Found {len(self.available_fonts)} fonts in {self.fonts_dir}")
            else:
                logger.warning(f"[FontValidator] Fonts directory not found: {self.fonts_dir}")
                self.available_fonts = {}
        except Exception as e:
            logger.error(f"[FontValidator] Error scanning fonts directory: {e}")
            self.available_fonts = {}

    def validate_document_fonts(self, layout_config: dict[str, Any]) -> FontValidationResult:
        """Validate fonts used in a document layout configuration

        Args:
            layout_config: Document layout configuration containing font information

        Returns:
            FontValidationResult with validation details
        """
        result = FontValidationResult()

        try:
            # Extract fonts from document structure
            fonts_used = self._extract_fonts_from_config(layout_config)
            result.fonts_required = fonts_used

            # Check font availability
            self._check_font_availability(fonts_used, result)

            # Check font coverage for text elements
            self._check_font_coverage(layout_config, result)

            # Generate validation summary
            self._generate_validation_summary(result)

        except Exception as e:
            logger.error(f"[FontValidator] Error during font validation: {e}")
            result.add_validation_message(f"Font validation failed: {e}", "error")

        return result

    def _extract_fonts_from_config(self, layout_config: dict[str, Any]) -> set[str]:
        """Extract all fonts used in the document configuration"""
        fonts_used: set[str] = set()

        try:
            document_structure = layout_config.get("document_structure", [])

            for doc_unit in document_structure:
                if doc_unit.get("type") == "page":
                    # Process page layers
                    layers = doc_unit.get("layers", [])
                    for layer in layers:
                        self._extract_fonts_from_layer(layer, fonts_used)
                elif doc_unit.get("type") == "canvas":
                    # Process canvas layers (for future PSD support)
                    layers = doc_unit.get("layers", [])
                    for layer in layers:
                        self._extract_fonts_from_layer(layer, fonts_used)

        except Exception as e:
            logger.error(f"[FontValidator] Error extracting fonts from config: {e}")

        return fonts_used

    def _extract_fonts_from_layer(self, layer: dict[str, Any], fonts_used: set[str]) -> None:
        """Extract fonts from a layer and its content"""
        try:
            # Process layer content
            content = layer.get("content", [])
            for element in content:
                if element.get("type") == "text":
                    font_details = element.get("font_details", {})
                    font_name = font_details.get("name")
                    if font_name and font_name != "Unnamed-T3":
                        fonts_used.add(font_name)

            # Process child layers recursively
            children = layer.get("children", [])
            for child_layer in children:
                self._extract_fonts_from_layer(child_layer, fonts_used)

        except Exception as e:
            logger.error(f"[FontValidator] Error extracting fonts from layer: {e}")

    def _check_font_availability(self, fonts_used: set[str], result: FontValidationResult) -> None:
        """Check which fonts are available and which are missing"""
        for font_name in fonts_used:
            if self._is_font_available(font_name):
                result.fonts_available.add(font_name)
            else:
                result.fonts_missing.add(font_name)
                result.add_validation_message(f"Font '{font_name}' is not available locally", "warning")

    def _is_font_available(self, font_name: str) -> bool:
        """Check if a font is available (standard PDF font or local file)"""
        # Check if it's a standard PDF font
        if font_name in STANDARD_PDF_FONTS:
            return True

        # Check if it's available in the fonts directory
        if font_name in self.available_fonts:
            return True

        # Check for direct file existence
        font_file_ttf = os.path.join(str(self.fonts_dir), f"{font_name}.ttf")
        font_file_otf = os.path.join(str(self.fonts_dir), f"{font_name}.otf")

        return os.path.exists(font_file_ttf) or os.path.exists(font_file_otf)

    def is_font_available(self, font_name: str) -> bool:
        """Public method to check if a font is available"""
        return self._is_font_available(font_name)

    def _check_font_coverage(self, layout_config: dict[str, Any], result: FontValidationResult) -> None:
        """Check font glyph coverage for text elements"""
        try:
            document_structure = layout_config.get("document_structure", [])

            for doc_unit in document_structure:
                if doc_unit.get("type") == "page":
                    page_number = doc_unit.get("page_number", 0)
                    layers = doc_unit.get("layers", [])
                    for layer in layers:
                        self._check_layer_font_coverage(layer, result, page_number)

        except Exception as e:
            logger.error(f"[FontValidator] Error checking font coverage: {e}")

    def _check_layer_font_coverage(self, layer: dict[str, Any], result: FontValidationResult, page_number: int) -> None:
        """Check font coverage for elements in a layer"""
        try:
            content = layer.get("content", [])
            for element in content:
                if element.get("type") == "text":
                    self._check_element_font_coverage(element, result, page_number)

            # Process child layers recursively
            children = layer.get("children", [])
            for child_layer in children:
                self._check_layer_font_coverage(child_layer, result, page_number)

        except Exception as e:
            logger.error(f"[FontValidator] Error checking layer font coverage: {e}")

    def _check_element_font_coverage(
        self, element: dict[str, Any], result: FontValidationResult, page_number: int
    ) -> None:
        """Check font coverage for a specific text element"""
        try:
            font_details = element.get("font_details", {})
            font_name = font_details.get("name")
            text_content = element.get("text", "")
            element_id = element.get("id", "unknown")

            if not font_name or not text_content or font_name == "Unnamed-T3":
                return

            # Get font path
            font_path = self._get_font_path(font_name)
            if not font_path:
                return

            # Check coverage
            if not font_covers_text(font_path, text_content):
                # Find missing characters
                missing_chars = self._find_missing_characters(font_path, text_content)
                result.add_coverage_issue(font_name, text_content, missing_chars, element_id)
                result.add_validation_message(
                    f"Font '{font_name}' missing glyphs for text in element '{element_id}' on page {page_number + 1}",
                    "warning",
                )

        except Exception as e:
            logger.error(f"[FontValidator] Error checking element font coverage: {e}")

    def _get_font_path(self, font_name: str) -> str | None:
        """Get the file path for a font"""
        if font_name in self.available_fonts:
            return self.available_fonts[font_name]

        # Check for direct file existence
        font_file_ttf = os.path.join(str(self.fonts_dir), f"{font_name}.ttf")
        font_file_otf = os.path.join(str(self.fonts_dir), f"{font_name}.otf")

        if os.path.exists(font_file_ttf):
            return font_file_ttf
        elif os.path.exists(font_file_otf):
            return font_file_otf

        return None

    def _find_missing_characters(self, font_path: str, text: str) -> list[str]:
        """Find characters that are not covered by the font"""
        try:
            # fontTools is not fully typed, so we have to ignore this import.
            # fontTools is not fully typed, so we have to ignore this import.
            from fontTools.ttLib import TTFont  # type: ignore[import-untyped]

            font = TTFont(font_path)
            cmap = set()
            # The `tables` attribute of `font["cmap"]` is not recognized by mypy due to incomplete stubs.
            for table in font["cmap"].tables:  # type: ignore[attr-defined]
                cmap.update(table.cmap.keys())

            missing_chars = []
            for char in text:
                if char.strip() and ord(char) not in cmap:
                    missing_chars.append(char)

            return missing_chars

        except Exception as e:
            logger.error(f"[FontValidator] Error finding missing characters: {e}")
            return []

    def _generate_validation_summary(self, result: FontValidationResult) -> None:
        """Generate a summary of the font validation results"""
        total_fonts = len(result.fonts_required)
        available_fonts = len(result.fonts_available)
        missing_fonts = len(result.fonts_missing)
        substitutions = len(result.fonts_substituted)
        coverage_issues = len(result.font_coverage_issues)

        # Add summary messages
        result.add_validation_message(f"Font validation summary: {total_fonts} fonts required")
        result.add_validation_message(f"Available fonts: {available_fonts}")

        if missing_fonts > 0:
            result.add_validation_message(f"Missing fonts: {missing_fonts}", "warning")
            for font in result.fonts_missing:
                result.add_validation_message(f"  - {font}", "warning")

        if substitutions > 0:
            result.add_validation_message(f"Font substitutions: {substitutions}", "info")

        if coverage_issues > 0:
            result.add_validation_message(f"Font coverage issues: {coverage_issues}", "warning")

        # Determine overall validation status
        if missing_fonts > 0 or coverage_issues > 0:
            result.validation_passed = False
            result.add_validation_message(
                "Font validation failed due to missing fonts or coverage issues",
                "error",
            )
        else:
            result.add_validation_message("Font validation passed", "info")

    def track_font_substitution(
        self,
        original_font: str,
        substituted_font: str,
        reason: str,
        text_content: str | None = None,
        element_id: str | None = None,
        page_number: int | None = None,
    ) -> None:
        """Track a font substitution that occurred during processing"""
        substitution = FontSubstitution(
            original_font=original_font,
            substituted_font=substituted_font,
            reason=reason,
            text_content=text_content,
            element_id=element_id,
            page_number=page_number,
        )
        self.substitution_tracker.append(substitution)

        logger.info(f"[FontValidator] Font substitution: {original_font} -> {substituted_font} ({reason})")

    def get_font_validation_report(self) -> dict[str, Any]:
        """Get a comprehensive font validation report"""
        return {
            "fonts_directory": self.fonts_dir,
            "available_fonts_count": len(self.available_fonts),
            "available_fonts": list(self.available_fonts.keys()),
            "substitutions_tracked": len(self.substitution_tracker),
            "substitutions": [
                {
                    "original_font": sub.original_font,
                    "substituted_font": sub.substituted_font,
                    "reason": sub.reason,
                    "text_content": sub.text_content,
                    "element_id": sub.element_id,
                    "page_number": sub.page_number,
                }
                for sub in self.substitution_tracker
            ],
        }
