import os
import pytest
import zipfile
import xml.etree.ElementTree as ET

from pdfrebuilder.engine.engine_selector import get_input_engine, get_output_engine
from tests.config import get_test_temp_dir, cleanup_test_output


def _create_dummy_kra(path, width=800, height=600):
    with zipfile.ZipFile(path, "w") as zf:
        # Create a dummy image file
        dummy_image_path = os.path.join(os.path.dirname(path), "layer_0.png")
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


def test_multi_engine_processing():
    """
    End-to-end test for processing a document with Krita engine.
    """
    temp_dir = get_test_temp_dir("test_multi_engine_processing")
    kra_path = os.path.join(temp_dir, "test.kra")
    _create_dummy_kra(kra_path)

    # Test Krita to Krita
    input_engine = get_input_engine("krita")
    output_engine = get_output_engine("krita")

    doc = input_engine.extract(kra_path)
    output_path = os.path.join(temp_dir, "output.kra")
    output_engine.generate(doc, output_path)

    assert os.path.exists(output_path)

    cleanup_test_output("test_multi_engine_processing")
