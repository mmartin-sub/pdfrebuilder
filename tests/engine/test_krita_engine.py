import os
import unittest
import zipfile
import xml.etree.ElementTree as ET

from pdfrebuilder.engine.krita_engine import KritaInputEngine, KritaOutputEngine
from pdfrebuilder.models.universal_idm import UniversalDocument, CanvasUnit, Layer, ImageElement, BoundingBox

from tests.config import get_test_temp_dir, get_fixture_path, cleanup_test_output


class TestKritaEngine(unittest.TestCase):
    def setUp(self):
        self.test_name = self.__class__.__name__ + "_" + self._testMethodName
        self.temp_dir = get_test_temp_dir(self.test_name)
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        cleanup_test_output(self.test_name)

    def _create_dummy_kra(self, path, width=800, height=600):
        with zipfile.ZipFile(path, "w") as zf:
            # Create a dummy image file
            dummy_image_path = os.path.join(self.temp_dir, "layer_0.png")
            with open(dummy_image_path, "wb") as f:
                f.write(b"dummy image data")
            zf.write(dummy_image_path, "layer_0.png")

            # Create maindoc.xml
            root = ET.Element("DOC", width=str(width), height=str(height))
            layers = ET.SubElement(root, "layers")
            ET.SubElement(
                layers,
                "layer",
                name="Layer 1",
                src="layer_0.png",
                visible="1",
                opacity="255",
            )
            xml_string = ET.tostring(root, encoding="unicode")
            zf.writestr("maindoc.xml", xml_string)

    def test_krita_input_engine(self):
        kra_path = os.path.join(self.temp_dir, "test.kra")
        self._create_dummy_kra(kra_path)

        engine = KritaInputEngine()
        doc = engine.extract(kra_path)

        self.assertIsInstance(doc, UniversalDocument)
        self.assertEqual(len(doc.document_structure), 1)
        canvas = doc.document_structure[0]
        self.assertIsInstance(canvas, CanvasUnit)
        self.assertEqual(canvas.size, (800, 600))
        self.assertEqual(len(canvas.layers), 1)
        layer = canvas.layers[0]
        self.assertEqual(layer.layer_name, "Layer 1")
        self.assertEqual(len(layer.content), 1)
        image_element = layer.content[0]
        self.assertIsInstance(image_element, ImageElement)
        self.assertTrue(os.path.exists(image_element.image_file))

    def test_krita_output_engine(self):
        # Create a UniversalDocument
        doc = UniversalDocument()
        canvas = CanvasUnit(size=(1024, 768))
        doc.add_document_unit(canvas)
        dummy_image_path = os.path.join(self.temp_dir, "source.png")
        with open(dummy_image_path, "wb") as f:
            f.write(b"source image data")
        image_element = ImageElement(id="img1", bbox=BoundingBox(0, 0, 1024, 768), image_file=dummy_image_path)
        layer = Layer(layer_id="layer1", layer_name="First Layer", content=[image_element])
        canvas.add_layer(layer)

        # Generate the .kra file
        output_path = os.path.join(self.output_dir, "output.kra")
        engine = KritaOutputEngine()
        engine.generate(doc, output_path)

        # Verify the output file
        self.assertTrue(os.path.exists(output_path))
        with zipfile.ZipFile(output_path, "r") as zf:
            self.assertIn("maindoc.xml", zf.namelist())
            self.assertIn("layer_0.png", zf.namelist())
            with zf.open("maindoc.xml") as f:
                tree = ET.parse(f)
                root = tree.getroot()
                self.assertEqual(root.attrib["width"], "1024")
                self.assertEqual(root.attrib["height"], "768")
                layer_xml = root.find("layers/layer")
                self.assertIsNotNone(layer_xml)
                self.assertEqual(layer_xml.attrib["name"], "First Layer")
                self.assertEqual(layer_xml.attrib["src"], "layer_0.png")

if __name__ == "__main__":
    unittest.main()
