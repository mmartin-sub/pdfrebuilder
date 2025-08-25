import os
import shutil
import unittest

from pdfrebuilder.font.utils import scan_available_fonts
from tests.config import get_test_fonts_dir, get_test_temp_dir, cleanup_test_output


class DebugFontSubstitution(unittest.TestCase):
    def setUp(self):
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)
        os.makedirs(self.test_fonts_dir, exist_ok=True)

    def tearDown(self):
        cleanup_test_output(self.test_name)

    def test_get_cjk_font_name(self):
        """Test to get the exact family name of the Noto Sans CJK font."""
        shutil.copy("tests/fixtures/fonts/NotoSansCJKjp-Regular.woff", os.path.join(self.test_fonts_dir, "NotoSans.woff"))

        font_map = scan_available_fonts(self.test_fonts_dir)

        # This will print the extracted font names
        print(f"Found fonts: {font_map.keys()}")

        # I will check the output of this print statement to see the correct name.
        self.assertIn("Noto Sans JP Thin", font_map)
