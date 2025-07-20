# batch_modifier

Batch modification engine for the Multi-Format Document Engine.

This module provides batch text replacement, variable substitution,
and font validation capabilities for template-based document generation.

## Classes

### BatchModificationResult

Result of a batch modification operation

### VariableSubstitution

Variable substitution configuration

### BatchModifier

Batch modification engine for document content.

Supports:

- Batch text replacement across multiple elements
- Variable substitution for template-based generation
- Font availability and licensing validation

#### Methods

##### __init__(font_validator)

Initialize the batch modifier.

Args:
    font_validator: Optional font validator for licensing checks

##### batch_text_replacement(document, replacements, element_ids, page_numbers, validate_fonts)

Perform batch text replacement across multiple elements.

Args:
    document: The document to modify
    replacements: List of (old_text, new_text) tuples
    element_ids: Optional list of specific element IDs to target
    page_numbers: Optional list of page numbers to target
    validate_fonts: Whether to validate font availability for new text

Returns:
    BatchModificationResult with operation details

##### variable_substitution(document, variables, template_mode)

Perform variable substitution for template-based generation.

Args:
    document: The document template to modify
    variables: List of variable substitutions to apply
    template_mode: Whether to operate in template mode (preserve original structure)

Returns:
    BatchModificationResult with operation details

##### validate_document_fonts(document, check_licensing)

Validate font availability and licensing for the entire document.

Args:
    document: The document to validate
    check_licensing: Whether to check font licensing compliance

Returns:
    Dictionary with validation results

##### _validate_text_font(element, new_text)

Validate that the element's font can render the new text.

Args:
    element: The text element
    new_text: The new text content

Returns:
    Warning message if validation fails, None otherwise

##### get_substitution_statistics(document)

Get statistics about variable substitutions in the document.

Args:
    document: The document to analyze

Returns:
    Dictionary with substitution statistics
