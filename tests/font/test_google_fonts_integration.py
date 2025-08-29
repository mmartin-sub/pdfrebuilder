"""
Unit tests for Google Fonts Integration

This module tests the Google Fonts download functionality,
including API interaction, error handling, and file management.
"""

import logging
import os
import unittest
from unittest.mock import Mock, patch

import requests

from pdfrebuilder.font.googlefonts import download_google_font

# Import test configuration
from tests.config import cleanup_test_output, get_test_temp_dir


class TestGoogleFontsAPI(unittest.TestCase):
    """Test Google Fonts API integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_single_font_weight(self, mock_get):
        """Test downloading a single font weight"""
        font_family = "Roboto"

        # Mock CSS response with single font URL
        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        @font-face {
          font-family: 'Roboto';
          font-style: normal;
          font-weight: 400;
          src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2) format('woff2');
        }
        """

        # Mock font file response
        font_response = Mock()
        font_response.content = b"fake woff2 font data"
        font_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response]

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(len(result), 1)
            self.assertTrue(result[0].endswith("KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2"))

            # Verify the file was created
            self.assertTrue(os.path.exists(result[0]))

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_download_multiple_font_weights(self, mock_get):
        """Test downloading multiple font weights (400 and 700)"""
        font_family = "Open Sans"

        # Mock CSS response with multiple font URLs
        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        @font-face {
          font-family: 'Open Sans';
          font-style: normal;
          font-weight: 400;
          src: url(https://fonts.gstatic.com/s/opensans/v34/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjB_mQ.woff2) format('woff2');
        }
        @font-face {
          font-family: 'Open Sans';
          font-style: normal;
          font-weight: 700;
          src: url(https://fonts.gstatic.com/s/opensans/v34/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVQUwaEQbjB_mQ.woff2) format('woff2');
        }
        """

        # Mock font file responses
        font_response_400 = Mock()
        font_response_400.content = b"fake woff2 font data 400"
        font_response_400.raise_for_status = Mock()

        font_response_700 = Mock()
        font_response_700.content = b"fake woff2 font data 700"
        font_response_700.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response_400, font_response_700]

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(len(result), 2)

            # Verify both files were created
            for file_path in result:
                self.assertTrue(os.path.exists(file_path))

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_font_family_name_with_spaces(self, mock_get):
        """Test downloading font with spaces in family name"""
        font_family = "Source Sans Pro"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        src: url(https://fonts.gstatic.com/s/sourcesanspro/v21/6xK3dSBYKcSV-LCoeQqfX1RYOo3qOK7lujVj9w.woff2);
        """

        font_response = Mock()
        font_response.content = b"fake font data"
        font_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response]

        result = download_google_font(font_family, self.temp_dir)

        # Verify the CSS URL was constructed correctly (spaces replaced with +)
        expected_css_url = "https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,700"
        # Check that the URL was called with timeout parameter
        mock_get.assert_any_call(expected_css_url, timeout=10)

        self.assertIsNotNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_css_fetch_http_error(self, mock_get):
        """Test handling of HTTP errors when fetching CSS"""
        font_family = "NonExistentFont"

        mock_get.side_effect = requests.exceptions.RequestException("HTTP error")

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="ERROR") as cm:
            result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, 3)
        self.assertIn("Could not fetch CSS for NonExistentFont", cm.output[0])

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_css_fetch_network_error(self, mock_get):
        """Test handling of network errors when fetching CSS"""
        font_family = "Roboto"

        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="ERROR") as cm:
            result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)
        self.assertEqual(mock_get.call_count, 3)
        self.assertIn("Could not fetch CSS for Roboto", cm.output[0])

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_font_file_download_error(self, mock_get):
        """Test handling of errors when downloading font files"""
        font_family = "Roboto"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = "src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2);"
        css_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response] + [requests.exceptions.RequestException("Download failed")] * 3

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="ERROR") as cm:
            result = download_google_font(font_family, self.temp_dir)

        self.assertEqual(result, [])
        self.assertIn(
            "Failed to download https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2",
            cm.output[0],
        )

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_partial_download_failure(self, mock_get):
        """Test handling when some font files download successfully and others fail"""
        font_family = "Roboto"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        src: url(https://fonts.gstatic.com/s/roboto/v30/regular.woff2);
        src: url(https://fonts.gstatic.com/s/roboto/v30/bold.woff2);
        """
        css_response.raise_for_status = Mock()

        font_response_success = Mock()
        font_response_success.content = b"fake font data"
        font_response_success.raise_for_status = Mock()

        mock_get.side_effect = [
            css_response,
            font_response_success,
        ] + [requests.exceptions.RequestException("Download failed")] * 3

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="ERROR") as cm:
            result = download_google_font(font_family, self.temp_dir)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(len(result), 1)
            self.assertTrue(result[0].endswith("regular.woff2"))
        self.assertIn("Failed to download https://fonts.gstatic.com/s/roboto/v30/bold.woff2", cm.output[0])

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_empty_css_response(self, mock_get):
        """Test handling of empty CSS response"""
        font_family = "EmptyFont"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = ""
        mock_get.return_value = css_response

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="WARNING"):
            result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_css_with_no_font_urls(self, mock_get):
        """Test handling of CSS response with no font URLs"""
        font_family = "NoUrlsFont"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        /* This is a CSS comment */
        .some-class {
            font-family: 'NoUrlsFont';
        }
        """
        mock_get.return_value = css_response

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="WARNING") as cm:
            result = download_google_font(font_family, self.temp_dir)

        self.assertIsNone(result)
        self.assertIn("No font files found for 'NoUrlsFont'", cm.output[0])

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_directory_creation(self, mock_get):
        """Test that destination directory is created if it doesn't exist"""
        font_family = "Roboto"
        dest_dir = os.path.join(self.temp_dir, "nested", "fonts", "directory")

        # Ensure directory doesn't exist initially
        self.assertFalse(os.path.exists(dest_dir))

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = "src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2);"
        css_response.raise_for_status = Mock()

        font_response = Mock()
        font_response.content = b"fake font data"
        font_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response]

        result = download_google_font(font_family, dest_dir)

        # Verify directory was created
        self.assertTrue(os.path.exists(dest_dir))
        self.assertIsNotNone(result)

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_file_write_permission_error(self, mock_file, mock_get):
        """Test handling of file write permission errors"""
        font_family = "Roboto"

        css_response = Mock()
        css_response.status_code = 200
        css_response.text = "src: url(https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.woff2);"
        css_response.raise_for_status = Mock()

        font_response = Mock()
        font_response.content = b"fake font data"
        font_response.raise_for_status = Mock()

        mock_get.side_effect = [css_response, font_response, font_response, font_response]

        with self.assertLogs("pdfrebuilder.font.googlefonts", level="ERROR") as cm:
            result = download_google_font(font_family, self.temp_dir)

        self.assertEqual(result, [])
        self.assertIn("Failed to download", cm.output[0])

    @patch("pdfrebuilder.font.googlefonts.requests.get")
    def test_url_extraction_regex_patterns(self, mock_get):
        """Test various URL patterns in CSS responses"""
        font_family = "TestFont"

        # Test different URL formats that might appear in Google Fonts CSS
        # Note: The current regex only matches URLs without quotes
        css_response = Mock()
        css_response.status_code = 200
        css_response.text = """
        /* No quotes - this will be matched */
        src: url(https://fonts.gstatic.com/s/test/no-quotes.woff2);

        /* With format specifier - this will be matched */
        src: url(https://fonts.gstatic.com/s/test/with-format.woff2) format('woff2');

        /* Multiple sources - both will be matched */
        src: url(https://fonts.gstatic.com/s/test/first.woff2) format('woff2'),
             url(https://fonts.gstatic.com/s/test/second.woff) format('woff');
        """

        # Mock font responses - expect 4 URLs to be extracted
        font_responses = []
        for i in range(4):
            response = Mock()
            response.content = f"fake font data {i}".encode()
            response.raise_for_status = Mock()
            font_responses.append(response)

        mock_get.side_effect = [css_response, *font_responses]

        result = download_google_font(font_family, self.temp_dir)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(len(result), 4)

            # Verify all expected files were created
            expected_files = [
                "no-quotes.woff2",
                "with-format.woff2",
                "first.woff2",
                "second.woff",
            ]

            for expected_file in expected_files:
                self.assertTrue(any(expected_file in path for path in result))

    def test_default_destination_directory(self):
        """Test using default destination directory"""
        font_family = "Roboto"

        with patch("pdfrebuilder.font.googlefonts.requests.get") as mock_get:
            css_response = Mock()
            css_response.status_code = 200
            css_response.text = """
            src: url(https://fonts.gstatic.com/s/roboto/v30/test.woff2);
            """

            font_response = Mock()
            font_response.content = b"fake font data"
            font_response.raise_for_status = Mock()

            mock_get.side_effect = [css_response, font_response]

            # Mock the default directory
            with patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", "./output/fonts"):
                # Call without specifying dest_dir (should use default)
                result = download_google_font(font_family)

                self.assertIsNotNone(result)
                # Should create the configured fonts directory
                self.assertTrue(os.path.exists("./output/fonts"))

                # Clean up
                import shutil

                shutil.rmtree("./output/fonts", ignore_errors=True)


class TestGoogleFontsIntegrationEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions in Google Fonts integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)

    def tearDown(self):
        """Clean up test fixtures"""
        cleanup_test_output(self.test_name)

    def test_font_family_with_special_characters(self):
        """Test font family names with special characters"""
        special_names = [
            "Font-Name",
            "Font_Name",
            "Font Name",
            "Font123",
            "Font & Co",
            "Font+Plus",
        ]

        for font_name in special_names:
            with patch("pdfrebuilder.font.googlefonts.requests.get") as mock_get:
                mock_get.side_effect = requests.exceptions.RequestException("HTTP error")

                with self.assertLogs("pdfrebuilder.font.googlefonts", level="ERROR") as cm:
                    result = download_google_font(font_name, self.temp_dir)
                self.assertIsNone(result)
                self.assertEqual(mock_get.call_count, 3)
                self.assertIn(f"Could not fetch CSS for {font_name}", cm.output[0])

    def test_very_large_font_file(self):
        """Test handling of very large font files"""
        font_family = "LargeFont"

        with patch("pdfrebuilder.font.googlefonts.requests.get") as mock_get:
            css_response = Mock()
            css_response.status_code = 200
            css_response.text = """
            src: url(https://fonts.gstatic.com/s/large/font.woff2);
            """

            # Mock a very large font file (10MB)
            font_response = Mock()
            font_response.content = b"x" * (10 * 1024 * 1024)
            font_response.raise_for_status = Mock()

            mock_get.side_effect = [css_response, font_response]

            result = download_google_font(font_family, self.temp_dir)

            self.assertIsNotNone(result)
            if result:
                # Verify the large file was written correctly
                self.assertTrue(os.path.exists(result[0]))
                self.assertEqual(os.path.getsize(result[0]), 10 * 1024 * 1024)

    def test_concurrent_downloads_same_font(self):
        """Test behavior when multiple processes try to download the same font"""
        # This test simulates race conditions that might occur in real usage
        font_family = "Roboto"

        with patch("pdfrebuilder.font.googlefonts.requests.get") as mock_get:
            css_response = Mock()
            css_response.status_code = 200
            css_response.text = """
            src: url(https://fonts.gstatic.com/s/roboto/v30/test.woff2);
            """

            font_response = Mock()
            font_response.content = b"fake font data"
            font_response.raise_for_status = Mock()

            mock_get.side_effect = [css_response, font_response]

            # First download
            result1 = download_google_font(font_family, self.temp_dir)

            # Reset mock for second download
            mock_get.side_effect = [css_response, font_response]

            # Second download to same directory
            result2 = download_google_font(font_family, self.temp_dir)

            # Both should succeed (second overwrites first)
            self.assertIsNotNone(result1)
            self.assertIsNotNone(result2)
