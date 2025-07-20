"""
CLI interface for testing ReportLab engine functionality.
"""

import argparse
import json
import logging
import sys

from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector, get_pdf_engine
from pdfrebuilder.models.universal_idm import (
    BlendMode,
    BoundingBox,
    Color,
    DocumentMetadata,
    DrawingElement,
    FontDetails,
    ImageElement,
    Layer,
    LayerType,
    PageUnit,
    TextElement,
    UniversalDocument,
)
from pdfrebuilder.settings import configure_logging


def create_test_document() -> UniversalDocument:
    """Create a test document for ReportLab engine testing."""
    # Create text elements
    text_elements: list[TextElement | ImageElement | DrawingElement] = [
        TextElement(
            id="title",
            bbox=BoundingBox(50, 50, 550, 100),
            raw_text="ReportLab Engine Test",
            text="ReportLab Engine Test",
            font_details=FontDetails(name="Helvetica", size=24, color=Color(0, 0, 0)),
            z_index=1,
        ),
        TextElement(
            id="subtitle",
            bbox=BoundingBox(50, 120, 550, 150),
            raw_text="Testing enhanced precision and font embedding",
            text="Testing enhanced precision and font embedding",
            font_details=FontDetails(name="Helvetica", size=16, color=Color(0.5, 0.5, 0.5)),
            z_index=2,
        ),
        TextElement(
            id="variable_test",
            bbox=BoundingBox(50, 180, 550, 200),
            raw_text="Variable: ${TEST_VARIABLE}",
            text="Variable: ${TEST_VARIABLE}",
            font_details=FontDetails(name="Helvetica", size=12, color=Color(0, 0, 0)),
            z_index=3,
        ),
    ]

    # Create layer
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

    # Create page
    page = PageUnit(
        size=(600, 400),
        background_color=None,
        layers=[layer],
        page_number=0,
    )

    # Create document
    document = UniversalDocument(
        metadata=DocumentMetadata(format="pdf", title="ReportLab Test Document"),
        document_structure=[page],
    )

    return document


def run_engine_info(args: argparse.Namespace) -> None:
    """Test engine information and capabilities."""
    print("=== ReportLab Engine Information ===")

    try:
        # Get engine selector
        selector = get_engine_selector()

        # List available engines
        engines = selector.list_available_engines()
        print(f"Available engines: {list(engines.keys())}")

        # Get ReportLab engine info
        reportlab_engine = get_pdf_engine("reportlab")
        info = reportlab_engine.get_engine_info()

        print(f"Engine: {info['engine']}")
        print(f"Version: {info['version']}")
        print(f"Supported features: {info['supported_features']}")
        print(f"Registered fonts: {info['registered_fonts']}")

    except Exception as e:
        print(f"Error getting engine info: {e}")


def run_font_validation(args: argparse.Namespace) -> None:
    """Test font validation and licensing."""
    print("=== Font Validation Test ===")

    try:
        engine = get_pdf_engine("reportlab")

        # Test fonts
        test_fonts = ["Helvetica", "Arial", "Times", "Courier", "Roboto"]

        for font_name in test_fonts:
            result = engine.validate_font_licensing(font_name)
            print(f"Font: {font_name}")
            print(f"  Available: {result['available']}")
            print(f"  Embeddable: {result['embeddable']}")
            print(f"  Status: {result['status']}")
            print(f"  Reason: {result['reason']}")
            print()

    except Exception as e:
        print(f"Error testing font validation: {e}")


def run_pdf_generation(args: argparse.Namespace) -> None:
    """Test PDF generation with ReportLab engine."""
    print("=== PDF Generation Test ===")

    try:
        # Create test document
        document = create_test_document()

        # Get engine
        engine = get_pdf_engine("reportlab")

        # Generate PDF
        output_path = args.output or "reportlab_test_output.pdf"
        engine.generate(document.to_dict(), output_path)

        print(f"PDF generated successfully: {output_path}")

        # Save document JSON for inspection
        json_path = output_path.replace(".pdf", ".json")
        with open(json_path, "w") as f:
            json.dump(document.to_dict(), f, indent=2)
        print(f"Document JSON saved: {json_path}")

    except Exception as e:
        print(f"Error generating PDF: {e}")


def run_engine_comparison(args: argparse.Namespace) -> None:
    """Compare ReportLab and PyMuPDF engines."""
    print("=== Engine Comparison ===")

    try:
        selector = get_engine_selector()
        comparison = selector.compare_engines("reportlab", "pymupdf")

        if "error" in comparison:
            print(f"Error comparing engines: {comparison['error']}")
            return

        print("Engine 1 (ReportLab):")
        print(f"  Name: {comparison['engine1']['name']}")
        print(f"  Version: {comparison['engine1']['version']}")
        print(f"  Features: {comparison['engine1']['features']}")

        print("\nEngine 2 (PyMuPDF):")
        print(f"  Name: {comparison['engine2']['name']}")
        print(f"  Version: {comparison['engine2']['version']}")
        print(f"  Features: {comparison['engine2']['features']}")

        if comparison["differences"]:
            print("\nFeature Differences:")
            for feature, diff in comparison["differences"].items():
                print(f"  {feature}: ReportLab={diff['engine1']}, PyMuPDF={diff['engine2']}")
        else:
            print("\nNo feature differences found.")

    except Exception as e:
        print(f"Error comparing engines: {e}")


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Test ReportLab engine functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info                    # Show engine information
  %(prog)s fonts                   # Test font validation
  %(prog)s generate --output test.pdf  # Generate test PDF
  %(prog)s compare                 # Compare engines
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Show engine information")

    # Fonts command
    subparsers.add_parser("fonts", help="Test font validation")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate test PDF")
    generate_parser.add_argument(
        "--output",
        "-o",
        help="Output PDF file path",
        default="reportlab_test_output.pdf",
    )

    # Compare command
    subparsers.add_parser("compare", help="Compare engines")

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    configure_logging(log_level=logging.INFO)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "info":
            run_engine_info(args)
        elif args.command == "fonts":
            run_font_validation(args)
        elif args.command == "generate":
            run_pdf_generation(args)
        elif args.command == "compare":
            run_engine_comparison(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
