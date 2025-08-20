import os
import sys
from unittest.mock import Mock, patch

# Add src directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pdfrebuilder.font_utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    FontValidator,
    ensure_font_registered,
    set_font_validator,
)


def run_debug_scenario():
    """
    Replicates the setup of the failing test to debug the font path issue.
    """
    print("--- Starting Debug Scenario ---")

    # 1. Setup mock environment
    mock_page = Mock()
    test_fonts_dir = "/tmp/fake_fonts"
    os.makedirs(test_fonts_dir, exist_ok=True)

    # 2. Setup FontValidator
    font_validator = FontValidator()
    set_font_validator(font_validator)

    # 3. Define test case variables
    font_name = "MissingFont"
    text = "Hello World"

    # 4. Define mocks and patches
    available_fonts = {
        "Arial": "/path/to/arial.ttf",
        "NotoSans": "/path/to/notosans.ttf",
        "DejaVu": "/path/to/dejavu.ttf",
    }

    def coverage_side_effect(font_path, test_text):
        # In the original test, this was more complex, but for debugging,
        # let's say Arial covers the text.
        if "arial" in font_path.lower():
            print(f"DEBUG: coverage_side_effect returning True for {font_path}")
            return True
        print(f"DEBUG: coverage_side_effect returning False for {font_path}")
        return False

    # 5. Apply patches
    with (
        patch("pdfrebuilder.font_utils.download_google_font", return_value=None) as mock_download,
        patch("pdfrebuilder.font_utils.scan_available_fonts", return_value=available_fonts) as mock_scan,
        patch("pdfrebuilder.font_utils.font_covers_text", side_effect=coverage_side_effect) as mock_covers,
        patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv",
        ),
        patch("os.path.exists", return_value=True),
        patch("os.path.isfile", return_value=True),
    ):
        print("--- Mocks are active. Calling ensure_font_registered ---")

        # Clear caches before running
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # 6. Run the function
        result = ensure_font_registered(mock_page, font_name, verbose=True, text=text)

        print("\n--- Function execution finished ---")
        print(f"Final result: {result}")
        print(f"Substitutions tracked: {len(font_validator.substitution_tracker)}")
        if font_validator.substitution_tracker:
            print("Tracked substitution details:")
            for sub in font_validator.substitution_tracker:
                print(f"  - {sub.original_font} -> {sub.substituted_font} (Reason: {sub.reason})")


if __name__ == "__main__":
    run_debug_scenario()
