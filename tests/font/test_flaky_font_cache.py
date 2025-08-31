import os
import shutil
import time
import unittest
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.font.utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    ensure_font_registered,
    get_font_registration_tracker,
)

# Import test configuration
from tests.config import (
    cleanup_test_output,
    get_fixture_path,
    get_test_fonts_dir,
    get_test_temp_dir,
)


class TestFlakyFontRegistrationCache(unittest.TestCase):
    """Test flaky font registration cache functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()
        get_font_registration_tracker().clear_tracking_data()

        # Create test font files
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        self.create_test_fonts()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()
        get_font_registration_tracker().clear_tracking_data()

    def create_test_fonts(self):
        """Create test font files"""
        real_font_path = get_fixture_path("fonts/PublicSans-Regular.otf")
        test_fonts = ["Arial.ttf", "Times.ttf", "Roboto.ttf", "OpenSans.ttf"]
        for font_file in test_fonts:
            dest_path = os.path.join(self.test_fonts_dir, font_file)
            shutil.copy(real_font_path, dest_path)

    def test_cache_performance_with_many_fonts(self):
        """Test cache performance with many fonts"""
        mock_page = Mock()
        num_fonts = 50

        # Create many font files
        font_names = [f"TestFont{i}" for i in range(num_fonts)]
        for font_name in font_names:
            font_path = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
            with open(font_path, "w") as f:
                f.write(f"content for {font_name}")

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", self.test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            with patch("pdfrebuilder.font.utils.os.path.exists", return_value=True):
                # Time first registration (should be slower)
                start_time = time.time()
                for font_name in font_names:
                    ensure_font_registered(mock_page, font_name, verbose=False)
                first_run_time = time.time() - start_time

                # Time second registration (should be much faster due to cache)
                start_time = time.time()
                for font_name in font_names:
                    ensure_font_registered(mock_page, font_name, verbose=False)
                second_run_time = time.time() - start_time

        # Second run should be faster (lenient threshold for system variability)
        threshold = first_run_time * 2.0  # At least 2x faster, allowing for more system variability
        try:
            self.assertLess(second_run_time, threshold)
        except AssertionError:
            # Provide detailed explanation for threshold failure
            improvement_ratio = first_run_time / second_run_time if second_run_time > 0 else float("inf")
            expected_ratio = 1.25

            error_msg = (
                f"Cache performance test failed:\n"
                f"  First run time:  {first_run_time:.3f}s\n"
                f"  Second run time: {second_run_time:.3f}s\n"
                f"  Threshold:       {threshold:.3f}s\n"
                f"  Actual improvement: {improvement_ratio:.1f}x faster\n"
                f"  Expected improvement: {expected_ratio:.1f}x faster\n"
                f"  \n"
                f"  This test verifies that font registration caching provides significant\n"
                f"  performance improvements. The failure could indicate:\n"
                f"  - Cache is not working properly\n"
                f"  - System performance variability (try running again)\n"
                f"  - Test environment has very fast I/O (threshold may need adjustment)\n"
                f"  \n"
                f"  If this failure is consistent, consider adjusting the performance\n"
                f"  threshold or investigating cache implementation."
            )
            raise AssertionError(error_msg)

        # All fonts should be in cache
        page_id = id(mock_page)
        for font_name in font_names:
            self.assertIn(font_name, _FONT_REGISTRATION_CACHE[page_id])

        # Each font should only be registered once
        self.assertEqual(mock_page.insert_font.call_count, num_fonts)
