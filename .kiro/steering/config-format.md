# Configuration File Format

## Universal Document Structure Schema (v1.0)

The configuration file contains extracted layout data from various document formats (PDF, PSD, etc.) using a universal schema designed for multi-engine compatibility. The structure supports both paginated documents (PDF) and canvas-based designs (PSD).

### Root Structure

```json
{
  "version": "1.0",
  "engine": "fitz",
  "engine_version": "PyMuPDF 1.26.23",
  "metadata": { /* Document metadata */ },
  "document_structure": [ /* Array of document units */ ]
}
```

### Document Units: Pages vs Canvas

The `document_structure` array contains different types of document units based on the source format:

#### Page-based Documents (PDF, Word, PowerPoint)

- **Type**: `"page"`
- **Characteristics**: Discrete, sequentially ordered, fixed-size areas for viewing/printing
- **Structure**: Multiple page objects for multi-page documents

#### Canvas-based Documents (PSD, Illustrator, Sketch, Figma)

- **Type**: `"canvas"`
- **Characteristics**: Single continuous design area with explicit layer hierarchy
- **Structure**: Typically one canvas object with rich layer organization

### Metadata Object

Contains PDF document properties:

```json
{
  "format": "PDF 1.4",
  "title": "Document Title",
  "author": "Author Name",
  "subject": "Document Subject",
  "keywords": "keyword1,keyword2",
  "creator": "Application Name",
  "producer": "PDF Producer",
  "creationDate": "D:20250717183732+00'00'",
  "modDate": "D:20250717183732+00'00'",
  "trapped": "",
  "encryption": null
}
```

## Document Structure Objects

### Page Object (PDF Engine)

```json
{
  "type": "page",
  "page_number": 0,
  "size": [1058.0, 1688.0],
  "page_background_color": [0.251, 0.239, 0.196],
  "layers": [
    {
      "layer_id": "page_0_base_layer",
      "layer_name": "Page Content",
      "layer_type": "base",
      "bbox": [0, 0, 1058.0, 1688.0],
      "visibility": true,
      "opacity": 1.0,
      "blend_mode": "Normal",
      "children": [],
      "content": [ /* Array of element objects */ ]
    }
  ]
}
```

### Canvas Object (PSD Engine - Future)

```json
{
  "type": "canvas",
  "canvas_size": [1920, 1080],
  "layers": [
    {
      "layer_id": "background_layer",
      "layer_name": "Background",
      "layer_type": "pixel",
      "bbox": [0, 0, 1920, 1080],
      "visibility": true,
      "opacity": 1.0,
      "blend_mode": "Normal",
      "children": [],
      "content": [ /* Layer-specific elements */ ]
    }
  ]
}
```

### Layer Object Structure

All layers (both PDF base layers and PSD layers) follow this structure:

- `layer_id`: Unique identifier for the layer
- `layer_name`: Human-readable layer name
- `layer_type`: Type of layer (`"base"` for PDF, `"pixel"/"text"/"shape"/"group"` for PSD)
- `bbox`: Layer bounding box [x1, y1, x2, y2]
- `visibility`: Whether layer is visible (boolean)
- `opacity`: Layer opacity (0.0-1.0)
- `blend_mode`: How layer blends with layers below
- `children`: Array of child layers (for group layers)
- `content`: Array of elements within this layer

### Element Types

#### Text Elements

```json
{
  "type": "text",
  "bbox": [x1, y1, x2, y2],
  "raw_text": "O r i g i n a l   T e x t",
  "text": "Original Text",
  "font_details": {
    "name": "Arial-Bold",
    "size": 25.48,
    "color": 0,
    "ascender": 18.5,
    "descender": -4.2,
    "is_superscript": false,
    "is_italic": false,
    "is_serif": false,
    "is_monospaced": false,
    "is_bold": true,
    "original_flags": 16
  },
  "writing_mode": 0,
  "writing_direction": [1.0, 0.0],
  "align": 0,
  "adjust_spacing": true,
  "background_color": [0.251, 0.239, 0.196],
  "id": "text_0"
}
```

**Text Element Properties:**

- `bbox`: Bounding box coordinates [left, top, right, bottom]
- `raw_text`: Original text before normalization (preserves spacing issues)
- `text`: Cleaned/normalized text content
- `font_details`: Comprehensive font information object
  - `name`: Font name (may be "Unnamed-T3" for embedded fonts)
  - `size`: Font size in points
  - `color`: Color as integer representing RGB hex
  - `ascender`/`descender`: Font metrics for precise positioning
  - `is_*` flags: Boolean font style indicators
  - `original_flags`: Raw PyMuPDF font flags for full fidelity
- `writing_mode`: Text writing mode (0=horizontal, 1=vertical)
- `writing_direction`: Direction vector [x, y] for text flow
- `align`: Text alignment (0=left, 1=center, 2=right)
- `adjust_spacing`: Whether spacing normalization was applied
- `background_color`: Background color behind text (RGB array or null)

#### Image Elements

```json
{
  "type": "image",
  "image_file": "./images/img_fbc04c5c.jpeg",
  "bbox": [135.36, 132.97, 484.11, 656.47],
  "id": "image_1"
}
```

- `image_file`: Path to extracted image file
- `bbox`: Position and size on page

#### Drawing/Shape Elements (Universal Format)

```json
{
  "type": "drawing",
  "bbox": [690.53, 135.37, 706.26, 154.26],
  "color": null,
  "fill": [0.251, 0.239, 0.196],
  "width": 1.0,
  "drawing_commands": [
    {"cmd": "M", "pts": [690.53, 154.26]},
    {"cmd": "L", "pts": [694.66, 154.26]},
    {"cmd": "C", "pts": [695.38, 152.30, 701.42, 152.30, 702.16, 154.26]},
    {"cmd": "H"},
    {"cmd": "rect", "bbox": [x1, y1, x2, y2]}
  ],
  "original_shape_type": null,
  "stroke_details": null,
  "fill_details": null,
  "id": "drawing_0"
}
```

**Drawing Element Properties:**

- `type`: `"drawing"` for PDF elements, `"shape"` for PSD elements
- `bbox`: Bounding box coordinates [left, top, right, bottom]
- `color`: Stroke color (null if no stroke)
- `fill`: Fill color as RGB array (null if no fill)
- `width`: Stroke width (default 1.0)
- `drawing_commands`: Standardized drawing commands array:
  - `{"cmd": "M", "pts": [x, y]}`: Move to point
  - `{"cmd": "L", "pts": [x, y]}`: Line to point
  - `{"cmd": "C", "pts": [x1, y1, x2, y2, x3, y3]}`: Cubic Bézier curve (control1, control2, end)
  - `{"cmd": "H"}`: Close path
  - `{"cmd": "rect", "bbox": [x1, y1, x2, y2]}`: Rectangle primitive
  - `{"cmd": "ellipse", "bbox": [x1, y1, x2, y2]}`: Ellipse primitive
- `original_shape_type`: Shape hint (`"rectangle"`, `"ellipse"`, `"polygon"`, `"path"`, or null)
- `stroke_details`: Extended stroke properties (rich for PSD, null/basic for PDF)
- `fill_details`: Extended fill properties (rich for PSD, null/basic for PDF)

#### Extended Properties for PSD Compatibility

**Stroke Details Object (PSD):**

```json
{
  "color": "#FF0000",
  "width": 2.5,
  "line_cap": "round",
  "line_join": "miter",
  "miter_limit": 10.0,
  "dashes": [5, 3, 2, 3],
  "alignment": "center"
}
```

**Fill Details Object (PSD):**

```json
{
  "type": "gradient",
  "color": "#FF0000",
  "gradient_info": {
    "type": "linear",
    "angle": 45,
    "stops": [
      {"position": 0.0, "color": "#FF0000"},
      {"position": 1.0, "color": "#0000FF"}
    ]
  },
  "pattern_info": null
}
```

## manual_overrides.json5 Structure

Override file for manual corrections using JSON5 format (supports comments):

### Text Block Overrides

```json5
{
  "text_block_overrides": {
    "block_135_1409": {  // Block ID from coordinates
      "font": "DancingScript-Regular",
      "color": 4209970,
      "text": "Corrected text content"
    }
  }
}
```

### Template Mode

```json5
{
  "use_original_as_template": true,
  // Other overrides...
}
```

### Image and Font Overrides

```json5
{
  "image_bboxes": {
    "image_1_fbc04c5c.jpeg": [270.0, 265.0, 965.0, 1308.0]
  },
  "text_fonts": {
    "Lato-Bold": "Lato-Bold.ttf"
  }
}
```

## Element ID Format

- Text elements: `text_0`, `text_1`, etc.
- Image elements: `image_1`, `image_2`, etc.
- Vector elements: `f_2`, `f_3`, etc.
- Block IDs for overrides: `block_{x}_{y}` (from top-left coordinates)

## Color Formats

- **Integer**: Single integer value (e.g., `0` for black, `4209970` for custom color)
- **RGB Array**: `[red, green, blue]` with values 0.0-1.0
- **Null**: No color/transparent

## Coordinate System

- Origin (0,0) at bottom-left of page
- X increases rightward
- Y increases upward
- All measurements in PDF units (typically 72 units per inch)

## Requirements (Engine Abstraction & Feature Support)

- All extractable objects (text, images, drawings, etc.) should capture rotation (if present) in the JSON.
- If a feature (e.g., rotation) cannot be extracted or reproduced by the engine, the system must log a warning and attempt a best-effort fallback.
- The engine abstraction must provide metadata (engine name, version, supported features) and expose a method to query feature support.
