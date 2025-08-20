import logging
import os
from io import StringIO

from pdfrebuilder.core.recreate_pdf_from_config import recreate_pdf_from_config
from pdfrebuilder.settings import configure_logging
from tests.config import get_test_output_path, get_unique_id

# Configure logging
configure_logging(log_level=logging.DEBUG)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "test_drawing_null_color_combinations.json")


def test_null_color_visual_verification():
    """
    Test that generates a visual verification PDF with various null color combinations.
    This test verifies that:
    1. Fill-only shapes (null stroke) render correctly
    2. Stroke-only shapes (null fill) render correctly
    3. Shapes with both stroke and fill render correctly
    4. Shapes with both null stroke and fill render without errors
    """
    unique = get_unique_id()
    output_pdf = get_test_output_path("visual_verification_null_color_test", unique)

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
            f"\n--- LOG OUTPUT for test_null_color_visual (PID: {os.getpid()}) ---\n",
            logs,
        )

        # Check for rendering errors
        assert "Failed to draw shape: Point: bad args" not in logs, "Shape rendering failed with 'bad args' error."
        assert "Error drawing shape" not in logs, "Shape rendering error detected in logs."

        # Check for appropriate warnings for the invisible shape
        assert "has neither stroke nor fill" in logs, "Missing warning for shape with both null stroke and fill."

        # Verify the PDF was created
        assert os.path.exists(output_pdf), f"Output PDF was not created: {output_pdf}"

        # Print detailed instructions for visual verification
        print("\n" + "=" * 80)
        print("VISUAL VERIFICATION INSTRUCTIONS")
        print("=" * 80)
        print(f"PDF generated at: {output_pdf}")
        print("\nPlease check the following in the PDF:")
        print("1. Case 1: A black filled rectangle with NO stroke (top left)")
        print("2. Case 2: A black stroke rectangle with NO fill (top right)")
        print("3. Case 3: A rectangle with both black stroke and gray fill (bottom left)")
        print("4. Case 4: No visible rectangle (bottom right) - this is correct behavior")
        print("\nThe test is successful if:")
        print("- All shapes render correctly according to their null/non-null properties")
        print("- No errors or warnings appear in the console output")
        print("- The PDF is generated and contains the expected visual elements")
        print("=" * 80)
    finally:
        logger.removeHandler(log_stream)
        log_stream.close()
        # Clean up the PDF file after successful test
        if os.path.exists(output_pdf):
            os.remove(output_pdf)


if __name__ == "__main__":
    test_null_color_visual_verification()
