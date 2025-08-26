# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Multi-Format Document Engine.

## Common Issues and Solutions

### Installation Issues

#### Issue: "hatch: command not found"

**Symptoms**: Cannot run hatch commands
**Solution**:

```bash
# Install hatch using pip
pip install hatch

# Or using pipx (recommended)
pipx install hatch

# Verify installation
hatch --version
```

#### Issue: "uv: command not found"

**Symptoms**: Fast dependency resolution not working
**Solution**:

```bash
# Install uv
pip install uv

# Or follow installation guide
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

#### Issue: Python version compatibility

**Symptoms**: "Python 3.8+ required" errors
**Solution**:

```bash
# Check Python version
python --version

# Use pyenv to install correct version
pyenv install 3.10.0
pyenv local 3.10.0

# Recreate environment
hatch env prune
hatch env create
```

### Document Processing Issues

#### Issue: "Cannot open PDF file"

**Symptoms**: File not found or permission errors
**Diagnosis**:

```bash
# Check file exists and permissions
ls -la input/your-file.pdf

# Test with a simple PDF
python main.py --input input/sample.pdf --mode extract
```

**Solutions**:

- Verify file path is correct
- Check file permissions (readable)
- Ensure PDF is not corrupted
- Try with a different PDF file

#### Issue: "Font not found" warnings

**Symptoms**: Missing fonts in output, text rendering issues
**Diagnosis**:

```python
# Check available fonts
python -c "
import fitz
doc = fitz.open('input/your-file.pdf')
fonts = set()
for page in doc:
    for block in page.get_text('dict')['blocks']:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    fonts.add(span['font'])
print('Fonts used:', fonts)
"
```

**Solutions**:

```bash
# 1. Let the system download fonts automatically
python main.py --input your-file.pdf

# 2. Manually add fonts to downloaded_fonts/
cp /path/to/font.ttf downloaded_fonts/

# 3. Use font overrides in manual_overrides.json5
{
  "text_fonts": {
    "ProblematicFont": "Arial.ttf"
  }
}
```

#### Issue: Layout differences in output

**Symptoms**: Text positioning, spacing, or formatting differs from original
**Diagnosis**:

```python
# Use debug mode to visualize layers
python main.py --mode debug --config layout_config.json --debugoutput debug.pdf

# Compare visually
python -m src.compare_pdfs_visual original.pdf output.pdf --output comparison.pdf
```

**Solutions**:

1. **Use template mode**:

   ```json5
   // In manual_overrides.json5
   {
     "use_original_as_template": true
   }
   ```

2. **Adjust text positioning**:

   ```json5
   {
     "text_block_overrides": {
       "block_100_200": {
         "bbox": [100, 200, 300, 220]
       }
     }
   }
   ```

3. **Fix spacing issues**:

   ```json5
   {
     "text_block_overrides": {
       "block_100_200": {
         "adjust_spacing": false
       }
     }
   }
   ```

### Configuration Issues

#### Issue: Invalid JSON in configuration files

**Symptoms**: JSON parsing errors
**Diagnosis**:

```bash
# Validate JSON syntax
python -c "import json; json.load(open('layout_config.json'))"

# For JSON5 files
python -c "import json5; json5.load(open('manual_overrides.json5'))"
```

**Solutions**:

- Use a JSON validator or linter
- Check for trailing commas, missing quotes
- Validate with online JSON validators

#### Issue: Configuration not taking effect

**Symptoms**: Changes in manual_overrides.json5 not applied
**Diagnosis**:

```bash
# Check file is being read
python main.py --mode generate --config layout_config.json --output test.pdf --verbose
```

**Solutions**:

- Ensure manual_overrides.json5 is in the same directory
- Check JSON5 syntax is valid
- Verify override keys match extracted elements

### Performance Issues

#### Issue: Slow processing of large documents

**Symptoms**: Long processing times, high memory usage
**Diagnosis**:

```bash
# Profile memory usage (install memory_profiler first)
pip install memory_profiler
python -m memory_profiler main.py --input large_document.pdf

# Time the process
time python main.py --input large_document.pdf

# Check document complexity
python -c "
import fitz
doc = fitz.open('large_document.pdf')
print(f'Pages: {doc.page_count}')
print(f'File size: {doc.metadata.get(\"filesize\", \"unknown\")}')
for i, page in enumerate(doc):
    if i < 3:  # Check first 3 pages
        text_blocks = len(page.get_text('dict')['blocks'])
        images = len(page.get_images())
        drawings = len(page.get_drawings())
        print(f'Page {i}: {text_blocks} text blocks, {images} images, {drawings} drawings')
doc.close()
"
```

**Solutions**:

1. **Process in batches**:

   ```python
   # Process pages in chunks
   import fitz

   def process_in_chunks(pdf_path, chunk_size=10):
       doc = fitz.open(pdf_path)
       total_pages = doc.page_count

       for start in range(0, total_pages, chunk_size):
           end = min(start + chunk_size, total_pages)
           print(f"Processing pages {start}-{end-1}")

           # Extract chunk to separate file
           chunk_doc = fitz.open()
           for page_num in range(start, end):
               chunk_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

           chunk_path = f"temp_chunk_{start}_{end}.pdf"
           chunk_doc.save(chunk_path)
           chunk_doc.close()

           # Process chunk
           python main.py --input chunk_path --output f"output/chunk_{start}_{end}.pdf"

           # Clean up
           import os
           os.remove(chunk_path)

       doc.close()
   ```

2. **Use template mode for complex documents**:

   ```json5
   // manual_overrides.json5
   {
     "use_original_as_template": true
   }
   ```

3. **Optimize extraction flags**:

   ```bash
   # Extract only what you need
   python main.py --mode extract --input large.pdf \
     --extract-text --no-extract-images --no-extract-drawings
   ```

4. **Reduce image quality**:

   ```python
   # In your processing script
   extraction_flags = {
       'extract_images': True,
       'image_quality_threshold': 0.5,  # Lower quality threshold
       'max_image_size': (1024, 1024)   # Resize large images
   }
   ```

#### Issue: Memory errors with large documents

**Symptoms**: "MemoryError" or system freezing
**Diagnosis**:

```python
# Monitor memory usage
import psutil
import os

def check_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Current memory usage: {memory_mb:.2f} MB")

    # System memory
    system_memory = psutil.virtual_memory()
    print(f"System memory: {system_memory.percent}% used")
    print(f"Available: {system_memory.available / 1024 / 1024:.2f} MB")

check_memory()
```

**Solutions**:

1. **Increase system memory** or use a machine with more RAM

2. **Process in smaller chunks**:

   ```python
   import gc

   def memory_efficient_processing(pdf_path):
       # Process one page at a time
       doc = fitz.open(pdf_path)

       for page_num in range(doc.page_count):
           print(f"Processing page {page_num + 1}")

           # Process single page
           single_page_doc = fitz.open()
           single_page_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

           # Save and process
           temp_path = f"temp_page_{page_num}.pdf"
           single_page_doc.save(temp_path)
           single_page_doc.close()

           # Process the single page
           # ... your processing logic here ...

           # Clean up
           os.remove(temp_path)
           gc.collect()  # Force garbage collection

       doc.close()
   ```

3. **Use streaming processing**:

   ```bash
   # Set memory limits
   export PYTHONHASHSEED=0
   ulimit -v 2097152  # Limit virtual memory to 2GB

   python main.py --input large.pdf --output output.pdf
   ```

4. **Optimize Python settings**:

   ```bash
   # Use Python with optimizations
   python -O main.py --input large.pdf

   # Or set memory-related environment variables
   export PYTHONMALLOC=malloc
   export MALLOC_ARENA_MAX=2
   ```

### Import and Module Issues

#### Issue: "ModuleNotFoundError" for src modules

**Symptoms**: Cannot import project modules
**Diagnosis**:

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify you're in hatch environment
which python
```

**Solutions**:

```bash
# Ensure you're in the hatch environment
hatch shell

# Install in development mode
hatch run pip install -e .

# Add src to Python path temporarily
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Issue: "ImportError" for dependencies

**Symptoms**: Missing required packages
**Solutions**:

```bash
# Reinstall dependencies
hatch env prune
hatch env create

# Install specific missing package
hatch run pip install missing-package

# Check installed packages
hatch run pip list
```

### Visual Validation Issues

#### Issue: Visual comparison shows differences

**Symptoms**: Comparison PDF highlights many differences, validation fails
**Diagnosis**:

```bash
# Generate detailed comparison with verbose output
python -m src.compare_pdfs_visual original.pdf recreated.pdf \
  output/detailed_comparison.png --verbose

# Check validation metrics
python -c "
from src.engine.visual_validator import validate_documents
from src.engine.validation_strategy import ValidationConfig

config = ValidationConfig(
    visual_similarity_threshold=0.95,
    generate_detailed_report=True,
    debug_mode=True
)

result = validate_documents('original.pdf', 'recreated.pdf', config)
print(f'Similarity score: {result.similarity_score:.2%}')
print(f'Text accuracy: {result.text_accuracy:.2%}')
print(f'Font similarity: {result.font_similarity:.2%}')
print(f'Issues found: {len(result.validation_issues)}')

for issue in result.validation_issues:
    print(f'  - {issue}')
"
```

**Solutions**:

1. **Adjust comparison threshold**:

   ```python
   # More lenient comparison
   python -m src.compare_pdfs_visual original.pdf recreated.pdf output/comparison.png --threshold 0.90

   # Or configure in validation_config.json
   {
     "validation_thresholds": {
       "visual_similarity": 0.90,
       "pixel_difference": 0.10,
       "text_accuracy": 0.95
     }
   }
   ```

2. **Use template mode** for pixel-perfect reproduction:

   ```json5
   // manual_overrides.json5
   {
     "use_original_as_template": true
   }
   ```

3. **Check font rendering** differences:

   ```python
   # Analyze font issues
   from src.font.font_validator import FontValidator

   validator = FontValidator()
   result = validator.validate_document_fonts('layout_config.json')

   for warning in result.font_warnings:
       print(f"Font issue: {warning}")
   ```

4. **Ignore minor differences**:

   ```json
   {
     "validation_options": {
       "ignore_minor_spacing": true,
       "ignore_font_hinting": true,
       "ignore_compression_artifacts": true,
       "color_tolerance": 15,
       "position_tolerance": 3.0
     }
   }
   ```

#### Issue: Specific elements causing validation failures

**Symptoms**: Validation fails on specific text or image elements
**Diagnosis**:

```python
# Debug specific elements
python main.py --mode debug --config layout_config.json --debugoutput debug_layers.pdf

# Check element-specific issues
python -c "
import json
with open('layout_config.json') as f:
    config = json.load(f)

# Find problematic elements
for page in config['document_structure']:
    for layer in page['layers']:
        for element in layer['content']:
            if element['type'] == 'text':
                print(f\"Text element {element['id']}: '{element['text'][:50]}...'\"")
                if 'font_details' in element:
                    font = element['font_details']
                    print(f\"  Font: {font.get('name', 'Unknown')} {font.get('size', 'Unknown')}pt\")
"
```

**Solutions**:

1. **Override specific elements**:

   ```json5
   // manual_overrides.json5
   {
     "text_block_overrides": {
       "block_100_200": {
         "text": "Corrected text",
         "font": "Arial-Bold",
         "color": 0
       }
     },
     "visibility_overrides": {
       "problematic_element_id": false  // Hide problematic elements
     }
   }
   ```

2. **Fix font issues**:

   ```json5
   {
     "text_fonts": {
       "ProblematicFont": "Arial.ttf",
       "MissingFont": "downloaded_fonts/replacement.ttf"
     }
   }
   ```

3. **Adjust element positioning**:

   ```json5
   {
     "text_block_overrides": {
       "block_150_300": {
         "bbox": [150, 300, 350, 320],  // Correct positioning
         "adjust_spacing": false
       }
     }
   }
   ```

### Debug Mode Issues

#### Issue: Debug PDF not generated

**Symptoms**: No debug output file created, debug mode fails silently
**Diagnosis**:

```bash
# Check permissions and disk space
df -h
ls -la output/

# Run with verbose output and logging
python main.py --mode debug --config layout_config.json \
  --debugoutput output/debug.pdf --log-level DEBUG

# Check if config file is valid
python -c "
import json
try:
    with open('layout_config.json') as f:
        config = json.load(f)
    print('Config file is valid JSON')
    print(f'Document has {len(config.get(\"document_structure\", []))} pages')
except Exception as e:
    print(f'Config file error: {e}')
"
```

**Solutions**:

1. **Ensure output directory exists**:

   ```bash
   mkdir -p output
   chmod 755 output
   ```

2. **Check available disk space**:

   ```bash
   # Check disk space
   df -h .

   # Clean up if needed
   rm -rf output/temp_*
   rm -rf images/temp_*
   ```

3. **Verify configuration file**:

   ```python
   # Validate and fix config
   import json

   with open('layout_config.json') as f:
       config = json.load(f)

   # Check required fields
   required_fields = ['version', 'engine', 'document_structure']
   for field in required_fields:
       if field not in config:
           print(f"Missing required field: {field}")

   # Check document structure
   if 'document_structure' in config:
       for i, page in enumerate(config['document_structure']):
           if 'layers' not in page:
               print(f"Page {i} missing layers")
   ```

4. **Run with error handling**:

   ```python
   # Debug with error handling
   try:
       from src.generate_debug_pdf_layers import generate_debug_pdf_layers
       generate_debug_pdf_layers('layout_config.json', 'output/debug.pdf')
       print("Debug PDF generated successfully")
   except Exception as e:
       print(f"Debug generation failed: {e}")
       import traceback
       traceback.print_exc()
   ```

#### Issue: Debug PDF shows unexpected content

**Symptoms**: Debug layers don't match expected content, missing elements
**Diagnosis**:

```python
# Analyze debug content
import json

with open('layout_config.json') as f:
    config = json.load(f)

print("Debug Analysis:")
for page_idx, page in enumerate(config['document_structure']):
    print(f"Page {page_idx}:")
    print(f"  Size: {page.get('size', 'Unknown')}")
    print(f"  Layers: {len(page.get('layers', []))}")

    for layer_idx, layer in enumerate(page.get('layers', [])):
        content = layer.get('content', [])
        print(f"  Layer {layer_idx} ({layer.get('layer_name', 'Unnamed')}):")
        print(f"    Content elements: {len(content)}")

        # Count element types
        element_types = {}
        for element in content:
            elem_type = element.get('type', 'unknown')
            element_types[elem_type] = element_types.get(elem_type, 0) + 1

        for elem_type, count in element_types.items():
            print(f"      {elem_type}: {count}")
```

**Solutions**:

1. **Check extraction flags**:

   ```bash
   # Re-extract with all content types
   python main.py --mode extract --input original.pdf \
     --extract-text --extract-images --extract-drawings \
     --extract-raw-backgrounds
   ```

2. **Verify element IDs**:

   ```python
   # Check for duplicate or missing IDs
   import json

   with open('layout_config.json') as f:
       config = json.load(f)

   all_ids = []
   for page in config['document_structure']:
       for layer in page['layers']:
           for element in layer['content']:
               if 'id' in element:
                   all_ids.append(element['id'])

   # Check for duplicates
   duplicates = [id for id in set(all_ids) if all_ids.count(id) > 1]
   if duplicates:
       print(f"Duplicate IDs found: {duplicates}")
   ```

3. **Regenerate configuration**:

   ```bash
   # Start fresh with clean extraction
   rm layout_config.json
   rm -rf images/
   rm -rf downloaded_fonts/

   python main.py --mode extract --input original.pdf
   python main.py --mode debug --config layout_config.json --debugoutput debug.pdf
   ```

### Batch Processing Issues

#### Issue: Batch operations fail on some documents

**Symptoms**: Some documents in batch fail to process, inconsistent results
**Diagnosis**:

```python
# Test batch processing with error handling
import os
from pathlib import Path

def diagnose_batch_issues(input_dir):
    input_path = Path(input_dir)

    for pdf_file in input_path.glob('*.pdf'):
        print(f"Testing {pdf_file.name}...")

        try:
            # Test basic operations
            import fitz
            doc = fitz.open(str(pdf_file))

            print(f"  Pages: {doc.page_count}")
            print(f"  Encrypted: {doc.is_encrypted}")
            print(f"  PDF version: {doc.pdf_version()}")

            # Test first page
            if doc.page_count > 0:
                page = doc[0]
                text_blocks = len(page.get_text('dict')['blocks'])
                images = len(page.get_images())
                print(f"  First page: {text_blocks} text blocks, {images} images")

            doc.close()
            print(f"  ✓ {pdf_file.name} appears processable")

        except Exception as e:
            print(f"  ✗ {pdf_file.name} has issues: {e}")

diagnose_batch_issues('input/')
```

**Solutions**:

1. **Handle problematic documents**:

   ```python
   def robust_batch_processing(input_dir, output_dir):
       input_path = Path(input_dir)
       output_path = Path(output_dir)
       output_path.mkdir(exist_ok=True)

       success_count = 0
       error_count = 0

       for pdf_file in input_path.glob('*.pdf'):
           try:
               print(f"Processing {pdf_file.name}...")

               # Pre-check document
               import fitz
               doc = fitz.open(str(pdf_file))

               if doc.is_encrypted:
                   print(f"  Skipping encrypted document: {pdf_file.name}")
                   doc.close()
                   continue

               if doc.page_count == 0:
                   print(f"  Skipping empty document: {pdf_file.name}")
                   doc.close()
                   continue

               doc.close()

               # Process document
               output_file = output_path / f"{pdf_file.stem}_processed.pdf"

               # Use subprocess for isolation
               import subprocess
               result = subprocess.run([
                   'python', 'main.py',
                   '--input', str(pdf_file),
                   '--output', str(output_file)
               ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

               if result.returncode == 0:
                   print(f"  ✓ Successfully processed {pdf_file.name}")
                   success_count += 1
               else:
                   print(f"  ✗ Failed to process {pdf_file.name}")
                   print(f"    Error: {result.stderr}")
                   error_count += 1

           except subprocess.TimeoutExpired:
               print(f"  ✗ Timeout processing {pdf_file.name}")
               error_count += 1
           except Exception as e:
               print(f"  ✗ Error processing {pdf_file.name}: {e}")
               error_count += 1

       print(f"\nBatch processing complete:")
       print(f"  Successful: {success_count}")
       print(f"  Failed: {error_count}")
   ```

2. **Skip problematic documents**:

   ```python
   def is_document_processable(pdf_path):
       """Check if document can be processed"""
       try:
           import fitz
           doc = fitz.open(pdf_path)

           # Basic checks
           if doc.is_encrypted:
               return False, "Document is encrypted"

           if doc.page_count == 0:
               return False, "Document has no pages"

           if doc.page_count > 1000:
               return False, "Document too large (>1000 pages)"

           # Test first page extraction
           page = doc[0]
           page.get_text('dict')

           doc.close()
           return True, "Document appears processable"

       except Exception as e:
           return False, f"Error checking document: {e}"

   # Use in batch processing
   processable, reason = is_document_processable('document.pdf')
   if not processable:
       print(f"Skipping document: {reason}")
   ```

#### Issue: Inconsistent results across batch

**Symptoms**: Same document type produces different results, quality varies
**Solutions**:

1. **Standardize processing settings**:

   ```python
   # Create standard configuration
   STANDARD_EXTRACTION_FLAGS = {
       'extract_text': True,
       'extract_images': True,
       'extract_drawings': True,
       'extract_raw_backgrounds': False,
       'normalize_text_spacing': True,
       'image_quality_threshold': 0.8
   }

   # Use consistent settings for all documents
   def standardized_processing(pdf_path, output_path):
       content = parse_document(pdf_path, STANDARD_EXTRACTION_FLAGS)
       # ... rest of processing
   ```

2. **Validate results consistently**:

   ```python
   # Standard validation for all outputs
   STANDARD_VALIDATION_CONFIG = ValidationConfig(
       visual_similarity_threshold=0.95,
       text_accuracy_threshold=0.98,
       font_similarity_threshold=0.90
   )

   def validate_batch_output(original_path, recreated_path):
       result = validate_documents(original_path, recreated_path, STANDARD_VALIDATION_CONFIG)
       return result.passed, result.similarity_score
   ```

## Diagnostic Tools

### System Information

```bash
# Check system info
python -c "
import sys
import platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
"

# Check dependencies
hatch run pip list | grep -E "(PyMuPDF|Pillow|json5)"
```

### Configuration Validation

```bash
# Validate configuration files
python -m src.tools.schema_tools validate-config layout_config.json

# Check manual overrides
python -c "
import json5
try:
    with open('manual_overrides.json5') as f:
        config = json5.load(f)
    print('Manual overrides valid')
except Exception as e:
    print(f'Error: {e}')
"
```

### Log Analysis

```bash
# Enable verbose logging
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python main.py --input document.pdf --verbose 2>&1 | tee processing.log

# Search for specific errors
grep -i error processing.log
grep -i warning processing.log
```

## Getting Additional Help

### Documentation Resources

1. **API Documentation**: [docs/api/](../api/)
2. **Architecture Guide**: [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
3. **Configuration Reference**: [docs/reference/configuration.md](../reference/configuration.md)

### Community Support

1. **GitHub Issues**: Report bugs and request features
2. **Discussions**: Ask questions and share solutions
3. **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

### Creating Bug Reports

When reporting issues, include:

1. **System Information**:

   ```bash
   python --version
   hatch --version
   uv --version
   ```

2. **Error Messages**: Full error output and stack traces

3. **Minimal Reproduction**: Smallest example that reproduces the issue

4. **Configuration Files**: Relevant configuration (sanitized)

5. **Expected vs Actual**: What you expected vs what happened

### Performance Profiling

```python
# Profile CPU usage
python -m cProfile -o profile.stats main.py --input document.pdf
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"

# Profile memory usage
pip install memory-profiler
python -m memory_profiler main.py --input document.pdf
```

## Prevention Tips

### Best Practices

1. **Test with small documents first**
2. **Keep backups of working configurations**
3. **Use version control for configuration files**
4. **Monitor system resources during processing**
5. **Validate configurations before processing**

### Regular Maintenance

```bash
# Clean up temporary files
find . -name "*.tmp" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Update dependencies periodically
hatch env prune
hatch env create

# Run tests to ensure everything works
hatch run test
```

## Known Test-time Warnings

### `PytestCollectionWarning` for `TestFileManager`

- **Problem**: You may see a `PytestCollectionWarning` for a class like `TestFileManager` in `tests/wip/unit/test_utils.py`. This happens if a test class has an `__init__` constructor, which prevents pytest from collecting it as a test class.
- **Analysis**: In our case, `TestFileManager` is a helper class for managing test files, not a test class itself. The warning is correct.
- **Solution**: The class was renamed to `_TestFileManager` to prevent pytest collection. If you encounter a similar issue, ensure that your test classes do not have an `__init__` constructor, and that any helper classes that are not tests are prefixed with an underscore to be ignored by the test collector.
- **Bibliography**: [Pytest good practices - Test discovery](https://docs.pytest.org/en/stable/explanation/goodpractices.html#test-discovery)

### `Not a TrueType or OpenType font (bad sfntVersion)` warnings

- **Problem**: Several tests in `tests/font/` may log warnings about being unable to read mock font files.
- **Analysis**: These warnings are expected. The tests in `tests/font/test_font_cache_integration.py` and other font tests are intentionally creating invalid font files with dummy content to test the error handling capabilities of the font management system. The warnings indicate that the system is correctly identifying these invalid font files.
- **Action**: To make the tests more explicit and to suppress the warnings from the test output, you can use `pytest.warns` to assert that these warnings are raised. This has been implemented for some tests, and the general test configuration has been updated to suppress these warnings from the console output during test runs.
- **Bibliography**: [pytest.warns documentation](https://docs.pytest.org/en/stable/how-to/capture-warnings.html#asserting-that-a-warning-was-raised)

### `Error: Could not fetch CSS for ...` warnings

- **Problem**: Several tests related to Google Fonts integration may log errors about failing to fetch CSS.
- **Analysis**: This can happen if a test calls `ensure_font_registered` with a font name that is not a valid Google Font (e.g., "Arial"). The call to `download_google_font` will then make a real network request that fails, triggering the warning. The test is not properly mocking the network call.
- **Solution**: The tests that were causing this issue have been patched to prevent the network requests. If you are writing a new test that involves font registration, ensure that you patch `download_google_font` if you are not testing the download functionality itself.
- **Bibliography**: [unittest.mock.patch](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch)

### `'cmap'` and `'name'` key errors in font tests

- **Problem**: Some font tests may log key errors when trying to access `cmap` or `name` attributes of a font object.
- **Analysis**: This happens when integration tests create dummy font files with invalid content. When `fontTools` tries to parse these files, it creates a `TTFont` object that is missing some tables, like `'cmap'` and `'name'`. When the code under test tries to access these tables, it raises a `KeyError`.
- **Solution**: The tests that were causing this issue have been patched to use a mock `TTFont` object that is correctly configured with the necessary attributes. This prevents the `KeyError` and the associated warnings.
- **Bibliography**: [fontTools documentation](https://fonttools.readthedocs.io/en/latest/)

Remember: Most issues can be resolved by carefully reading error messages and checking the basics (file paths, permissions, environment setup).
