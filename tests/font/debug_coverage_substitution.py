import os
import shutil
import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.font.utils import ensure_font_registered
from tests.config import cleanup_test_output, get_test_fonts_dir, get_test_temp_dir


class DebugCoverageSubstitution(unittest.TestCase):
    def setUp(self):
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        self.mock_page = Mock()
        self.mock_page.insert_font.return_value = 0

    def tearDown(self):
        cleanup_test_output(self.test_name)

    @patch("pdfrebuilder.font.utils.download_google_font")
    def test_debug_coverage_substitution(self, mock_download):
        font_name = "MissingFont"
        text = "Hello 世界"

        shutil.copy("tests/fixtures/fonts/PublicSans-Regular.otf", os.path.join(self.test_fonts_dir, "Arial.ttf"))
        shutil.copy(
            "tests/fixtures/fonts/NotoSansCJKjp-Regular.woff", os.path.join(self.test_fonts_dir, "NotoSans.woff")
        )

        mock_download.return_value = None

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            result = ensure_font_registered(self.mock_page, font_name, verbose=True, text=text)

        print(f"Result of ensure_font_registered: '{result}'")
        self.assertEqual(result, "Noto Sans JP Thin")
