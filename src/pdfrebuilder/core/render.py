import logging
import math
import os
from functools import singledispatch
from typing import Any, TypedDict

# from pdfrebuilder.pdf_engine import FitzPDFEngine  # Remove if not directly used
import fitz  # Only for types/constants; all I/O should use FitzPDFEngine

from pdfrebuilder.engine.tool_fritz import _convert_color_to_rgb
from pdfrebuilder.font.utils import ensure_font_registered

# Set up logging
logger = logging.getLogger(__name__)


class FontPreValidationResult(TypedDict):
    """Typed structure for pre-validation results to satisfy mypy."""

    total_fonts: int
    successful_validations: int
    failed_validations: int
    critical_failures: int
    font_mapping: dict[str, str]
    validation_errors: list[dict[str, Any]]
    elements_with_font_issues: list[str]


@singledispatch
def json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for various types."""
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


@json_serializer.register(bytes)
def _(obj: bytes):
    return obj.decode("utf-8", "ignore")


@json_serializer.register(fitz.Rect)
def _(obj: fitz.Rect) -> list[float]:
    return [obj.x0, obj.y0, obj.x1, obj.y1]


@json_serializer.register(fitz.Point)
def _(obj: fitz.Point) -> list[float]:
    return [obj.x, obj.y]


@json_serializer.register(fitz.Matrix)
def _(obj: fitz.Matrix) -> list[float]:
    return [obj.a, obj.b, obj.c, obj.d, obj.e, obj.f]


@json_serializer.register(float)
def _(obj: float):
    # Convert special float values to strings
    if math.isnan(obj):
        return "nan"
    if math.isinf(obj):
        return "inf" if obj > 0 else "-inf"
    return obj


@json_serializer.register(set)
def _(obj: set):
    return list(obj)


@json_serializer.register(tuple)
def _(obj: tuple):
    return list(obj)


def _render_text_with_fallback(
    page,
    rect_obj,
    text,
    font,
    size,
    color,
    elem_id="N/A",
    use_textbox=False,
    use_htmlbox=False,
):
    """
    Renders text using either a rectangle (insert_textbox), a starting point (insert_text), or insert_htmlbox.
    If use_textbox is True, uses insert_textbox (with fallback logic). Otherwise, uses insert_text at the bottom-left of rect_obj.
    If use_htmlbox is True, uses insert_htmlbox with the rect.

    Enhanced with comprehensive font error handling and registration validation.
    """
    from pdfrebuilder.font.utils import FontRegistrationError, register_font_with_validation

    # Enhanced font registration with comprehensive error handling
    try:
        registration_result = register_font_with_validation(
            page=page,
            font_name=font,
            text_content=text,
            element_id=elem_id,
            verbose=True,
        )

        if not registration_result.success:
            if registration_result.is_critical_failure():
                # Critical failure should propagate and fail the test
                error_msg = (
                    f"Critical font registration failure in text rendering: "
                    f"font='{font}', element='{elem_id}', error='{registration_result.error_message}'"
                )
                logger.critical(error_msg)
                raise FontRegistrationError(
                    message=error_msg,
                    font_name=font,
                    context={
                        "element_id": elem_id,
                        "text_content": text[:100],
                        "rect": (list(rect_obj) if hasattr(rect_obj, "__iter__") else str(rect_obj)),
                    },
                )
            else:
                # Non-critical failure, log warning and continue with fallback
                logger.warning(
                    f"Font registration failed for '{font}' in element '{elem_id}', "
                    f"but continuing with available fallback"
                )

        # Use the actual registered font name
        actual_font = registration_result.actual_font_used or font

        if registration_result.fallback_used:
            logger.info(f"Using fallback font for element '{elem_id}': '{font}' -> '{actual_font}'")

    except FontRegistrationError:
        # Re-raise critical font errors to fail tests
        raise
    except Exception as e:
        # Handle unexpected errors in font registration
        logger.error(f"Unexpected error in font registration for '{font}' in element '{elem_id}': {e}")
        # Use original font name and hope for the best
        actual_font = font
    final_kwargs = {
        "fontname": actual_font,  # Use the actual registered font
        "fontsize": size,
        "color": color,
        "lineheight": 1.0,  # Use explicit, tight line height for predictability
    }
    if use_htmlbox:
        # Use insert_htmlbox for advanced layout
        rc = page.insert_htmlbox(rect_obj, text)
        logger.info(f"Inserted HTML text for ID {elem_id} in rect {list(rect_obj)}.")
        final_kwargs["htmlbox_rect"] = list(rect_obj)
        final_kwargs["htmlbox_rc"] = rc
        return final_kwargs
    if use_textbox:
        # --- CONSTANTS FOR THE FALLBACK LOGIC ---
        SECOND_PASS_SHRINK_FACTOR = 0.85  # Reduce to 85% of the original size
        MINIMUM_FONT_SIZE = 4  # Do not attempt to render text smaller than this.

        return_code = page.insert_textbox(rect_obj, text, **final_kwargs)
        if return_code < 0:
            logger.warning(
                f"Initial render failed for ID {elem_id} (box too small, font='{actual_font}', size={size}). "
                f"Attempting a 'second pass' with a reduced font size."
            )
            new_size = size * SECOND_PASS_SHRINK_FACTOR * 0.95  # Margin error
            if new_size < MINIMUM_FONT_SIZE:
                logger.error(
                    f"Auto-shrink for ID {elem_id} resulted in unreadable font size ({new_size:.2f}pt, font='{actual_font}'). Aborting."
                )
            else:
                logger.info(
                    f"Second Pass for ID {elem_id}: Reducing font size from {size:.2f} to {new_size:.2f} (font='{actual_font}')."
                )
                final_kwargs["fontsize"] = new_size
                return_code = page.insert_textbox(rect_obj, text, **final_kwargs)
        if return_code != 0:
            if return_code < 0:
                logger.error(
                    f"CRITICAL RENDER FAILURE for ID {elem_id}: Could not render even after second pass. Final code: {return_code:.2f}. (font='{actual_font}', size={final_kwargs['fontsize']})"
                )
            else:
                logger.warning(
                    f"Render Overflow for ID {elem_id}: Text rendered but did not fit. Final code: {return_code:.2f}. (font='{actual_font}', size={final_kwargs['fontsize']})"
                )
        return final_kwargs
    else:
        # Use insert_text at the bottom-left corner of the rect
        point = rect_obj.bl  # bottom-left
        page.insert_text(point, text, **final_kwargs)
        logger.info(f"Inserted text for ID {elem_id} at point {point} (font='{actual_font}', size={size}).")
        final_kwargs["text_content"] = text
        final_kwargs["point"] = list(point)
        return final_kwargs


def _render_vector_element(page, element_data):
    """
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
    """
    drawing_commands = element_data.get("drawing_commands")
    if not drawing_commands:
        logger.warning(f"Vector element ID {element_data.get('id', 'N/A')} has no 'drawing_commands'. Skipping.")
        return {"error": "Vector element missing 'drawing_commands'."}

    # --- 1. Safe Extraction of Style Properties ---
    stroke_details = element_data.get("stroke_details") or {}
    fill_details = element_data.get("fill_details") or {}

    stroke_color_val = stroke_details.get("color") or element_data.get("color")
    stroke_color = _convert_color_to_rgb(stroke_color_val)

    stroke_width = float(stroke_details.get("width") or element_data.get("width") or 1.0)
    stroke_opacity = float(stroke_details.get("opacity") or element_data.get("stroke_opacity") or 1.0)

    line_cap_map = {"butt": 0, "round": 1, "square": 2}
    line_join_map = {"miter": 0, "round": 1, "bevel": 2}
    line_cap = line_cap_map.get(stroke_details.get("line_cap", "").lower(), 0)
    line_join = line_join_map.get(stroke_details.get("line_join", "").lower(), 0)
    dashes = stroke_details.get("dashes")

    fill_color_val = fill_details.get("color") or element_data.get("fill")
    fill_color = _convert_color_to_rgb(fill_color_val)
    fill_opacity = float(fill_details.get("opacity") or element_data.get("fill_opacity") or 1.0)

    # Determine if we have valid stroke and fill
    has_stroke = stroke_color is not None and stroke_width > 0
    has_fill = fill_color is not None

    elem_id = element_data.get("id", "N/A")

    # Log rendering decisions
    if not has_stroke:
        logger.debug(f"Vector element ID {elem_id}: Skipping stroke due to null color or zero width")
    if not has_fill:
        logger.debug(f"Vector element ID {elem_id}: Skipping fill due to null color")

    # Log warning if both stroke and fill are null
    if not has_stroke and not has_fill:
        logger.warning(f"Vector element ID {elem_id} has neither stroke nor fill. Rendering as invisible shape.")

    # --- 2. Use the Shape API to Build and Draw the Vector Graphic ---
    try:
        shape = page.new_shape()

        # Collect all M and L commands to create a polyline
        polyline_points = []

        for cmd_data in drawing_commands:
            cmd_type = cmd_data.get("cmd")
            pts = cmd_data.get("pts", [])
            bbox_cmd = cmd_data.get("bbox")

            if cmd_type in ("M", "L"):
                # Collect points for polyline
                try:
                    if isinstance(pts, list) and len(pts) == 2 and all(isinstance(p, int | float) for p in pts):
                        # Single point as [x, y]
                        polyline_points.append(fitz.Point(pts[0], pts[1]))
                    elif isinstance(pts, list) and len(pts) > 2 and all(isinstance(p, int | float) for p in pts):
                        # Multiple coordinates as flat list [x1, y1, x2, y2, ...]
                        for i in range(0, len(pts), 2):
                            if i + 1 < len(pts):
                                polyline_points.append(fitz.Point(pts[i], pts[i + 1]))
                    elif all(isinstance(p, list | tuple) and len(p) == 2 for p in pts):
                        # Points as [[x1, y1], [x2, y2], ...]
                        for p in pts:
                            polyline_points.append(fitz.Point(p[0], p[1]))
                except Exception as e:
                    logger.warning(f"Could not create points from {pts}: {e}")
                    # Skip this command but continue with others

            elif cmd_type == "C":  # Cubic Bezier
                if len(pts) < 4:
                    continue
                try:
                    # Handle different formats of points
                    if all(isinstance(p, list | tuple) and len(p) == 2 for p in pts):
                        # Format: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                        p1 = fitz.Point(pts[0][0], pts[0][1])  # Start point
                        p2 = fitz.Point(pts[1][0], pts[1][1])  # Control point 1
                        p3 = fitz.Point(pts[2][0], pts[2][1])  # Control point 2
                        p4 = fitz.Point(pts[3][0], pts[3][1])  # End point
                    elif len(pts) == 8 and all(isinstance(p, int | float) for p in pts):
                        # Format: [x1, y1, x2, y2, x3, y3, x4, y4]
                        p1 = fitz.Point(pts[0], pts[1])
                        p2 = fitz.Point(pts[2], pts[3])
                        p3 = fitz.Point(pts[4], pts[5])
                        p4 = fitz.Point(pts[6], pts[7])
                    else:
                        logger.warning(f"Unsupported point format for bezier curve: {pts}")
                        continue

                    shape.draw_bezier(p1, p2, p3, p4)
                except Exception as e:
                    logger.warning(f"Could not create bezier curve from {pts}: {e}")
                    # Skip this command but continue with others

            elif cmd_type == "H":  # Close path
                # The 'finish' method has a 'closePath' argument that handles this.
                # We will set a flag to use it later.
                pass  # This command is handled by shape.finish(closePath=True)

            elif cmd_type == "rect":
                if not bbox_cmd or len(bbox_cmd) < 4:
                    continue
                if isinstance(bbox_cmd[0], list):
                    bbox_cmd = bbox_cmd[0]
                shape.draw_rect(fitz.Rect(bbox_cmd))

            elif cmd_type == "ellipse":
                if not bbox_cmd or len(bbox_cmd) < 4:
                    continue
                shape.draw_oval(fitz.Rect(bbox_cmd))

        # Draw the polyline if we have collected points
        if len(polyline_points) > 1:
            shape.draw_polyline(polyline_points)
        elif len(polyline_points) == 1:
            # For a single point, we can draw a small circle or just skip
            logger.debug(f"Vector element ID {elem_id}: Single point detected, skipping polyline")

        # Check if any command was 'H' to determine if we should close the path.
        should_close_path = any(cmd.get("cmd") == "H" for cmd in drawing_commands)

        if dashes and has_stroke:
            shape.set_line_dash(dashes)

        # Build finish parameters based on what we have
        finish_kwargs: dict[str, object] = {
            "closePath": should_close_path,
        }

        # Only add stroke parameters if we have a stroke
        if has_stroke:
            finish_kwargs.update(
                {
                    "color": stroke_color,
                    "width": stroke_width,
                    "lineCap": line_cap,
                    "lineJoin": line_join,
                    "stroke_opacity": stroke_opacity,
                }
            )

        # Only add fill parameters if we have a fill
        if has_fill:
            finish_kwargs.update(
                {
                    "fill": fill_color,
                    "fill_opacity": fill_opacity,
                }
            )

        shape.finish(**finish_kwargs)

        shape.commit(overlay=False)

        return {
            "pymupdf_call": "shape.commit",
            "pymupdf_kwargs": {
                "color": stroke_color,
                "fill": fill_color,
                "width": stroke_width,
                "has_stroke": has_stroke,
                "has_fill": has_fill,
                # ... and so on for other properties
            },
        }
    except Exception as e:
        elem_id = element_data.get("id", "N/A")
        error_msg = f"Error drawing shape for element ID {elem_id}: {e}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": f"Failed to draw shape: {e}",
            "element_id": elem_id,
            "element_type": element_data.get("type", "unknown"),
            "has_stroke": has_stroke,
            "has_fill": has_fill,
        }


def _validate_fonts_before_rendering(page, elements, page_idx, config):
    """
    Pre-validate all fonts required for rendering before attempting to render elements.
    This helps catch font issues early and provides better error reporting.

    Args:
        page: PyMuPDF page object
        elements: List of elements to be rendered
        page_idx: Page index for logging
        config: Configuration dictionary

    Returns:
        Dictionary with validation results and font mapping
    """
    from pdfrebuilder.font.utils import FontRegistrationError, register_font_with_validation

    logger.info(f"Pre-validating fonts for page {page_idx} with {len(elements)} elements")

    validation_results: FontPreValidationResult = {
        "total_fonts": 0,
        "successful_validations": 0,
        "failed_validations": 0,
        "critical_failures": 0,
        "font_mapping": {},  # requested_font -> actual_font
        "validation_errors": [],
        "elements_with_font_issues": [],
    }

    # Collect all unique fonts needed for this page
    required_fonts: set[str] = set()
    font_to_elements: dict[str, list[str]] = {}  # Track which elements need which fonts

    for element in elements:
        if element.get("type") == "text":
            elem_id = element.get("id", "unknown")
            font_name = element.get("font_details", {}).get("name")

            if font_name:
                required_fonts.add(font_name)
                if font_name not in font_to_elements:
                    font_to_elements[font_name] = []
                font_to_elements[font_name].append(elem_id)

    validation_results["total_fonts"] = len(required_fonts)

    if not required_fonts:
        logger.debug(f"No fonts to validate for page {page_idx}")
        return validation_results

    # Validate each required font
    for font_name in required_fonts:
        try:
            # Get a sample text for this font (from first element that uses it)
            sample_element_id: str = font_to_elements[font_name][0]
            sample_element = next((elem for elem in elements if elem.get("id") == sample_element_id), None)
            sample_text: str = sample_element.get("text", "Sample text") if sample_element else "Sample text"

            # Attempt font registration
            registration_result = register_font_with_validation(
                page=page,
                font_name=font_name,
                text_content=sample_text,
                element_id=f"pre_validation_{page_idx}",
                verbose=False,  # Reduce noise during pre-validation
            )

            if registration_result.success and registration_result.actual_font_used is not None:
                validation_results["successful_validations"] += 1
                validation_results["font_mapping"][font_name] = registration_result.actual_font_used

                if registration_result.fallback_used:
                    logger.info(
                        f"Pre-validation: Font '{font_name}' will use fallback '{registration_result.actual_font_used}' "
                        f"for elements: {font_to_elements[font_name]}"
                    )
                else:
                    logger.debug(f"Pre-validation: Font '{font_name}' validated successfully")

            else:
                validation_results["failed_validations"] += 1

                if registration_result.is_critical_failure():
                    validation_results["critical_failures"] += 1

                    # Record critical failure details
                    error_info: dict[str, Any] = {
                        "font_name": font_name,
                        "error_message": registration_result.error_message,
                        "affected_elements": font_to_elements[font_name],
                        "is_critical": True,
                    }
                    validation_results["validation_errors"].append(error_info)
                    validation_results["elements_with_font_issues"].extend(font_to_elements[font_name])

                    logger.critical(
                        f"Pre-validation CRITICAL FAILURE: Font '{font_name}' failed validation "
                        f"for elements {font_to_elements[font_name]} on page {page_idx}. "
                        f"Error: {registration_result.error_message}"
                    )
                else:
                    # Non-critical failure
                    error_info = {
                        "font_name": font_name,
                        "error_message": registration_result.error_message,
                        "affected_elements": font_to_elements[font_name],
                        "is_critical": False,
                    }
                    validation_results["validation_errors"].append(error_info)

                    logger.warning(
                        f"Pre-validation: Font '{font_name}' failed validation but may have fallbacks "
                        f"for elements {font_to_elements[font_name]} on page {page_idx}"
                    )

        except FontRegistrationError as e:
            # Critical font registration error during pre-validation
            validation_results["failed_validations"] += 1
            validation_results["critical_failures"] += 1

            error_info = {
                "font_name": font_name,
                "error_message": str(e),
                "affected_elements": font_to_elements[font_name],
                "is_critical": True,
                "exception_type": "FontRegistrationError",
            }
            validation_results["validation_errors"].append(error_info)
            validation_results["elements_with_font_issues"].extend(font_to_elements[font_name])

            logger.critical(
                f"Pre-validation: Critical font registration error for '{font_name}' "
                f"affecting elements {font_to_elements[font_name]} on page {page_idx}: {e}"
            )

        except Exception as e:
            # Unexpected error during pre-validation
            validation_results["failed_validations"] += 1

            error_info = {
                "font_name": font_name,
                "error_message": f"Unexpected validation error: {e!s}",
                "affected_elements": font_to_elements[font_name],
                "is_critical": False,
                "exception_type": type(e).__name__,
            }
            validation_results["validation_errors"].append(error_info)

            logger.error(
                f"Pre-validation: Unexpected error validating font '{font_name}' "
                f"for elements {font_to_elements[font_name]} on page {page_idx}: {e}"
            )

    # Log summary
    logger.info(
        f"Pre-validation complete for page {page_idx}: "
        f"{validation_results['successful_validations']}/{validation_results['total_fonts']} fonts validated, "
        f"{validation_results['critical_failures']} critical failures"
    )

    return validation_results


def _render_element(page, element, page_idx, page_overrides, config, use_htmlbox=False):
    """
    Renders a single element on the given page, with comprehensive type handling
    and a robust two-pass, auto-shrinking text rendering strategy.
    Uses ensure_font_registered for per-page font registration.
    Enhanced with pre-rendering font validation.
    """
    effective_params = {"type": element.get("type", "unknown")}
    elem_id = element.get("id", "N/A")

    try:
        elem_type = element.get("type")
        if not elem_type:
            logger.warning(f"Element on page {page_idx}, ID {elem_id} has no 'type'. Skipping.")
            return {"skipped": True, "error": "Element type not specified."}

        rect_coords = element.get("bbox")  # Always use 'bbox' for consistency

        # Handle all vector elements using the new unified function
        if elem_type in ["drawing", "background_drawing_raw", "shape"]:
            render_info = _render_vector_element(page, element)
            effective_params.update(render_info)

        elif elem_type == "text":
            if not (rect_coords := element.get("bbox")):
                logger.warning(f"Skipping text element with no bbox: ID {elem_id}")
                return {"error": "Text element missing bbox."}

            rect_obj = fitz.Rect(rect_coords)
            override_data = page_overrides.get(str(element.get("id")), {})

            text = override_data.get("text", element.get("text", ""))
            font_name_from_element = element.get("font_details", {}).get("name")
            requested_font = override_data.get("font", font_name_from_element or config.get("default_font", "helv"))
            font_size_from_element = element.get("font_details", {}).get("size")
            size = float(override_data.get("size", font_size_from_element or 12.0))
            font_color_from_element = element.get("font_details", {}).get("color")
            color = _convert_color_to_rgb(override_data.get("color", font_color_from_element))

            # Enhanced font registration with comprehensive error handling
            try:
                from pdfrebuilder.font.utils import FontRegistrationError

                actual_font = ensure_font_registered(page, requested_font, verbose=True, text=text)

                # Log font registration details for debugging
                logger.debug(
                    f"Font registration for element '{elem_id}': "
                    f"requested='{requested_font}', actual='{actual_font}', "
                    f"text_length={len(text)}"
                )

                final_kwargs = _render_text_with_fallback(
                    page,
                    rect_obj,
                    text,
                    actual_font,
                    size,
                    color,
                    elem_id,
                    use_textbox=False,
                    use_htmlbox=use_htmlbox,
                )

            except FontRegistrationError as font_error:
                # Critical font error - this should fail the test
                error_msg = (
                    f"Critical font registration error in element '{elem_id}': "
                    f"{font_error}. This indicates a serious font system issue."
                )
                logger.critical(error_msg)

                # Add detailed context to the error
                effective_params.update(
                    {
                        "error": error_msg,
                        "font_error_details": {
                            "requested_font": requested_font,
                            "element_id": elem_id,
                            "text_content": text[:100],
                            "error_context": getattr(font_error, "context", {}),
                            "is_critical": True,
                        },
                    }
                )

                # Re-raise to fail the test
                raise font_error

            except Exception as font_error:
                # Unexpected font-related error
                error_msg = (
                    f"Unexpected font error in element '{elem_id}': {font_error}. "
                    f"Font: '{requested_font}', Text: '{text[:50]}...'"
                )
                logger.error(error_msg)

                # Try to continue with a fallback approach
                try:
                    # Use a guaranteed working font as last resort
                    from pdfrebuilder.font.utils import get_fallback_font_validator

                    validator = get_fallback_font_validator()
                    guaranteed_font = validator.get_guaranteed_working_font()

                    if guaranteed_font:
                        logger.warning(
                            f"Using guaranteed fallback font '{guaranteed_font}' for element '{elem_id}' "
                            f"after font error with '{requested_font}'"
                        )

                        final_kwargs = _render_text_with_fallback(
                            page,
                            rect_obj,
                            text,
                            guaranteed_font,
                            size,
                            color,
                            elem_id,
                            use_textbox=False,
                            use_htmlbox=use_htmlbox,
                        )

                        # Mark as having font issues but continue
                        effective_params["font_fallback_used"] = True
                        effective_params["original_font_error"] = str(font_error)

                    else:
                        # No guaranteed font available - this is critical
                        critical_error = (
                            f"No guaranteed working font available after font error in element '{elem_id}'. "
                            f"This indicates a critical font system failure."
                        )
                        logger.critical(critical_error)
                        effective_params["error"] = critical_error
                        return effective_params

                except Exception as fallback_error:
                    # Even fallback failed - this is definitely critical
                    critical_error = (
                        f"Font fallback also failed for element '{elem_id}': {fallback_error}. "
                        f"Original error: {font_error}"
                    )
                    logger.critical(critical_error)
                    effective_params["error"] = critical_error
                    return effective_params

            effective_params["pymupdf_call"] = "page.insert_htmlbox" if use_htmlbox else "page.insert_text"
            final_kwargs["text_content"] = text
            final_kwargs["rect"] = [rect_obj.x0, rect_obj.y0, rect_obj.x1, rect_obj.y1]
            effective_params["pymupdf_kwargs"] = final_kwargs

        elif elem_type == "image":
            if not (rect_coords := element.get("bbox")):
                logger.warning(f"Skipping image element with no bbox: ID {elem_id}")
                return {"error": "Image element missing bbox."}
            rect_obj = fitz.Rect(rect_coords)

            if (image_file := element.get("image_file")) and os.path.exists(image_file):
                page.insert_image(rect_obj, filename=image_file, overlay=True)
                effective_params.update(
                    {
                        "pymupdf_call": "page.insert_image",
                        "pymupdf_kwargs": {
                            "rect": [rect_obj.x0, rect_obj.y0, rect_obj.x1, rect_obj.y1],
                            "filename": image_file,
                        },
                    }
                )
            else:
                error_msg = f"Image file not found: '{image_file or 'Path not provided'}'."
                logger.warning(f"{error_msg}. Drawing placeholder.")
                page.draw_rect(rect_obj, color=(1, 0, 0), fill=(1, 0, 0), overlay=True)
                effective_params.update({"skipped": True, "error": error_msg})

        else:
            effective_params["error"] = f"Unsupported element type: '{elem_type}'."
            logger.warning(f"Render: {effective_params['error']} on page {page_idx}, ID {elem_id}.")

    except Exception as e:
        effective_params["error"] = str(e)
        logger.error(
            f"Critical Error rendering element ID {elem_id}: {e}\nFull element data: {element}",
            exc_info=True,
        )

    return effective_params
