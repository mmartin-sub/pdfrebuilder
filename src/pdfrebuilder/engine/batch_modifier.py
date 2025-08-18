"""
Batch modification engine for the Multi-Format Document Engine.

This module provides batch text replacement, variable substitution,
and font validation capabilities for template-based document generation.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from pdfrebuilder.font.font_validator import FontValidator
from pdfrebuilder.models.universal_idm import PageUnit, TextElement, UniversalDocument

logger = logging.getLogger(__name__)


@dataclass
class BatchModificationResult:
    """Result of a batch modification operation"""

    success: bool
    modified_elements: int = 0
    skipped_elements: int = 0
    font_warnings: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class VariableSubstitution:
    """Variable substitution configuration"""

    variable_name: str
    replacement_value: str
    element_id: str | None = None
    page_number: int | None = None
    case_sensitive: bool = True


class BatchModifier:
    """
    Batch modification engine for document content.

    Supports:
    - Batch text replacement across multiple elements
    - Variable substitution for template-based generation
    - Font availability and licensing validation
    """

    def __init__(self, font_validator: FontValidator | None = None):
        """
        Initialize the batch modifier.

        Args:
            font_validator: Optional font validator for licensing checks
        """
        self.font_validator = font_validator or FontValidator()
        self._substitution_cache: dict[str, str] = {}

    def batch_text_replacement(
        self,
        document: UniversalDocument,
        replacements: list[tuple[str, str]],
        element_ids: list[str] | None = None,
        page_numbers: list[int] | None = None,
        validate_fonts: bool = True,
    ) -> BatchModificationResult:
        """
        Perform batch text replacement across multiple elements.

        Args:
            document: The document to modify
            replacements: List of (old_text, new_text) tuples
            element_ids: Optional list of specific element IDs to target
            page_numbers: Optional list of page numbers to target
            validate_fonts: Whether to validate font availability for new text

        Returns:
            BatchModificationResult with operation details
        """
        result = BatchModificationResult(success=True)

        # Build replacement mapping
        replacement_map = dict(replacements)

        # Track modifications
        modified_count = 0
        skipped_count = 0
        font_warnings = []

        # Process each document unit
        for unit in document.document_structure:
            if not isinstance(unit, PageUnit):
                continue

            page_num = unit.page_number

            # Skip if page filtering is applied and this page doesn't match
            if page_numbers is not None and page_num not in page_numbers:
                continue

            # Process each layer
            for layer in unit.layers:
                for element in layer.content:
                    if not isinstance(element, TextElement):
                        continue

                    # Skip if element filtering is applied and this element doesn't match
                    if element_ids is not None and element.id not in element_ids:
                        skipped_count += 1
                        continue

                    # Check if this element's text needs replacement
                    current_text = element.text
                    modified = False

                    for old_text, new_text in replacement_map.items():
                        if old_text in current_text:
                            # Perform replacement
                            current_text = current_text.replace(old_text, new_text)
                            modified = True

                            logger.info(f"Replaced text in element {element.id}: '{old_text}' -> '{new_text}'")

                    if modified:
                        # Validate font if requested
                        if validate_fonts:
                            font_warning = self._validate_text_font(element, current_text)
                            if font_warning:
                                font_warnings.append(font_warning)

                        # Update element
                        element.text = current_text
                        element.raw_text = current_text  # Keep raw_text in sync
                        modified_count += 1
                    else:
                        skipped_count += 1

        result.modified_elements = modified_count
        result.skipped_elements = skipped_count
        result.font_warnings = font_warnings
        result.details = {
            "total_replacements": len(replacement_map),
            "targeted_elements": len(element_ids) if element_ids else "all",
            "targeted_pages": len(page_numbers) if page_numbers else "all",
        }

        logger.info(f"Batch text replacement completed: {modified_count} modified, {skipped_count} skipped")
        return result

    def variable_substitution(
        self,
        document: UniversalDocument,
        variables: list[VariableSubstitution],
        template_mode: bool = True,
    ) -> BatchModificationResult:
        """
        Perform variable substitution for template-based generation.

        Args:
            document: The document template to modify
            variables: List of variable substitutions to apply
            template_mode: Whether to operate in template mode (preserve original structure)

        Returns:
            BatchModificationResult with operation details
        """
        result = BatchModificationResult(success=True)

        modified_count = 0
        skipped_count = 0
        font_warnings = []

        # Process each document unit
        for unit in document.document_structure:
            if not isinstance(unit, PageUnit):
                continue

            # Process each layer
            for layer in unit.layers:
                for element in layer.content:
                    if not isinstance(element, TextElement):
                        continue

                    # Check if this element contains variables
                    original_text = element.text
                    modified = False

                    # Handle case-insensitive variable substitution
                    for var in variables:
                        if var.case_sensitive:
                            var_pattern_str = f"${{{var.variable_name}}}"
                            if var_pattern_str in original_text:
                                # Perform variable substitution
                                original_text = original_text.replace(var_pattern_str, var.replacement_value)
                                modified = True

                                logger.info(
                                    f"Substituted variable in element {element.id}: {var_pattern_str} -> '{var.replacement_value}'"
                                )
                        else:
                            # Case-insensitive matching
                            import re

                            var_pattern_re = re.compile(re.escape(f"${{{var.variable_name}}}"), re.IGNORECASE)
                            if var_pattern_re.search(original_text):
                                # Perform case-insensitive variable substitution
                                original_text = var_pattern_re.sub(var.replacement_value, original_text)
                                modified = True

                                logger.info(
                                    f"Substituted variable (case-insensitive) in element {element.id}: {var.variable_name} -> '{var.replacement_value}'"
                                )

                    if modified:
                        # Validate font for new content
                        font_warning = self._validate_text_font(element, original_text)
                        if font_warning:
                            font_warnings.append(font_warning)

                        # Update element
                        element.text = original_text
                        element.raw_text = original_text
                        modified_count += 1
                    else:
                        skipped_count += 1

        result.modified_elements = modified_count
        result.skipped_elements = skipped_count
        result.font_warnings = font_warnings
        result.details = {
            "variables_applied": len(variables),
            "template_mode": template_mode,
        }

        logger.info(f"Variable substitution completed: {modified_count} modified, {skipped_count} skipped")
        return result

    def validate_document_fonts(
        self,
        document: UniversalDocument,
        check_licensing: bool = True,
    ) -> dict[str, Any]:
        """
        Validate font availability and licensing for the entire document.

        Args:
            document: The document to validate
            check_licensing: Whether to check font licensing compliance

        Returns:
            Dictionary with validation results
        """
        validation_result: dict[str, Any] = {
            "overall_status": "passed",
            "fonts_used": set[str](),
            "fonts_missing": set[str](),
            "fonts_unlicensed": set[str](),
            "elements_with_issues": list[dict[str, Any]](),
        }

        # Collect all fonts used in the document
        for unit in document.document_structure:
            if not isinstance(unit, PageUnit):
                continue

            for layer in unit.layers:
                for element in layer.content:
                    if isinstance(element, TextElement):
                        font_details = element.font_details
                        if isinstance(font_details, dict):
                            font_name = font_details.get("name")
                        else:
                            font_name = font_details.name

                        if font_name:
                            validation_result["fonts_used"].add(font_name)
                        else:
                            # Handle case where font_name is not found
                            continue

                        # Check font availability
                        if not self.font_validator.is_font_available(font_name):
                            validation_result["fonts_missing"].add(font_name)
                            validation_result["elements_with_issues"].append(
                                {
                                    "element_id": element.id,
                                    "page_number": unit.page_number,
                                    "font_name": font_name,
                                    "issue": "font_missing",
                                    "text_sample": (
                                        element.text[:50] + "..." if len(element.text) > 50 else element.text
                                    ),
                                }
                            )

                        # Check licensing if requested (simplified for now)
                        elif check_licensing and font_name not in [
                            "Arial",
                            "Times",
                            "Helvetica",
                        ]:
                            validation_result["fonts_unlicensed"].add(font_name)
                            validation_result["elements_with_issues"].append(
                                {
                                    "element_id": element.id,
                                    "page_number": unit.page_number,
                                    "font_name": font_name,
                                    "issue": "font_unlicensed",
                                    "text_sample": (
                                        element.text[:50] + "..." if len(element.text) > 50 else element.text
                                    ),
                                }
                            )

        # Convert sets to lists for JSON serialization
        validation_result["fonts_used"] = list(validation_result["fonts_used"])
        validation_result["fonts_missing"] = list(validation_result["fonts_missing"])
        validation_result["fonts_unlicensed"] = list(validation_result["fonts_unlicensed"])

        # Determine overall status
        if validation_result["fonts_missing"] or validation_result["fonts_unlicensed"]:
            validation_result["overall_status"] = "failed"

        return validation_result

    def _validate_text_font(self, element: TextElement, new_text: str) -> str | None:
        """
        Validate that the element's font can render the new text.

        Args:
            element: The text element
            new_text: The new text content

        Returns:
            Warning message if validation fails, None otherwise
        """
        # Handle case where font_details might be a dictionary
        font_details = element.font_details
        if isinstance(font_details, dict):
            font_name = font_details.get("name")
        else:
            font_name = font_details.name

        if not font_name:
            return f"No font name found for text: '{new_text[:30]}...'"

        # Check if font is available
        if not self.font_validator.is_font_available(font_name):
            return f"Font '{font_name}' not available for text: '{new_text[:30]}...'"

        # Check glyph coverage (simplified for now)
        # TODO: Implement proper glyph coverage checking
        return None

    def get_substitution_statistics(self, document: UniversalDocument) -> dict[str, Any]:
        """
        Get statistics about variable substitutions in the document.

        Args:
            document: The document to analyze

        Returns:
            Dictionary with substitution statistics
        """
        total_text_elements: int = 0
        elements_with_variables: int = 0
        variable_patterns_found: set[str] = set()
        substitution_opportunities: list[dict[str, Any]] = []

        # Find variable patterns in the document
        for unit in document.document_structure:
            if not isinstance(unit, PageUnit):
                continue

            for layer in unit.layers:
                for element in layer.content:
                    if isinstance(element, TextElement):
                        total_text_elements += 1

                        # Look for variable patterns like ${VARIABLE_NAME}
                        variable_patterns = re.findall(r"\$\{([^}]+)\}", element.text)

                        if variable_patterns:
                            elements_with_variables += 1
                            variable_patterns_found.update(variable_patterns)

                            substitution_opportunities.append(
                                {
                                    "element_id": element.id,
                                    "page_number": unit.page_number,
                                    "variables": variable_patterns,
                                    "text_sample": (
                                        element.text[:100] + "..." if len(element.text) > 100 else element.text
                                    ),
                                }
                            )

        # Build result dict
        return {
            "total_text_elements": total_text_elements,
            "elements_with_variables": elements_with_variables,
            "variable_patterns_found": list(variable_patterns_found),
            "substitution_opportunities": substitution_opportunities,
        }
