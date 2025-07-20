#!/usr/bin/env python3
"""
API Usage Examples for Multi-Format Document Engine

This file contains comprehensive examples showing how to use the various APIs
provided by the Multi-Format Document Engine.
"""

import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_pdf_extraction():
    """
    Example 1: Basic PDF content extraction

    Shows how to extract content from a PDF file using the Universal IDM format.
    """
    print("=== Example 1: Basic PDF Extraction ===")

    try:
        from src.engine.extract_pdf_content_fitz import extract_pdf_content

        # Extract PDF content
        input_file = "input/sample.pdf"
        if not Path(input_file).exists():
            print(f"Sample file {input_file} not found. Skipping example.")
            return

        document = extract_pdf_content(input_file)

        # Display document information
        print(f"Document version: {document.version}")
        print(f"Engine: {document.engine} v{document.engine_version}")
        print(f"Pages: {len(document.document_structure)}")

        # Iterate through pages
        for i, page in enumerate(document.document_structure):
            print(f"\nPage {i + 1}:")
            print(f"  Size: {page.size}")
            print(f"  Layers: {len(page.layers)}")

            # Show layer content
            for layer in page.layers:
                print(f"    Layer '{layer.layer_name}': {len(layer.content)} elements")

                # Show element types
                element_types = {}
                for element in layer.content:
                    element_type = type(element).__name__
                    element_types[element_type] = element_types.get(element_type, 0) + 1

                for elem_type, count in element_types.items():
                    print(f"      {elem_type}: {count}")

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"Error during PDF extraction: {e}")


def example_universal_idm_manipulation():
    """
    Example 2: Working with Universal IDM data structures

    Shows how to create, modify, and serialize Universal IDM documents.
    """
    print("\n=== Example 2: Universal IDM Manipulation ===")

    try:
        from src.models.universal_idm import (
            BoundingBox,
            Color,
            DocumentMetadata,
            FontDetails,
            ImageElement,
            Layer,
            LayerType,
            PageUnit,
            TextElement,
            UniversalDocument,
        )

        # Create a new document
        metadata = DocumentMetadata(title="Example Document", author="API Example", format="Custom")

        document = UniversalDocument(engine="example_engine", engine_version="1.0", metadata=metadata)

        # Create a page
        page = PageUnit(
            size=(612, 792),  # Letter size
            page_number=1,
        )

        # Create a layer
        layer = Layer(
            layer_id="main_content",
            layer_name="Main Content",
            layer_type=LayerType.BASE,
            bbox=BoundingBox(0, 0, 612, 792),
        )

        # Create text element
        font_details = FontDetails(
            name="Arial",
            size=12.0,
            color=Color(0, 0, 0, 1),  # Black
            ascender=10.0,
            descender=-2.0,
            is_bold=False,
            is_italic=False,
            is_serif=False,
            is_monospaced=False,
            is_superscript=False,
            original_flags=0,
        )

        text_element = TextElement(
            id="text_1",
            bbox=BoundingBox(50, 700, 300, 720),
            raw_text="Hello, World!",
            text="Hello, World!",
            font_details=font_details,
        )

        # Create image element
        image_element = ImageElement(
            id="image_1",
            bbox=BoundingBox(50, 500, 250, 650),
            image_file="./images/example.jpg",
        )

        # Assemble the document structure
        layer.content = [text_element, image_element]
        page.layers = [layer]
        document.document_structure = [page]

        # Convert to JSON
        json_output = document.to_json(indent=2)
        print("Document JSON structure (first 500 chars):")
        print(json_output[:500] + "..." if len(json_output) > 500 else json_output)

        # Save to file
        output_path = Path("output/example_document.json")
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            f.write(json_output)

        print(f"\nDocument saved to: {output_path}")

        # Load back from JSON
        loaded_document = UniversalDocument.from_json(json_output)
        print(f"Loaded document has {len(loaded_document.document_structure)} pages")

    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error during IDM manipulation: {e}")


def example_document_parsing():
    """
    Example 3: Using the universal document parser

    Shows how to use the document parser interface to parse different formats.
    """
    print("\n=== Example 3: Universal Document Parsing ===")

    try:
        from src.engine.document_parser import parse_document

        # List of sample files to try
        sample_files = ["input/sample.pdf", "input/sample.psd", "input/example.pdf"]

        for file_path in sample_files:
            if not Path(file_path).exists():
                print(f"File {file_path} not found, skipping...")
                continue

            print(f"\nParsing: {file_path}")

            try:
                document, manifest = parse_document(file_path)

                print(f"  Format: {document.metadata.format if document.metadata else 'Unknown'}")
                print(f"  Engine: {document.engine}")
                print(f"  Document units: {len(document.document_structure)}")

                # Show asset manifest
                print("  Extracted assets:")
                print(f"    Images: {len(manifest.images)}")
                print(f"    Fonts: {len(manifest.fonts)}")
                print(f"    Other: {len(manifest.other_assets)}")

                # Show first few images
                for i, image in enumerate(manifest.images[:3]):
                    print(f"      Image {i + 1}: {image['path']}")

            except Exception as e:
                print(f"  Error parsing {file_path}: {e}")

    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error during document parsing: {e}")


def example_configuration_management():
    """
    Example 4: Configuration management

    Shows how to work with the configuration system.
    """
    print("\n=== Example 4: Configuration Management ===")

    try:
        from src.settings import get_config_value, set_config_value

        # Display current configuration
        print("Current configuration (selected values):")

        config_keys = [
            "image_dir",
            "fonts_dir",
            "visual_diff_threshold",
            "default_font",
            "debug_font",
        ]

        for key in config_keys:
            value = get_config_value(key)
            print(f"  {key}: {value}")

        # Modify configuration
        print("\nModifying configuration...")
        original_threshold = get_config_value("visual_diff_threshold")
        set_config_value("visual_diff_threshold", 10)

        print(
            f"  visual_diff_threshold changed from {original_threshold} to {get_config_value('visual_diff_threshold')}"
        )

        # Restore original value
        set_config_value("visual_diff_threshold", original_threshold)
        print(f"  Restored to original value: {get_config_value('visual_diff_threshold')}")

        # Show dynamic path resolution
        print("\nDynamic path resolution:")
        image_dir = get_config_value("image_dir")
        print(f"  Image directory: {image_dir}")

    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error during configuration management: {e}")


def example_visual_validation():
    """
    Example 5: Visual validation and comparison

    Shows how to use visual validation tools.
    """
    print("\n=== Example 5: Visual Validation ===")

    try:
        from src.compare_pdfs_visual import compare_pdfs_visual
        from src.engine.visual_validator import VisualValidator
        from src.settings import get_config_value

        # Sample PDF files for comparison
        original_pdf = "input/sample.pdf"
        rebuilt_pdf = "output/rebuilt.pdf"

        if not all(Path(f).exists() for f in [original_pdf, rebuilt_pdf]):
            print("Sample PDF files not found. Creating mock comparison...")

            # Show how to use the visual validator
            validator = VisualValidator()
            print(f"Visual validator initialized with threshold: {validator.threshold}")

            # Example of validation configuration
            print("Validation configuration options:")
            print("  - threshold: Pixel difference threshold for validation")
            print("  - ssim_threshold: Structural similarity threshold")
            print("  - ignore_regions: Regions to ignore during comparison")

            return

        # Perform visual comparison
        print(f"Comparing {original_pdf} with {rebuilt_pdf}")

        result = compare_pdfs_visual(original_pdf, rebuilt_pdf)

        if result:
            print("Visual comparison completed successfully")
            print(f"Difference image saved to: {get_config_value('diff_image')}")
        else:
            print("Visual comparison failed or files are identical")

    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error during visual validation: {e}")


def example_batch_processing():
    """
    Example 6: Batch processing multiple documents

    Shows how to process multiple documents efficiently.
    """
    print("\n=== Example 6: Batch Processing ===")

    try:
        import glob

        from src.engine.document_parser import parse_document

        # Find all PDF files in input directory
        input_pattern = "input/*.pdf"
        pdf_files = glob.glob(input_pattern)

        if not pdf_files:
            print(f"No PDF files found matching {input_pattern}")
            print("Creating example batch processing workflow...")

            # Show batch processing concepts
            print("Batch processing workflow:")
            print("1. Scan input directory for supported files")
            print("2. Parse each file using appropriate parser")
            print("3. Apply modifications or transformations")
            print("4. Generate outputs in desired formats")
            print("5. Create summary report")

            return

        print(f"Found {len(pdf_files)} PDF files to process")

        # Process each file
        results = []
        for pdf_file in pdf_files[:3]:  # Limit to first 3 files
            print(f"\nProcessing: {pdf_file}")

            try:
                document, manifest = parse_document(pdf_file)

                result = {
                    "file": pdf_file,
                    "success": True,
                    "pages": len(document.document_structure),
                    "images": len(manifest.images),
                    "fonts": len(manifest.fonts),
                }

                print(f"  Success: {result['pages']} pages, {result['images']} images")

            except Exception as e:
                result = {"file": pdf_file, "success": False, "error": str(e)}
                print(f"  Error: {e}")

            results.append(result)

        # Summary report
        print("\n=== Batch Processing Summary ===")
        successful = sum(1 for r in results if r["success"])
        print(f"Processed: {len(results)} files")
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")

        if successful > 0:
            total_pages = sum(r.get("pages", 0) for r in results if r["success"])
            total_images = sum(r.get("images", 0) for r in results if r["success"])
            print(f"Total pages: {total_pages}")
            print(f"Total images: {total_images}")

    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error during batch processing: {e}")


def main():
    """
    Run all API usage examples
    """
    print("Multi-Format Document Engine - API Usage Examples")
    print("=" * 60)

    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)

    # Run examples
    examples = [
        example_basic_pdf_extraction,
        example_universal_idm_manipulation,
        example_document_parsing,
        example_configuration_management,
        example_visual_validation,
        example_batch_processing,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error running {example_func.__name__}: {e}")

        print()  # Add spacing between examples

    print("=" * 60)
    print("All examples completed!")


if __name__ == "__main__":
    main()
