import os
import xml.etree.ElementTree as ET
import zipfile

import pytest
from wand.image import Image

from pdfrebuilder.engine.krita_engine import KritaInputEngine, KritaOutputEngine
from pdfrebuilder.models.universal_idm import (
    BoundingBox,
    CanvasUnit,
    ImageElement,
    Layer,
    UniversalDocument,
)
from tests.config import cleanup_test_output, get_test_temp_dir


@pytest.fixture(scope="module")
def test_env():
    test_name = "test_krita_engine"
    temp_dir = get_test_temp_dir(test_name)
    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    yield temp_dir, output_dir

    cleanup_test_output(test_name)


@pytest.fixture(scope="module")
def sample_kra_file(test_env):
    temp_dir, _ = test_env
    kra_path = os.path.join(temp_dir, "sample.kra")

    with zipfile.ZipFile(kra_path, "w") as zf:
        # Create a dummy image file
        dummy_image_path = os.path.join(temp_dir, "layer0.png")
        with Image(width=100, height=100, background="red") as img:
            img.format = "png"
            img.save(filename=dummy_image_path)

        zf.write(dummy_image_path, "layer0.png")

        # Create maindoc.xml
        root = ET.Element("DOC", width="800", height="600", mimemajor="2", mimeminor="8")
        layers = ET.SubElement(root, "layers")
        ET.SubElement(
            layers,
            "layer",
            name="Red Layer",
            src="layer0.png",
            visible="1",
            opacity="255",
        )
        xml_string = ET.tostring(root, encoding="unicode")
        zf.writestr("maindoc.xml", xml_string)
        zf.writestr("mimetype", "application/x-krita")

    return kra_path


def test_krita_input_engine(sample_kra_file):
    """Test parsing a .kra file with KritaInputEngine."""
    engine = KritaInputEngine()
    engine.initialize()

    assert engine.can_parse(sample_kra_file)
    doc = engine.parse(sample_kra_file)

    assert isinstance(doc, UniversalDocument)
    assert len(doc.document_structure) == 1

    canvas = doc.document_structure[0]
    assert isinstance(canvas, CanvasUnit)
    assert canvas.size == (800, 600)

    assert len(canvas.layers) == 1
    layer = canvas.layers[0]
    assert layer.layer_name == "Red Layer"
    assert layer.opacity == 1.0

    assert len(layer.content) == 1
    image_element = layer.content[0]
    assert isinstance(image_element, ImageElement)
    assert os.path.exists(image_element.image_file)
    assert image_element.original_format.upper() == "PNG"


def test_krita_output_engine(test_env):
    """Test rendering a UniversalDocument to a .kra file."""
    temp_dir, output_dir = test_env

    # Create a UniversalDocument
    doc = UniversalDocument()
    canvas = CanvasUnit(size=(1024, 768))
    doc.add_document_unit(canvas)

    # Create a dummy image for the layer
    dummy_image_path = os.path.join(temp_dir, "source.jpg")
    with Image(width=200, height=200, background="blue") as img:
        img.format = "jpeg"
        img.save(filename=dummy_image_path)

    image_element = ImageElement(id="img1", bbox=BoundingBox(0, 0, 1024, 768), image_file=dummy_image_path)
    layer = Layer(layer_id="layer1", layer_name="First Layer", content=[image_element])
    canvas.add_layer(layer)

    # Generate the .kra file
    output_path = os.path.join(output_dir, "output.kra")
    engine = KritaOutputEngine()
    engine.initialize()

    assert engine.can_render(doc)
    engine.render(doc, output_path)

    # Verify the output file
    assert os.path.exists(output_path)
    with zipfile.ZipFile(output_path, "r") as zf:
        assert "maindoc.xml" in zf.namelist()
        assert "layer0.png" in zf.namelist()  # Should be converted to png
        assert "mimetype" in zf.namelist()

        with zf.open("maindoc.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            assert root.attrib["width"] == "1024"
            assert root.attrib["height"] == "768"
            layer_xml = root.find("layers/layer")
            assert layer_xml is not None
            assert layer_xml.attrib["name"] == "First Layer"
            assert layer_xml.attrib["src"] == "layer0.png"


def test_e2e_krita_processing(sample_kra_file, test_env):
    """Test the full cycle of parsing and rendering a Krita file."""
    _, output_dir = test_env

    # 1. Parse the input file
    input_engine = KritaInputEngine()
    input_engine.initialize()
    doc = input_engine.parse(sample_kra_file)

    # 2. Render the document back to a new file
    output_path = os.path.join(output_dir, "e2e_output.kra")
    output_engine = KritaOutputEngine()
    output_engine.initialize()
    output_engine.render(doc, output_path)

    # 3. Verify the new file
    assert os.path.exists(output_path)
    with zipfile.ZipFile(output_path, "r") as zf:
        assert "maindoc.xml" in zf.namelist()
        assert "layer0.png" in zf.namelist()

        with zf.open("maindoc.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            # Check a few key attributes to ensure consistency
            assert root.attrib["width"] == "800"
            assert root.attrib["height"] == "600"
            layer_xml = root.find("layers/layer")
            assert layer_xml is not None
            assert layer_xml.attrib["name"] == "Red Layer"
