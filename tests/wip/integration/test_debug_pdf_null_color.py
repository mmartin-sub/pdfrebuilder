import logging
import os
import sys
from io import StringIO
from pathlib import Path

# Ensure project root is on sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pdfrebuilder.core.generate_debug_pdf_layers import generate_debug_pdf_layers
from pdfrebuilder.settings import configure_logging

# Configure logging
configure_logging(log_level=logging.DEBUG)

CONFIG_PATH = str(Path(__file__).parent / "test_drawing_null_color_config.json")
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_generate_debug_pdf_layers_null_color():
    # Use a descriptive filename with a unique identifier
    output_pdf = OUTPUT_DIR / f"debug_layer_null_color_test_{os.getpid()}.pdf"

    # Set up log capture
    logger = logging.getLogger()

    log_capture = StringIO()
    log_stream = logging.StreamHandler(log_capture)
    logger.addHandler(log_stream)

    try:
        generate_debug_pdf_layers(CONFIG_PATH, str(output_pdf))
        log_stream.flush()
        logs = log_capture.getvalue()
        print(
            f"\n--- LOG OUTPUT for test_debug_pdf_null_color (PID: {os.getpid()}) ---\n",
            logs,
        )

        # Check for invalid color warning
        assert "Invalid color format encountered" not in logs, "Unexpected invalid color warning in color conversion."

        # Check for rendering errors
        assert "Failed to draw shape: Point: bad args" not in logs, "Shape rendering failed with 'bad args' error."
        assert "Error drawing shape" not in logs, "Shape rendering error detected in logs."

        # Verify the PDF was created
        assert output_pdf.exists(), f"Output PDF was not created: {output_pdf}"

        # Print detailed instructions for verification
        print("\n" + "=" * 80)
        print("DEBUG LAYER TEST VERIFICATION")
        print("=" * 80)
        print(f"PDF generated at: {output_pdf}")
        print("\nThis test uses generate_debug_pdf_layers to create a debug PDF with layer information.")
        print("\nExpected behavior:")
        print("1. The PDF should contain debug pages for each element in the test configuration")
        print("2. Each debug page should show the element's properties and rendering information")
        print("3. No errors should be reported in the debug information")
        print("\nThe test is successful if:")
        print("- No errors appear in the console output")
        print("- The PDF contains debug pages for all elements")
        print("- The debug information doesn't show 'Failed to draw shape: Point: bad args'")
        print("=" * 80)
    finally:
        logger.removeHandler(log_stream)
        log_stream.close()
        # Clean up the PDF file after successful test
        if output_pdf.exists():
            output_pdf.unlink()


if __name__ == "__main__":
    test_generate_debug_pdf_layers_null_color()
