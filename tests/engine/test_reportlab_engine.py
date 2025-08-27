import os

import pytest
from pdfrebuilder.engine.reportlab_engine import ReportLabEngine
from pdfrebuilder.models.universal_idm import (
    BoundingBox,
    Color,
    DrawingCommand,
    DrawingElement,
    FontDetails,
    ImageElement,
    Layer,
    PageUnit,
    TextElement,
    UniversalDocument,
)
from tests.config import cleanup_test_output, get_fixture_path, get_test_temp_dir


class TestReportLabEngine:
    def setup_method(self, method):
        self.test_name = self.__class__.__name__ + "_" + method.__name__
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.output_pdf_path = os.path.join(self.temp_dir, "output.pdf")

    def teardown_method(self, method):
        cleanup_test_output(self.test_name)

    def test_render_drawing_element(self):
        """Test rendering of a DrawingElement with the ReportLabEngine."""
        engine = ReportLabEngine()

        drawing_element = DrawingElement(
            id="test_drawing",
            bbox=BoundingBox(x1=100, y1=100, x2=200, y2=200),
            color=Color(r=0, g=0, b=0),
            fill=Color(r=0.5, g=0.5, b=0.5),
            width=2.0,
            drawing_commands=[
                DrawingCommand(cmd="rect", bbox=BoundingBox(x1=100, y1=100, x2=200, y2=200)),
                DrawingCommand(cmd="line", pts=[100, 100, 200, 200]),
            ],
        )

        layer = Layer(
            layer_id="test_layer",
            layer_name="Test Layer",
            content=[drawing_element],
        )

        page_unit = PageUnit(
            page_number=0,
            size=(612, 792),
            layers=[layer],
        )

        document = UniversalDocument(
            version="1.0",
            engine="reportlab",
            document_structure=[page_unit],
        )

        try:
            engine.generate(document.to_dict(), self.output_pdf_path)
            assert os.path.exists(self.output_pdf_path)
        except Exception as e:
            pytest.fail(f"Rendering failed with exception: {e}")

    def test_render_text_element(self):
        """Test rendering of a TextElement with the ReportLabEngine."""
        engine = ReportLabEngine()

        text_element = TextElement(
            id="test_text",
            bbox=BoundingBox(x1=100, y1=700, x2=500, y2=720),
            text="Hello, ReportLab!",
            font_details=FontDetails(
                name="Helvetica",
                size=12,
                color=Color(r=0, g=0, b=0),
            ),
        )

        layer = Layer(
            layer_id="test_layer",
            layer_name="Test Layer",
            content=[text_element],
        )

        page_unit = PageUnit(
            page_number=0,
            size=(612, 792),
            layers=[layer],
        )

        document = UniversalDocument(
            version="1.0",
            engine="reportlab",
            document_structure=[page_unit],
        )

        try:
            engine.generate(document.to_dict(), self.output_pdf_path)
            assert os.path.exists(self.output_pdf_path)
        except Exception as e:
            pytest.fail(f"Rendering failed with exception: {e}")

    def test_render_image_element(self):
        """Test rendering of an ImageElement with the ReportLabEngine."""
        engine = ReportLabEngine()

        image_element = ImageElement(
            id="test_image",
            bbox=BoundingBox(x1=100, y1=400, x2=300, y2=600),
            image_file=get_fixture_path("dummy_image.png"),
        )

        layer = Layer(
            layer_id="test_layer",
            layer_name="Test Layer",
            content=[image_element],
        )

        page_unit = PageUnit(
            page_number=0,
            size=(612, 792),
            layers=[layer],
        )

        document = UniversalDocument(
            version="1.0",
            engine="reportlab",
            document_structure=[page_unit],
        )

        try:
            engine.generate(document.to_dict(), self.output_pdf_path)
            assert os.path.exists(self.output_pdf_path)
        except Exception as e:
            pytest.fail(f"Rendering failed with exception: {e}")

    def test_generate_multi_page_document(self):
        """Test generation of a multi-page document."""
        engine = ReportLabEngine()

        page1 = PageUnit(
            page_number=0,
            size=(612, 792),
            layers=[
                Layer(
                    layer_id="page1_layer",
                    layer_name="Page 1 Layer",
                    content=[
                        TextElement(
                            id="text1",
                            bbox=BoundingBox(x1=100, y1=700, x2=500, y2=720),
                            text="Page 1",
                            font_details=FontDetails(name="Helvetica", size=12, color=Color(r=0, g=0, b=0)),
                        )
                    ],
                )
            ],
        )

        page2 = PageUnit(
            page_number=1,
            size=(612, 792),
            layers=[
                Layer(
                    layer_id="page2_layer",
                    layer_name="Page 2 Layer",
                    content=[
                        TextElement(
                            id="text2",
                            bbox=BoundingBox(x1=100, y1=700, x2=500, y2=720),
                            text="Page 2",
                            font_details=FontDetails(name="Helvetica", size=12, color=Color(r=0, g=0, b=0)),
                        )
                    ],
                )
            ],
        )

        document = UniversalDocument(
            version="1.0",
            engine="reportlab",
            document_structure=[page1, page2],
        )

        try:
            engine.generate(document.to_dict(), self.output_pdf_path)
            assert os.path.exists(self.output_pdf_path)
        except Exception as e:
            pytest.fail(f"Rendering failed with exception: {e}")
