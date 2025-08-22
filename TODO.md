# TODO List

This file tracks pending tasks and issues to be addressed in the `pdfrebuilder` project.

## Pytest Warnings

-   **`PytestCollectionWarning` for `TestFileManager` in `tests/wip/unit/test_utils.py`**:
    -   **Problem**: The test class `TestFileManager` has an `__init__` constructor, which prevents pytest from collecting it as a test class.
    -   **Status**: **Resolved**.
    -   **Analysis**: `TestFileManager` is a helper class for managing test files, not a test class itself. The warning is correct.
    -   **Action Taken**: Renamed the class to `_TestFileManager` to prevent pytest collection.
    -   **Bibliography**: [Pytest good practices - Test discovery](https://docs.pytest.org/en/stable/explanation/goodpractices.html#test-discovery)

## Application Warnings during Tests

-   **`Not a TrueType or OpenType font (bad sfntVersion)` warnings**:
    -   **Problem**: Several tests in `tests/font/` are logging warnings about being unable to read mock font files.
    -   **Status**: **Confirmed**.
    -   **Analysis**: The tests in `tests/font/test_font_cache_integration.py` and other font tests are intentionally creating invalid font files with dummy content to test the error handling capabilities of the font management system. The warnings are expected and indicate that the system is correctly identifying invalid font files.
    -   **Action**: To make the tests more explicit and to suppress the warnings from the test output, use `pytest.warns` to assert that these warnings are raised.
    -   **Bibliography**: [pytest.warns documentation](https://docs.pytest.org/en/stable/how-to/capture-warnings.html#asserting-that-a-warning-was-raised)

-   **`Error: Could not fetch CSS for ...` warnings**:
    -   **Problem**: Several tests related to Google Fonts integration are logging errors about failing to fetch CSS.
    -   **Status**: **Resolved**.
    -   **Analysis**: A test is calling `ensure_font_registered` with the font "Arial". Since "Arial" is not a Google Font, the call to `download_google_font` makes a real network request that fails, triggering the warning. The test is not properly mocking the network call.
    -   **Action Taken**: I have identified several tests in `tests/font/test_font_substitution.py` and `tests/font/test_font_integration_workflows.py` that were missing a patch for `download_google_font`. I have added the `@patch("pdfrebuilder.font.utils.download_google_font")` decorator to these tests to prevent the network requests.
    -   **Bibliography**:
        -   [unittest.mock.patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch)

-   **`'cmap'` and `'name'` key errors in font tests**:
    -   **Problem**: Some font tests are logging key errors when trying to access `cmap` or `name` attributes of a font object.
    -   **Status**: **Resolved**.
    -   **Analysis**: Some integration tests were creating dummy font files with invalid content. When `fontTools` tries to parse these files, it creates a `TTFont` object that is missing some tables, like `'cmap'` and `'name'`. When the code under test tries to access these tables, it raises a `KeyError`.
    -   **Action Taken**: I have identified the tests that were causing this issue and patched them to use a mock `TTFont` object that is correctly configured with the necessary attributes. This prevents the `KeyError` and the associated warnings.
    -   **Bibliography**:
        -   [fontTools documentation](https://fonttools.readthedocs.io/en/latest/)

-   **`Unsupported element type` warnings in `reportlab_engine`**:
    -   **Problem**: The `reportlab_engine` is logging warnings about unsupported element types (`DrawingElement`).
    -   **Status**: **Analysis Complete**. This is a feature gap.
    -   **Analysis**: The `reportlab_engine`'s `_render_page_canvas` function only handles `TextElement` and `ImageElement` types. It does not have a case for `DrawingElement`, which causes the warning.
    -   **Next Steps**: To resolve this, the following actions are needed:
        1.  **Import `DrawingElement`**: In `src/pdfrebuilder/engine/reportlab_engine.py`, import the `DrawingElement` class from `pdfrebuilder.models.universal_idm`.
        2.  **Implement `_render_drawing_element_canvas`**: Create a new method in the `ReportLabEngine` class to handle the rendering of `DrawingElement` objects. This method should:
            -   Take the `canvas`, `DrawingElement`, `layer`, and `page_size` as arguments.
            -   Set the stroke color, fill color, and line width on the canvas based on the element's properties.
            -   Iterate through the `drawing_commands` of the element and use the appropriate `reportlab.graphics.shapes` to draw the lines, curves, and rectangles.
        3.  **Update `_render_page_canvas`**: Add a new condition to the `for` loop in `_render_page_canvas` to call `_render_drawing_element_canvas` when an element of type `DrawingElement` is encountered.
    -   **Bibliography**:
        -   [ReportLab Graphics Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf) (Chapter 2: Graphics)
