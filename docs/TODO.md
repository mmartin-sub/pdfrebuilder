# TODO List

This file tracks pending tasks and issues to be addressed in the `pdfrebuilder` project.

## Application Warnings during Tests

- **`Unsupported element type` warnings in `reportlab_engine`**:
  - **Problem**: The `reportlab_engine` is logging warnings about unsupported element types (`DrawingElement`).
  - **Status**: **Analysis Complete**. This is a feature gap.
  - **Analysis**: The `reportlab_engine`'s `_render_page_canvas` function only handles `TextElement` and `ImageElement` types. It does not have a case for `DrawingElement`, which causes the warning.
  - **Next Steps**: To resolve this, the following actions are needed:
        1. **Import `DrawingElement`**: In `src/pdfrebuilder/engine/reportlab_engine.py`, import the `DrawingElement` class from `pdfrebuilder.models.universal_idm`.
        2. **Implement `_render_drawing_element_canvas`**: Create a new method in the `ReportLabEngine` class to handle the rendering of `DrawingElement` objects. This method should:
            - Take the `canvas`, `DrawingElement`, `layer`, and `page_size` as arguments.
            - Set the stroke color, fill color, and line width on the canvas based on the element's properties.
            - Iterate through the `drawing_commands` of the element and use the appropriate `reportlab.graphics.shapes` to draw the lines, curves, and rectangles.
        3. **Update `_render_page_canvas`**: Add a new condition to the `for` loop in `_render_page_canvas` to call `_render_drawing_element_canvas` when an element of type `DrawingElement` is encountered.
  - **Bibliography**:
    - [ReportLab Graphics Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf) (Chapter 2: Graphics)
