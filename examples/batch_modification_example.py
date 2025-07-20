#!/usr/bin/env python3
"""
Example script demonstrating batch modification capabilities.

This script shows how to use the batch modification engine for:
- Batch text replacement
- Variable substitution
- Font validation
"""

import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup - required for src module access
from pdfrebuilder.engine.batch_modifier import BatchModifier, VariableSubstitution
from pdfrebuilder.models.universal_idm import (
    BlendMode,
    BoundingBox,
    Color,
    DocumentMetadata,
    FontDetails,
    Layer,
    LayerType,
    PageUnit,
    TextElement,
    UniversalDocument,
)


def create_sample_document() -> UniversalDocument:
    """Create a sample document for demonstration."""
    # Create text elements with variables
    text_elements = [
        TextElement(
            id="header",
            bbox=BoundingBox(50, 50, 550, 100),
            raw_text="Welcome to ${COMPANY_NAME}",
            text="Welcome to ${COMPANY_NAME}",
            font_details=FontDetails(name="Arial", size=24, color=Color(0, 0, 0)),
            z_index=1,
        ),
        TextElement(
            id="subtitle",
            bbox=BoundingBox(50, 120, 550, 150),
            raw_text="Invoice #${INVOICE_NUMBER}",
            text="Invoice #${INVOICE_NUMBER}",
            font_details=FontDetails(name="Arial", size=16, color=Color(0.5, 0.5, 0.5)),
            z_index=2,
        ),
        TextElement(
            id="date",
            bbox=BoundingBox(50, 180, 550, 200),
            raw_text="Date: ${INVOICE_DATE}",
            text="Date: ${INVOICE_DATE}",
            font_details=FontDetails(name="Arial", size=12, color=Color(0, 0, 0)),
            z_index=3,
        ),
        TextElement(
            id="amount",
            bbox=BoundingBox(50, 250, 550, 280),
            raw_text="Total Amount: ${TOTAL_AMOUNT}",
            text="Total Amount: ${TOTAL_AMOUNT}",
            font_details=FontDetails(name="Arial", size=18, color=Color(0, 0, 0)),
            z_index=4,
        ),
    ]

    # Create a layer
    layer = Layer(
        layer_id="main_content",
        layer_name="Main Content",
        layer_type=LayerType.BASE,
        bbox=BoundingBox(0, 0, 600, 400),
        visibility=True,
        opacity=1.0,
        blend_mode=BlendMode.NORMAL,
        children=[],
        content=text_elements,
    )

    # Create a page
    page = PageUnit(
        size=(600, 400),
        background_color=None,
        layers=[layer],
        page_number=0,
    )

    # Create document
    document = UniversalDocument(
        metadata=DocumentMetadata(format="pdf", title="Invoice Template"),
        document_structure=[page],
    )

    return document


def demonstrate_batch_text_replacement():
    """Demonstrate batch text replacement."""
    print("=== Batch Text Replacement Demo ===")

    # Create sample document
    document = create_sample_document()

    # Create batch modifier
    modifier = BatchModifier()

    # Define replacements
    replacements = [
        ("Welcome to", "Hello from"),
        ("Invoice #", "Receipt #"),
    ]

    # Perform batch replacement
    result = modifier.batch_text_replacement(
        document=document,
        replacements=replacements,
        validate_fonts=False,  # Skip font validation for demo
    )

    print(f"Modified elements: {result.modified_elements}")
    print(f"Skipped elements: {result.skipped_elements}")
    print(f"Font warnings: {len(result.font_warnings)}")

    # Show modified content
    text_elements = document.document_structure[0].layers[0].content
    for element in text_elements:
        print(f"  {element.id}: {element.text}")

    print()


def demonstrate_variable_substitution():
    """Demonstrate variable substitution."""
    print("=== Variable Substitution Demo ===")

    # Create sample document
    document = create_sample_document()

    # Create batch modifier
    modifier = BatchModifier()

    # Define variables
    variables = [
        VariableSubstitution(variable_name="COMPANY_NAME", replacement_value="Acme Corporation"),
        VariableSubstitution(variable_name="INVOICE_NUMBER", replacement_value="INV-2024-001"),
        VariableSubstitution(variable_name="INVOICE_DATE", replacement_value="2024-01-15"),
        VariableSubstitution(variable_name="TOTAL_AMOUNT", replacement_value="$1,250.00"),
    ]

    # Perform variable substitution
    result = modifier.variable_substitution(
        document=document,
        variables=variables,
    )

    print(f"Modified elements: {result.modified_elements}")
    print(f"Skipped elements: {result.skipped_elements}")
    print(f"Font warnings: {len(result.font_warnings)}")

    # Show substituted content
    text_elements = document.document_structure[0].layers[0].content
    for element in text_elements:
        print(f"  {element.id}: {element.text}")

    print()


def demonstrate_font_validation():
    """Demonstrate font validation."""
    print("=== Font Validation Demo ===")

    # Create sample document
    document = create_sample_document()

    # Create batch modifier
    modifier = BatchModifier()

    # Perform font validation
    validation_result = modifier.validate_document_fonts(
        document=document,
        check_licensing=True,
    )

    print(f"Overall status: {validation_result['overall_status']}")
    print(f"Fonts used: {validation_result['fonts_used']}")
    print(f"Fonts missing: {validation_result['fonts_missing']}")
    print(f"Fonts unlicensed: {validation_result['fonts_unlicensed']}")
    print(f"Elements with issues: {len(validation_result['elements_with_issues'])}")

    if validation_result["elements_with_issues"]:
        print("\nIssues found:")
        for issue in validation_result["elements_with_issues"]:
            print(f"  - Element {issue['element_id']}: {issue['issue']} - {issue['font_name']}")

    print()


def demonstrate_substitution_statistics():
    """Demonstrate substitution statistics."""
    print("=== Substitution Statistics Demo ===")

    # Create sample document
    document = create_sample_document()

    # Create batch modifier
    modifier = BatchModifier()

    # Get statistics
    stats = modifier.get_substitution_statistics(document)

    print(f"Total text elements: {stats['total_text_elements']}")
    print(f"Elements with variables: {stats['elements_with_variables']}")
    print(f"Variable patterns found: {stats['variable_patterns_found']}")

    if stats["substitution_opportunities"]:
        print("\nSubstitution opportunities:")
        for opp in stats["substitution_opportunities"]:
            print(f"  - Element {opp['element_id']}: {opp['variables']}")
            print(f"    Text: {opp['text_sample']}")

    print()


def save_document_to_json(document: UniversalDocument, filename: str):
    """Save document to JSON file."""
    output_dir = Path("examples/output")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"Document saved to: {output_path}")


def main():
    """Main demonstration function."""
    print("Batch Modification Engine Demo")
    print("=" * 50)

    # Demonstrate each feature
    demonstrate_batch_text_replacement()
    demonstrate_variable_substitution()
    demonstrate_font_validation()
    demonstrate_substitution_statistics()

    # Create and save a sample document
    print("=== Saving Sample Document ===")
    document = create_sample_document()
    save_document_to_json(document, "invoice_template.json")

    print("\nDemo completed! Check the 'examples/output' directory for generated files.")


if __name__ == "__main__":
    main()
