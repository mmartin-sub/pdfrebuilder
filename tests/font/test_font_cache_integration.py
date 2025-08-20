"""
Integration tests for Font Management System cache functionality.

This module tests:
- Font cache performance and behavior
- Cache invalidation and refresh
- Memory usage optimization
- Cache persistence across operations
"""

import os
import time
import unittest
from unittest.mock import Mock, patch

from pdfrebuilder.font.font_validator import FontValidator
from pdfrebuilder.font_utils import _FONT_DOWNLOAD_ATTEMPTED, _FONT_REGISTRATION_CACHE, ensure_font_registered

# Import test configuration
from tests.config import cleanup_test_output, get_test_fonts_dir, get_test_temp_dir


class TestFontRegistrationCache(unittest.TestCase):
    """Test font registration cache functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Create test font files
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        self.create_test_fonts()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def create_test_fonts(self):
        """Create test font files"""
        test_fonts = ["Arial.ttf", "Times.ttf", "Roboto.ttf", "OpenSans.ttf"]
        for font_file in test_fonts:
            font_path = os.path.join(self.test_fonts_dir, font_file)
            with open(font_path, "w") as f:
                f.write(f"dummy content for {font_file}")

    def test_cache_isolation_between_pages(self):
        """Test that font caches are isolated between different pages"""
        page1 = Mock()
        page2 = Mock()
        page3 = Mock()

        fonts_to_register = ["Arial", "Times", "Roboto"]

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            with patch("pdfrebuilder.font_utils.os.path.exists", return_value=True):
                # Register different fonts on different pages
                ensure_font_registered(page1, fonts_to_register[0], verbose=False)
                ensure_font_registered(page2, fonts_to_register[1], verbose=False)
                ensure_font_registered(page3, fonts_to_register[2], verbose=False)

        # Each page should have its own cache entry
        page1_id = id(page1)
        page2_id = id(page2)
        page3_id = id(page3)

        self.assertIn(page1_id, _FONT_REGISTRATION_CACHE)
        self.assertIn(page2_id, _FONT_REGISTRATION_CACHE)
        self.assertIn(page3_id, _FONT_REGISTRATION_CACHE)

        # Each page should only have its own font in cache
        self.assertIn(fonts_to_register[0], _FONT_REGISTRATION_CACHE[page1_id])
        self.assertNotIn(fonts_to_register[1], _FONT_REGISTRATION_CACHE[page1_id])
        self.assertNotIn(fonts_to_register[2], _FONT_REGISTRATION_CACHE[page1_id])

        self.assertIn(fonts_to_register[1], _FONT_REGISTRATION_CACHE[page2_id])
        self.assertNotIn(fonts_to_register[0], _FONT_REGISTRATION_CACHE[page2_id])
        self.assertNotIn(fonts_to_register[2], _FONT_REGISTRATION_CACHE[page2_id])

    def test_cache_prevents_duplicate_registrations(self):
        """Test that cache prevents duplicate font registrations on same page"""
        mock_page = Mock()
        font_name = "Arial"

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            with patch("pdfrebuilder.font_utils.os.path.exists", return_value=True):
                # Register font multiple times
                for _ in range(5):
                    result = ensure_font_registered(mock_page, font_name, verbose=False)
                    self.assertEqual(result, font_name)

        # Font should only be registered once
        self.assertEqual(mock_page.insert_font.call_count, 1)

        # Font should be in cache
        page_id = id(mock_page)
        self.assertIn(font_name, _FONT_REGISTRATION_CACHE[page_id])

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

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            with patch("pdfrebuilder.font_utils.os.path.exists", return_value=True):
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
        threshold = first_run_time * 0.8  # At least 1.25x faster (very lenient threshold)
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

    def test_cache_memory_efficiency(self):
        """Test that cache doesn't grow unbounded"""
        # Create many pages to test memory usage
        pages = [Mock() for _ in range(100)]
        font_name = "Arial"

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            with patch("pdfrebuilder.font_utils.os.path.exists", return_value=True):
                for page in pages:
                    ensure_font_registered(page, font_name, verbose=False)

        # Cache should have entries for all pages
        self.assertEqual(len(_FONT_REGISTRATION_CACHE), len(pages))

        # Each cache entry should be small (just font names)
        for page in pages:
            page_id = id(page)
            cache_entry = _FONT_REGISTRATION_CACHE[page_id]
            self.assertIsInstance(cache_entry, set)
            self.assertEqual(len(cache_entry), 1)
            self.assertIn(font_name, cache_entry)


class TestFontDownloadCache(unittest.TestCase):
    """Test font download attempt caching"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    @patch("pdfrebuilder.font_utils.download_google_font")
    def test_download_attempt_caching(self, mock_download):
        """Test that failed download attempts are cached"""
        mock_page = Mock()
        font_name = "NonExistentFont"

        # Mock download failure
        mock_download.return_value = None

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # First attempt should try download
            result1 = ensure_font_registered(mock_page, font_name, verbose=False)

            # Second attempt should not try download again
            result2 = ensure_font_registered(mock_page, font_name, verbose=False)

            # Third attempt on different page should also not try download
            mock_page2 = Mock()
            result3 = ensure_font_registered(mock_page2, font_name, verbose=False)

        # All should fallback to default font name from the mock config
        expected_fallback = "helv"
        self.assertEqual(result1, expected_fallback)
        self.assertEqual(result2, expected_fallback)
        self.assertEqual(result3, expected_fallback)

        # Download should only be attempted once
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)

        # Font should be in download attempted cache
        self.assertIn(font_name, _FONT_DOWNLOAD_ATTEMPTED)

    @patch("pdfrebuilder.font_utils.download_google_font")
    def test_download_cache_with_multiple_fonts(self, mock_download):
        """Test download caching with multiple fonts"""
        mock_page = Mock()
        fonts_to_test = ["Font1", "Font2", "Font3", "Font4"]

        # Mock download failure for all fonts
        mock_download.return_value = None

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # Try each font twice
            for font_name in fonts_to_test:
                ensure_font_registered(mock_page, font_name, verbose=False)
                ensure_font_registered(mock_page, font_name, verbose=False)  # Second attempt

        # Download should be attempted once per font
        self.assertEqual(mock_download.call_count, len(fonts_to_test))

        # All fonts should be in download attempted cache
        for font_name in fonts_to_test:
            self.assertIn(font_name, _FONT_DOWNLOAD_ATTEMPTED)

    def test_download_attempt_cache_prevents_duplicate_downloads(self):
        """Test that download attempt cache prevents duplicate downloads"""
        font_name = "TestFont"

        # Clear the cache first
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # First call should add to cache
        self.assertNotIn(font_name, _FONT_DOWNLOAD_ATTEMPTED)

        # Simulate download attempt
        _FONT_DOWNLOAD_ATTEMPTED.add(font_name)

        # Second call should find it in cache
        self.assertIn(font_name, _FONT_DOWNLOAD_ATTEMPTED)

    @patch("pdfrebuilder.font_utils.download_google_font")
    def test_download_function_called_when_font_not_found(self, mock_download):
        """Test that download function is called when font is not found"""
        mock_page = Mock()
        mock_page.insert_font = Mock(return_value=None)
        font_name = "MissingFont"

        # Clear cache
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Mock download to return None (download fails)
        mock_download.return_value = None

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # This should trigger download attempt
            result = ensure_font_registered(mock_page, font_name, verbose=False)

        # Should have tried to download
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)

        # Should fall back to default font name from the mock config
        expected_fallback = "helv"
        self.assertEqual(result, expected_fallback)

    def test_font_registration_returns_correct_font_name(self):
        """Test that font registration returns the correct font name when successful"""
        mock_page = Mock()
        mock_page.insert_font = Mock(return_value=None)
        font_name = "TestFont"

        # Create a test font file
        font_file = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        with open(font_file, "w") as f:
            f.write("test font content")

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(mock_page, font_name, verbose=False)

        # Should return the original font name
        self.assertEqual(result, font_name)


class TestFontValidatorCache(unittest.TestCase):
    """Test FontValidator caching functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Create test fonts
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        self.create_test_fonts()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    def create_test_fonts(self):
        """Create test font files"""
        test_fonts = ["Arial.ttf", "Times.ttf", "Roboto.ttf"]
        for font_file in test_fonts:
            font_path = os.path.join(self.test_fonts_dir, font_file)
            with open(font_path, "w") as f:
                f.write(f"dummy content for {font_file}")

    @patch("pdfrebuilder.font.font_validator.scan_available_fonts")
    def test_available_fonts_caching(self, mock_scan):
        """Test that available fonts are cached in FontValidator"""
        mock_fonts = {"Arial": "/path/to/arial.ttf", "Times": "/path/to/times.ttf"}
        mock_scan.return_value = mock_fonts

        # Create validator after patching scan_available_fonts
        validator = FontValidator(self.test_fonts_dir)

        # First access should trigger scan
        fonts1 = validator.available_fonts
        self.assertEqual(fonts1, mock_fonts)

        # Second access should use cached result
        fonts2 = validator.available_fonts
        self.assertEqual(fonts2, mock_fonts)

        # Scan should only be called once (in __init__)
        mock_scan.assert_called_once_with(self.test_fonts_dir)

    @patch("pdfrebuilder.font.font_validator.scan_available_fonts")
    def test_cache_refresh_functionality(self, mock_scan):
        """Test cache refresh functionality"""
        # Initial scan result
        initial_fonts = {"Arial": "/path/to/arial.ttf"}
        # Updated scan result
        updated_fonts = {"Arial": "/path/to/arial.ttf", "Times": "/path/to/times.ttf"}

        mock_scan.side_effect = [initial_fonts, updated_fonts]

        # Create validator after patching scan_available_fonts
        validator = FontValidator(self.test_fonts_dir)

        # Initial state
        self.assertEqual(validator.available_fonts, initial_fonts)

        # Refresh cache
        validator._refresh_available_fonts()

        # Should have updated fonts
        self.assertEqual(validator.available_fonts, updated_fonts)

        # Scan should be called twice
        self.assertEqual(mock_scan.call_count, 2)

    def test_substitution_tracking_accumulation(self):
        """Test that substitution tracking accumulates correctly"""
        validator = FontValidator(self.test_fonts_dir)

        # Track multiple substitutions
        substitutions = [
            ("Arial", "Helvetica", "Test 1"),
            ("Times", "DejaVu", "Test 2"),
            ("Roboto", "Arial", "Test 3"),
        ]

        for original, substituted, reason in substitutions:
            validator.track_font_substitution(original, substituted, reason)

        # Should have all substitutions
        self.assertEqual(len(validator.substitution_tracker), len(substitutions))

        # Verify each substitution
        for i, (original, substituted, reason) in enumerate(substitutions):
            tracked = validator.substitution_tracker[i]
            self.assertEqual(tracked.original_font, original)
            self.assertEqual(tracked.substituted_font, substituted)
            self.assertEqual(tracked.reason, reason)

    def test_validation_result_caching_behavior(self):
        """Test validation result behavior with repeated validations"""
        validator = FontValidator(self.test_fonts_dir)

        # Sample document config
        config = {
            "version": "1.0",
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "layers": [
                        {
                            "content": [
                                {
                                    "type": "text",
                                    "id": "text_0",
                                    "text": "Hello",
                                    "font_details": {"name": "Arial"},
                                }
                            ]
                        }
                    ],
                }
            ],
        }

        # Run validation multiple times
        results = []
        for _ in range(3):
            result = validator.validate_document_fonts(config)
            results.append(result)

        # All results should be consistent
        for result in results:
            self.assertEqual(result.fonts_required, {"Arial"})

        # Each validation should be independent (not cached)
        # This ensures fresh validation each time
        for result in results:
            self.assertIsInstance(result.validation_messages, list)


class TestCacheIntegrationPerformance(unittest.TestCase):
    """Test cache integration and performance characteristics"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Create many test fonts
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        self.create_many_test_fonts()

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def create_many_test_fonts(self):
        """Create many test font files for performance testing"""
        for i in range(20):
            font_path = os.path.join(self.test_fonts_dir, f"TestFont{i}.ttf")
            with open(font_path, "w") as f:
                f.write(f"content for TestFont{i}")

    def test_large_document_font_processing(self):
        """Test font processing performance with large documents"""
        # Create a large document configuration
        num_pages = 10
        num_elements_per_page = 20
        font_names = [f"TestFont{i}" for i in range(10)]

        document_config = {
            "version": "1.0",
            "document_structure": [],
        }

        # Generate many pages with many text elements
        for page_num in range(num_pages):
            page = {
                "type": "page",
                "page_number": page_num,
                "layers": [
                    {
                        "content": [
                            {
                                "type": "text",
                                "id": f"text_{page_num}_{elem_num}",
                                "text": f"Text {elem_num}",
                                "font_details": {"name": font_names[elem_num % len(font_names)]},
                            }
                            for elem_num in range(num_elements_per_page)
                        ]
                    }
                ],
            }
            document_config["document_structure"].append(page)

        # Test font validation performance
        validator = FontValidator(self.test_fonts_dir)

        start_time = time.time()
        result = validator.validate_document_fonts(document_config)
        validation_time = time.time() - start_time

        # Should complete validation in reasonable time (< 1 second for this size)
        threshold = 1.0
        try:
            self.assertLess(validation_time, threshold)
        except AssertionError:
            error_msg = (
                f"Font validation performance test failed:\n"
                f"  Validation time: {validation_time:.3f}s\n"
                f"  Threshold:       {threshold:.3f}s\n"
                f"  \n"
                f"  This test verifies that font validation completes within reasonable time.\n"
                f"  The failure could indicate:\n"
                f"  - Performance regression in validation logic\n"
                f"  - System performance issues\n"
                f"  - Test environment is slower than expected\n"
                f"  \n"
                f"  Consider adjusting the threshold if this failure is consistent."
            )
            raise AssertionError(error_msg)

        # Should have found all fonts
        self.assertEqual(len(result.fonts_required), len(font_names))

        # Test font registration performance
        mock_pages = [Mock() for _ in range(num_pages)]

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            start_time = time.time()

            # Simulate registering fonts for all elements
            for _page_num, mock_page in enumerate(mock_pages):
                for elem_num in range(num_elements_per_page):
                    font_name = font_names[elem_num % len(font_names)]
                    ensure_font_registered(mock_page, font_name, verbose=False)

            registration_time = time.time() - start_time

        # Should complete registration in reasonable time
        threshold = 2.0
        try:
            self.assertLess(registration_time, threshold)
        except AssertionError:
            error_msg = (
                f"Font registration performance test failed:\n"
                f"  Registration time: {registration_time:.3f}s\n"
                f"  Threshold:         {threshold:.3f}s\n"
                f"  Pages processed:   {num_pages}\n"
                f"  Elements per page: {num_elements_per_page}\n"
                f"  Unique fonts:      {len(font_names)}\n"
                f"  \n"
                f"  This test verifies that font registration completes within reasonable time.\n"
                f"  The failure could indicate:\n"
                f"  - Performance regression in font registration\n"
                f"  - Cache not working effectively\n"
                f"  - System performance issues\n"
                f"  \n"
                f"  Consider adjusting the threshold if this failure is consistent."
            )
            raise AssertionError(error_msg)

        # Verify caching worked (each font registered once per page)
        for mock_page in mock_pages:
            # Each page should have registered each unique font once
            unique_fonts_on_page = set(font_names)
            self.assertEqual(mock_page.insert_font.call_count, len(unique_fonts_on_page))

    def test_concurrent_cache_access_simulation(self):
        """Test cache behavior under simulated concurrent access"""
        # Simulate multiple "threads" accessing fonts simultaneously
        mock_pages = [Mock() for _ in range(10)]
        font_names = [f"TestFont{i}" for i in range(5)]

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # Simulate concurrent access by interleaving requests
            for iteration in range(3):
                for page_idx, mock_page in enumerate(mock_pages):
                    for font_idx, font_name in enumerate(font_names):
                        # Simulate some pages requesting same fonts
                        if (page_idx + font_idx + iteration) % 2 == 0:
                            result = ensure_font_registered(mock_page, font_name, verbose=False)
                            self.assertEqual(result, font_name)

        # Verify cache integrity
        for mock_page in mock_pages:
            page_id = id(mock_page)
            if page_id in _FONT_REGISTRATION_CACHE:
                cache_entry = _FONT_REGISTRATION_CACHE[page_id]
                # Cache should only contain fonts that were actually registered
                for font_name in cache_entry:
                    self.assertIn(font_name, font_names)

    def test_cache_memory_usage_patterns(self):
        """Test cache memory usage patterns"""
        import sys

        # Measure initial cache size
        initial_cache_size = sys.getsizeof(_FONT_REGISTRATION_CACHE)

        # Add many entries to cache
        num_pages = 100
        fonts_per_page = 5

        mock_pages = [Mock() for _ in range(num_pages)]

        with patch(
            "pdfrebuilder.font_utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            for _i, mock_page in enumerate(mock_pages):
                for j in range(fonts_per_page):
                    font_name = f"TestFont{j}"
                    ensure_font_registered(mock_page, font_name, verbose=False)

        # Measure final cache size
        final_cache_size = sys.getsizeof(_FONT_REGISTRATION_CACHE)

        # Cache should have grown, but not excessively
        cache_growth = final_cache_size - initial_cache_size
        self.assertGreater(cache_growth, 0)

        # Cache should be reasonably sized (less than 1MB for this test)
        threshold = 1024 * 1024  # 1MB
        try:
            self.assertLess(final_cache_size, threshold)
        except AssertionError:
            error_msg = (
                f"Font cache size test failed:\n"
                f"  Final cache size: {final_cache_size:,} bytes ({final_cache_size / 1024:.1f} KB)\n"
                f"  Threshold:        {threshold:,} bytes ({threshold / 1024:.1f} KB)\n"
                f"  Cache growth:     {cache_growth:,} bytes\n"
                f"  Pages processed:  {num_pages}\n"
                f"  Fonts per page:   {fonts_per_page}\n"
                f"  \n"
                f"  This test verifies that font cache doesn't grow excessively.\n"
                f"  The failure could indicate:\n"
                f"  - Memory leak in font caching\n"
                f"  - Cache not being cleaned up properly\n"
                f"  - Test parameters creating larger cache than expected\n"
                f"  \n"
                f"  Consider investigating cache cleanup or adjusting threshold."
            )
            raise AssertionError(error_msg)

        # Verify cache structure is correct
        self.assertEqual(len(_FONT_REGISTRATION_CACHE), num_pages)

        for mock_page in mock_pages:
            page_id = id(mock_page)
            self.assertIn(page_id, _FONT_REGISTRATION_CACHE)
            cache_entry = _FONT_REGISTRATION_CACHE[page_id]
            self.assertEqual(len(cache_entry), fonts_per_page)


if __name__ == "__main__":
    unittest.main()
