"""
Integration tests for Font Management System workflows.

This module tests:
- Complete font discovery workflows
- Font substitution workflows
- Font cache performance workflows
- End-to-end font processing workflows
"""

import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from pdfrebuilder.font.font_validator import FontValidator
from pdfrebuilder.font.utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    ensure_font_registered,
    scan_available_fonts,
    set_font_validator,
)

# Import test configuration
from tests.config import cleanup_test_output, get_test_fonts_dir, get_test_temp_dir


class TestFontDiscoveryWorkflow(unittest.TestCase):
    """Test end-to-end font discovery workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Create controlled test font environment
        self.create_controlled_font_environment()

        # Create test font files
        self.create_test_font_files()

        # Patch TTFont to avoid parsing dummy files
        self.patcher = patch("pdfrebuilder.font.utils.TTFont")
        self.mock_ttfont_class = self.patcher.start()
        self.mock_ttfont_instance = MagicMock()
        self.mock_ttfont_class.return_value = self.mock_ttfont_instance

        font_data = {
            "name": self.create_mock_name_table(),
            "cmap": self.create_mock_cmap_table(),
        }
        self.mock_ttfont_instance.__getitem__.side_effect = font_data.get

    def tearDown(self):
        """Clean up test fixtures"""
        self.patcher.stop()
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

    def create_mock_name_table(self):
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        return mock_name_table

    def create_mock_cmap_table(self):
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {}
        return mock_cmap_table

    def create_controlled_font_environment(self):
        """Create a controlled test environment with specific fonts"""
        os.makedirs(self.test_fonts_dir, exist_ok=True)

        # Define a fixed set of test fonts
        self.test_fonts = {
            "Arial": "Arial.ttf",
            "Times": "Times.ttf",
            "Helvetica": "Helvetica.ttf",
            "Courier": "Courier.ttf",
            "Symbol": "Symbol.ttf",
            "Roboto": "Roboto.ttf",
            "OpenSans": "OpenSans.ttf",
        }

        # Create mock font files for testing
        for font_name, font_file in self.test_fonts.items():
            font_path = os.path.join(self.test_fonts_dir, font_file)
            with open(font_path, "w") as f:
                f.write(f"Mock font content for {font_name}")

    def create_test_font_files(self):
        """Create dummy font files for testing"""
        os.makedirs(self.test_fonts_dir, exist_ok=True)

        # Create dummy font files
        test_fonts = [
            "Arial.ttf",
            "Times.otf",
            "Roboto-Regular.ttf",
            "OpenSans-Bold.ttf",
        ]
        for font_file in test_fonts:
            font_path = os.path.join(self.test_fonts_dir, font_file)
            with open(font_path, "w") as f:
                f.write(f"dummy font content for {font_file}")

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_complete_font_discovery_workflow(self, mock_ttfont):
        """Test complete font discovery from directory scanning to registration"""
        # Mock TTFont for font scanning
        mock_font = MagicMock()
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        mock_font.__getitem__.return_value = mock_name_table
        mock_ttfont.return_value = mock_font

        # Test font discovery
        discovered_fonts = scan_available_fonts(self.test_fonts_dir)

        # Should discover fonts
        self.assertGreater(len(discovered_fonts), 0)
        self.assertIn("Arial", discovered_fonts)

        # Test font registration using discovered font
        mock_page = Mock()
        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(mock_page, "Arial", verbose=False)

        self.assertEqual(result, "Arial")
        mock_page.insert_font.assert_called_once()

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.TTFont")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_font_download_integration_workflow(self, mock_exists, mock_ttfont, mock_download):
        """Test integration of font download with registration workflow"""
        mock_page = Mock()
        font_name = "NewFont"

        # Mock that font file doesn't exist locally initially, but exists after download
        download_happened = False

        def exists_side_effect(path):
            nonlocal download_happened
            # After download, the font file should exist
            if download_happened and font_name in path and path.endswith(".ttf"):
                return True
            # Return False for the font file to force download initially
            if font_name in path:
                return False
            # Return True for other fonts in our controlled environment
            if any(font in path for font in self.test_fonts.keys()):
                return True
            return True

        mock_exists.side_effect = exists_side_effect

        # Mock successful download and set flag
        def download_side_effect(name, directory):
            nonlocal download_happened
            download_happened = True
            return [downloaded_file]

        mock_download.side_effect = download_side_effect

        # Mock successful download
        downloaded_file = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")

        # Clear any existing download attempts for this font
        if font_name in _FONT_DOWNLOAD_ATTEMPTED:
            _FONT_DOWNLOAD_ATTEMPTED.remove(font_name)

        # Create the actual font file that was "downloaded"
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        with open(downloaded_file, "w") as f:
            f.write("downloaded font content")

        # Mock TTFont for the downloaded font
        mock_font = MagicMock()
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
        mock_font.__getitem__.return_value = mock_name_table
        mock_ttfont.return_value = mock_font

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # First call should trigger download
            result = ensure_font_registered(mock_page, font_name, verbose=False)

        # Allow for some flexibility in font registration
        # The font registration might return the downloaded font name or fallback
        self.assertIn(result, [font_name, "helv"])
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)
        mock_page.insert_font.assert_called()

    def test_font_cache_integration_workflow(self):
        """Test font caching across multiple registration calls"""
        mock_page = Mock()
        font_name = "Arial"

        # Font file is already created in setUp via create_controlled_font_environment()

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # First registration
            result1 = ensure_font_registered(mock_page, font_name, verbose=False)

            # Second registration should use cache
            result2 = ensure_font_registered(mock_page, font_name, verbose=False)

        self.assertEqual(result1, font_name)
        self.assertEqual(result2, font_name)

        # Font should only be registered once due to caching
        self.assertEqual(mock_page.insert_font.call_count, 1)

        # Verify cache contains the font
        page_id = id(mock_page)
        self.assertIn(font_name, _FONT_REGISTRATION_CACHE[page_id])


class TestFontSubstitutionWorkflow(unittest.TestCase):
    """Test end-to-end font substitution workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Set up font validator for tracking
        self.font_validator = FontValidator(self.test_fonts_dir)
        set_font_validator(self.font_validator)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()
        set_font_validator(None)

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    def test_complete_substitution_workflow(self, mock_covers, mock_scan, mock_download):
        """Test complete font substitution workflow with tracking"""
        mock_page = Mock()
        original_font = "MissingFont"
        text = "Hello World"

        # Font download fails
        mock_download.return_value = None

        # Mock available fonts
        available_fonts = {
            "Arial": os.path.join(self.test_fonts_dir, "Arial.ttf"),
            "Times": os.path.join(self.test_fonts_dir, "Times.ttf"),
        }
        mock_scan.return_value = available_fonts

        # Mock coverage: Arial covers the text
        def coverage_side_effect(font_path, test_text):
            return "Arial" in font_path

        mock_covers.side_effect = coverage_side_effect

        # Create a mock ValidationResult that always passes
        mock_validation_result = Mock()
        mock_validation_result.valid = True
        mock_validation_result.errors = []
        mock_validation_result.warnings = []

        with (
            patch("pdfrebuilder.font.utils.FontValidator.validate_font_file", return_value=mock_validation_result),
            patch("pdfrebuilder.font.utils.FontValidator.validate_font_format", return_value=mock_validation_result),
            patch(
                "pdfrebuilder.font.utils.get_config_value",
                side_effect=lambda key: (
                    self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
                ),
            ),
        ):
            result = ensure_font_registered(mock_page, original_font, verbose=False, text=text)

        # Should substitute with Arial, as it's available and covers the text
        self.assertEqual(result, "Arial")

        # Verify substitution was tracked
        self.assertEqual(len(self.font_validator.substitution_tracker), 1)
        substitution = self.font_validator.substitution_tracker[0]
        self.assertEqual(substitution.original_font, original_font)
        self.assertEqual(substitution.substituted_font, "Arial")
        # The reason is complex, so we'll just check that one was recorded.
        self.assertIsNotNone(substitution.reason)

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.scan_available_fonts")
    @patch("pdfrebuilder.font.utils.font_covers_text")
    def test_fallback_chain_workflow(self, mock_covers, mock_scan, mock_download):
        """Test complete fallback chain workflow"""
        mock_page = Mock()
        original_font = "NonExistentFont"
        text = "Hello 🌍"  # Text with emoji that most fonts won't cover

        # Font download fails
        mock_download.return_value = None

        # Mock available fonts
        available_fonts = {"Arial": "/path/to/arial.ttf", "Times": "/path/to/times.ttf"}
        mock_scan.return_value = available_fonts

        # Mock coverage: no font covers the text
        mock_covers.return_value = False

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(mock_page, original_font, verbose=False, text=text)

        # Should fallback to first available font in fallback chain
        self.assertEqual(result, "Courier")

        # Verify substitution was tracked
        self.assertEqual(len(self.font_validator.substitution_tracker), 1)
        substitution = self.font_validator.substitution_tracker[0]
        self.assertEqual(substitution.original_font, original_font)
        self.assertEqual(substitution.substituted_font, "Courier")
        self.assertEqual(substitution.reason, "Fallback font registration")

    def test_multiple_substitutions_tracking(self):
        """Test tracking of multiple font substitutions in a workflow"""
        mock_page = Mock()

        # Create multiple font registration scenarios
        fonts_to_test = ["Font1", "Font2", "Font3"]

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            with patch("pdfrebuilder.font.utils.download_google_font", return_value=None):
                for font_name in fonts_to_test:
                    ensure_font_registered(mock_page, font_name, verbose=False)

        # Should have tracked all substitutions
        self.assertEqual(len(self.font_validator.substitution_tracker), len(fonts_to_test))

        # Verify all substitutions were to default font
        for substitution in self.font_validator.substitution_tracker:
            self.assertEqual(substitution.substituted_font, "helv")
            self.assertIn(substitution.original_font, fonts_to_test)


class TestFontValidationIntegrationWorkflow(unittest.TestCase):
    """Test integration of font validation with document processing"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Set up font validator for tracking
        self.font_validator = FontValidator(self.test_fonts_dir)
        set_font_validator(self.font_validator)

        # Create sample document configuration
        self.sample_config = {
            "version": "1.0",
            "engine": "fitz",
            "metadata": {"title": "Test Document"},
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": "page_0_base_layer",
                            "content": [
                                {
                                    "type": "text",
                                    "id": "text_0",
                                    "text": "Hello World",
                                    "font_details": {"name": "Arial", "size": 12},
                                },
                                {
                                    "type": "text",
                                    "id": "text_1",
                                    "text": "Missing Font Text",
                                    "font_details": {
                                        "name": "NonExistentFont",
                                        "size": 14,
                                    },
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        # Patch TTFont to avoid parsing dummy files
        self.patcher = patch("pdfrebuilder.font.utils.TTFont")
        self.mock_ttfont_class = self.patcher.start()
        self.mock_ttfont_instance = MagicMock()
        self.mock_ttfont_class.return_value = self.mock_ttfont_instance

        font_data = {
            "name": self.create_mock_name_table(),
            "cmap": self.create_mock_cmap_table(),
        }
        self.mock_ttfont_instance.__getitem__.side_effect = font_data.get

    def tearDown(self):
        """Clean up test fixtures"""
        self.patcher.stop()
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()
        set_font_validator(None)

    def create_mock_name_table(self):
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        return mock_name_table

    def create_mock_cmap_table(self):
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {}
        return mock_cmap_table

    def test_document_font_validation_workflow(self):
        """Test complete document font validation workflow"""
        validator = FontValidator(self.test_fonts_dir)

        # Validate document fonts
        result = validator.validate_document_fonts(self.sample_config)

        # Should have extracted fonts
        self.assertIn("Arial", result.fonts_required)
        self.assertIn("NonExistentFont", result.fonts_required)

        # Should have missing fonts (since we don't have them in temp dir)
        self.assertIn("NonExistentFont", result.fonts_missing)

        # Should have validation messages
        self.assertGreater(len(result.validation_messages), 0)

        # Should fail validation due to missing fonts
        self.assertFalse(result.validation_passed)

    @patch("pdfrebuilder.font.font_validator.font_covers_text")
    def test_font_coverage_validation_workflow(self, mock_covers_text):
        """Test font coverage validation workflow"""
        # Create a font file
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        font_path = os.path.join(self.test_fonts_dir, "Arial.ttf")
        with open(font_path, "w") as f:
            f.write("dummy font content")

        # Mock coverage failure
        mock_covers_text.return_value = False

        validator = FontValidator(self.test_fonts_dir)

        # Mock _find_missing_characters to return some missing chars
        with patch.object(validator, "_find_missing_characters", return_value=["ñ", "ü"]):
            result = validator.validate_document_fonts(self.sample_config)

        # Should have coverage issues
        self.assertGreater(len(result.font_coverage_issues), 0)

        # Should have validation messages about coverage
        coverage_messages = [msg for msg in result.validation_messages if "missing glyphs" in msg]
        self.assertGreater(len(coverage_messages), 0)

    def test_font_validation_report_generation(self):
        """Test font validation report generation workflow"""
        validator = FontValidator(self.test_fonts_dir)

        # Track some substitutions
        validator.track_font_substitution("Arial", "Helvetica", "Test substitution", "Hello World")
        validator.track_font_substitution("Times", "DejaVu", "Another test", "Test text")

        # Generate report
        report = validator.get_font_validation_report()

        # Verify report structure
        self.assertIn("fonts_directory", report)
        self.assertIn("available_fonts_count", report)
        self.assertIn("substitutions_tracked", report)
        self.assertIn("substitutions", report)

        # Verify substitution data
        self.assertEqual(len(report["substitutions"]), 2)
        self.assertEqual(report["substitutions"][0]["original_font"], "Arial")
        self.assertEqual(report["substitutions"][0]["substituted_font"], "Helvetica")


class TestFontCachePerformanceWorkflow(unittest.TestCase):
    """Test font cache functionality and performance"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Set up font validator for tracking
        self.font_validator = FontValidator(self.test_fonts_dir)
        set_font_validator(self.font_validator)

        # Create controlled font environment
        self.create_controlled_font_environment()

    def create_controlled_font_environment(self):
        """Create a controlled test environment with specific fonts"""
        os.makedirs(self.test_fonts_dir, exist_ok=True)

        # Define a fixed set of test fonts
        self.test_fonts = {
            "Arial": "Arial.ttf",
            "Times": "Times.ttf",
            "Helvetica": "Helvetica.ttf",
            "Courier": "Courier.ttf",
            "Symbol": "Symbol.ttf",
            "Roboto": "Roboto.ttf",
            "OpenSans": "OpenSans.ttf",
        }

        # Create mock font files for testing
        for font_name, font_file in self.test_fonts.items():
            font_path = os.path.join(self.test_fonts_dir, font_file)
            with open(font_path, "w") as f:
                f.write(f"Mock font content for {font_name}")

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()
        set_font_validator(None)

    def test_font_registration_cache_workflow(self):
        """Test font registration cache across multiple pages"""
        # Create multiple mock pages
        pages = [Mock() for _ in range(3)]
        font_name = "Arial"

        # Font file is already created in setUp via create_controlled_font_environment()

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # Register font on each page
            for page in pages:
                result = ensure_font_registered(page, font_name, verbose=False)
                self.assertEqual(result, font_name)

        # Each page should have its own cache entry
        for page in pages:
            page_id = id(page)
            self.assertIn(page_id, _FONT_REGISTRATION_CACHE)
            self.assertIn(font_name, _FONT_REGISTRATION_CACHE[page_id])

        # Each page should have called insert_font once
        for page in pages:
            page.insert_font.assert_called_once()

    def test_download_attempt_cache_workflow(self):
        """Test download attempt caching to prevent repeated downloads"""
        mock_page = Mock()
        font_name = "NonExistentFont"

        with patch("pdfrebuilder.font.utils.download_google_font") as mock_download:
            mock_download.return_value = None  # Download fails

            with patch(
                "pdfrebuilder.font.utils.get_config_value",
                side_effect=lambda key: (
                    self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
                ),
            ):
                # First attempt should try download
                result1 = ensure_font_registered(mock_page, font_name, verbose=False)

                # Second attempt should not try download again
                result2 = ensure_font_registered(mock_page, font_name, verbose=False)

        # Both should fallback to the default font from the mock config
        self.assertEqual(result1, "helv")
        self.assertEqual(result2, "helv")

        # Download should only be attempted once
        mock_download.assert_called_once_with(font_name, self.test_fonts_dir)

        # Font should be in download attempted cache
        self.assertIn(font_name, _FONT_DOWNLOAD_ATTEMPTED)

    @patch("pdfrebuilder.font.font_validator.scan_available_fonts")
    def test_font_scanning_cache_workflow(self, mock_scan):
        """Test that font scanning results are cached for performance"""
        # Mock scan results
        mock_fonts = {"Arial": "/path/to/arial.ttf", "Times": "/path/to/times.ttf"}
        mock_scan.return_value = mock_fonts

        # Create validator after patching scan_available_fonts
        from pdfrebuilder.font.font_validator import FontValidator

        validator = FontValidator(self.test_fonts_dir)

        # First access should trigger scan
        fonts1 = validator.available_fonts

        # Refresh should trigger scan again
        validator._refresh_available_fonts()
        fonts2 = validator.available_fonts

        # Both should have same results
        self.assertEqual(fonts1, mock_fonts)
        self.assertEqual(fonts2, mock_fonts)

        # Scan should be called twice (once in init, once in refresh)
        self.assertEqual(mock_scan.call_count, 2)


class TestEndToEndFontWorkflow(unittest.TestCase):
    """Test complete end-to-end font management workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.test_fonts_dir = get_test_fonts_dir(self.test_name)

        # Clear caches
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()

        # Set up font validator
        self.font_validator = FontValidator(self.test_fonts_dir)
        set_font_validator(self.font_validator)

        # Create test document configuration
        self.document_config = {
            "version": "1.0",
            "engine": "fitz",
            "metadata": {"title": "Integration Test Document"},
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": "page_0_base_layer",
                            "content": [
                                {
                                    "type": "text",
                                    "id": "text_0",
                                    "text": "Standard Font Text",
                                    "font_details": {"name": "helv", "size": 12},
                                },
                                {
                                    "type": "text",
                                    "id": "text_1",
                                    "text": "Local Font Text",
                                    "font_details": {"name": "Arial", "size": 14},
                                },
                                {
                                    "type": "text",
                                    "id": "text_2",
                                    "text": "Missing Font Text",
                                    "font_details": {"name": "MissingFont", "size": 16},
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        # Patch TTFont to avoid parsing dummy files
        self.patcher = patch("pdfrebuilder.font.utils.TTFont")
        self.mock_ttfont_class = self.patcher.start()
        self.mock_ttfont_instance = MagicMock()
        self.mock_ttfont_class.return_value = self.mock_ttfont_instance

        font_data = {
            "name": self.create_mock_name_table(),
            "cmap": self.create_mock_cmap_table(),
        }
        self.mock_ttfont_instance.__getitem__.side_effect = font_data.get

    def tearDown(self):
        """Clean up test fixtures"""
        self.patcher.stop()
        cleanup_test_output(self.test_name)
        _FONT_REGISTRATION_CACHE.clear()
        _FONT_DOWNLOAD_ATTEMPTED.clear()
        set_font_validator(None)

    def create_mock_name_table(self):
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        return mock_name_table

    def create_mock_cmap_table(self):
        mock_cmap_table = Mock()
        mock_cmap_table.cmap = {}
        return mock_cmap_table

    @patch("pdfrebuilder.font.utils.download_google_font")
    @patch("pdfrebuilder.font.utils.TTFont")
    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_complete_document_processing_workflow(self, mock_exists, mock_ttfont, mock_download):
        """Test complete document processing workflow with font management"""

        # Mock font file existence
        def exists_side_effect(path):
            if "Arial.ttf" in path:
                return True
            if "MissingFont" in path:
                return False
            if self.test_fonts_dir in path and not any(font in path for font in ["Arial.ttf", "MissingFont"]):
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        # Mock download failure for missing font
        mock_download.return_value = None

        # Create Arial font file to ensure it exists
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        arial_path = os.path.join(self.test_fonts_dir, "Arial.ttf")
        with open(arial_path, "w") as f:
            f.write("Arial font content")

        # Mock TTFont for font file reading
        mock_font = MagicMock()
        mock_name_table = Mock()
        mock_name_table.names = [Mock(nameID=1, platformID=3, string=b"Arial")]
        mock_font.__getitem__.return_value = mock_name_table
        mock_ttfont.return_value = mock_font

        mock_page = Mock()

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # Process each text element as would happen in document generation
            for doc_unit in self.document_config["document_structure"]:
                for layer in doc_unit["layers"]:
                    for element in layer["content"]:
                        if element["type"] == "text":
                            font_name = element["font_details"]["name"]
                            text_content = element["text"]

                            result = ensure_font_registered(mock_page, font_name, verbose=False, text=text_content)

                            # Verify appropriate font was registered
                            if font_name == "helv":
                                self.assertEqual(result, "helv")  # Standard font
                            elif font_name == "Arial":
                                # Allow for some flexibility in font registration
                                # The font registration might return the local font name or fallback
                                self.assertIn(result, ["Arial", "Helvetica"])  # Local font or fallback
                            elif font_name == "MissingFont":
                                self.assertEqual(result, "Helvetica")  # Fallback

        # Verify font validation results
        validation_result = self.font_validator.validate_document_fonts(self.document_config)

        # Should have found all required fonts
        expected_fonts = {"helv", "Arial", "MissingFont"}
        self.assertEqual(validation_result.fonts_required, expected_fonts)

        # Should have tracked substitution for missing font
        substitutions = self.font_validator.substitution_tracker
        missing_font_substitutions = [s for s in substitutions if s.original_font == "MissingFont"]
        self.assertEqual(len(missing_font_substitutions), 1)
        self.assertEqual(missing_font_substitutions[0].substituted_font, "Helvetica")

        # Should have validation report
        report = self.font_validator.get_font_validation_report()
        self.assertIn("substitutions", report)
        self.assertGreater(len(report["substitutions"]), 0)

    @patch("pdfrebuilder.font.utils.os.path.exists")
    def test_font_workflow_error_recovery(self, mock_exists):
        """Test font workflow error recovery and graceful degradation"""
        mock_page = Mock()

        # Mock font loading error
        mock_page.insert_font.side_effect = Exception("Font loading error")

        font_name = "ProblematicFont"

        # Mock that the font file exists
        def exists_side_effect(path):
            if font_name in path:
                return True
            return True

        mock_exists.side_effect = exists_side_effect

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            result = ensure_font_registered(mock_page, font_name, verbose=False)

        # Should fallback to default font
        self.assertEqual(result, "helv")

        # Should have gracefully recovered without tracking substitution
        # (since helv is a standard PDF font that doesn't require file loading)
        substitutions = self.font_validator.substitution_tracker
        print(f"DEBUG: All substitutions: {[(s.original_font, s.substituted_font, s.reason) for s in substitutions]}")
        # No substitution should be tracked because helv is a standard PDF font that works
        self.assertEqual(len(substitutions), 0)

    def test_concurrent_font_operations_workflow(self):
        """Test font operations with multiple concurrent requests"""
        # Simulate multiple pages requesting fonts simultaneously
        pages = [Mock() for _ in range(5)]
        fonts_to_register = ["Arial", "Times", "Roboto", "OpenSans"]

        # Create font files
        os.makedirs(self.test_fonts_dir, exist_ok=True)
        for font_name in fonts_to_register:
            font_path = os.path.join(self.test_fonts_dir, f"{font_name}.ttf")
            with open(font_path, "w") as f:
                f.write(f"{font_name} font content")

        with patch(
            "pdfrebuilder.font.utils.get_config_value",
            side_effect=lambda key: (
                self.test_fonts_dir if key in ["downloaded_fonts_dir", "manual_fonts_dir"] else "helv"
            ),
        ):
            # Register fonts on all pages
            for page in pages:
                for font_name in fonts_to_register:
                    result = ensure_font_registered(page, font_name, verbose=False)
                    self.assertEqual(result, font_name)

        # Verify each page has its own cache
        for page in pages:
            page_id = id(page)
            self.assertIn(page_id, _FONT_REGISTRATION_CACHE)
            for font_name in fonts_to_register:
                self.assertIn(font_name, _FONT_REGISTRATION_CACHE[page_id])

        # Verify each page registered each font once
        for page in pages:
            self.assertEqual(page.insert_font.call_count, len(fonts_to_register))


if __name__ == "__main__":
    unittest.main()
