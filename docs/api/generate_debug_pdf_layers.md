# generate_debug_pdf_layers

## Functions

### _create_summarized_json(data_dict)

Creates a summarized, compact, single-line JSON string.

### _wrap_text(text_block, width)

Manually wraps a block of text to a specified character width.

### generate_debug_pdf_layers(config_path, output_debug_pdf_base)

Creates a debug PDF using a fixed-size box and manually wrapped text for maximum compatibility.
Now supports both 'pages' and 'document_structure' as the root key.
Logs statistics and errors for unrecognized structures.
