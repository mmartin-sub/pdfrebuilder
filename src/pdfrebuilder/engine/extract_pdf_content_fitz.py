import hashlib
import logging
import os
import traceback
from collections import Counter

import pymupdf as fitz

from pdfrebuilder.models.universal_idm import (
    BlendMode,
    BoundingBox,
    Color,
    DocumentMetadata,
    DrawingCommand,
    DrawingElement,
    FontDetails,
    ImageElement,
    Layer,
    LayerType,
    PageUnit,
    TextElement,
    UniversalDocument,
)
from pdfrebuilder.settings import settings
from pdfrebuilder.tools import normalize_text_spacing

logger = logging.getLogger(__name__)


# NOTE: All fitz-based extraction logic has been moved to FitzPDFEngine.extract() in src/pdf_engine.py.
# This file should only contain utility functions if needed, or can be removed if redundant.


def _process_image_block(block, image_dir, element_id):
    """Processes an image block, saves the image, and returns an ImageElement."""
    try:
        img_bytes = block["image"]
        # Replace MD5 with SHA-256 for more secure hashing
        img_hash = hashlib.sha256(img_bytes).hexdigest()
        path = os.path.join(image_dir, f"img_{img_hash[:8]}.{block['ext']}")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(img_bytes)

        bbox = BoundingBox.from_list(list(block["bbox"]))
        return ImageElement(
            id=element_id,
            bbox=bbox,
            image_file=path,
            original_format=block.get("ext", "unknown"),
        )
    except Exception as e:
        logger.error(f"❌ Error processing image: {e}")
        traceback.print_exc()
        return None


def _process_text_block(block, space_density_threshold, element_id_counter):
    """Processes a text block and returns a list of TextElement objects."""
    text_elements = []
    try:
        for line in block.get("lines", []):
            line_wmode = line.get("wmode")
            line_dir = line.get("dir")

            for span in line.get("spans", []):
                raw_text = span.get("text", "")
                if not raw_text.strip():
                    continue

                clean_text, needs_spacing = normalize_text_spacing(raw_text, space_density_threshold)

                font_flags = span.get("flags", 0)

                # Convert color from integer to Color object
                color_int = span["color"]
                if isinstance(color_int, int):
                    # Convert from integer RGB to normalized RGB
                    r = ((color_int >> 16) & 0xFF) / 255.0
                    g = ((color_int >> 8) & 0xFF) / 255.0
                    b = (color_int & 0xFF) / 255.0
                    color = Color(r, g, b)
                else:
                    color = Color(0, 0, 0)  # Default to black

                font_details = FontDetails(
                    name=span["font"],
                    size=span["size"],
                    color=color,
                    ascender=span.get("ascender", 0),
                    descender=span.get("descender", 0),
                    is_superscript=bool(font_flags & 1),
                    is_italic=bool(font_flags & 2),
                    is_serif=bool(font_flags & 4),
                    is_monospaced=bool(font_flags & 8),
                    is_bold=bool(font_flags & 16),
                    original_flags=font_flags,
                )

                bbox = BoundingBox.from_list(list(span["bbox"]))
                element_id = f"text_{element_id_counter[0]}"
                element_id_counter[0] += 1

                text_element = TextElement(
                    id=element_id,
                    bbox=bbox,
                    raw_text=raw_text,
                    text=clean_text,
                    font_details=font_details,
                    writing_mode=line_wmode,
                    writing_direction=tuple(line_dir) if line_dir else (1.0, 0.0),
                    align=0,
                    adjust_spacing=needs_spacing,
                    background_color=None,  # This will be filled in later
                )
                text_elements.append(text_element)
    except (KeyError, IndexError) as e:
        logger.warning(f"⚠️ Warning: Skipping malformed text block/span. Error: {e}")

    return text_elements


def _process_drawing(drawing, drawing_idx):
    """Processes a drawing and returns a DrawingElement."""
    # DEBUG: Log the full drawing dict and rect
    logger.debug(f"[DRAWING EXTRACTION] drawing_idx={drawing_idx} drawing dict: {drawing}")
    logger.debug(f"[DRAWING EXTRACTION] drawing_idx={drawing_idx} drawing.get('rect'): {drawing.get('rect')}")
    # Convert drawing commands
    drawing_commands = []
    for item in drawing.get("items", []):
        cmd = item[0]
        pts = list(item[1:])

        if cmd == "m":
            drawing_commands.append(DrawingCommand(cmd="M", pts=pts))
        elif cmd == "l":
            drawing_commands.append(DrawingCommand(cmd="L", pts=pts))
        elif cmd == "c":
            drawing_commands.append(DrawingCommand(cmd="C", pts=pts))
        elif cmd == "h":
            drawing_commands.append(DrawingCommand(cmd="H"))
        elif cmd == "re":
            # Handle both [Rect, ...] and [x0, y0, x1, y1]
            if (
                len(pts) == 1
                and hasattr(pts[0], "x0")
                and hasattr(pts[0], "y0")
                and hasattr(pts[0], "x1")
                and hasattr(pts[0], "y1")
            ):
                rect = pts[0]
                drawing_commands.append(
                    DrawingCommand(
                        cmd="rect",
                        bbox=BoundingBox(rect.x0, rect.y0, rect.x1, rect.y1),
                    )
                )
            elif len(pts) == 4 and all(isinstance(p, int | float) for p in pts):
                rect = fitz.Rect(*pts)
                drawing_commands.append(
                    DrawingCommand(
                        cmd="rect",
                        bbox=BoundingBox(rect.x0, rect.y0, rect.x1, rect.y1),
                    )
                )
            else:
                logger.warning(f"Skipping malformed rectangle drawing due to invalid coordinates: {pts}")

    # If no drawing_commands were found, but a valid bbox exists, add a default rect command
    rect = drawing.get("rect")
    # Accept fitz.Rect as well as list/tuple
    if rect:
        if hasattr(rect, "x0") and hasattr(rect, "y0") and hasattr(rect, "x1") and hasattr(rect, "y1"):
            rect_list = [rect.x0, rect.y0, rect.x1, rect.y1]
        elif isinstance(rect, list | tuple) and len(rect) == 4 and all(isinstance(x, int | float) for x in rect):
            rect_list = list(rect)
        else:
            logger.error(
                f"[DRAWING EXTRACTION] drawing_idx={drawing_idx} rect is not a valid list/tuple or fitz.Rect: {rect} (type: {type(rect)})"
            )
            rect_list = None
        if rect_list:
            drawing_commands.append(
                DrawingCommand(
                    cmd="rect",
                    bbox=BoundingBox.from_list(rect_list),
                )
            )

    # Create stroke and fill colors
    stroke_color = Color.from_rgb_tuple(drawing.get("color")) if drawing.get("color") else None
    fill_color = Color.from_rgb_tuple(drawing.get("fill")) if drawing.get("fill") else None

    # Create drawing element
    bbox_val = drawing.get("rect", [])
    if hasattr(bbox_val, "x0") and hasattr(bbox_val, "y0") and hasattr(bbox_val, "x1") and hasattr(bbox_val, "y1"):
        bbox_val = [bbox_val.x0, bbox_val.y0, bbox_val.x1, bbox_val.y1]
    elif not (
        isinstance(bbox_val, list | tuple) and len(bbox_val) == 4 and all(isinstance(x, int | float) for x in bbox_val)
    ):
        logger.error(
            f"[DRAWING EXTRACTION] drawing_idx={drawing_idx} bbox for DrawingElement is not valid: {bbox_val} (type: {type(bbox_val)})"
        )
        bbox_val = [0.0, 0.0, 0.0, 0.0]
    return DrawingElement(
        id=f"drawing_{drawing_idx}",
        bbox=BoundingBox.from_list(list(bbox_val)),
        z_index=drawing_idx,
        color=stroke_color,
        fill=fill_color,
        width=drawing.get("width", 1.0),
        drawing_commands=drawing_commands,
    )


def extract_pdf_content(pdf_path, extraction_flags=None):
    """
    Extracts all content from a PDF, organizing it by page and a default 'base' layer for reconstruction.

    This version uses the Universal IDM classes to create a structured document representation
    with full support for layer hierarchies and complex element types.

    Returns:
        UniversalDocument: A complete document object with all extracted content
    """
    if extraction_flags is None:
        extraction_flags = {
            "include_text": True,
            "include_images": True,
            "include_drawings": True,
            "include_raw_background_drawings": False,
        }

    try:
        doc: fitz.Document = fitz.open(pdf_path)
    except RuntimeError as e:
        raise ValueError(f"Could not open or parse PDF file at '{pdf_path}': {e}")

    # Get engine info
    # engine_info = get_engine_info("fitz") # This line is removed as per the edit hint.

    # Create document metadata
    pdf_metadata = doc.metadata or {}
    metadata = DocumentMetadata(
        format="PDF",
        title=pdf_metadata.get("title"),
        author=pdf_metadata.get("author"),
        subject=pdf_metadata.get("subject"),
        keywords=pdf_metadata.get("keywords"),
        creator=pdf_metadata.get("creator"),
        producer=pdf_metadata.get("producer"),
        creation_date=pdf_metadata.get("creationDate"),
        modification_date=pdf_metadata.get("modDate"),
    )

    # Create the Universal Document
    universal_doc = UniversalDocument(
        version="1.0",  # Placeholder, as engine_info is removed
        engine="fitz",  # Placeholder, as engine_info is removed
        engine_version="1.0",  # Placeholder, as engine_info is removed
        metadata=metadata,
        document_structure=[],
    )

    image_dir = settings.image_dir or "images"
    space_density_threshold = settings.processing.space_density_threshold

    for page_num in range(doc.page_count):
        logger.info(f"Extraction progress: Processing page {page_num + 1}/{doc.page_count}")
        page: fitz.Page = doc[page_num]

        # Create a new page unit
        page_unit = PageUnit(
            page_number=page_num,
            size=(page.rect.width, page.rect.height),
            background_color=None,  # Will be set later if detected
            layers=[],
        )

        # Get raw content from the page
        raw_blocks = (
            page.get_text("dict").get("blocks", [])  # type: ignore[attr-defined]
            if (extraction_flags.get("include_text", True) or extraction_flags.get("include_images", True))
            else []
        )
        raw_drawings = page.get_drawings() if extraction_flags.get("include_drawings", True) else []

        logger.debug(f"[EXTRACTION] page {page_num}: raw_drawings = {raw_drawings}")

        # Track background colors and filled rectangles
        page_bg_color_candidates: Counter[tuple[float, float, float]] = Counter()
        filled_rects = [d for d in raw_drawings if d.get("type") == "f" and d.get("fill")]

        # Create the base layer for this page
        base_layer = Layer(
            layer_id=f"page_{page_num}_base_layer",
            layer_name="Page Content",
            layer_type=LayerType.BASE,
            bbox=BoundingBox(0, 0, page.rect.width, page.rect.height),
            visibility=True,
            opacity=1.0,
            blend_mode=BlendMode.NORMAL,
            children=[],
            content=[],
        )

        # --- Z-Order Strategy for PDF Base Layer ---
        # Process drawings first
        for drawing_idx, drawing in enumerate(raw_drawings):
            if drawing.get("used_for_background", False):
                continue  # Skip if already used for text background

            drawing_element = _process_drawing(drawing, drawing_idx)
            base_layer.content.append(drawing_element)

        # Process text and image blocks
        element_id_counter = [0]  # Use a list to allow modification in nested functions
        temp_text_elements = []

        for block in raw_blocks:
            if block.get("type") == 0 and extraction_flags.get("include_text", True):
                # Process text blocks but hold them for background detection
                processed_texts = _process_text_block(block, space_density_threshold, element_id_counter)
                temp_text_elements.extend(processed_texts)

            elif block.get("type") == 1 and extraction_flags.get("include_images", True):
                # Process and add image blocks
                image_id = f"image_{element_id_counter[0]}"
                element_id_counter[0] += 1
                image_element = _process_image_block(block, image_dir, image_id)
                if image_element:
                    base_layer.content.append(image_element)

        # Apply background detection to text elements
        raw_background_drawings: list[DrawingElement] = []
        for text_elem in temp_text_elements:
            text_rect = fitz.Rect(text_elem.bbox.to_list())
            for rect_draw in filled_rects:
                if not rect_draw.get("used_for_background"):
                    bg_rect = fitz.Rect(rect_draw["rect"])
                    intersection_area = (text_rect & bg_rect).get_area()  # type: ignore[attr-defined]
                    if text_rect.contains(bg_rect) or intersection_area > (text_rect.get_area() * 0.8):  # type: ignore[attr-defined]
                        # Set background color for text
                        if rect_draw.get("fill"):
                            text_elem.background_color = Color.from_rgb_tuple(rect_draw["fill"])

                        rect_draw["used_for_background"] = True
                        page_bg_color_candidates[tuple(rect_draw["fill"])] += 1

                        # If raw background drawings are to be included
                        if extraction_flags.get("include_raw_background_drawings", False):
                            bg_drawing_id = f"bg_drawing_{len(raw_background_drawings)}"
                            bg_rect_list = [bg_rect.x0, bg_rect.y0, bg_rect.x1, bg_rect.y1]
                            bg_drawing_cmd = DrawingCommand(cmd="rect", bbox=BoundingBox.from_list(bg_rect_list))
                            bg_drawing = DrawingElement(
                                id=bg_drawing_id,
                                bbox=BoundingBox.from_list(bg_rect_list),
                                color=None,
                                fill=(Color.from_rgb_tuple(rect_draw["fill"]) if rect_draw.get("fill") else None),
                                drawing_commands=[bg_drawing_cmd],
                            )
                            raw_background_drawings.append(bg_drawing)
                        break

        # Add text elements to the base layer
        base_layer.content.extend(temp_text_elements)

        # Add raw background drawings if requested
        if extraction_flags.get("include_raw_background_drawings", False) and raw_background_drawings:
            base_layer.content.extend(raw_background_drawings)

        # Set page background color if detected
        if page_bg_color_candidates:
            most_common_color = page_bg_color_candidates.most_common(1)[0][0]
            page_unit.background_color = Color.from_rgb_tuple(most_common_color)

        # Add the base layer to the page
        page_unit.layers.append(base_layer)

        # Add the page to the document
        universal_doc.document_structure.append(page_unit)

    logger.info(f"✅ Extraction complete: {doc.page_count} pages processed with Universal IDM structure.")
    doc.close()

    return universal_doc
