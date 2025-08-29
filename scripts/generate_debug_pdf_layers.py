import json
import logging
import os
import textwrap

import fitz
import json5

from pdfrebuilder.core.render import _render_element, json_serializer
from pdfrebuilder.settings import settings

UNFINDABLE_FONT_NAMES = {"Unnamed-T3"}


### FIX: Modified to produce compact, single-line JSON as you suggested ###
def _create_summarized_json(data_dict):
    """Creates a summarized, compact, single-line JSON string."""
    if not isinstance(data_dict, dict):
        return str(data_dict)
    summary_dict = {}
    for key, value in data_dict.items():
        if key == "items" and isinstance(value, list) and len(value) > 10:
            summary_dict[key] = f"[... long list of {len(value)} vector coordinates ...]"
        else:
            summary_dict[key] = value
    # indent=None creates the compact string
    return json.dumps(summary_dict, indent=None, default=json_serializer)


def _wrap_text(text_block, width):
    """Manually wraps a block of text to a specified character width."""
    wrapped_lines = []
    for line in text_block.split("\n"):
        # This handles both pre-existing newlines and wraps very long lines
        wrapped_lines.extend(textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False))
    return "\n".join(wrapped_lines)


# Add logger setup
logger = logging.getLogger(__name__)


def generate_debug_pdf_layers(config_path, output_debug_pdf_base):
    """
    Creates a debug PDF using a fixed-size box and manually wrapped text for maximum compatibility.
    Now supports both 'pages' and 'document_structure' as the root key.
    Logs statistics and errors for unrecognized structures.
    """
    logger.info("--- Running Layer-by-Layer Debugging Tool ---")
    try:
        with open(config_path) as f:
            config_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"ERROR: Could not read or parse config file '{config_path}': {e}")
        return

    # --- Support both 'pages' and 'document_structure' as root keys ---
    if "pages" in config_data:
        pages = config_data["pages"]
        logger.info(f"Config uses 'pages' key. Number of pages: {len(pages)}")
    elif "document_structure" in config_data:
        pages = config_data["document_structure"]
        logger.info(f"Config uses 'document_structure' key. Number of pages: {len(pages)}")
    else:
        logger.error(f"Unrecognized config structure. Top-level keys: {list(config_data.keys())}")
        return

    # --- Log statistics: number of pages, layers, elements ---
    total_layers = 0
    total_elements = 0
    for page in pages:
        page_layers = page.get("layers", [])
        total_layers += len(page_layers)
        for layer in page_layers:
            total_elements += len(layer.get("content", []))
    logger.info(f"Config statistics: pages={len(pages)}, layers={total_layers}, elements={total_elements}")

    overrides = {}
    if os.path.exists(settings.override_config_path):
        try:
            with open(settings.override_config_path) as f_override:
                overrides = json5.load(f_override)
        except Exception as e:
            logger.error(f"Error decoding overrides file '{settings.override_config_path}': {e}")
            return

    debug_doc: fitz.Document = fitz.open()

    for source_page_idx, page_data in enumerate(pages):
        logger.info(f"Generating debug pages for source page {source_page_idx} ...")
        page_overrides = overrides.get("text_block_overrides", {}).get(str(source_page_idx), {})
        page_size = page_data.get("size", (595, 842))
        # For each layer in the page
        for layer in page_data.get("layers", []):
            for element_idx, element in enumerate(layer.get("content", [])):
                debug_page = debug_doc.new_page(width=page_size[0], height=page_size[1])  # type: ignore[attr-defined]
                effective_params = _render_element(debug_page, element, source_page_idx, page_overrides, settings)
                debug_font_name = settings.debug.font_name
                debug_fontsize = settings.debug.fontsize
                debug_line_height = settings.debug.line_height
                wrap_width = settings.debug.text_wrap_width
                debug_text_unwrapped = (
                    f"Source Page {source_page_idx} / Element Index {element_idx} (ID: {element.get('id', 'N/A')})\n"
                    f"Type: {element.get('type', 'N/A')}\n\n"
                    "--- JSON Source (compact) ---\n"
                    f"{_create_summarized_json(element)}\n\n"
                    "--- PyMuPDF Effective Call (compact) ---\n"
                    f"{_create_summarized_json(effective_params)}"
                )
                final_text_to_render = _wrap_text(debug_text_unwrapped, width=wrap_width)
                debug_text_margin = 10
                page_width, page_height = debug_page.rect.width, debug_page.rect.height

                rect_height = page_height / 3  # Use exactly 1/3 of the page height
                rect_y_start = page_height - rect_height - debug_text_margin

                text_rect = fitz.Rect(
                    debug_text_margin,
                    rect_y_start,
                    page_width - debug_text_margin,
                    page_height - debug_text_margin,
                )

                # --- Step 3: Draw the background and insert the pre-wrapped text ---
                debug_page.draw_rect(
                    text_rect,
                    fill=(0.1, 0.1, 0.1),
                    fill_opacity=0.8,
                    overlay=True,
                    width=0,
                )

                debug_page.insert_textbox(
                    text_rect,
                    final_text_to_render,
                    fontsize=debug_fontsize,
                    fontname=debug_font_name,
                    lineheight=debug_line_height,
                    color=(0.95, 0.95, 0.95),
                    align=fitz.TEXT_ALIGN_LEFT,
                    overlay=True,
                )

                logger.debug(f"Debug page added for Element {element_idx}.")

    try:
        debug_doc.save(output_debug_pdf_base, garbage=4, deflate=True)
        logger.info(f"Consolidated debug PDF saved to: {output_debug_pdf_base}")
    except Exception as e:
        logger.error(f"Failed to save the final PDF. Reason: {e}")
    finally:
        if debug_doc:
            debug_doc.close()
