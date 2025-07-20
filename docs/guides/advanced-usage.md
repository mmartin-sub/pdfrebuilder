# Advanced Usage Guide

This guide covers advanced features of the Multi-Format Document Engine, including multi-format processing, batch operations, custom configurations, and performance optimization.

## Multi-Format Processing

### Current Format Support

The engine currently supports:

- **PDF**: Full extraction and generation support via PyMuPDF (fitz)
- **PSD**: Extraction support in development (Photoshop files)

### PDF Advanced Processing

#### Engine Configuration

The system uses an engine abstraction layer for flexibility:

```python
from src.engine.extract_pdf_content_fitz import FitzPDFEngine

# Initialize engine with custom settings
engine = FitzPDFEngine()

# Check engine capabilities
print(f"Engine: {engine.get_engine_info()['name']}")
print(f"Version: {engine.get_engine_info()['version']}")
print(f"Supported features: {engine.get_supported_features()}")
```

#### Advanced Extraction Options

```bash
# Extract with custom flags
python main.py --mode extract --input complex_document.pdf \
  --extract-text --extract-images --extract-drawings \
  --extract-raw-backgrounds  # Include background elements for debugging
```

#### Custom Output Directories

```bash
# Organize outputs in custom directories
python main.py --input document.pdf \
  --output-dir ./custom_output \
  --test-output-dir ./custom_output/tests \
  --reports-output-dir ./custom_output/reports
```

### PSD Processing (Beta)

PSD support is currently in development. Basic extraction is available:

```python
# Note: PSD support is experimental
try:
    python main.py --mode extract --input design.psd --config psd_layout.json
except NotImplementedError as e:
    print("PSD support is currently being implemented")
```

## Batch Operations

### Batch Text Replacement

Use the BatchModifier for efficient text processing:

```python
from src.engine.batch_modifier import BatchModifier, VariableSubstitution
from src.models.universal_idm import UniversalDocument
import json

# Load document
with open('layout_config.json') as f:
    config = json.load(f)

doc = UniversalDocument.from_dict(config)
modifier = BatchModifier()

# Simple batch replacement
replacements = [
    ('{{company_name}}', 'Acme Corporation'),
    ('{{date}}', '2025-01-15'),
    ('{{amount}}', '$1,234.56')
]

result = modifier.replace_text_batch(doc, replacements)
print(f"Modified {result.modified_elements} elements")
print(f"Skipped {result.skipped_elements} elements")

# Variable substitution with targeting
substitutions = [
    VariableSubstitution(
        variable_name='{{invoice_number}}',
        replacement_value='INV-2025-001',
        page_number=0,  # Only on first page
        case_sensitive=True
    ),
    VariableSubstitution(
        variable_name='{{customer_name}}',
        replacement_value='John Doe',
        element_id='text_5'  # Specific element only
    )
]

result = modifier.substitute_variables(doc, substitutions)
```### Ba
tch Document Processing

Process multiple documents with consistent settings:

```python
import os
import json
from pathlib import Path
from src.engine.document_parser import parse_document
from src.engine.document_renderer import serialize_pdf_content_to_config
from src.engine.extract_pdf_content_fitz import FitzPDFEngine

def batch_process_documents(input_dir, output_dir, template_overrides=None):
    """Process multiple PDFs with consistent settings"""

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Common extraction flags
    extraction_flags = {
        'extract_text': True,
        'extract_images': True,
        'extract_drawings': True,
        'extract_raw_backgrounds': False
    }

    engine = FitzPDFEngine()

    for pdf_file in input_path.glob('*.pdf'):
        print(f"Processing {pdf_file.name}...")

        try:
            # Extract content
            content = parse_document(str(pdf_file), extraction_flags)

            # Save configuration
            config_file = output_path / f"{pdf_file.stem}_config.json"
            serialize_pdf_content_to_config(content, str(config_file))

            # Apply template overrides if provided
            if template_overrides:
                with open(config_file) as f:
                    config = json.load(f)

                # Apply batch modifications here
                # ... (modification logic)

                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)

            # Generate output PDF
            output_pdf = output_path / f"{pdf_file.stem}_processed.pdf"
            with open(config_file) as f:
                config = json.load(f)

            engine.generate(config, str(output_pdf), str(pdf_file))

            print(f"✓ Completed {pdf_file.name}")

        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")

# Usage
batch_process_documents('input/', 'output/batch/')
```

### Template-Based Generation

Create document templates with variable placeholders:

```python
def create_invoice_template(template_config, invoice_data):
    """Generate invoice from template with variable substitution"""

    from src.engine.batch_modifier import BatchModifier
    from src.models.universal_idm import UniversalDocument

    # Load template
    with open(template_config) as f:
        config = json.load(f)

    doc = UniversalDocument.from_dict(config)
    modifier = BatchModifier()

    # Define variable mappings
    variables = [
        ('{{invoice_number}}', invoice_data['invoice_number']),
        ('{{customer_name}}', invoice_data['customer_name']),
        ('{{invoice_date}}', invoice_data['invoice_date']),
        ('{{due_date}}', invoice_data['due_date']),
        ('{{total_amount}}', f"${invoice_data['total_amount']:.2f}"),
    ]

    # Apply substitutions
    result = modifier.replace_text_batch(doc, variables)

    # Validate fonts
    font_result = modifier.validate_fonts(doc)
    if font_result.validation_errors:
        print("Font validation warnings:")
        for warning in font_result.font_warnings:
            print(f"  - {warning}")

    return doc.to_dict()

# Usage
invoice_data = {
    'invoice_number': 'INV-2025-001',
    'customer_name': 'Acme Corp',
    'invoice_date': '2025-01-15',
    'due_date': '2025-02-15',
    'total_amount': 1234.56
}

config = create_invoice_template('invoice_template.json', invoice_data)

# Generate final PDF
from src.engine.extract_pdf_content_fitz import FitzPDFEngine
engine = FitzPDFEngine()
engine.generate(config, 'output/invoice_001.pdf')
```

## Advanced Configuration

### Custom Manual Overrides

Create sophisticated override configurations:

```json5
// manual_overrides.json5
{
  // Use original as pixel-perfect template
  "use_original_as_template": true,

  // Text block overrides with precise targeting
  "text_block_overrides": {
    "block_100_200": {
      "text": "Corrected text content",
      "font": "Arial-Bold",
      "color": 4209970,  // Custom color as integer
      "bbox": [100, 200, 300, 220]  // Adjust positioning
    },
    "block_150_300": {
      "text": "Another correction",
      "font_size": 14.0,
      "adjust_spacing": false  // Preserve original spacing
    }
  },

  // Image positioning overrides
  "image_bboxes": {
    "image_1_abc123.jpeg": [270.0, 265.0, 965.0, 1308.0]
  },

  // Font mapping overrides
  "text_fonts": {
    "ProblematicFont": "Arial.ttf",
    "CustomFont": "downloaded_fonts/custom-font.ttf",
    "Lato-Bold": "Lato-Bold.ttf"
  },

  // Color overrides (RGB arrays)
  "color_overrides": {
    "text_0": [0.0, 0.0, 1.0],  // Blue text
    "drawing_1": [1.0, 0.0, 0.0]  // Red drawing
  },

  // Element visibility overrides
  "visibility_overrides": {
    "text_5": false,  // Hide specific text element
    "image_2": false  // Hide specific image
  }
}
```

### Advanced Extraction Configuration

Configure extraction behavior programmatically:

```python
from src.engine.document_parser import parse_document

# Custom extraction flags
extraction_flags = {
    'extract_text': True,
    'extract_images': True,
    'extract_drawings': True,
    'extract_raw_backgrounds': True,  # Include background elements
    'normalize_text_spacing': True,   # Fix spacing issues
    'preserve_font_metrics': True,    # Keep detailed font info
    'extract_metadata': True,         # Include document metadata
    'image_quality_threshold': 0.8,   # Minimum image quality
    'text_size_threshold': 6.0,       # Minimum text size to extract
}

# Parse with custom settings
content = parse_document('complex_document.pdf', extraction_flags)
```

## Performance Optimization

### Memory Management

Handle large documents efficiently:

```python
import gc
from src.settings import configure_output_directories

def process_large_document(pdf_path, chunk_size=10):
    """Process large documents in chunks to manage memory"""

    import fitz

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    # Process in chunks
    for start_page in range(0, total_pages, chunk_size):
        end_page = min(start_page + chunk_size, total_pages)

        print(f"Processing pages {start_page}-{end_page-1}")

        # Extract chunk
        chunk_config = extract_page_range(doc, start_page, end_page)

        # Process chunk
        process_chunk(chunk_config, start_page)

        # Force garbage collection
        gc.collect()

    doc.close()

def extract_page_range(doc, start_page, end_page):
    """Extract specific page range"""
    # Implementation for page range extraction
    pass
```

### Parallel Processing

Process multiple documents in parallel:

```python
import concurrent.futures
import multiprocessing
from pathlib import Path

def process_single_document(pdf_path):
    """Process a single document"""
    try:
        # Your processing logic here
        result = f"Processed {pdf_path.name}"
        return result
    except Exception as e:
        return f"Error processing {pdf_path.name}: {e}"

def parallel_batch_processing(input_dir, max_workers=None):
    """Process multiple documents in parallel"""

    if max_workers is None:
        max_workers = min(4, multiprocessing.cpu_count())

    input_path = Path(input_dir)
    pdf_files = list(input_path.glob('*.pdf'))

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_file = {
            executor.submit(process_single_document, pdf_file): pdf_file
            for pdf_file in pdf_files
        }

        # Collect results
        for future in concurrent.futures.as_completed(future_to_file):
            pdf_file = future_to_file[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Error with {pdf_file.name}: {e}")

# Usage
parallel_batch_processing('input/', max_workers=4)
```

### Caching and Optimization

Implement caching for repeated operations:

```python
import hashlib
import json
from pathlib import Path

class DocumentCache:
    """Cache for processed documents"""

    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_key(self, pdf_path, extraction_flags):
        """Generate cache key based on file and settings"""
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()

        flags_hash = hashlib.md5(
            json.dumps(extraction_flags, sort_keys=True).encode(), usedforsecurity=False
        ).hexdigest()

        return f"{file_hash}_{flags_hash}.json"

    def get_cached_config(self, pdf_path, extraction_flags):
        """Get cached configuration if available"""
        cache_key = self.get_cache_key(pdf_path, extraction_flags)
        cache_file = self.cache_dir / cache_key

        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def cache_config(self, pdf_path, extraction_flags, config):
        """Cache configuration for future use"""
        cache_key = self.get_cache_key(pdf_path, extraction_flags)
        cache_file = self.cache_dir / cache_key

        with open(cache_file, 'w') as f:
            json.dump(config, f, indent=2)

# Usage
cache = DocumentCache()

def cached_extract(pdf_path, extraction_flags):
    """Extract with caching"""

    # Check cache first
    cached_config = cache.get_cached_config(pdf_path, extraction_flags)
    if cached_config:
        print(f"Using cached configuration for {pdf_path}")
        return cached_config

    # Extract and cache
    print(f"Extracting {pdf_path}")
    content = parse_document(pdf_path, extraction_flags)

    # Convert to config format and cache
    config = content.to_dict()  # Assuming this method exists
    cache.cache_config(pdf_path, extraction_flags, config)

    return config
```## Cust
om Engine Development

### Creating Custom Parsers

Extend the system with custom document parsers:

```python
from src.engine.document_parser import DocumentParserBase
from src.models.universal_idm import UniversalDocument, PageUnit

class CustomFormatParser(DocumentParserBase):
    """Custom parser for a specific document format"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.custom', '.myformat']

    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the file"""
        return any(file_path.lower().endswith(ext) for ext in self.supported_extensions)

    def parse(self, file_path: str, extraction_flags: dict) -> UniversalDocument:
        """Parse the custom format file"""

        # Your custom parsing logic here
        # This is a simplified example

        doc = UniversalDocument(
            version="1.0",
            engine="custom_parser",
            engine_version="1.0.0",
            metadata={
                "title": "Custom Document",
                "format": "Custom Format"
            },
            document_structure=[]
        )

        # Add pages/content based on your format
        page = PageUnit(
            type="page",
            page_number=0,
            size=[612.0, 792.0],
            layers=[]
        )

        doc.document_structure.append(page)
        return doc

    def get_engine_info(self) -> dict:
        """Return engine information"""
        return {
            "name": "CustomFormatParser",
            "version": "1.0.0",
            "supported_formats": self.supported_extensions
        }

# Register custom parser
from src.engine.document_parser import register_parser
register_parser(CustomFormatParser())
```

### Custom Rendering Engines

Create custom output generators:

```python
from src.engine.document_renderer import DocumentRendererBase
from src.models.universal_idm import UniversalDocument

class CustomRenderer(DocumentRendererBase):
    """Custom renderer for specific output formats"""

    def __init__(self):
        super().__init__()
        self.supported_formats = ['.html', '.svg', '.custom']

    def can_render(self, output_format: str) -> bool:
        """Check if this renderer can handle the output format"""
        return any(output_format.lower().endswith(fmt) for fmt in self.supported_formats)

    def render(self, document: UniversalDocument, output_path: str, original_file: str = None):
        """Render document to custom format"""

        # Your custom rendering logic here
        output_content = self.convert_to_custom_format(document)

        with open(output_path, 'w') as f:
            f.write(output_content)

    def convert_to_custom_format(self, document: UniversalDocument) -> str:
        """Convert Universal IDM to custom format"""
        # Implementation specific to your format
        return "<!-- Custom format output -->"

# Register custom renderer
from src.engine.document_renderer import register_renderer
register_renderer(CustomRenderer())
```

## Integration Examples

### REST API Integration

Create a web service wrapper:

```python
from flask import Flask, request, jsonify, send_file
import tempfile
import os
from pathlib import Path

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_document():
    """Extract document content via REST API"""

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        file.save(tmp_file.name)

        try:
            # Extract content
            extraction_flags = request.json.get('extraction_flags', {
                'extract_text': True,
                'extract_images': True,
                'extract_drawings': True
            })

            content = parse_document(tmp_file.name, extraction_flags)
            config = content.to_dict()

            return jsonify({
                'success': True,
                'config': config
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

        finally:
            os.unlink(tmp_file.name)

@app.route('/generate', methods=['POST'])
def generate_document():
    """Generate document from configuration"""

    config = request.json.get('config')
    if not config:
        return jsonify({'error': 'No configuration provided'}), 400

    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        try:
            from src.engine.extract_pdf_content_fitz import FitzPDFEngine
            engine = FitzPDFEngine()
            engine.generate(config, tmp_file.name)

            return send_file(tmp_file.name, as_attachment=True,
                           download_name='generated.pdf')

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### CI/CD Integration

Integrate with continuous integration pipelines:

```yaml
# .github/workflows/document-processing.yml
name: Document Processing Pipeline

on:
  push:
    paths:
      - 'documents/**'
      - 'templates/**'

jobs:
  process-documents:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install hatch
        hatch env create

    - name: Process documents
      run: |
        hatch run python scripts/batch_process.py \
          --input documents/ \
          --output processed/ \
          --template templates/

    - name: Validate outputs
      run: |
        hatch run python scripts/validate_outputs.py processed/

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: processed-documents
        path: processed/
```

### Database Integration

Store and retrieve document configurations:

```python
import sqlite3
import json
from datetime import datetime

class DocumentDatabase:
    """Database for storing document configurations"""

    def __init__(self, db_path='documents.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                config_json TEXT NOT NULL,
                extraction_flags TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_hash ON documents(file_hash)
        ''')

        conn.commit()
        conn.close()

    def store_document(self, filename, file_hash, config, extraction_flags):
        """Store document configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO documents
            (filename, file_hash, config_json, extraction_flags, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            filename,
            file_hash,
            json.dumps(config),
            json.dumps(extraction_flags),
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def get_document(self, file_hash):
        """Retrieve document configuration by hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT config_json FROM documents WHERE file_hash = ?
        ''', (file_hash,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return None

# Usage
db = DocumentDatabase()

# Store processed document
config = {...}  # Your document configuration
db.store_document('document.pdf', 'abc123hash', config, extraction_flags)

# Retrieve later
cached_config = db.get_document('abc123hash')
```

## Troubleshooting Advanced Issues

### Memory Optimization

For very large documents:

```python
import psutil
import gc

def monitor_memory_usage():
    """Monitor memory usage during processing"""
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")

def process_with_memory_management(pdf_path):
    """Process document with memory monitoring"""

    print("Starting processing...")
    monitor_memory_usage()

    # Process document
    content = parse_document(pdf_path, extraction_flags)

    print("After extraction:")
    monitor_memory_usage()

    # Force garbage collection
    gc.collect()

    print("After garbage collection:")
    monitor_memory_usage()

    return content
```

### Performance Profiling

Profile your processing pipeline:

```python
import cProfile
import pstats
from pstats import SortKey

def profile_processing(pdf_path):
    """Profile document processing performance"""

    profiler = cProfile.Profile()
    profiler.enable()

    # Your processing code here
    content = parse_document(pdf_path, extraction_flags)

    profiler.disable()

    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(20)  # Top 20 functions

    return content
```

This advanced usage guide covers the sophisticated features and integration patterns available in the Multi-Format Document Engine. For specific implementation details, refer to the API documentation and source code examples.
