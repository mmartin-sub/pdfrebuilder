import importlib.util
import logging
import os
import xml.etree.ElementTree as ET
import zipfile
from typing import Any

from wand.image import Image

from pdfrebuilder.engine.document_parser import DocumentParser, DocumentParsingError
from pdfrebuilder.engine.document_renderer import DocumentRenderer, RenderingError
from pdfrebuilder.models.universal_idm import (
    BlendMode,
    BoundingBox,
    CanvasUnit,
    ImageElement,
    Layer,
    LayerType,
    UniversalDocument,
)
from pdfrebuilder.settings import settings

logger = logging.getLogger(__name__)


def check_krita_availability() -> tuple[bool, dict[str, Any]]:
    """
    Check if the necessary components for handling Krita files are available.
    .kra files are zip archives, so we just need standard libraries.
    """
    if importlib.util.find_spec("zipfile") and importlib.util.find_spec("xml.etree.ElementTree"):
        return True, {"status": "available"}
    else:
        return False, {"error": "A required standard library (zipfile or xml.etree.ElementTree) is missing."}


class KritaInputEngine(DocumentParser):
    """
    Input engine for Krita (.kra) files.

    This engine extracts content from Krita files by treating them as zip
    archives, parsing the maindoc.xml to understand the layer structure,
    and using Wand to process the embedded layer images.
    """

    engine_name = "krita"
    engine_version = "0.1.0"

    def initialize(self, config: dict | None = None):
        """Initializes the Krita input engine."""
        self.config = config or {}
        is_available, info = check_krita_availability()
        if not is_available:
            raise DocumentParsingError(f"Krita engine dependencies not met: {info.get('error')}")

    def can_parse(self, file_path: str) -> bool:
        """Checks if the file is a .kra file."""
        return file_path.lower().endswith(".kra")

    def parse(self, file_path: str, extraction_flags: dict | None = None) -> UniversalDocument:
        """Parses a .kra file and returns a UniversalDocument."""
        if not os.path.exists(file_path):
            raise DocumentParsingError(f"Input file not found: {file_path}")

        logger.info(f"Starting Krita extraction for: {file_path}")

        try:
            temp_dir = self._create_temp_dir(file_path)

            with zipfile.ZipFile(file_path, "r") as kra_zip:
                if "maindoc.xml" not in kra_zip.namelist():
                    raise DocumentParsingError("Invalid .kra file: maindoc.xml not found.")

                with kra_zip.open("maindoc.xml") as maindoc_file:
                    tree = ET.parse(maindoc_file)
                    root = tree.getroot()

                    doc_width = int(root.attrib.get("width", 0))
                    doc_height = int(root.attrib.get("height", 0))

                    document = UniversalDocument(engine=self.engine_name, engine_version=self.engine_version)
                    canvas_unit = CanvasUnit(size=(doc_width, doc_height))
                    document.add_document_unit(canvas_unit)

                    layers_element = root.find("layers")
                    if layers_element is not None:
                        for i, layer_element in enumerate(layers_element.findall("layer")):
                            layer = self._parse_layer(layer_element, kra_zip, temp_dir, i, doc_width, doc_height)
                            if layer:
                                canvas_unit.add_layer(layer)

            logger.info(f"Successfully extracted content from {file_path}")
            return document

        except Exception as e:
            logger.error(f"Failed to process Krita file: {e}")
            raise DocumentParsingError(f"Failed to process Krita file: {e}") from e

    def _parse_layer(
        self,
        layer_element: ET.Element,
        kra_zip: zipfile.ZipFile,
        temp_dir: str,
        index: int,
        doc_width: int,
        doc_height: int,
    ) -> Layer | None:
        """Parses a single layer from the maindoc.xml."""
        layer_name = layer_element.attrib.get("name", f"Layer {index}")
        image_src = layer_element.attrib.get("src")
        visible = layer_element.attrib.get("visible", "1") == "1"
        opacity_str = layer_element.attrib.get("opacity", "255")
        opacity = int(opacity_str) / 255.0

        if not visible or not image_src:
            return None

        # Extract the image file to a temporary directory
        image_path = os.path.join(temp_dir, os.path.basename(image_src))
        with kra_zip.open(image_src) as src_file, open(image_path, "wb") as dst_file:
            dst_file.write(src_file.read())

        # Process the image with Wand
        with Image(filename=image_path) as img:
            image_element = ImageElement(
                id=f"image_{index}",
                bbox=BoundingBox(0, 0, doc_width, doc_height),
                image_file=image_path,
                z_index=index,
                original_format=img.format,
                dpi=int(img.resolution[0]) if img.resolution else 72,
                color_space=img.colorspace,
                has_transparency=img.alpha_channel,
            )

        # Create Layer
        layer = Layer(
            layer_id=f"layer_{index}",
            layer_name=layer_name,
            opacity=opacity,
            content=[image_element],
            layer_type=LayerType.PIXEL,  # Krita layers are pixel based
            blend_mode=BlendMode.NORMAL,  # Krita blend modes can be mapped here in future
            bbox=BoundingBox(0, 0, doc_width, doc_height),
        )

        return layer

    def _create_temp_dir(self, input_path: str) -> str:
        """Creates a temporary directory to store extracted images."""
        temp_dir = os.path.join(
            settings.image_dir, "krita_extraction", os.path.splitext(os.path.basename(input_path))[0]
        )
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def extract_assets(self, file_path: str, output_dir: str):
        """Extracts all assets from a .kra file."""
        # This can be implemented to extract all images without creating a UniversalDocument
        pass


class KritaOutputEngine(DocumentRenderer):
    """
    Output engine for Krita (.kra) files.

    This engine takes a UniversalDocument and generates a .kra file.
    """

    engine_name = "krita"
    engine_version = "0.1.0"

    def initialize(self, config: dict | None = None):
        """Initializes the Krita output engine."""
        pass

    def can_render(self, document: UniversalDocument) -> bool:
        """Checks if the document can be rendered as a .kra file."""
        # For now, we can render any document with at least one canvas unit.
        return any(isinstance(unit, CanvasUnit) for unit in document.document_structure)

    def render(self, document: UniversalDocument, output_path: str, config: dict | None = None) -> None:
        """Renders a UniversalDocument to a .kra file."""
        if not output_path.lower().endswith(".kra"):
            raise RenderingError("Output path must have a .kra extension.")

        logger.info(f"Starting Krita rendering for: {output_path}")

        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as kra_zip:
                # We only consider the first canvas for now.
                canvas = next((unit for unit in document.document_structure if isinstance(unit, CanvasUnit)), None)

                if not canvas:
                    raise RenderingError("No canvas unit found in the document to render.")

                doc_width, doc_height = canvas.size

                # Create maindoc.xml
                root = ET.Element("DOC")
                root.set("mimemajor", "2")
                root.set("mimeminor", "8")
                root.set("width", str(int(doc_width)))
                root.set("height", str(int(doc_height)))

                layers_element = ET.SubElement(root, "layers")

                for i, layer in enumerate(canvas.layers):
                    if not layer.content or not isinstance(layer.content[0], ImageElement):
                        continue

                    image_element = layer.content[0]
                    image_path = image_element.image_file

                    # Ensure the image is PNG, as it's standard for Krita layers
                    with Image(filename=image_path) as img:
                        if img.format.lower() != "png":
                            # Convert to png if necessary
                            png_path = os.path.splitext(image_path)[0] + ".png"
                            img.format = "png"
                            img.save(filename=png_path)
                            image_path = png_path

                    image_filename = f"layer{i}.png"
                    kra_zip.write(image_path, image_filename)

                    ET.SubElement(
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

                # Add mimetype file
                kra_zip.writestr("mimetype", "application/x-krita")

            logger.info(f"Successfully rendered Krita file to {output_path}")

        except Exception as e:
            logger.error(f"Failed to generate Krita file: {e}")
            raise RenderingError(f"Failed to generate Krita file: {e}") from e
