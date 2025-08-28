import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Any

from pdfrebuilder.engine.document_parser import DocumentParser, DocumentParsingError
from pdfrebuilder.engine.document_renderer import DocumentRenderer, RenderingError
from pdfrebuilder.models.universal_idm import (
    BoundingBox,
    CanvasUnit,
    ImageElement,
    Layer,
    UniversalDocument,
)


class KritaOutputEngine(DocumentRenderer):
    """
    An output engine for Krita (.kra) files.
    """

    engine_name = "krita"
    engine_version = "0.1.0"

    def initialize(self, config: dict = None):
        pass

    def can_render(self, file_path: str) -> bool:
        return file_path.lower().endswith(".kra")

    def render(self, document: UniversalDocument, output_path: str, config=None) -> None:
        self.generate(document, output_path)

    def generate(self, document: UniversalDocument, output_path: str) -> None:
        """
        Generates a Krita (.kra) file from a UniversalDocument object.

        Args:
            document: The UniversalDocument object to convert.
            output_path: The path to save the output .kra file.
        """
        try:
            with zipfile.ZipFile(output_path, "w") as kra_zip:
                # Create maindoc.xml
                root = ET.Element("DOC")
                if document.document_structure:
                    first_unit = document.document_structure[0]
                    if isinstance(first_unit, CanvasUnit):
                        width, height = first_unit.size
                        root.set("width", str(int(width)))
                        root.set("height", str(int(height)))

                layers_element = ET.SubElement(root, "layers")

                for i, unit in enumerate(document.document_structure):
                    if isinstance(unit, CanvasUnit):
                        for j, layer in enumerate(unit.layers):
                            if layer.content and isinstance(layer.content[0], ImageElement):
                                image_element = layer.content[0]
                                image_path = image_element.image_file
                                image_filename = f"layer_{j}.png"
                                kra_zip.write(image_path, image_filename)

                                layer_xml = ET.SubElement(
                                    layers_element,
                                    "layer",
                                    name=layer.layer_name,
                                    src=image_filename,
                                    visible="1" if layer.visibility else "0",
                                    opacity=str(int(layer.opacity * 255)),
                                )

                # Write maindoc.xml
                xml_string = ET.tostring(root, encoding="unicode")
                kra_zip.writestr("maindoc.xml", xml_string)

        except Exception as e:
            raise RenderingError(f"Failed to generate Krita file: {e}") from e


class KritaInputEngine(DocumentParser):
    """
    An input engine for Krita (.kra) files.
    """

    engine_name = "krita"
    engine_version = "0.1.0"

    def initialize(self, config: dict = None):
        pass

    def can_parse(self, file_path: str) -> bool:
        return file_path.lower().endswith(".kra")

    def parse(self, file_path: str, extraction_flags: dict = None) -> UniversalDocument:
        return self.extract(file_path)

    def extract(self, file_path: str) -> UniversalDocument:
        """
        Extracts content from a Krita (.kra) file and converts it to the Universal Document Model.

        Args:
            file_path: The path to the input .kra file.

        Returns:
            A UniversalDocument object representing the content of the .kra file.
        """
        if not os.path.exists(file_path):
            raise DocumentParsingError(f"Input file not found: {file_path}")

        try:
            with zipfile.ZipFile(file_path, "r") as kra_zip:
                if "maindoc.xml" not in kra_zip.namelist():
                    raise DocumentParsingError("Invalid .kra file: maindoc.xml not found.")

                with kra_zip.open("maindoc.xml") as maindoc_file:
                    tree = ET.parse(maindoc_file)
                    root = tree.getroot()

                    doc_width = int(root.attrib.get("width", 0))
                    doc_height = int(root.attrib.get("height", 0))

                    document = UniversalDocument()
                    canvas_unit = CanvasUnit(size=(doc_width, doc_height))
                    document.add_document_unit(canvas_unit)

                    temp_dir = self._create_temp_dir(file_path)

                    layers_element = root.find("layers")
                    if layers_element is not None:
                        for i, layer_element in enumerate(layers_element.findall("layer")):
                            layer_name = layer_element.attrib.get("name", f"Layer {i}")
                            image_src = layer_element.attrib.get("src")
                            visible = layer_element.attrib.get("visible", "1") == "1"
                            opacity = int(layer_element.attrib.get("opacity", 255)) / 255.0

                            if not visible or not image_src:
                                continue

                            # Extract the image file
                            image_path = os.path.join(temp_dir, os.path.basename(image_src))
                            with kra_zip.open(image_src) as src_file, open(image_path, "wb") as dst_file:
                                dst_file.write(src_file.read())

                            # Create ImageElement
                            image_element = ImageElement(
                                id=f"image_{i}",
                                bbox=BoundingBox(0, 0, doc_width, doc_height),
                                image_file=image_path,
                                z_index=i,
                            )

                            # Create Layer
                            layer = Layer(
                                layer_id=f"layer_{i}",
                                layer_name=layer_name,
                                opacity=opacity,
                                content=[image_element],
                            )
                            canvas_unit.add_layer(layer)

            return document

        except Exception as e:
            raise DocumentParsingError(f"Failed to process Krita file: {e}") from e

    def extract_assets(self, file_path: str, output_dir: str):
        pass

    def _create_temp_dir(self, input_path: str) -> str:
        """Creates a temporary directory to store extracted images."""
        temp_dir = os.path.join(os.path.dirname(input_path), "temp_krita_extraction")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
