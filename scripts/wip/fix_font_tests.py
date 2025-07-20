#!/usr/bin/env python3
"""Script to fix font test mock issues systematically"""

import os
import re


def fix_font_test_mocks():
    """Fix all font test mock issues by updating the get_config_value side_effect"""

    # Files to fix
    test_files = [
        "tests/test_font_substitution.py",
        "tests/test_font_document_integration.py",
        "tests/test_font_cache_integration.py",
        "tests/test_font_manager.py",
    ]

    # Pattern to find and replace
    old_pattern = r'side_effect=lambda key: self\.test_fonts_dir if key == "downloaded_fonts_dir" else "helv"'
    new_pattern = (
        'side_effect=lambda key: self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"'
    )

    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping")
            continue

        print(f"Processing {file_path}...")

        # Read the file
        with open(file_path) as f:
            content = f.read()

        # Count occurrences
        old_count = len(re.findall(old_pattern, content))

        # Replace the pattern
        new_content = re.sub(old_pattern, new_pattern, content)

        # Write back if changes were made
        if old_count > 0:
            with open(file_path, "w") as f:
                f.write(new_content)
            print(f"  Fixed {old_count} occurrences in {file_path}")
        else:
            print(f"  No occurrences found in {file_path}")


if __name__ == "__main__":
    fix_font_test_mocks()
