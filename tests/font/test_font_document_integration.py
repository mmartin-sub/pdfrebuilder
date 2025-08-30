"""
Integration tests for Font Management System with document processing.

This module tests:
- Font integration with PDF generation pipeline
- Font validation in document processing workflow
- Error handling and recovery in document context
- Performance with real document structures
"""

import os
import pytest
from unittest.mock import MagicMock, Mock, patch

from pdfrebuilder.font.font_validator import FontValidator
from pdfrebuilder.font.utils import (
    _FONT_DOWNLOAD_ATTEMPTED,
    _FONT_REGISTRATION_CACHE,
    ensure_font_registered,
    get_font_error_reporter,
    set_font_validator,
)

# Import test configuration
from tests.config import cleanup_test_output, get_test_fonts_dir, get_test_temp_dir


@pytest.fixture
def document_font_integration_test(request):
    """Set up test fixtures for document font integration tests."""
    test_name = request.node.name
    temp_dir = get_test_temp_dir(test_name)
    test_fonts_dir = get_test_fonts_dir(test_name)

    # Clear caches before each test
    _FONT_REGISTRATION_CACHE.clear()
    _FONT_DOWNLOAD_ATTEMPTED.clear()
    reporter = get_font_error_reporter()
    reporter.clear_errors()

    # Create a controlled test environment with specific fonts
    os.makedirs(test_fonts_dir, exist_ok=True)
    test_fonts = {
        "Arial": "Arial.ttf",
        "Times": "Times.ttf",
        "Helvetica": "Helvetica.ttf",
        "Courier": "Courier.ttf",
        "Symbol": "Symbol.ttf",
        "Roboto": "Roboto.ttf",
        "OpenSans": "OpenSans.ttf",
    }
    for _font_name, font_file in test_fonts.items():
        font_path = os.path.join(test_fonts_dir, font_file)
        with open(font_path, "wb") as f:
            f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)

    # Set up font validator
    font_validator = FontValidator(test_fonts_dir)
    set_font_validator(font_validator)

    # Create a realistic document configuration
    document_config = {
        "version": "1.0",
        "engine": "fitz",
        "metadata": {"title": "Integration Test Document", "author": "Test Suite"},
        "document_structure": [
            {
                "type": "page", "page_number": 0, "size": [612, 792],
                "layers": [{
                    "content": [
                        {"type": "text", "id": "title_text", "text": "Document Title", "font_details": {"name": "Arial-Bold", "size": 24}},
                        {"type": "text", "id": "body_text", "text": "This is the main body text.", "font_details": {"name": "Times-Roman", "size": 12}},
                        {"type": "text", "id": "special_text", "text": "Special text with custom font", "font_details": {"name": "CustomFont", "size": 14}},
                    ]
                }]
            },
            {
                "type": "page", "page_number": 1, "size": [612, 792],
                "layers": [{
                    "content": [
                        {"type": "text", "id": "page2_header", "text": "Page 2 Header", "font_details": {"name": "Helvetica", "size": 18}},
                        {"type": "text", "id": "unicode_text", "text": "Unicode text: Héllo Wörld 世界 🌍", "font_details": {"name": "NotoSans", "size": 12}},
                    ]
                }]
            }
        ]
    }

    # Yield the test setup
    yield test_name, temp_dir, test_fonts_dir, font_validator, document_config

    # Teardown
    cleanup_test_output(test_name)
    _FONT_REGISTRATION_CACHE.clear()
    _FONT_DOWNLOAD_ATTEMPTED.clear()
    set_font_validator(None)


class TestDocumentFontIntegration:
    """Test font integration with document processing pipeline"""

    def test_complete_document_font_processing(self, document_font_integration_test):
        """Test complete document font processing workflow"""
        test_name, temp_dir, test_fonts_dir, font_validator, document_config = document_font_integration_test

        # Create some local font files
        os.makedirs(test_fonts_dir, exist_ok=True)
        local_fonts = ["Arial-Bold.ttf", "Times-Roman.ttf", "Helvetica.ttf"]
        for font_file in local_fonts:
            font_path = os.path.join(test_fonts_dir, font_file)
            with open(font_path, "wb") as f:
                f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)

        # Mock pages for each page in document
        mock_pages = [Mock() for _ in range(2)]

        with patch("pdfrebuilder.font.utils.TTFont") as mock_ttfont:
            def create_mock_font(font_path):
                mock_font = MagicMock()
                font_name = os.path.basename(font_path).replace(".ttf", "").replace(".otf", "")
                mock_name_table = Mock()
                mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
                mock_cmap_table = Mock()
                char_map = {ord(c): i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ")}
                mock_cmap_table.cmap = char_map
                mock_cmap_subtable = Mock()
                mock_cmap_subtable.tables = [mock_cmap_table]
                def getitem_side_effect(key):
                    if key == "name": return mock_name_table
                    elif key == "cmap": return mock_cmap_subtable
                    else: return Mock()
                mock_font.__getitem__.side_effect = getitem_side_effect
                return mock_font
            mock_ttfont.side_effect = create_mock_font

            with (
                patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", test_fonts_dir),
                patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", test_fonts_dir),
                patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
            ):
                for page_idx, doc_unit in enumerate(document_config["document_structure"]):
                    if doc_unit["type"] == "page":
                        for layer in doc_unit["layers"]:
                            for content in layer["content"]:
                                if content["type"] == "text":
                                    font_name = content["font_details"]["name"]
                                    ensure_font_registered(mock_pages[page_idx], font_name, verbose=False)

        validation_result = font_validator.validate_document_fonts(document_config)
        expected_fonts = {"Arial-Bold", "Times-Roman", "CustomFont", "Helvetica", "NotoSans"}
        assert validation_result.fonts_required == expected_fonts
        assert len(validation_result.fonts_available) > 0
        assert len(validation_result.fonts_missing) > 0

        substitutions = font_validator.substitution_tracker
        custom_font_sub = [s for s in substitutions if s.original_font == "CustomFont"]
        noto_sans_sub = [s for s in substitutions if s.original_font == "NotoSans"]
        assert len(custom_font_sub) > 0
        assert len(noto_sans_sub) > 0

    @patch("pdfrebuilder.font.utils._find_font_file_for_name", return_value=None)
    @patch("pdfrebuilder.font.utils.download_google_font")
    def test_document_with_google_fonts_integration(self, mock_download, mock_find_font, document_font_integration_test):
        """Test document processing with Google Fonts integration"""
        test_name, temp_dir, test_fonts_dir, font_validator, document_config = document_font_integration_test

        def download_side_effect(font_name, dest_dir):
            if font_name in ["Roboto", "OpenSans"]:
                downloaded_file = os.path.join(dest_dir, f"{font_name}.ttf")
                os.makedirs(dest_dir, exist_ok=True)
                with open(downloaded_file, "wb") as f:
                    f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)
                return [downloaded_file]
            return None
        mock_download.side_effect = download_side_effect

        google_fonts_config = {
            "version": "1.0",
            "document_structure": [{
                "type": "page", "page_number": 0,
                "layers": [{"content": [
                    {"type": "text", "text": "Text with Roboto", "font_details": {"name": "Roboto"}},
                    {"type": "text", "text": "Text with Open Sans", "font_details": {"name": "OpenSans"}},
                    {"type": "text", "text": "Text with unavailable font", "font_details": {"name": "UnavailableFont"}},
                ]}]
            }]
        }
        mock_page = Mock()

        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            fonts_in_doc = [
                element["font_details"]["name"]
                for doc_unit in google_fonts_config["document_structure"]
                for layer in doc_unit["layers"]
                for element in layer["content"]
                if element["type"] == "text"
            ]
            registered_fonts = set()
            for font_name in fonts_in_doc:
                if font_name in _FONT_DOWNLOAD_ATTEMPTED:
                    _FONT_DOWNLOAD_ATTEMPTED.remove(font_name)
                result = ensure_font_registered(mock_page, font_name, verbose=False)
                registered_fonts.add(result)

        assert mock_download.call_count == 3
        assert "Roboto" in registered_fonts or "helv" in registered_fonts
        assert "OpenSans" in registered_fonts or "helv" in registered_fonts
        assert "helv" in registered_fonts

        substitutions = font_validator.substitution_tracker
        unavailable_sub = [s for s in substitutions if s.original_font == "UnavailableFont"]
        assert len(unavailable_sub) > 0

    def test_document_font_coverage_validation(self, document_font_integration_test):
        """Test font coverage validation in document context"""
        test_name, temp_dir, test_fonts_dir, font_validator, document_config = document_font_integration_test

        unicode_config = {
            "version": "1.0",
            "document_structure": [{
                "type": "page", "page_number": 0,
                "layers": [{"content": [
                    {"type": "text", "text": "Basic Latin text", "font_details": {"name": "Arial"}},
                    {"type": "text", "text": "Accented text: café", "font_details": {"name": "Arial"}},
                    {"type": "text", "text": "Chinese text: 你好世界", "font_details": {"name": "Arial"}},
                    {"type": "text", "text": "Emoji text: 🌍🚀💻", "font_details": {"name": "Arial"}},
                ]}]
            }]
        }
        os.makedirs(test_fonts_dir, exist_ok=True)
        arial_path = os.path.join(test_fonts_dir, "Arial.ttf")
        with open(arial_path, "wb") as f:
            f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)

        def coverage_side_effect(font_path, text):
            return "你好世界" not in text and "🌍🚀💻" not in text

        with patch("pdfrebuilder.font.utils.TTFont") as mock_ttfont:
            def create_mock_font(font_path):
                mock_font = MagicMock()
                font_name = os.path.basename(font_path).replace(".ttf", "").replace(".otf", "")
                mock_name_table = Mock()
                mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
                mock_cmap_table = Mock()
                char_map = {ord(c): i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ")}
                mock_cmap_table.cmap = char_map
                mock_cmap_subtable = Mock()
                mock_cmap_subtable.tables = [mock_cmap_table]
                def getitem_side_effect(key):
                    if key == "name": return mock_name_table
                    elif key == "cmap": return mock_cmap_subtable
                    else: return Mock()
                mock_font.__getitem__.side_effect = getitem_side_effect
                return mock_font
            mock_ttfont.side_effect = create_mock_font

            with patch("pdfrebuilder.font.font_validator.font_covers_text", side_effect=coverage_side_effect):
                with patch.object(font_validator, "_find_missing_characters", return_value=["你", "好", "🌍"]):
                    validation_result = font_validator.validate_document_fonts(unicode_config)

        assert len(validation_result.font_coverage_issues) > 0
        assert any("missing glyphs" in msg for msg in validation_result.validation_messages)

    def test_document_error_recovery_workflow(self, document_font_integration_test):
        """Test error recovery in document processing workflow"""
        test_name, temp_dir, test_fonts_dir, font_validator, document_config = document_font_integration_test

        error_config = {
            "version": "1.0",
            "document_structure": [{
                "type": "page", "page_number": 0,
                "layers": [{"content": [
                    {"type": "text", "text": "Good text", "font_details": {"name": "helv"}},
                    {"type": "text", "text": "Problematic text", "font_details": {"name": "ProblematicFont"}},
                    {"type": "text", "text": "Unnamed T3 text", "font_details": {"name": "Unnamed-T3"}},
                ]}]
            }]
        }
        os.makedirs(test_fonts_dir, exist_ok=True)
        problematic_path = os.path.join(test_fonts_dir, "ProblematicFont.ttf")
        with open(problematic_path, "wb") as f:
            f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)

        mock_page = Mock()
        def insert_font_side_effect(fontfile=None, fontname=None):
            if fontname == "ProblematicFont":
                raise Exception("Font loading error")
        mock_page.insert_font.side_effect = insert_font_side_effect

        with patch("pdfrebuilder.font.utils.TTFont") as mock_ttfont:
            def create_mock_font(font_path):
                mock_font = MagicMock()
                font_name = os.path.basename(font_path).replace(".ttf", "").replace(".otf", "")
                mock_name_table = Mock()
                mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
                mock_cmap_table = Mock()
                char_map = {ord(c): i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ")}
                mock_cmap_table.cmap = char_map
                mock_cmap_subtable = Mock()
                mock_cmap_subtable.tables = [mock_cmap_table]
                def getitem_side_effect(key):
                    if key == "name": return mock_name_table
                    elif key == "cmap": return mock_cmap_subtable
                    else: return Mock()
                mock_font.__getitem__.side_effect = getitem_side_effect
                return mock_font
            mock_ttfont.side_effect = create_mock_font

            with (
                patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", "/nonexistent"),
                patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
                patch("pdfrebuilder.font.utils.download_google_font", return_value=None),
                patch("pdfrebuilder.font.utils._find_font_file_for_name") as mock_find,
            ):
                def find_side_effect(font_name):
                    if font_name == "ProblematicFont":
                        return problematic_path
                    return None
                mock_find.side_effect = find_side_effect

                for doc_unit in error_config["document_structure"]:
                    for layer in doc_unit["layers"]:
                        for element in layer["content"]:
                            if element["type"] == "text":
                                font_name = element["font_details"]["name"]
                                text_content = element["text"]
                                result = ensure_font_registered(mock_page, font_name, verbose=False, text=text_content)
                                if font_name == "helv":
                                    assert result == "helv"
                                elif font_name in ["ProblematicFont", "Unnamed-T3"]:
                                    assert result in ["helv", "Helvetica"]

        substitutions = font_validator.substitution_tracker
        problematic_substitutions = [s for s in substitutions if any(keyword in s.reason.lower() for keyword in ["not supported", "no font covers", "font not found", "loading error", "font registration failed"])]
        assert len(problematic_substitutions) > 0
        t3_substitutions = [s for s in substitutions if s.original_font == "Unnamed-T3"]
        assert len(t3_substitutions) == 1

        reporter = get_font_error_reporter()
        assert reporter._error_counts.get("registration", 0) > 0

    def test_large_document_performance(self, document_font_integration_test):
        """Test font processing performance with large documents"""
        import time
        test_name, temp_dir, test_fonts_dir, font_validator, document_config = document_font_integration_test

        large_config = {"version": "1.0", "document_structure": []}
        font_names = list(font_validator.available_fonts.keys())[:5]
        if not font_names:
            pytest.skip("No available fonts found for performance test.")

        for page_num in range(50):
            page = {
                "type": "page", "page_number": page_num,
                "layers": [{"content": [
                    {"type": "text", "id": f"text_{page_num}_{elem_num}", "text": f"Text on page {page_num}", "font_details": {"name": font_names[elem_num % len(font_names)]}}
                    for elem_num in range(10)
                ]}]
            }
            large_config["document_structure"].append(page)

        with patch("pdfrebuilder.font.utils.TTFont") as mock_ttfont:
            def create_mock_font(font_path):
                mock_font = MagicMock()
                font_name = os.path.basename(font_path).replace(".ttf", "").replace(".otf", "")
                mock_name_table = Mock()
                mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
                mock_cmap_table = Mock()
                char_map = {ord(c): i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ")}
                mock_cmap_table.cmap = char_map
                mock_cmap_subtable = Mock()
                mock_cmap_subtable.tables = [mock_cmap_table]
                def getitem_side_effect(key):
                    if key == "name": return mock_name_table
                    elif key == "cmap": return mock_cmap_subtable
                    else: return Mock()
                mock_font.__getitem__.side_effect = getitem_side_effect
                return mock_font
            mock_ttfont.side_effect = create_mock_font

            start_time = time.time()
            validation_result = font_validator.validate_document_fonts(large_config)
            validation_time = time.time() - start_time
        assert validation_time < 2.0

        expected_fonts = set(font_names)
        actual_fonts = set(validation_result.fonts_required)
        assert len(actual_fonts) == len(expected_fonts)

        mock_pages = [Mock() for _ in range(50)]
        with (
            patch("pdfrebuilder.settings.settings.font_management.manual_fonts_dir", test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", test_fonts_dir),
            patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
        ):
            start_time = time.time()
            for page_idx, doc_unit in enumerate(large_config["document_structure"]):
                mock_page = mock_pages[page_idx]
                for layer in doc_unit["layers"]:
                    for element in layer["content"]:
                        if element["type"] == "text":
                            font_name = element["font_details"]["name"]
                            ensure_font_registered(mock_page, font_name, verbose=False)
            registration_time = time.time() - start_time
        assert registration_time < 3.0

        for mock_page in mock_pages:
            assert mock_page.insert_font.call_count >= 1
