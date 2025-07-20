# Multi-Format Document Engine API Documentation

This document provides comprehensive API documentation for the Multi-Format Document Engine, including class interfaces, method signatures, and usage examples.

## Core Architecture

The engine follows a modular architecture with clear separation of concerns:

- **Document Parsers**: Format-specific extraction engines
- **Universal IDM**: Format-agnostic document representation
- **Visual Validators**: Automated quality assurance
- **Font Management**: Intelligent font handling
- **Rendering Engines**: Multi-format output generation

## Document Parsing API

### DocumentParser (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from src.models.universal_idm import UniversalDocument

class DocumentParser(ABC):
    """Abstract base class for document parsers"""

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        pass

    @abstractmethod
    def parse(self, file_path: str, extraction_flags: dict[str, bool] = None) -> UniversalDocument:
        """Parse document into Universal IDM"""
        pass

    @abstractmethod
    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        """Extract and save images, fonts, and other assets"""
        pass
```

### PDFParser

```python
from src.engine.document_parser import PDFParser

# Initialize parser
parser = PDFParser()

# Check if file can be parsed
if parser.can_parse("document.pdf"):
    # Parse document
    document = parser.parse("document.pdf", {
        "include_text": True,
        "include_images": True,
        "include_drawings": True,
        "include_raw_background_drawings": False
    })
```

### PSDParser

```python
from src.engine.document_parser import PSDParser

# Initialize parser (requires psd-tools)
parser = PSDParser()

# Parse PSD file
if parser.can_parse("design.psd"):
    document = parser.parse("design.psd", {
        "include_text": True,
        "include_images": True,
        "include_drawings": True
    })
```

### Unified Parsing Interface

```python
from src.engine.document_parser import parse_document

# Automatically selects appropriate parser
document = parse_document("input/file.pdf")  # Uses PDFParser
document = parse_document("input/file.psd")  # Uses PSDParser

# With extraction flags
document = parse_document("input/file.pdf", {
    "include_text": True,
    "include_images": False,
    "include_drawings": True
})
```

## Universal Document Model API

### UniversalDocument

The main document container supporting serialization and deserialization:

```python
from src.models.universal_idm import UniversalDocument, DocumentMetadata

# Create new document
document = UniversalDocument(
    version="1.0",
    engine="fitz",
    engine_version="PyMuPDF 1.26.23",
    metadata=DocumentMetadata(
        format="PDF 1.4",
        title="My Document",
        author="Author Name"
    )
)

# Serialize to JSON
json_str = document.to_json(indent=2)

# Save to file
with open("document.json", "w") as f:
    f.write(json_str)

# Load from JSON
with open("document.json", "r") as f:
    loaded_document = UniversalDocument.from_json(f.read())

# Convert to dictionary
doc_dict = document.to_dict()
```

### Document Structure

#### PageUnit (PDF Documents)

```python
from src.models.universal_idm import PageUnit, Layer, LayerType, BoundingBox

# Create page
page = PageUnit(
    page_number=0,
    size=(1058.0, 1688.0),
    background_color=Color.from_rgb_tuple((0.251, 0.239, 0.196))
)

# Add layer
layer = Layer(
    layer_id="page_0_base_layer",
    layer_name="Page Content",
    layer_type=LayerType.BASE,
    bbox=BoundingBox(0, 0, 1058.0, 1688.0)
)
page.layers.append(layer)
```

#### CanvasUnit (PSD Documents)

```python
from src.models.universal_idm import CanvasUnit, Layer, LayerType

# Create canvas
canvas = CanvasUnit(
    canvas_name="Design Canvas",
    size=(1920.0, 1080.0)
)

# Add layer with hierarchy
group_layer = Layer(
    layer_id="group_1",
    layer_name="Text Group",
    layer_type=LayerType.GROUP,
    bbox=BoundingBox(0, 0, 1920.0, 1080.0)
)

text_layer = Layer(
    layer_id="text_1",
    layer_name="Headline",
    layer_type=LayerType.TEXT,
    bbox=BoundingBox(100, 100, 800, 200),
    opacity=0.9,
    blend_mode=BlendMode.MULTIPLY
)

group_layer.children.append(text_layer)
canvas.layers.append(group_layer)
```

### Element Types

#### TextElement

```python
from src.models.universal_idm import TextElement, FontDetails, Color, BoundingBox

# Create text element
text_element = TextElement(
    id="text_0",
    bbox=BoundingBox(100, 200, 300, 250),
    raw_text="H e l l o   W o r l d",  # Original with spacing issues
    text="Hello World",  # Normalized
    font_details=FontDetails(
        name="Arial-Bold",
        size=24.0,
        color=Color(0, 0, 0, 1),  # Black
        is_bold=True,
        ascender=18.5,
        descender=-4.2
    ),
    align=0,  # Left aligned
    adjust_spacing=True
)

# Convert to dictionary
text_dict = text_element.to_dict()

# Create from dictionary
text_element = TextElement.from_dict(text_dict)
```

#### ImageElement

```python
from src.models.universal_idm import ImageElement, BoundingBox

# Create image element
image_element = ImageElement(
    id="image_1",
    bbox=BoundingBox(135.36, 132.97, 484.11, 656.47),
    image_file="./images/img_fbc04c5c.jpeg",
    original_format="JPEG",
    dpi=300,
    color_space="RGB",
    has_transparency=False
)
```

#### DrawingElement

```python
from src.models.universal_idm import DrawingElement, DrawingCommand, Color, BoundingBox

# Create drawing element
drawing_element = DrawingElement(
    id="drawing_0",
    bbox=BoundingBox(690.53, 135.37, 706.26, 154.26),
    color=Color(0, 0, 0, 1),  # Black stroke
    fill=Color(0.251, 0.239, 0.196, 1),  # Gray fill
    width=1.0,
    drawing_commands=[
        DrawingCommand(cmd="M", pts=[690.53, 154.26]),
        DrawingCommand(cmd="L", pts=[694.66, 154.26]),
        DrawingCommand(cmd="C", pts=[695.38, 152.30, 701.42, 152.30, 702.16, 154.26]),
        DrawingCommand(cmd="H")  # Close path
    ],
    original_shape_type="path"
)
```

## Visual Validation API

### VisualValidator

```python
from src.engine.visual_validator import VisualValidator
from src.engine.validation_strategy import ValidationConfig

# Create validator with custom config
config = ValidationConfig(
    ssim_threshold=0.98,
    rendering_dpi=300,
    generate_diff_images=True
)

validator = VisualValidator(config)

# Validate single document
result = validator.validate(
    original_path="original.pdf",
    generated_path="rebuilt.pdf",
    diff_image_path="diff.png"
)

print(f"SSIM Score: {result.ssim_score}")
print(f"Passed: {result.passed}")
print(f"Details: {result.details}")
```

### ValidationResult

```python
from src.engine.validation_report import ValidationResult

# Access validation results
if result.passed:
    print(f"Validation passed with score: {result.ssim_score:.3f}")
else:
    print(f"Validation failed. Score: {result.ssim_score:.3f}, Threshold: {result.threshold}")
    print(f"Diff image saved to: {result.diff_image_path}")
```

### Batch Validation

```python
from src.engine.visual_validator import batch_validate_documents

# Validate multiple document pairs
document_pairs = [
    ("original1.pdf", "rebuilt1.pdf"),
    ("original2.pdf", "rebuilt2.pdf"),
    ("original3.pdf", "rebuilt3.pdf")
]

report = batch_validate_documents(
    document_pairs=document_pairs,
    output_dir="validation_output",
    report_name="batch_validation",
    config={"ssim_threshold": 0.95}
)

# Access batch results
print(f"Overall success rate: {report.success_rate:.2%}")
for result in report.results:
    print(f"Document: {result.original_path} - Score: {result.ssim_score:.3f}")
```

## Font Management API

### FontManager

```python
from src.font.font_manager import FontManager, FontConfig

# Initialize font manager
config = FontConfig(
    font_directory="./downloaded_fonts",
    download_directory="./downloaded_fonts",
    enable_google_fonts=True,
    fallback_font="Arial",
    cache_file="font_cache.json"
)

font_manager = FontManager(config)

# Register font
success = font_manager.register_font("Arial-Bold", "/path/to/arial-bold.ttf")

# Get font information
font_info = font_manager.get_font("Arial-Bold", "Sample text")
if font_info:
    print(f"Font: {font_info.name}, Path: {font_info.path}")

# Find substitute font
substitute = font_manager.find_substitute("MissingFont", "Sample text")
if substitute:
    print(f"Using substitute: {substitute}")

# Refresh font cache
font_manager.refresh_cache()
```

### Font Discovery

```python
from src.font.font_discovery import FontDiscoveryService

# Initialize discovery service
discovery = FontDiscoveryService()

# Scan directory for fonts
fonts = discovery.scan_directory("./fonts")
print(f"Found {len(fonts)} fonts")

# Search for specific font
font_path = discovery.search_font("Arial-Bold")
if font_path:
    print(f"Found Arial-Bold at: {font_path}")

# Download from Google Fonts
downloaded_path = discovery.download_font("Open Sans")
if downloaded_path:
    print(f"Downloaded Open Sans to: {downloaded_path}")
```

## Document Rendering API

### DocumentRenderer

```python
from src.engine.document_renderer import DocumentRenderer, RenderConfig

# Create render configuration
config = RenderConfig(
    output_dpi=300,
    embed_fonts=True,
    color_space="RGB",
    compression_quality=95
)

# Initialize renderer
renderer = DocumentRenderer()

# Render document
result = renderer.render(
    document=universal_document,
    output_path="output.pdf",
    config=config
)

if result.success:
    print(f"Document rendered successfully to: {result.output_path}")
else:
    print(f"Rendering failed: {result.error_message}")
```

## Error Handling

### Exception Hierarchy

```python
from src.engine.document_parser import DocumentEngineError, ParseError, RenderError

try:
    document = parse_document("invalid_file.pdf")
except ParseError as e:
    print(f"Parse error: {e}")
except DocumentEngineError as e:
    print(f"General engine error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Asset Management

```python
from src.engine.document_parser import AssetManifest

# Create asset manifest
manifest = AssetManifest()

# Add assets
manifest.add_image("./images/logo.png", "logo.png", {"dpi": 300})
manifest.add_font("./fonts/arial.ttf", "Arial", {"weight": "normal"})

# Convert to dictionary
manifest_dict = manifest.to_dict()
print(f"Images: {len(manifest_dict['images'])}")
print(f"Fonts: {len(manifest_dict['fonts'])}")
```

## Configuration and Settings

### System Configuration

```python
from src.settings import CONFIG

# Access configuration values
image_dir = CONFIG["image_dir"]
font_dir = CONFIG["downloaded_fonts_dir"]
ssim_threshold = CONFIG.get("ssim_threshold", 0.98)

# Update configuration
CONFIG["debug_mode"] = True
CONFIG["custom_setting"] = "value"
```

### Validation Configuration

```python
from src.engine.validation_strategy import ValidationConfig

# Create custom validation config
config = ValidationConfig(
    ssim_threshold=0.95,
    rendering_dpi=600,
    comparison_engine="opencv",
    generate_diff_images=True,
    fail_on_font_substitution=False
)
```

## Utility Functions

### File Format Detection

```python
from src.tools import detect_file_format

# Detect file format
format_type = detect_file_format("document.pdf")  # Returns "pdf"
format_type = detect_file_format("design.psd")    # Returns "psd"
```

### Schema Validation

```python
from src.models.universal_idm import validate_schema_version, migrate_schema

# Validate schema version
data = {"version": "1.0", "engine": "fitz"}
is_valid = validate_schema_version(data)

# Migrate schema if needed
migrated_data = migrate_schema(data, target_version="1.0")
```

## Advanced Usage

### Custom Parser Implementation

```python
from src.engine.document_parser import DocumentParser
from src.models.universal_idm import UniversalDocument

class CustomParser(DocumentParser):
    def can_parse(self, file_path: str) -> bool:
        return file_path.lower().endswith('.custom')

    def parse(self, file_path: str, extraction_flags: dict = None) -> UniversalDocument:
        # Custom parsing logic
        document = UniversalDocument(
            engine="custom",
            engine_version="1.0"
        )
        # Add parsing implementation
        return document

    def extract_assets(self, file_path: str, output_dir: str) -> AssetManifest:
        # Custom asset extraction
        return AssetManifest()

# Register custom parser
from src.engine.document_parser import _PARSERS
_PARSERS.append(CustomParser())
```

### Template-Based Generation

```python
from src.models.universal_idm import UniversalDocument

# Load template
with open("template.json", "r") as f:
    template = UniversalDocument.from_json(f.read())

# Modify template content
for unit in template.document_structure:
    for layer in unit.layers:
        for element in layer.content:
            if element.type == "text" and element.id == "title":
                element.text = "New Title"
                element.font_details.size = 32.0

# Generate new document
output_path = "customized_document.pdf"
# Use renderer to create final document
```

This API documentation provides comprehensive coverage of the Multi-Format Document Engine's capabilities, enabling developers to effectively integrate and extend the system for their specific use cases.
