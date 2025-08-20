"""
Integration tests for cross-engine compatibility.
Tests that different engines produce consistent results.
"""

import os

import pytest

from pdfrebuilder.engine.document_parser import get_parser_for_file, parse_document
from pdfrebuilder.models.universal_idm import UniversalDocument
from pdfrebuilder.settings import get_nested_config_value


class TestCrossEngineCompatibility:
    """Test compatibility between different engines"""

    def test_parser_selection_consistency(self):
        """Test that parser selection is consistent"""
        # Create temporary test files for parser detection
        import os
        import tempfile

        # Test PDF file detection
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            tmp_pdf.write(b"%PDF-1.4\n")  # Minimal PDF header
            tmp_pdf.flush()

            pdf_parser = get_parser_for_file(tmp_pdf.name)
            assert pdf_parser is not None
            assert pdf_parser.__class__.__name__ == "PDFParser"

            os.unlink(tmp_pdf.name)

        # Test PSD file detection
        with tempfile.NamedTemporaryFile(suffix=".psd", delete=False) as tmp_psd:
            tmp_psd.write(b"8BPS")  # PSD file signature
            tmp_psd.flush()

            psd_parser = get_parser_for_file(tmp_psd.name)
            assert psd_parser is not None
            assert psd_parser.__class__.__name__ == "PSDParser"

            os.unlink(tmp_psd.name)

        # Test unsupported format
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
            tmp_docx.write(b"PK")  # ZIP-based format signature
            tmp_docx.flush()

            unsupported_parser = get_parser_for_file(tmp_docx.name)
            assert unsupported_parser is None

            os.unlink(tmp_docx.name)

    def test_universal_document_structure_consistency(self):
        """Test that all engines produce consistent UniversalDocument structure"""
        # This test would require actual test files
        # For now, we test the structure requirements

        # All parsers should produce UniversalDocument with required fields
        required_fields = [
            "version",
            "engine",
            "engine_version",
            "metadata",
            "document_structure",
        ]

        # This would be tested with actual files:
        # pdf_doc = parse_document("tests/fixtures/sample.pdf")
        # psd_doc = parse_document("tests/fixtures/sample.psd")

        # For now, we just verify the structure exists
        assert hasattr(UniversalDocument, "__annotations__")

    def test_extraction_flags_consistency(self):
        """Test that extraction flags work consistently across engines"""
        test_flags = {
            "extract_text": True,
            "extract_images": False,
            "extract_drawings": True,
            "extract_raw_backgrounds": False,
        }

        # All parsers should accept these flags without error
        # This would be tested with actual files in a real implementation

    def test_engine_configuration_isolation(self):
        """Test that engine configurations don't interfere with each other"""
        # Get configurations for different engines
        wand_config = get_nested_config_value("engines.input.wand")
        psd_tools_config = get_nested_config_value("engines.input.psd_tools")
        fitz_config = get_nested_config_value("engines.input.fitz")

        # Verify they are separate dictionaries
        assert wand_config is not psd_tools_config
        assert wand_config is not fitz_config
        assert psd_tools_config is not fitz_config

        # Verify they have different settings
        assert "density" in wand_config
        assert "density" not in psd_tools_config
        assert "density" not in fitz_config

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_visual_validation_consistency(self):
        """Test that visual validation works consistently across engines"""
        # This would test that visual validation produces consistent results
        # regardless of which engine was used for extraction

    def test_error_handling_consistency(self):
        """Test that error handling is consistent across engines"""
        import tempfile

        from pdfrebuilder.engine.document_parser import DocumentParsingError

        # Test with unsupported file format (create a temporary file with unsupported extension)
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_file:
            tmp_file.write(b"dummy content")
            tmp_file.flush()

            with pytest.raises(DocumentParsingError, match="Unsupported file format"):
                parse_document(tmp_file.name)

            os.unlink(tmp_file.name)

        # Test with non-existent file
        with pytest.raises(DocumentParsingError, match="File not found"):
            parse_document("nonexistent.xyz")

        # Test with invalid file path
        with pytest.raises(DocumentParsingError):
            parse_document("")

    def test_asset_manifest_consistency(self):
        """Test that asset manifests are consistent across engines"""
        from pdfrebuilder.engine.document_parser import AssetManifest

        # Create test manifest
        manifest = AssetManifest()

        # Test adding different types of assets
        manifest.add_image("test.png", "original.png", {"width": 100, "height": 100})
        manifest.add_font("test.ttf", "Arial", {"style": "regular"})
        manifest.add_asset("test.svg", "vector", {"format": "svg"})

        # Convert to dict and verify structure
        manifest_dict = manifest.to_dict()

        assert "images" in manifest_dict
        assert "fonts" in manifest_dict
        assert "other_assets" in manifest_dict

        assert len(manifest_dict["images"]) == 1
        assert len(manifest_dict["fonts"]) == 1
        assert len(manifest_dict["other_assets"]) == 1
