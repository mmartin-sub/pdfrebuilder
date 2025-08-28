import os
import xml.etree.ElementTree as ET
import zipfile

from wand.image import Image

from pdfrebuilder.engine.engine_selector import get_input_engine, get_output_engine
from pdfrebuilder.models.universal_idm import UniversalDocument
from tests.config import cleanup_test_output, get_test_temp_dir


def _create_dummy_kra(path, width=800, height=600):
    with zipfile.ZipFile(path, "w") as zf:
        # Create a dummy image file
        temp_dir = os.path.dirname(path)
        dummy_image_path = os.path.join(temp_dir, "layer_0.png")
        with Image(width=100, height=100, background="green") as img:
            img.format = "png"
            img.save(filename=dummy_image_path)
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
        zf.writestr("mimetype", "application/x-krita")


def test_multi_engine_processing():
    """
    End-to-end test for processing a document with Krita engine.
    """
    test_name = "test_multi_engine_processing"
    temp_dir = get_test_temp_dir(test_name)
    kra_path = os.path.join(temp_dir, "test.kra")
    _create_dummy_kra(kra_path)

    # Test Krita to Krita
    input_engine = get_input_engine("krita")
    output_engine = get_output_engine("krita")

    doc = input_engine.parse(kra_path)
    assert isinstance(doc, UniversalDocument)

    output_path = os.path.join(temp_dir, "output.kra")
    output_engine.render(doc, output_path)

    assert os.path.exists(output_path)

    cleanup_test_output(test_name)
