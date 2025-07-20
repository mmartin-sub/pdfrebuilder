#!/usr/bin/env python3
"""
PSD Processing Examples

This file contains examples showing how to process PSD files
using the Multi-Format Document Engine. Note that PSD support
is currently in development.
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from pdfrebuilder.engine.extract_psd_content import extract_psd_content

    PSD_SUPPORT_AVAILABLE = True
except ImportError as e:
    print(f"PSD support not fully available: {e}")
    PSD_SUPPORT_AVAILABLE = False


def example_basic_psd_extraction():
    """
    Example 1: Basic PSD content extraction

    Demonstrates the fundamental workflow of extracting content from a PSD file.
    """
    print("=== Example 1: Basic PSD Extraction ===")

    if not PSD_SUPPORT_AVAILABLE:
        print("❌ PSD support is not available in this build.")
        print("This example shows the intended interface for PSD processing.")
        print("To enable PSD support, install the required dependencies:")
        print("  pip install psd-tools3")
        return

    # Define paths
    input_psd = project_root / "input" / "sample.psd"
    output_json = project_root / "examples" / "output" / "psd_extraction.json"

    # Create output directory
    output_json.parent.mkdir(parents=True, exist_ok=True)

    # Check if input file exists
    if not input_psd.exists():
        print(f"Input file not found: {input_psd}")
        print("Looking for PSD files in input directory...")

        # Look for any PSD files in input directory
        input_dir = project_root / "input"
        if input_dir.exists():
            psd_files = list(input_dir.glob("*.psd"))
            if psd_files:
                input_psd = psd_files[0]
                print(f"Using: {input_psd}")
            else:
                print("No PSD files found in input directory.")
                print("This example demonstrates the intended PSD processing interface.")
                _demonstrate_psd_interface()
                return
        else:
            print("Input directory does not exist.")
            return

    try:
        # Extract PSD content with basic flags
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_shapes": True,
            "include_effects": True,
            "flatten_groups": False,  # Preserve layer hierarchy
            "extract_hidden_layers": False,  # Skip hidden layers
        }

        print(f"Extracting content from: {input_psd}")
        document = extract_psd_content(str(input_psd), extraction_flags)

        # Save to JSON
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

        print("✅ Extraction successful!")
        print(f"   Output saved to: {output_json}")

        # Display basic statistics
        if hasattr(document, "document_structure"):
            canvases = document.document_structure
            print(f"   Canvases extracted: {len(canvases)}")

            total_layers = 0
            total_elements = 0
            layer_types = {}

            for canvas in canvases:
                if hasattr(canvas, "layers"):
                    total_layers += len(canvas.layers)

                    for layer in canvas.layers:
                        layer_type = layer.layer_type if hasattr(layer, "layer_type") else "unknown"
                        layer_types[layer_type] = layer_types.get(layer_type, 0) + 1

                        if hasattr(layer, "content"):
                            total_elements += len(layer.content)

            print(f"   Total layers: {total_layers}")
            print(f"   Total elements: {total_elements}")
            print("   Layer types:")
            for layer_type, count in layer_types.items():
                print(f"     {layer_type}: {count}")

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("This might be due to:")
        print("  - Unsupported PSD version")
        print("  - Missing psd-tools3 dependency")
        print("  - Corrupted PSD file")
        print("  - Complex layer effects not yet supported")


def example_advanced_psd_extraction():
    """
    Example 2: Advanced PSD extraction with layer hierarchy

    Shows how to extract PSD files while preserving complex layer structures.
    """
    print("\n=== Example 2: Advanced PSD Extraction ===")

    if not PSD_SUPPORT_AVAILABLE:
        print("❌ PSD support is not available.")
        _demonstrate_advanced_psd_interface()
        return

    input_psd = project_root / "input" / "sample.psd"
    output_json = project_root / "examples" / "output" / "advanced_psd_extraction.json"

    # Create output directory
    output_json.parent.mkdir(parents=True, exist_ok=True)

    if not input_psd.exists():
        print("No PSD files available for advanced extraction example.")
        _demonstrate_advanced_psd_interface()
        return

    try:
        # Advanced extraction flags
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_shapes": True,
            "include_effects": True,
            "include_layer_styles": True,  # Extract layer effects
            "include_smart_objects": True,  # Extract smart object content
            "flatten_groups": False,  # Preserve group hierarchy
            "extract_hidden_layers": True,  # Include hidden layers
            "extract_masks": True,  # Extract layer masks
            "preserve_blend_modes": True,  # Preserve blend modes
            "extract_metadata": True,  # Extract PSD metadata
        }

        print(f"Performing advanced extraction on: {input_psd}")
        print("Advanced options enabled:")
        for flag, enabled in extraction_flags.items():
            if enabled:
                print(f"  ✓ {flag}")

        document = extract_psd_content(str(input_psd), extraction_flags)

        # Save with pretty formatting
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

        print("✅ Advanced extraction completed!")
        print(f"   Output: {output_json}")

        # Show detailed analysis
        if hasattr(document, "metadata") and document.metadata:
            print("   Document metadata:")
            metadata = document.metadata
            if hasattr(metadata, "title") and metadata.title:
                print(f"     Title: {metadata.title}")
            if hasattr(metadata, "format") and metadata.format:
                print(f"     Format: {metadata.format}")

        # Analyze layer hierarchy
        if hasattr(document, "document_structure"):
            print("   Layer hierarchy analysis:")

            for i, canvas in enumerate(document.document_structure):
                print(f"     Canvas {i + 1}:")
                if hasattr(canvas, "canvas_size"):
                    print(f"       Size: {canvas.canvas_size}")

                if hasattr(canvas, "layers"):
                    _analyze_layer_hierarchy(canvas.layers, indent="       ")

    except Exception as e:
        print(f"❌ Advanced extraction failed: {e}")
        import traceback

        traceback.print_exc()


def _analyze_layer_hierarchy(layers: list, indent: str = ""):
    """Helper function to analyze and display layer hierarchy."""
    for layer in layers:
        layer_name = getattr(layer, "layer_name", "Unnamed")
        layer_type = getattr(layer, "layer_type", "unknown")
        visibility = getattr(layer, "visibility", True)
        opacity = getattr(layer, "opacity", 1.0)

        status = "visible" if visibility else "hidden"
        print(f"{indent}Layer '{layer_name}' ({layer_type}) - {status}, opacity: {opacity}")

        # Show content summary
        if hasattr(layer, "content") and layer.content:
            content_types = {}
            for element in layer.content:
                element_type = type(element).__name__
                content_types[element_type] = content_types.get(element_type, 0) + 1

            content_summary = ", ".join(f"{count} {elem_type}" for elem_type, count in content_types.items())
            print(f"{indent}  Content: {content_summary}")

        # Recursively analyze child layers
        if hasattr(layer, "children") and layer.children:
            print(f"{indent}  Child layers:")
            _analyze_layer_hierarchy(layer.children, indent + "    ")


def example_psd_to_pdf_conversion():
    """
    Example 3: Convert PSD to PDF

    Shows how to convert a PSD file to PDF format.
    """
    print("\n=== Example 3: PSD to PDF Conversion ===")

    if not PSD_SUPPORT_AVAILABLE:
        print("❌ PSD support is not available.")
        _demonstrate_psd_to_pdf_interface()
        return

    input_psd = project_root / "input" / "sample.psd"
    output_pdf = project_root / "examples" / "output" / "converted_from_psd.pdf"

    # Create output directory
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    if not input_psd.exists():
        print("No PSD files available for conversion example.")
        _demonstrate_psd_to_pdf_interface()
        return

    try:
        print(f"Converting PSD to PDF: {input_psd}")

        # Step 1: Extract PSD content
        print("Step 1: Extracting PSD content...")
        document = extract_psd_content(str(input_psd))

        # Step 2: Convert to PDF-compatible format
        print("Step 2: Converting to PDF format...")

        # This would involve converting canvas-based structure to page-based
        # and handling PSD-specific features that don't have PDF equivalents

        # For now, demonstrate the intended interface
        from pdfrebuilder.engine.document_renderer import render_document

        render_options = {
            "output_format": "pdf",
            "flatten_layers": True,  # Flatten PSD layers for PDF
            "preserve_transparency": False,  # PDF doesn't support transparency like PSD
            "convert_blend_modes": True,  # Convert PSD blend modes to PDF equivalents
            "rasterize_effects": True,  # Convert layer effects to raster images
        }

        render_document(document, str(output_pdf), render_options)

        print("✅ Conversion completed!")
        print(f"   Output PDF: {output_pdf}")

        # Check if the file was created
        if output_pdf.exists():
            file_size = output_pdf.stat().st_size
            print(f"   File size: {file_size:,} bytes")

    except Exception as e:
        print(f"❌ PSD to PDF conversion failed: {e}")
        print("Common issues:")
        print("  - Complex layer effects not supported")
        print("  - Blend modes that don't translate to PDF")
        print("  - Very large canvas sizes")


def example_psd_layer_manipulation():
    """
    Example 4: PSD layer manipulation

    Shows how to modify PSD layer properties and content.
    """
    print("\n=== Example 4: PSD Layer Manipulation ===")

    if not PSD_SUPPORT_AVAILABLE:
        print("❌ PSD support is not available.")
        _demonstrate_layer_manipulation_interface()
        return

    input_psd = project_root / "input" / "sample.psd"
    output_json = project_root / "examples" / "output" / "modified_psd.json"

    if not input_psd.exists():
        print("No PSD files available for layer manipulation example.")
        _demonstrate_layer_manipulation_interface()
        return

    try:
        print(f"Manipulating PSD layers: {input_psd}")

        # Extract PSD content
        document = extract_psd_content(str(input_psd))

        modifications_made = 0

        # Example modifications
        if hasattr(document, "document_structure"):
            for canvas in document.document_structure:
                if hasattr(canvas, "layers"):
                    for layer in canvas.layers:
                        # Example 1: Modify layer opacity
                        if hasattr(layer, "opacity") and layer.opacity > 0.5:
                            layer.opacity = 0.8
                            modifications_made += 1

                        # Example 2: Hide certain layers
                        if hasattr(layer, "layer_name") and "background" in layer.layer_name.lower():
                            layer.visibility = False
                            modifications_made += 1

                        # Example 3: Modify text content
                        if hasattr(layer, "content"):
                            for element in layer.content:
                                if hasattr(element, "text") and element.text:
                                    if not element.text.startswith("[MODIFIED]"):
                                        element.text = f"[MODIFIED] {element.text}"
                                        modifications_made += 1

        print(f"   Made {modifications_made} modifications")

        # Save modified document
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

        print("✅ Layer manipulation completed!")
        print(f"   Modified document saved to: {output_json}")

    except Exception as e:
        print(f"❌ Layer manipulation failed: {e}")


def _demonstrate_psd_interface():
    """Demonstrate the intended PSD processing interface when PSD support is not available."""
    print("\n--- PSD Processing Interface Demo ---")
    print("When PSD support is available, you would use:")
    print()
    print("```python")
    print("from pdfrebuilder.engine.extract_psd_content import extract_psd_content")
    print()
    print("# Extract PSD content")
    print("document = extract_psd_content('input/sample.psd', {")
    print("    'include_text': True,")
    print("    'include_images': True,")
    print("    'include_shapes': True,")
    print("    'include_effects': True,")
    print("    'flatten_groups': False")
    print("})")
    print()
    print("# Access canvas-based structure")
    print("for canvas in document.document_structure:")
    print("    print(f'Canvas size: {canvas.canvas_size}')")
    print("    for layer in canvas.layers:")
    print("        print(f'Layer: {layer.layer_name} ({layer.layer_type})')")
    print("```")


def _demonstrate_advanced_psd_interface():
    """Demonstrate advanced PSD processing interface."""
    print("\n--- Advanced PSD Processing Interface Demo ---")
    print("Advanced PSD extraction would support:")
    print("  • Layer hierarchy preservation")
    print("  • Blend mode extraction")
    print("  • Layer effects and styles")
    print("  • Smart object content")
    print("  • Layer masks")
    print("  • Text layer formatting")
    print("  • Vector shape layers")
    print("  • Adjustment layers")


def _demonstrate_psd_to_pdf_interface():
    """Demonstrate PSD to PDF conversion interface."""
    print("\n--- PSD to PDF Conversion Interface Demo ---")
    print("PSD to PDF conversion would involve:")
    print("  1. Extract PSD content with full layer information")
    print("  2. Convert canvas-based structure to page-based")
    print("  3. Flatten layers or convert to PDF layer equivalents")
    print("  4. Handle blend modes and effects")
    print("  5. Rasterize unsupported features")
    print("  6. Generate PDF with preserved visual fidelity")


def _demonstrate_layer_manipulation_interface():
    """Demonstrate layer manipulation interface."""
    print("\n--- Layer Manipulation Interface Demo ---")
    print("Layer manipulation would support:")
    print("  • Modify layer visibility and opacity")
    print("  • Change layer blend modes")
    print("  • Edit text layer content")
    print("  • Adjust layer positions and sizes")
    print("  • Add/remove layer effects")
    print("  • Reorder layer hierarchy")


def main():
    """
    Run all PSD processing examples
    """
    print("PSD Processing Examples")
    print("=" * 50)

    if not PSD_SUPPORT_AVAILABLE:
        print("⚠️  PSD support is currently in development.")
        print("These examples demonstrate the intended interface.")
        print("To enable PSD support, install: pip install psd-tools3")
        print()

    # Ensure output directory exists
    output_dir = project_root / "examples" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run all examples
    examples = [
        example_basic_psd_extraction,
        example_advanced_psd_extraction,
        example_psd_to_pdf_conversion,
        example_psd_layer_manipulation,
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 50)
    print("All PSD processing examples completed!")
    print(f"Check the output directory: {output_dir}")


if __name__ == "__main__":
    main()
