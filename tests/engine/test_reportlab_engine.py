import os
import unittest

from pdfrebuilder.engine.reportlab_engine import ReportLabEngine
from pdfrebuilder.models.universal_idm import (
    BoundingBox,
    DrawingCommand,
    DrawingElement,
    Layer,
    PageUnit,
    UniversalDocument,
)
from tests.config import cleanup_test_output, get_test_temp_dir


class TestReportLabEngine(unittest.TestCase):
    def setUp(self):
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.output_pdf_path = os.path.join(self.temp_dir, "output.pdf")

    def tearDown(self):
        cleanup_test_output(self.test_name)

    def test_render_drawing_element(self):
        """Test rendering of a DrawingElement with the ReportLabEngine."""
        engine = ReportLabEngine()

        drawing_element = DrawingElement(
            id="test_drawing",
            bbox=[100, 100, 200, 200],
            color=[0, 0, 0],
            fill=[0.5, 0.5, 0.5],
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
            self.assertTrue(os.path.exists(self.output_pdf_path))
        except Exception as e:
            self.fail(f"Rendering failed with exception: {e}")


if __name__ == "__main__":
    unittest.main()
