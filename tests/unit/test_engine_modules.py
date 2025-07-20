"""
Tests for engine modules functionality.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.engine.document_parser import DocumentParsingError, parse_document
from pdfrebuilder.engine.document_renderer import RenderingError, RenderResult, render_document
from pdfrebuilder.engine.validation_report import SimpleValidationReport as ValidationReport
from pdfrebuilder.engine.validation_report import generate_validation_report_simple as generate_validation_report

# Import optional dependencies with pytest.importorskip
psd_tools = pytest.importorskip(
    "psd_tools",
    reason="psd-tools not available. Install with: pip install 'pdfrebuilder[psd]'",
)


class TestDocumentParser:
    """Test document parsing functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_pdf = os.path.join(self.temp_dir, "sample.pdf")

        # Create a dummy PDF file
        with open(self.sample_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n%dummy content\n%%EOF")

    @patch("src.engine.document_parser.extract_pdf_content")
    def test_parse_document_pdf_success(self, mock_extract_pdf):
        """Test successful PDF document parsing"""
        # Mock the extract_pdf_content function
        mock_document = Mock()
        mock_document.to_dict.return_value = {"version": "1.0"}
        mock_extract_pdf.return_value = mock_document

        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
        }

        result = parse_document(self.sample_pdf, extraction_flags, engine="fitz")

        assert result == mock_document
        mock_extract_pdf.assert_called_once_with(self.sample_pdf, extraction_flags)

    def test_parse_document_file_not_found(self):
        """Test parsing non-existent document"""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.pdf")

        with pytest.raises(DocumentParsingError, match="File not found"):
            parse_document(non_existent_file, {})

    def test_parse_document_unsupported_format(self):
        """Test parsing unsupported document format"""
        unsupported_file = os.path.join(self.temp_dir, "document.xyz")
        with open(unsupported_file, "w") as f:
            f.write("unsupported content")

        with pytest.raises(DocumentParsingError, match="Unsupported file format"):
            parse_document(unsupported_file, {})

    @patch("src.engine.document_parser.extract_pdf_content")
    def test_parse_document_extraction_error(self, mock_extract_pdf):
        """Test handling of extraction errors"""
        # Mock extract_pdf_content to raise exception
        mock_extract_pdf.side_effect = Exception("Extraction failed")

        with pytest.raises(DocumentParsingError, match="Failed to parse document"):
            parse_document(self.sample_pdf, {}, engine="fitz")

    @patch("src.engine.document_parser.detect_file_format")
    @patch("src.engine.document_parser.WandParser.parse")
    def test_parse_document_wand_engine(self, mock_wand_parse, mock_detect_format):
        """Test parsing with Wand engine"""
        # Mock file format detection to return a supported format
        mock_detect_format.return_value = "png"

        # Mock Wand parser
        mock_document = Mock()
        mock_wand_parse.return_value = mock_document

        # Create a test image file that Wand can handle
        test_image = os.path.join(self.temp_dir, "test.png")
        with open(test_image, "wb") as f:
            f.write(b"fake png content")

        result = parse_document(test_image, {}, engine="wand")

        assert result == mock_document
        mock_wand_parse.assert_called_once()

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


@pytest.mark.psd
@pytest.mark.optional_deps
class TestDocumentRenderer:
    """Test document rendering functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, "output.pdf")

        # Sample document structure
        self.sample_document = {
            "version": "1.0",
            "engine": "fitz",
            "document_structure": [{"type": "page", "page_number": 0, "size": [612, 792], "layers": []}],
        }

    def test_render_document_success(self):
        """Test successful document rendering"""
        result = render_document(self.sample_document, self.output_path)

        assert isinstance(result, RenderResult)
        assert result.success is True
        assert self.output_path in result.output_paths

    def test_render_document_rendering_error(self):
        """Test handling of rendering errors"""
        # Test with invalid document structure
        invalid_document = {}

        with pytest.raises(RenderingError, match="Invalid document structure"):
            render_document(invalid_document, self.output_path)

    def test_render_document_invalid_structure(self):
        """Test rendering with invalid document structure"""
        invalid_document = {
            "version": "1.0"
            # Missing required fields
        }

        with pytest.raises(RenderingError, match="Invalid document structure"):
            render_document(invalid_document, self.output_path)

    def test_render_document_fitz_engine(self):
        """Test rendering with Fitz engine"""
        # Test with fitz engine specified in document
        fitz_document = {
            "version": "1.0",
            "engine": "fitz",
            "document_structure": [{"type": "page", "page_number": 0, "size": [612, 792], "layers": []}],
        }

        result = render_document(fitz_document, self.output_path)

        assert isinstance(result, RenderResult)
        assert result.success is True

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestValidationReport:
    """Test validation report functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.report_path = os.path.join(self.temp_dir, "validation_report.html")

    def test_validation_report_creation(self):
        """Test creating ValidationReport instance"""
        report = ValidationReport(
            original_document="original.pdf",
            generated_document="generated.pdf",
            ssim_score=0.95,
            differences_found=False,
        )

        assert report.original_document == "original.pdf"
        assert report.generated_document == "generated.pdf"
        assert report.ssim_score == 0.95
        assert report.differences_found is False

    def test_validation_report_with_differences(self):
        """Test ValidationReport with differences detected"""
        report = ValidationReport(
            original_document="original.pdf",
            generated_document="generated.pdf",
            ssim_score=0.85,
            differences_found=True,
            difference_details=[
                {"type": "color_mismatch", "location": [100, 100]},
                {"type": "missing_element", "element_id": "text_1"},
            ],
        )

        assert report.differences_found is True
        assert len(report.difference_details) == 2
        assert report.difference_details[0]["type"] == "color_mismatch"

    @patch("src.engine.validation_report.validate_documents")
    def test_generate_validation_report_success(self, mock_validate):
        """Test successful validation report generation"""
        # Mock validation results
        mock_validate.return_value = {
            "is_valid": True,
            "ssim_score": 0.98,
            "differences_found": False,
            "validation_details": {},
        }

        original_path = os.path.join(self.temp_dir, "original.pdf")
        generated_path = os.path.join(self.temp_dir, "generated.pdf")

        # Create dummy files
        for path in [original_path, generated_path]:
            with open(path, "w") as f:
                f.write("dummy content")

        report = generate_validation_report(original_path, generated_path, self.report_path)

        assert isinstance(report, ValidationReport)
        assert report.ssim_score == 0.98
        assert report.differences_found is False
        mock_validate.assert_called_once()

    @patch("src.engine.validation_report.validate_documents")
    def test_generate_validation_report_with_differences(self, mock_validate):
        """Test validation report generation with differences"""
        # Mock validation results with differences
        mock_validate.return_value = {
            "is_valid": False,
            "ssim_score": 0.82,
            "differences_found": True,
            "validation_details": {
                "font_substitutions": [{"original": "Arial", "substituted": "Helvetica"}],
                "color_differences": [
                    {
                        "location": [50, 50],
                        "expected": [1.0, 0.0, 0.0],
                        "actual": [0.9, 0.1, 0.0],
                    }
                ],
            },
        }

        original_path = os.path.join(self.temp_dir, "original.pdf")
        generated_path = os.path.join(self.temp_dir, "generated.pdf")

        # Create dummy files
        for path in [original_path, generated_path]:
            with open(path, "w") as f:
                f.write("dummy content")

        report = generate_validation_report(original_path, generated_path, self.report_path)

        assert report.differences_found is True
        assert report.ssim_score == 0.82
        assert len(report.font_substitutions) == 1
        assert len(report.color_differences) == 1

    def test_generate_validation_report_file_not_found(self):
        """Test validation report generation with missing files"""
        non_existent_original = os.path.join(self.temp_dir, "nonexistent_original.pdf")
        non_existent_generated = os.path.join(self.temp_dir, "nonexistent_generated.pdf")

        with pytest.raises(FileNotFoundError):
            generate_validation_report(non_existent_original, non_existent_generated, self.report_path)

    @patch("src.engine.validation_report.validate_documents")
    def test_generate_validation_report_validation_error(self, mock_validate):
        """Test handling of validation errors"""
        # Mock validation to raise exception
        mock_validate.side_effect = Exception("Validation failed")

        original_path = os.path.join(self.temp_dir, "original.pdf")
        generated_path = os.path.join(self.temp_dir, "generated.pdf")

        # Create dummy files
        for path in [original_path, generated_path]:
            with open(path, "w") as f:
                f.write("dummy content")

        with pytest.raises(Exception, match="Validation failed"):
            generate_validation_report(original_path, generated_path, self.report_path)

    def test_validation_report_to_dict(self):
        """Test converting ValidationReport to dictionary"""
        report = ValidationReport(
            original_document="original.pdf",
            generated_document="generated.pdf",
            ssim_score=0.95,
            differences_found=False,
        )

        result = report.to_dict()

        assert isinstance(result, dict)
        assert result["original_document"] == "original.pdf"
        assert result["generated_document"] == "generated.pdf"
        assert result["ssim_score"] == 0.95
        assert result["differences_found"] is False

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
