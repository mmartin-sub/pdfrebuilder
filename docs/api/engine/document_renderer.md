# document_renderer

Document rendering module for the Multi-Format Document Engine

## Classes

### RenderConfig

Configuration for document rendering

#### Methods

##### __init__(output_dpi, output_format, color_space, compression_quality, transparent_background, page_numbers)

### RenderResult

Result of a document rendering operation

#### Methods

##### __init__(success, output_paths, error_message, metadata)

### DocumentRenderer

Abstract base class for document renderers

#### Methods

##### can_render(file_path)

Check if this renderer can handle the given file

Args:
    file_path: Path to the file to check

Returns:
    True if this renderer can handle the file, False otherwise

##### render(file_path, output_dir, config)

Render a document to high-resolution images

Args:
    file_path: Path to the file to render
    output_dir: Directory to save rendered images to
    config: Optional rendering configuration

Returns:
    RenderResult object containing rendering results

### PDFRenderer

PDF document renderer using PyMuPDF (fitz)

#### Methods

##### can_render(file_path)

Check if this renderer can handle the given file

##### render(file_path, output_dir, config)

Render a PDF document to high-resolution images

### PSDRenderer

PSD document renderer using psd-tools and Pillow

#### Methods

##### can_render(file_path)

Check if this renderer can handle the given file

##### render(file_path, output_dir, config)

Render a PSD document to high-resolution images

### RendererRegistry

Registry of document renderers

#### Methods

##### __init__()

##### register(renderer)

Register a renderer

##### get_renderer(file_path)

Get a renderer that can handle the given file

##### render(file_path, output_dir, config)

Render a document using an appropriate renderer

## Functions

### create_renderer_registry()

Create and configure the renderer registry

### render_document(file_path, output_dir, config)

Render a document using an appropriate renderer

Args:
    file_path: Path to the file to render
    output_dir: Directory to save rendered images to
    config: Optional rendering configuration

Returns:
    RenderResult object containing rendering results
