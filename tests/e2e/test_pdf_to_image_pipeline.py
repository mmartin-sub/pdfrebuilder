import os
from reportlab.lib.pagesizes import letter
from wand.image import Image

from pdfrebuilder.engine.document_parser import parse_document
from pdfrebuilder.engine.engine_selector import get_output_engine
from tests.config import get_sample_input_path, get_test_output_path, cleanup_test_output

def test_pdf_to_image_pipeline():
    """
    End-to-end test for parsing a PDF and rendering it to a PNG image using Wand.
    """
    test_name = "test_pdf_to_image_pipeline"
    pdf_path = get_sample_input_path("sample.pdf")
    output_path = get_test_output_path(test_name, ext=".png")

    # 1. Ensure the sample PDF exists
    assert os.path.exists(pdf_path)

    # 2. Parse the PDF using the auto-selected parser
    doc = parse_document(pdf_path)
    assert doc is not None
    pages = doc.get_pages()
    assert len(pages) > 0 # sample.pdf has multiple pages

    # 3. Get the Wand image output engine
    output_engine = get_output_engine("wand_image")
    assert output_engine.engine_name == "WandImageEngine"

    # 4. Render the document to a PNG
    # The engine currently renders only the first page
    output_engine.render(doc, output_path)

    # 5. Verify the output
    assert os.path.exists(output_path)
    with Image(filename=output_path) as img:
        assert img.format == 'PNG'
        # The sample.pdf might not be standard letter size, so we check for non-zero dimensions
        assert img.width > 0
        assert img.height > 0

    # 6. Clean up the specific output file
    if os.path.exists(output_path):
        os.remove(output_path)
