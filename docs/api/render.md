# render

## Functions

### json_serializer(obj)

Custom JSON serializer for various types.

### _(obj)

### _(obj)

### _(obj)

### _render_text_with_fallback(page, rect_obj, text, font, size, color, elem_id, use_textbox, use_htmlbox)

Renders text using either a rectangle (insert_textbox), a starting point (insert_text), or insert_htmlbox.
If use_textbox is True, uses insert_textbox (with fallback logic). Otherwise, uses insert_text at the bottom-left of rect_obj.
If use_htmlbox is True, uses insert_htmlbox with the rect.

### _render_vector_element(page, element_data)

Renders a vector element (drawing or shape) by creating a Shape object,
populating it with drawing commands, and committing it to the page.
This version properly handles null color values for stroke and fill.

Null color handling:

- If stroke color is null, no stroke is applied (interpreted as "no stroke")
- If fill color is null, no fill is applied (interpreted as "no fill")
- If both stroke and fill are null, a warning is logged and an invisible shape is rendered
- Appropriate debug logs are generated for each case

Examples:
    1. Stroke only (no fill):
       ```json
       {
           "type": "drawing",
           "color": [0.0, 0.0, 0.0],
           "fill": null,
           "width": 2.0,
           "drawing_commands": [...]
       }
       ```

    2. Fill only (no stroke):
       ```json
       {
           "type": "drawing",
           "color": null,
           "fill": [0.0, 0.0, 0.0],
           "width": 1.0,
           "drawing_commands": [...]
       }
       ```

    3. Both stroke and fill:
       ```json
       {
           "type": "drawing",
           "color": [0.0, 0.0, 0.0],
           "fill": [0.8, 0.8, 0.8],
           "width": 2.0,
           "drawing_commands": [...]
       }
       ```

    4. Neither stroke nor fill (invisible shape):
       ```json
       {
           "type": "drawing",
           "color": null,
           "fill": null,
           "width": 1.0,
           "drawing_commands": [...]
       }
       ```

Args:
    page: The PyMuPDF page object to render on
    element_data: Dictionary containing the vector element data

Returns:
    Dictionary with information about the rendering operation

### _render_element(page, element, page_idx, page_overrides, config, use_htmlbox)

Renders a single element on the given page, with comprehensive type handling
and a robust two-pass, auto-shrinking text rendering strategy.
Uses ensure_font_registered for per-page font registration.
