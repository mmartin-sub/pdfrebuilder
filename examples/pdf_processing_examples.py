#!/usr/bin/env python3
"""
PDF Processing Examples

This file contains comprehensive examples showing how to process PDF files
using the Multi-Format Document Engine.
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup - this is necessary for the imports to work
from pdfrebuilder.engine.extract_pdf_content_fitz import extract_pdf_content
from pdfrebuilder.recreate_pdf_from_config import recreate_pdf_from_config
from pdfrebuilder.tools import serialize_pdf_content_to_config


def example_basic_pdf_extraction():
    """
    Example 1: Basic PDF content extraction

    Demonstrates the fundamental workflow of extracting content from a PDF file.
    """
    print("=== Example 1: Basic PDF Extraction ===")

    # Define paths
    input_pdf = project_root / "input" / "sample.pdf"
    output_json = project_root / "examples" / "output" / "basic_extraction.json"

    # Create output directory
    output_json.parent.mkdir(parents=True, exist_ok=True)

    # Check if input file exists
    if not input_pdf.exists():
        print(f"Input file not found: {input_pdf}")
        print("Creating a minimal example with available files...")

        # Look for any PDF files in input directory
        input_dir = project_root / "input"
        if input_dir.exists():
            pdf_files = list(input_dir.glob("*.pdf"))
            if pdf_files:
                input_pdf = pdf_files[0]
                print(f"Using: {input_pdf}")
            else:
                print("No PDF files found in input directory.")
                return
        else:
            print("Input directory does not exist.")
            return

    try:
        # Extract PDF content with basic flags
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
            "include_raw_background_drawings": False,
        }

        print(f"Extracting content from: {input_pdf}")
        document = extract_pdf_content(str(input_pdf), extraction_flags)

        # Save to JSON
        serialize_pdf_content_to_config(document, str(output_json))

        print("✅ Extraction successful!")
        print(f"   Output saved to: {output_json}")

        # Display basic statistics
        if hasattr(document, "document_structure"):
            pages = document.document_structure
            print(f"   Pages extracted: {len(pages)}")

            total_elements = 0
            element_types = {}

            for page in pages:
                if hasattr(page, "layers"):
                    for layer in page.layers:
                        if hasattr(layer, "content"):
                            for element in layer.content:
                                total_elements += 1
                                element_type = type(element).__name__
                                element_types[element_type] = element_types.get(element_type, 0) + 1

            print(f"   Total elements: {total_elements}")
            for elem_type, count in element_types.items():
                print(f"     {elem_type}: {count}")

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("This might be due to:")
        print("  - Unsupported PDF format")
        print("  - Missing dependencies")
        print("  - Corrupted PDF file")


def example_advanced_pdf_extraction():
    """
    Example 2: Advanced PDF extraction with all options

    Shows how to use advanced extraction options and handle complex PDFs.
    """
    print("\n=== Example 2: Advanced PDF Extraction ===")

    input_pdf = project_root / "input" / "sample.pdf"
    output_json = project_root / "examples" / "output" / "advanced_extraction.json"

    # Create output directory
    output_json.parent.mkdir(parents=True, exist_ok=True)

    if not input_pdf.exists():
        # Try to find any PDF file
        input_dir = project_root / "input"
        if input_dir.exists():
            pdf_files = list(input_dir.glob("*.pdf"))
            if pdf_files:
                input_pdf = pdf_files[0]
            else:
                print("No PDF files available for advanced extraction example.")
                return
        else:
            print("Input directory not found.")
            return

    try:
        # Advanced extraction flags
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
            "include_raw_background_drawings": True,  # Include background graphics
            "extract_fonts": True,  # Extract font information
            "preserve_whitespace": True,  # Preserve text spacing
            "extract_metadata": True,  # Extract document metadata
        }

        print(f"Performing advanced extraction on: {input_pdf}")
        print("Advanced options enabled:")
        for flag, enabled in extraction_flags.items():
            if enabled:
                print(f"  ✓ {flag}")

        document = extract_pdf_content(str(input_pdf), extraction_flags)

        # Save with pretty formatting
        serialize_pdf_content_to_config(document, str(output_json))

        print("✅ Advanced extraction completed!")
        print(f"   Output: {output_json}")

        # Show detailed analysis
        if hasattr(document, "metadata") and document.metadata:
            print("   Document metadata:")
            metadata = document.metadata
            if hasattr(metadata, "title") and metadata.title:
                print(f"     Title: {metadata.title}")
            if hasattr(metadata, "author") and metadata.author:
                print(f"     Author: {metadata.author}")
            if hasattr(metadata, "format") and metadata.format:
                print(f"     Format: {metadata.format}")

        # Analyze extracted content
        if hasattr(document, "document_structure"):
            print("   Content analysis:")

            for i, page in enumerate(document.document_structure):
                print(f"     Page {i + 1}:")
                if hasattr(page, "size"):
                    print(f"       Size: {page.size}")

                if hasattr(page, "layers"):
                    for layer in page.layers:
                        if hasattr(layer, "content") and layer.content:
                            print(f"       Layer '{layer.layer_name}': {len(layer.content)} elements")

                            # Show element details
                            text_elements = [e for e in layer.content if hasattr(e, "text")]
                            image_elements = [e for e in layer.content if hasattr(e, "image_file")]
                            drawing_elements = [e for e in layer.content if hasattr(e, "drawing_commands")]

                            if text_elements:
                                print(f"         Text elements: {len(text_elements)}")
                                # Show first text element as example
                                first_text = text_elements[0]
                                if hasattr(first_text, "text"):
                                    sample_text = (
                                        first_text.text[:50] + "..." if len(first_text.text) > 50 else first_text.text
                                    )
                                    print(f"         Sample text: '{sample_text}'")

                            if image_elements:
                                print(f"         Image elements: {len(image_elements)}")

                            if drawing_elements:
                                print(f"         Drawing elements: {len(drawing_elements)}")

    except Exception as e:
        print(f"❌ Advanced extraction failed: {e}")
        import traceback

        traceback.print_exc()


def example_pdf_reconstruction():
    """
    Example 3: PDF reconstruction from JSON

    Shows how to rebuild a PDF from extracted JSON configuration.
    """
    print("\n=== Example 3: PDF Reconstruction ===")

    # Use the output from basic extraction
    input_json = project_root / "examples" / "output" / "basic_extraction.json"
    output_pdf = project_root / "examples" / "output" / "reconstructed.pdf"

    # Create output directory
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    if not input_json.exists():
        print(f"Input JSON not found: {input_json}")
        print("Please run the basic extraction example first.")
        return

    try:
        print(f"Reconstructing PDF from: {input_json}")

        # Load the JSON configuration
        with open(input_json, encoding="utf-8") as f:
            config_data = json.load(f)

        # Reconstruct the PDF
        recreate_pdf_from_config(str(input_json), str(output_pdf))

        print("✅ PDF reconstruction completed!")
        print(f"   Output PDF: {output_pdf}")

        # Check if the file was created and get its size
        if output_pdf.exists():
            file_size = output_pdf.stat().st_size
            print(f"   File size: {file_size:,} bytes")

        # Show configuration summary
        if isinstance(config_data, dict):
            if "document_structure" in config_data:
                pages = config_data["document_structure"]
                print(f"   Reconstructed {len(pages)} pages")

            if config_data.get("metadata"):
                print("   Document metadata preserved")

    except Exception as e:
        print(f"❌ PDF reconstruction failed: {e}")
        print("Common causes:")
        print("  - Invalid JSON configuration")
        print("  - Missing image files")
        print("  - Font issues")
        print("  - Insufficient permissions")


def example_pdf_modification():
    """
    Example 4: PDF modification workflow

    Demonstrates extracting, modifying, and rebuilding a PDF.
    """
    print("\n=== Example 4: PDF Modification Workflow ===")

    input_pdf = project_root / "input" / "sample.pdf"
    temp_json = project_root / "examples" / "output" / "temp_modification.json"
    output_pdf = project_root / "examples" / "output" / "modified.pdf"

    # Create output directory
    temp_json.parent.mkdir(parents=True, exist_ok=True)

    if not input_pdf.exists():
        # Try to find any PDF file
        input_dir = project_root / "input"
        if input_dir.exists():
            pdf_files = list(input_dir.glob("*.pdf"))
            if pdf_files:
                input_pdf = pdf_files[0]
            else:
                print("No PDF files available for modification example.")
                return
        else:
            print("Input directory not found.")
            return

    try:
        print(f"Starting modification workflow with: {input_pdf}")

        # Step 1: Extract content
        print("Step 1: Extracting content...")
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
        }

        document = extract_pdf_content(str(input_pdf), extraction_flags)
        serialize_pdf_content_to_config(document, str(temp_json))

        # Step 2: Modify the JSON configuration
        print("Step 2: Modifying content...")

        with open(temp_json, encoding="utf-8") as f:
            config_data = json.load(f)

        modifications_made = 0

        # Example modification: Change text content
        if "document_structure" in config_data:
            for page in config_data["document_structure"]:
                if "layers" in page:
                    for layer in page["layers"]:
                        if "content" in layer:
                            for element in layer["content"]:
                                if element.get("type") == "text" and "text" in element:
                                    # Example: Add a prefix to text elements
                                    original_text = element["text"]
                                    if not original_text.startswith("[MODIFIED]"):
                                        element["text"] = f"[MODIFIED] {original_text}"
                                        modifications_made += 1

                                        # Also update raw_text if it exists
                                        if "raw_text" in element:
                                            element["raw_text"] = f"[MODIFIED] {element['raw_text']}"

        print(f"   Modified {modifications_made} text elements")

        # Save modified configuration
        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        # Step 3: Rebuild PDF
        print("Step 3: Rebuilding PDF...")
        recreate_pdf_from_config(str(temp_json), str(output_pdf))

        print("✅ Modification workflow completed!")
        print(f"   Original PDF: {input_pdf}")
        print(f"   Modified PDF: {output_pdf}")
        print(f"   Modifications: {modifications_made} text elements prefixed")

        # Compare file sizes
        if input_pdf.exists() and output_pdf.exists():
            original_size = input_pdf.stat().st_size
            modified_size = output_pdf.stat().st_size
            print(f"   File sizes: {original_size:,} → {modified_size:,} bytes")

    except Exception as e:
        print(f"❌ Modification workflow failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up temporary file
        if temp_json.exists():
            temp_json.unlink()


def example_pdf_analysis():
    """
    Example 5: PDF content analysis

    Shows how to analyze PDF content without reconstruction.
    """
    print("\n=== Example 5: PDF Content Analysis ===")

    input_pdf = project_root / "input" / "sample.pdf"

    if not input_pdf.exists():
        # Try to find any PDF file
        input_dir = project_root / "input"
        if input_dir.exists():
            pdf_files = list(input_dir.glob("*.pdf"))
            if pdf_files:
                input_pdf = pdf_files[0]
            else:
                print("No PDF files available for analysis.")
                return
        else:
            print("Input directory not found.")
            return

    try:
        print(f"Analyzing PDF content: {input_pdf}")

        # Extract with full analysis
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
            "include_raw_background_drawings": True,
        }

        document = extract_pdf_content(str(input_pdf), extraction_flags)

        # Perform detailed analysis
        analysis_results = {
            "total_pages": 0,
            "total_elements": 0,
            "text_elements": 0,
            "image_elements": 0,
            "drawing_elements": 0,
            "fonts_used": set(),
            "colors_used": set(),
            "page_sizes": [],
            "text_content_length": 0,
            "languages_detected": set(),
        }

        if hasattr(document, "document_structure"):
            analysis_results["total_pages"] = len(document.document_structure)

            for page in document.document_structure:
                if hasattr(page, "size"):
                    analysis_results["page_sizes"].append(page.size)

                if hasattr(page, "layers"):
                    for layer in page.layers:
                        if hasattr(layer, "content"):
                            for element in layer.content:
                                analysis_results["total_elements"] += 1

                                # Analyze by element type
                                if hasattr(element, "text"):
                                    analysis_results["text_elements"] += 1
                                    analysis_results["text_content_length"] += len(element.text)

                                    # Extract font information
                                    if hasattr(element, "font_details") and element.font_details:
                                        if hasattr(element.font_details, "name"):
                                            analysis_results["fonts_used"].add(element.font_details.name)

                                        # Extract color information
                                        if hasattr(element.font_details, "color"):
                                            analysis_results["colors_used"].add(str(element.font_details.color))

                                elif hasattr(element, "image_file"):
                                    analysis_results["image_elements"] += 1

                                elif hasattr(element, "drawing_commands"):
                                    analysis_results["drawing_elements"] += 1

        # Display analysis results
        print("✅ Analysis completed!")
        print("   Document Statistics:")
        print(f"     Total pages: {analysis_results['total_pages']}")
        print(f"     Total elements: {analysis_results['total_elements']}")
        print(f"     Text elements: {analysis_results['text_elements']}")
        print(f"     Image elements: {analysis_results['image_elements']}")
        print(f"     Drawing elements: {analysis_results['drawing_elements']}")
        print(f"     Total text length: {analysis_results['text_content_length']:,} characters")

        if analysis_results["fonts_used"]:
            print(f"     Fonts used: {len(analysis_results['fonts_used'])}")
            for font in sorted(analysis_results["fonts_used"]):
                print(f"       - {font}")

        if analysis_results["page_sizes"]:
            unique_sizes = list(
                {tuple(size) if isinstance(size, list | tuple) else size for size in analysis_results["page_sizes"]}
            )
            print(f"     Page sizes: {len(unique_sizes)} unique")
            for size in unique_sizes:
                print(f"       - {size}")

        # Save analysis report
        report_file = project_root / "examples" / "output" / "pdf_analysis_report.json"

        # Convert sets to lists for JSON serialization
        serializable_results = analysis_results.copy()
        serializable_results["fonts_used"] = list(analysis_results["fonts_used"])
        serializable_results["colors_used"] = list(analysis_results["colors_used"])
        serializable_results["languages_detected"] = list(analysis_results["languages_detected"])

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        print(f"   Analysis report saved to: {report_file}")

    except Exception as e:
        print(f"❌ PDF analysis failed: {e}")
        import traceback

        traceback.print_exc()


def main():
    """
    Run all PDF processing examples
    """
    print("PDF Processing Examples")
    print("=" * 50)

    # Ensure output directory exists
    output_dir = project_root / "examples" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run all examples
    examples = [
        example_basic_pdf_extraction,
        example_advanced_pdf_extraction,
        example_pdf_reconstruction,
        example_pdf_modification,
        example_pdf_analysis,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 50)
    print("All PDF processing examples completed!")
    print(f"Check the output directory: {output_dir}")


if __name__ == "__main__":
    main()
