# reportlab_engine

ReportLab PDF Engine Implementation

This module provides a ReportLab-based PDF rendering engine with enhanced precision,
proper font embedding, and licensing verification capabilities.

## Classes

### ReportLabEngine

ReportLab-based PDF engine with enhanced precision and font embedding.

#### Methods

##### __init__(font_validator)

Initialize the ReportLab engine.

##### extract(input_pdf_path)

Extract content from PDF using ReportLab (limited functionality).

##### generate(config, output_pdf_path, original_pdf_for_template)

Generate PDF from universal JSON config using ReportLab.

##### _create_document(document, output_path)

Create a ReportLab document with proper configuration.

##### _render_page_canvas(output_path, page_unit, document)

Render a single page using ReportLab canvas.

##### _render_text_element_canvas(c, element, layer, page_size)

Render a text element using ReportLab canvas.

##### _render_page(doc, page_unit, document)

Render a single page using ReportLab.

##### _render_text_element(story, element, layer)

Render a text element using ReportLab.

##### _create_text_style(element)

Create a ReportLab paragraph style for a text element.

##### _convert_color(color)

Convert our Color object to ReportLab Color.

##### _register_font(font_name)

Register a font with ReportLab.

##### _get_font_path(font_name)

Get the file path for a font.

##### validate_font_licensing(font_name)

Validate font licensing for embedding.

##### get_engine_info()

Get information about the ReportLab engine.
