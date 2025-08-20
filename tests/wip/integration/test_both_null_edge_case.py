import logging
import os
import sys
from io import StringIO
from pathlib import Path

# Ensure project root is on sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pdfrebuilder.core.recreate_pdf_from_config import recreate_pdf_from_config
from pdfrebuilder.settings import configure_logging, get_config_value

# Configure logging
configure_logging(log_level=logging.DEBUG)

CONFIG_PATH = str(Path(__file__).parent / "test_drawing_both_null.json")
OUTPUT_DIR = Path(get_config_value("test_output_dir"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_both_null_edge_case():
    """
    Test specifically for the edge case where both stroke and fill are null.
    This test verifies that:
    1. A warning is logged for the shape with both null stroke and fill
    2. No errors are raised during rendering
    3. The PDF is still generated successfully
    """
    # Use a descriptive filename with a unique identifier
    output_pdf = OUTPUT_DIR / f"edge_case_both_null_test_{os.getpid()}.pdf"

    # Set up log capture
    logger = logging.getLogger()

    log_capture = StringIO()
    log_stream = logging.StreamHandler(log_capture)
    logger.addHandler(log_stream)

    try:
        # Generate the PDF with the test configuration
        recreate_pdf_from_config(CONFIG_PATH, str(output_pdf))

        log_stream.flush()
        logs = log_capture.getvalue()
        print(
            f"\n--- LOG OUTPUT for test_both_null_edge_case (PID: {os.getpid()}) ---\n",
            logs,
        )

        # Check for the expected warning
        assert "has neither stroke nor fill" in logs, "Missing warning for shape with both null stroke and fill."
        assert "drawing_both_null" in logs, "Warning should include the element ID."

        # Check that no errors were raised
        assert "Failed to draw shape" not in logs, "Shape rendering failed unexpectedly."
        assert "Error drawing shape" not in logs, "Shape rendering error detected in logs."

        # Verify the PDF was created
        assert output_pdf.exists(), f"Output PDF was not created: {output_pdf}"

        # Print detailed instructions for verification
        print("\n" + "=" * 80)
        print("EDGE CASE TEST VERIFICATION")
        print("=" * 80)
        print(f"PDF generated at: {output_pdf}")
        print("\nThis test verifies the edge case where both stroke and fill are null.")
        print("\nExpected behavior:")
        print("1. The PDF should be generated without errors")
        print("2. A warning should be logged about 'neither stroke nor fill'")
        print("3. The rectangle should be invisible (this is correct behavior)")
        print("\nThe test is successful if:")
        print("- No errors appear in the console output")
        print("- A warning about 'neither stroke nor fill' is logged")
        print("- The PDF contains only the text elements, with no visible rectangle")
        print("=" * 80)
    finally:
        logger.removeHandler(log_stream)
        log_stream.close()
        # Clean up the PDF file after successful test
        if output_pdf.exists():
            output_pdf.unlink()


if __name__ == "__main__":
    test_both_null_edge_case()
