#!/usr/bin/env python3
"""Debug font registration path checking"""

import os
from unittest.mock import MagicMock, Mock, patch


def test_minimal_download_calls():
    """Test minimal download calls to understand the issue"""

    # Import the function
    from pdfrebuilder.font_utils import _FONT_DOWNLOAD_ATTEMPTED, ensure_font_registered

    # Clear the download attempted set
    _FONT_DOWNLOAD_ATTEMPTED.clear()

    # Create mock page
    mock_page = Mock()

    # Test fonts directory - use secure temporary directory
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent / "src"))

    from security.path_utils import create_secure_temp_dir

    # Create secure temporary directory for testing
    temp_base = create_secure_temp_dir("font_debug_test_")
    test_fonts_dir = str(temp_base)

    def download_side_effect(font_name, dest_dir):
        print(f"DEBUG: download_google_font called with font_name='{font_name}', dest_dir='{dest_dir}'")
        if font_name in ["Roboto", "OpenSans"]:
            return [f"{dest_dir}/{font_name}.ttf"]
        elif font_name == "UnavailableFont":
            return None
        return None

    def exists_side_effect(path):
        print(f"DEBUG: os.path.exists called with '{path}'")
        if test_fonts_dir in path:
            if any(font in path for font in ["Roboto.ttf", "OpenSans.ttf", "Roboto.otf", "OpenSans.otf"]):
                print("  -> Returning False (font file)")
                return False
            print("  -> Returning True (directory)")
            return True
        print("  -> Returning False (not in test dir)")
        return False

    # Mock the functions
    with patch("src.font_utils.download_google_font", side_effect=download_side_effect) as mock_download:
        with patch("src.font_utils.os.path.exists", side_effect=exists_side_effect):
            with patch(
                "src.font_utils.get_config_value",
                side_effect=lambda key: (
                    test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
                ),
            ):
                with patch("src.font_utils.TTFont") as mock_ttfont:
                    # Mock TTFont
                    def create_mock_font(font_path):
                        mock_font = MagicMock()
                        font_name = os.path.basename(font_path).replace(".ttf", "").replace(".otf", "")
                        mock_name_table = Mock()
                        mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
                        mock_cmap_table = Mock()
                        char_map = {ord(c): i for i, c in enumerate("Text with Roboto OpenSans")}
                        mock_cmap_table.cmap = char_map
                        mock_cmap_subtable = Mock()
                        mock_cmap_subtable.tables = [mock_cmap_table]

                        def getitem_side_effect(key):
                            if key == "name":
                                return mock_name_table
                            elif key == "cmap":
                                return mock_cmap_subtable
                            return Mock()

                        mock_font.__getitem__.side_effect = getitem_side_effect
                        return mock_font

                    mock_ttfont.side_effect = create_mock_font

                    # Test each font individually
                    test_fonts = ["Roboto", "OpenSans", "UnavailableFont"]

                    print(f"\nDEBUG: Starting test with {len(test_fonts)} fonts")
                    print(f"DEBUG: Initial _FONT_DOWNLOAD_ATTEMPTED: {_FONT_DOWNLOAD_ATTEMPTED}")

                    for i, font_name in enumerate(test_fonts):
                        print(f"\nDEBUG: Testing font {i + 1}/{len(test_fonts)}: '{font_name}'")
                        print(f"DEBUG: _FONT_DOWNLOAD_ATTEMPTED before: {_FONT_DOWNLOAD_ATTEMPTED}")

                        result = ensure_font_registered(
                            mock_page,
                            font_name,
                            verbose=True,
                            text=f"Text with {font_name}",
                        )

                        print(f"DEBUG: Result: {result}")
                        print(f"DEBUG: _FONT_DOWNLOAD_ATTEMPTED after: {_FONT_DOWNLOAD_ATTEMPTED}")
                        print(f"DEBUG: Download call count: {mock_download.call_count}")

                    print(f"\nDEBUG: Final download call count: {mock_download.call_count}")
                    print(f"DEBUG: Expected: {len(test_fonts)}")


if __name__ == "__main__":
    test_minimal_download_calls()
