import os
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

from pdfrebuilder.engine.document_renderer import DocumentRenderer
from pdfrebuilder.models.universal_idm import UniversalDocument, Page, TextElement, DrawingElement, ImageElement

class WandImageOutputEngine(DocumentRenderer):
    """
    An output engine that renders a UniversalDocument to an image format using Wand.
    """
    def __init__(self):
        self.engine_name = "WandImageEngine"
        self.engine_version = "0.1.0"
        self.supported_features = ["png", "jpg", "tiff"]

    def initialize(self, config: dict):
        pass

    def render(self, document: UniversalDocument, output_path: str, options: dict = None):
        """
        Renders the document to an image. For multi-page documents, it renders the first page.
        """
        from pdfrebuilder.engine.document_renderer import RenderingError
        pages = document.get_pages()
        if not pages:
            raise RenderingError("Cannot render an empty document with no pages.")

        page_to_render = pages[0]

        output_format = os.path.splitext(output_path)[1].lstrip('.').lower()
        if not output_format:
            output_format = 'png' # default to png
            output_path += '.png'

        if output_format not in self.supported_features:
            from pdfrebuilder.engine.document_renderer import RenderingError
            raise RenderingError(f"Unsupported image format: {output_format}. Supported formats: {self.supported_features}")

        width, height = page_to_render.size
        with Image(width=int(width), height=int(height), background=Color('white')) as img:
            draw = Drawing()

            for layer in reversed(page_to_render.layers): # Render from bottom to top
                if not layer.visibility:
                    continue

                for element in layer.content:
                    if isinstance(element, TextElement):
                        # Basic text rendering
                        draw.font_size = element.font_details.size
                        # Note: Font family requires more complex mapping. Using a default.
                        draw.font = element.font_details.name
                        if element.font_details.color:
                            color = element.font_details.color
                            # Wand's Color constructor is flexible. This works.
                            draw.fill_color = Color(f'rgba({color.r*255}, {color.g*255}, {color.b*255}, {color.a})')
                        draw.text(int(element.bbox.x1), int(element.bbox.y2), element.text)

                    elif isinstance(element, ImageElement):
                        # Basic image rendering
                        with Image(filename=element.image_file) as elem_img:
                            img.composite(elem_img, left=int(element.bbox.x1), top=int(element.bbox.y1))

                    # DrawingElement rendering would be more complex and is omitted for this example.

            draw(img)
            img.format = output_format
            img.save(filename=output_path)

        if not os.path.exists(output_path):
            from pdfrebuilder.engine.document_renderer import RenderingError
            raise RenderingError(f"Failed to save output image to {output_path}")

    def can_render(self, document: UniversalDocument, output_format: str) -> bool:
        return output_format.lower() in self.supported_features
