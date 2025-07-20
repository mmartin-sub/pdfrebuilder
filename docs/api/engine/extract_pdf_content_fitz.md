# extract_pdf_content_fitz

## Functions

### _process_image_block(block, image_dir, element_id)

Processes an image block, saves the image, and returns an ImageElement.

### _process_text_block(block, space_density_threshold, element_id_counter)

Processes a text block and returns a list of TextElement objects.

### _process_drawing(drawing, drawing_idx)

Processes a drawing and returns a DrawingElement.

### extract_pdf_content(pdf_path, extraction_flags)

Extracts all content from a PDF, organizing it by page and a default 'base' layer for reconstruction.

This version uses the Universal IDM classes to create a structured document representation
with full support for layer hierarchies and complex element types.

Returns:
    UniversalDocument: A complete document object with all extracted content
