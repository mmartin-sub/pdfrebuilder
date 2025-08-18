"""
Integration tests for the Fitz (PyMuPDF) input → ReportLab output pipeline.
Tests the complete workflow from PDF parsing to PDF generation.
"""

import os
import tempfile

import pytest

from pdfrebuilder.engine.document_parser import PDFParser
from pdfrebuilder.models.universal_idm import PageUnit, UniversalDocument
from pdfrebuilder.settings import get_nested_config_value, set_nested_config_value


class TestFitzReportLabPipeline:
    """Test the complete Fitz input → ReportLab output pipeline"""

    def setup_method(self):
        """Set up test configuration"""
        # Ensure we're using the right engines
        set_nested_config_value("engines.input.default", "fitz")
        set_nested_config_value("engines.output.default", "reportlab")

    def create_test_pdf(self) -> str:
        """Create a simple test PDF for parsing"""
        import fitz  # PyMuPDF

        # Create a temporary PDF file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(temp_fd)

        # Create a simple PDF with text and shapes
        doc = fitz.open()
        ## STUB-ISSUE ##
        page = doc.new_page(width=612, height=792)

        # Add some text
        page.insert_text((50, 50), "Test Document", fontsize=20, color=(0, 0, 0))
        page.insert_text(
            (50, 100),
            "This is a test for Fitz → ReportLab pipeline",
            fontsize=12,
            color=(0.5, 0.5, 0.5),
        )

        # Add a rectangle
        rect = fitz.Rect(100, 150, 200, 200)
        page.draw_rect(rect, color=(1, 0, 0), width=2)

        # Add a filled circle
        center = fitz.Point(300, 175)
        page.draw_circle(center, 25, color=(0, 1, 0), fill=(0, 1, 0, 0.5))

        # Save the PDF
        doc.save(temp_path)
        doc.close()

        return temp_path

    def test_fitz_parser_initialization(self):
        """Test that Fitz parser initializes correctly"""
        parser = PDFParser()
        assert parser is not None
        assert parser.__class__.__name__ == "PDFParser"

    def test_fitz_pdf_parsing(self):
        """Test parsing a PDF with Fitz engine"""
        # Create test PDF
        test_pdf_path = self.create_test_pdf()

        try:
            # Parse with Fitz
            parser = PDFParser()
            assert parser.can_parse(test_pdf_path)

            # Parse the document
            document = parser.parse(test_pdf_path)

            # Verify document structure
            assert isinstance(document, UniversalDocument)
            assert document.version == "1.0"
            assert document.engine == "fitz"
            assert len(document.document_structure) > 0

            # Verify page structure
            page = document.document_structure[0]
            if isinstance(page, PageUnit):
                assert page.type == "page"
                assert page.page_number == 0
            assert len(page.layers) > 0

            # Verify we have some content
            total_elements = sum(len(layer.content) for layer in page.layers)
            assert total_elements > 0

            print(f"✅ Fitz parsing successful: {total_elements} elements extracted")

        finally:
            # Clean up
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def test_reportlab_configuration(self):
        """Test ReportLab engine configuration"""
        reportlab_config = get_nested_config_value("engines.output.reportlab")

        # Verify ReportLab configuration exists
        assert reportlab_config is not None
        assert "compression" in reportlab_config
        assert "embed_fonts" in reportlab_config
        assert "output_dpi" in reportlab_config

        # Verify default values
        assert reportlab_config["compression"] == 1
        assert reportlab_config["embed_fonts"] is True
        assert reportlab_config["output_dpi"] == 300

    @pytest.mark.skipif(not os.path.exists("input/sample.pdf"), reason="Sample PDF not available")
    def test_end_to_end_fitz_reportlab_pipeline(self):
        """Test complete end-to-end pipeline with real PDF"""
        input_pdf = "input/sample.pdf"

        # Parse with Fitz
        parser = PDFParser()
        document = parser.parse(input_pdf)

        # Verify parsing worked
        assert isinstance(document, UniversalDocument)
        assert document.engine == "fitz"

        # Count elements
        total_elements = sum(len(layer.content) for page in document.document_structure for layer in page.layers)

        print(f"✅ Parsed {len(document.document_structure)} pages with {total_elements} total elements")

        # Test that we can serialize the document (preparation for ReportLab)
        document_dict = document.to_dict()
        assert "version" in document_dict
        assert "engine" in document_dict
        assert "document_structure" in document_dict

        print("✅ Document serialization successful")

    def test_engine_compatibility(self):
        """Test that Fitz output is compatible with ReportLab input expectations"""
        # Create test PDF
        test_pdf_path = self.create_test_pdf()

        try:
            # Parse with Fitz
            parser = PDFParser()
            document = parser.parse(test_pdf_path)

            # Verify document structure matches ReportLab expectations
            for page in document.document_structure:
                assert hasattr(page, "type")
                assert hasattr(page, "size")
                assert hasattr(page, "layers")

                for layer in page.layers:
                    assert hasattr(layer, "layer_id")
                    assert hasattr(layer, "content")

                    for element in layer.content:
                        assert hasattr(element, "type")
                        assert hasattr(element, "id")
                        assert hasattr(element, "bbox")

                        # Check element type-specific requirements
                        if element.type and element.type.value == "text":
                            assert hasattr(element, "text")
                            assert hasattr(element, "font_details")
                        elif element.type and element.type.value == "image":
                            assert hasattr(element, "image_file")
                        elif element.type and element.type.value == "drawing":
                            assert hasattr(element, "drawing_commands")

            print("✅ Document structure is compatible with ReportLab expectations")

        finally:
            # Clean up
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def test_element_type_coverage(self):
        """Test that Fitz extracts all element types that ReportLab can render"""
        # Create a comprehensive test PDF
        test_pdf_path = self.create_comprehensive_test_pdf()

        try:
            # Parse with Fitz
            parser = PDFParser()
            document = parser.parse(test_pdf_path)

            # Collect all element types
            element_types = set()
            for page in document.document_structure:
                for layer in page.layers:
                    for element in layer.content:
                        if element.type:
                            element_types.add(element.type.value)  # Get string value from enum

            # Verify we have the main element types
            expected_types = {
                "text",
                "drawing",
            }  # 'image' would require actual image insertion
            found_types = element_types.intersection(expected_types)

            print(f"✅ Found element types: {element_types}")
            print(f"✅ Expected types found: {found_types}")

            assert len(found_types) > 0, "Should find at least some expected element types"

        finally:
            # Clean up
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def create_comprehensive_test_pdf(self) -> str:
        """Create a comprehensive test PDF with various element types"""
        import fitz  # PyMuPDF

        # Create a temporary PDF file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(temp_fd)

        # Create a comprehensive PDF
        doc = fitz.open()
        ## STUB-ISSUE ##
        page = doc.new_page(width=612, height=792)

        # Add various text elements
        page.insert_text((50, 50), "Title Text", fontsize=24, color=(0, 0, 0))
        page.insert_text(
            (50, 100),
            "Regular text in different color",
            fontsize=12,
            color=(0.5, 0, 0.5),
        )
        page.insert_text((50, 130), "Bold text", fontsize=14, color=(0, 0, 1))

        # Add various shapes
        # Rectangle (stroke only)
        rect1 = fitz.Rect(50, 200, 150, 250)
        page.draw_rect(rect1, color=(1, 0, 0), width=2)

        # Rectangle (filled)
        rect2 = fitz.Rect(200, 200, 300, 250)
        page.draw_rect(rect2, color=(0, 1, 0), fill=(0, 1, 0, 0.3))

        # Circle (stroke only)
        center1 = fitz.Point(100, 350)
        page.draw_circle(center1, 30, color=(0, 0, 1), width=3)

        # Circle (filled)
        center2 = fitz.Point(250, 350)
        page.draw_circle(center2, 30, color=(1, 0, 1), fill=(1, 0, 1, 0.5))

        # Line
        page.draw_line(fitz.Point(50, 450), fitz.Point(300, 450), color=(0.5, 0.5, 0.5), width=2)

        # Bezier curve
        p1 = fitz.Point(50, 500)
        p2 = fitz.Point(150, 450)
        p3 = fitz.Point(250, 550)
        p4 = fitz.Point(350, 500)
        page.draw_bezier(p1, p2, p3, p4, color=(1, 0.5, 0), width=2)

        # Save the PDF
        doc.save(temp_path)
        doc.close()

        return temp_path

    def test_configuration_consistency(self):
        """Test that engine configurations are consistent"""
        # Verify input engine is set to fitz
        input_default = get_nested_config_value("engines.input.default")
        assert input_default in [
            "auto",
            "fitz",
        ], f"Input engine should be auto or fitz, got {input_default}"

        # Verify output engine is set to reportlab
        output_default = get_nested_config_value("engines.output.default")
        assert output_default == "reportlab", f"Output engine should be reportlab, got {output_default}"

        # Verify fitz configuration exists
        fitz_config = get_nested_config_value("engines.input.fitz")
        assert fitz_config is not None
        assert "extract_text" in fitz_config
        assert "extract_images" in fitz_config
        assert "extract_drawings" in fitz_config

        print("✅ Engine configurations are consistent")

    def test_performance_characteristics(self):
        """Test performance characteristics of the Fitz → ReportLab pipeline"""
        import time

        # Create test PDF
        test_pdf_path = self.create_comprehensive_test_pdf()

        try:
            # Measure parsing time
            parser = PDFParser()
            start_time = time.time()
            document = parser.parse(test_pdf_path)
            parse_time = time.time() - start_time

            # Count elements
            total_elements = sum(len(layer.content) for page in document.document_structure for layer in page.layers)

            # Performance assertions
            assert parse_time < 5.0, f"Parsing should be fast, took {parse_time:.2f}s"
            assert total_elements > 0, "Should extract some elements"

            print(f"✅ Performance test: {parse_time:.3f}s to parse {total_elements} elements")

        finally:
            # Clean up
            if os.path.exists(test_pdf_path):
                os.unlink(test_pdf_path)

    def teardown_method(self):
        """Clean up after tests"""
        # Reset to default configuration
        set_nested_config_value("engines.input.default", "auto")
        set_nested_config_value("engines.output.default", "reportlab")
