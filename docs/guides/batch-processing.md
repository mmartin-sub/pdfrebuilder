# Batch Processing Guide

This guide covers batch processing capabilities for handling multiple documents efficiently, including batch text replacement, template-based generation, and automated workflows.

## Overview

The Multi-Format Document Engine provides powerful batch processing capabilities through the BatchModifier engine and command-line tools. You can process multiple documents, perform batch text replacements, and generate documents from templates at scale.

## Basic Batch Processing

### Processing Multiple Documents

Process multiple PDFs in a directory:

```bash
#!/bin/bash
# Simple batch processing script

input_dir="input"
output_dir="output/batch"

# Create output directory
mkdir -p "$output_dir"

# Process all PDFs
for pdf in "$input_dir"/*.pdf; do
    if [ -f "$pdf" ]; then
        basename=$(basename "$pdf" .pdf)
        echo "Processing $basename..."

        python main.py \
            --input "$pdf" \
            --output "$output_dir/${basename}_processed.pdf" \
            --config "$output_dir/${basename}_config.json"

        echo "Completed $basename"
    fi
done

echo "Batch processing complete"
```

### Parallel Processing

Process documents in parallel for better performance:

```python
import concurrent.futures
import multiprocessing
from pathlib import Path
import subprocess

def process_single_document(pdf_path, output_dir):
    """Process a single document"""
    try:
        output_path = output_dir / f"{pdf_path.stem}_processed.pdf"
        config_path = output_dir / f"{pdf_path.stem}_config.json"

        # Use subprocess for isolation
        result = subprocess.run([
            'python', 'main.py',
            '--input', str(pdf_path),
            '--output', str(output_path),
            '--config', str(config_path)
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            return f"✓ Successfully processed {pdf_path.name}"
        else:
            return f"✗ Failed to process {pdf_path.name}: {result.stderr}"

    except Exception as e:
        return f"✗ Error processing {pdf_path.name}: {e}"

def parallel_batch_processing(input_dir, output_dir, max_workers=None):
    """Process multiple documents in parallel"""

    if max_workers is None:
        max_workers = min(4, multiprocessing.cpu_count())

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    pdf_files = list(input_path.glob('*.pdf'))

    print(f"Processing {len(pdf_files)} documents with {max_workers} workers...")

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_file = {
            executor.submit(process_single_document, pdf_file, output_path): pdf_file
            for pdf_file in pdf_files
        }

        # Collect results
        for future in concurrent.futures.as_completed(future_to_file):
            pdf_file = future_to_file[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"✗ Error with {pdf_file.name}: {e}")

# Usage
parallel_batch_processing('input/', 'output/batch/', max_workers=4)
```

## Batch Text Replacement

### Using the BatchModifier Engine

The BatchModifier provides sophisticated text replacement capabilities:

```python
from src.engine.batch_modifier import BatchModifier, VariableSubstitution
from src.models.universal_idm import UniversalDocument
import json

def batch_text_replacement(config_path, replacements, output_path):
    """Perform batch text replacement on a document"""

    # Load document configuration
    with open(config_path) as f:
        config = json.load(f)

    doc = UniversalDocument.from_dict(config)
    modifier = BatchModifier()

    # Perform batch replacement
    result = modifier.replace_text_batch(doc, replacements)

    print(f"Batch replacement results:")
    print(f"  Modified elements: {result.modified_elements}")
    print(f"  Skipped elements: {result.skipped_elements}")

    if result.font_warnings:
        print("Font warnings:")
        for warning in result.font_warnings:
            print(f"  - {warning}")

    # Save modified configuration
    modified_config = doc.to_dict()
    with open(output_path, 'w') as f:
        json.dump(modified_config, f, indent=2)

    return result

# Example usage
replacements = [
    ('{{company_name}}', 'Acme Corporation'),
    ('{{date}}', '2025-01-15'),
    ('{{amount}}', '$1,234.56'),
    ('{{customer}}', 'John Doe')
]

result = batch_text_replacement(
    'invoice_template.json',
    replacements,
    'invoice_modified.json'
)
```

### Advanced Variable Substitution

Use targeted variable substitution for precise control:

```python
def advanced_variable_substitution(config_path, substitutions):
    """Perform advanced variable substitution with targeting"""

    with open(config_path) as f:
        config = json.load(f)

    doc = UniversalDocument.from_dict(config)
    modifier = BatchModifier()

    # Create targeted substitutions
    targeted_substitutions = [
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
        ),
        VariableSubstitution(
            variable_name='{{total_amount}}',
            replacement_value='$1,234.56',
            page_number=1,  # Only on second page
            case_sensitive=False
        )
    ]

    # Apply substitutions
    result = modifier.substitute_variables(doc, targeted_substitutions)

    return doc.to_dict(), result

# Usage
modified_config, result = advanced_variable_substitution(
    'complex_template.json',
    substitutions
)
```

## Template-Based Generation

### Creating Document Templates

Create reusable templates with placeholders:

```python
def create_invoice_template():
    """Create an invoice template with placeholders"""

    # Start with a base document
    python main.py --mode extract --input templates/invoice_base.pdf --config invoice_template.json

    # Add placeholders to the extracted configuration
    with open('invoice_template.json') as f:
        config = json.load(f)

    # Replace specific text with placeholders
    placeholders = {
        'Invoice #12345': '{{invoice_number}}',
        'Customer Name': '{{customer_name}}',
        'January 15, 2025': '{{invoice_date}}',
        'February 15, 2025': '{{due_date}}',
        '$1,000.00': '{{total_amount}}',
        'Acme Corp': '{{company_name}}'
    }

    # Apply placeholders
    for page in config['document_structure']:
        for layer in page['layers']:
            for element in layer['content']:
                if element['type'] == 'text':
                    for original, placeholder in placeholders.items():
                        if original in element['text']:
                            element['text'] = element['text'].replace(original, placeholder)

    # Save template
    with open('invoice_template.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("Invoice template created: invoice_template.json")

create_invoice_template()
```

### Generating from Templates

Generate multiple documents from a template:

```python
def generate_from_template(template_path, data_list, output_dir):
    """Generate multiple documents from a template"""

    from src.engine.extract_pdf_content_fitz import FitzPDFEngine

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    engine = FitzPDFEngine()

    for i, data in enumerate(data_list):
        print(f"Generating document {i+1}/{len(data_list)}...")

        # Load template
        with open(template_path) as f:
            template_config = json.load(f)

        doc = UniversalDocument.from_dict(template_config)
        modifier = BatchModifier()

        # Create variable substitutions from data
        substitutions = []
        for key, value in data.items():
            substitutions.append((f'{{{{{key}}}}}', str(value)))

        # Apply substitutions
        result = modifier.replace_text_batch(doc, substitutions)

        # Generate PDF
        output_file = output_path / f"{data.get('filename', f'document_{i+1}')}.pdf"
        modified_config = doc.to_dict()

        engine.generate(modified_config, str(output_file))

        print(f"  Generated: {output_file.name}")
        print(f"  Modified {result.modified_elements} elements")

# Example data
invoice_data = [
    {
        'filename': 'invoice_001',
        'invoice_number': 'INV-2025-001',
        'customer_name': 'John Doe',
        'invoice_date': '2025-01-15',
        'due_date': '2025-02-15',
        'total_amount': '$1,234.56',
        'company_name': 'Acme Corp'
    },
    {
        'filename': 'invoice_002',
        'invoice_number': 'INV-2025-002',
        'customer_name': 'Jane Smith',
        'invoice_date': '2025-01-16',
        'due_date': '2025-02-16',
        'total_amount': '$2,345.67',
        'company_name': 'Acme Corp'
    }
]

generate_from_template('invoice_template.json', invoice_data, 'output/invoices/')
```

## Automated Workflows

### CSV-Driven Document Generation

Generate documents from CSV data:

```python
import csv
from pathlib import Path

def csv_to_documents(csv_path, template_path, output_dir):
    """Generate documents from CSV data"""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Read CSV data
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data_list = list(reader)

    print(f"Processing {len(data_list)} records from {csv_path}")

    # Generate documents
    generate_from_template(template_path, data_list, output_dir)

    print(f"Generated {len(data_list)} documents in {output_dir}")

# Example CSV structure:
# invoice_number,customer_name,invoice_date,due_date,total_amount
# INV-2025-001,John Doe,2025-01-15,2025-02-15,$1234.56
# INV-2025-002,Jane Smith,2025-01-16,2025-02-16,$2345.67

csv_to_documents('invoices.csv', 'invoice_template.json', 'output/batch_invoices/')
```

### Database-Driven Generation

Generate documents from database records:

```python
import sqlite3
import json

def database_to_documents(db_path, query, template_path, output_dir):
    """Generate documents from database records"""

    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()

    # Execute query
    cursor.execute(query)
    records = cursor.fetchall()

    print(f"Processing {len(records)} records from database")

    # Convert records to dictionaries
    data_list = []
    for record in records:
        data = dict(record)
        # Add filename based on record data
        data['filename'] = f"document_{data.get('id', len(data_list))}"
        data_list.append(data)

    # Generate documents
    generate_from_template(template_path, data_list, output_dir)

    conn.close()
    print(f"Generated {len(data_list)} documents")

# Example usage
query = """
SELECT
    invoice_id as invoice_number,
    customer_name,
    invoice_date,
    due_date,
    total_amount
FROM invoices
WHERE status = 'pending'
"""

database_to_documents('invoices.db', query, 'invoice_template.json', 'output/pending_invoices/')
```

## Quality Control and Validation

### Batch Validation

Validate all generated documents:

```python
from src.engine.visual_validator import validate_documents
from src.engine.validation_strategy import ValidationConfig

def batch_validation(original_dir, generated_dir, report_dir):
    """Validate all generated documents against originals"""

    original_path = Path(original_dir)
    generated_path = Path(generated_dir)
    report_path = Path(report_dir)
    report_path.mkdir(exist_ok=True)

    # Validation configuration
    config = ValidationConfig(
        visual_similarity_threshold=0.95,
        text_accuracy_threshold=0.98,
        generate_detailed_report=True
    )

    validation_results = []

    for generated_file in generated_path.glob('*.pdf'):
        # Find corresponding original (if exists)
        original_file = original_path / generated_file.name

        if original_file.exists():
            print(f"Validating {generated_file.name}...")

            try:
                result = validate_documents(
                    str(original_file),
                    str(generated_file),
                    config
                )

                validation_results.append({
                    'filename': generated_file.name,
                    'passed': result.passed,
                    'similarity_score': result.similarity_score,
                    'text_accuracy': result.text_accuracy,
                    'issues': result.validation_issues
                })

                status = "PASSED" if result.passed else "FAILED"
                print(f"  {status} - Similarity: {result.similarity_score:.2%}")

            except Exception as e:
                print(f"  ERROR validating {generated_file.name}: {e}")
                validation_results.append({
                    'filename': generated_file.name,
                    'passed': False,
                    'error': str(e)
                })

    # Generate summary report
    summary_path = report_path / 'validation_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(validation_results, f, indent=2)

    # Print summary
    passed = sum(1 for r in validation_results if r.get('passed', False))
    total = len(validation_results)
    print(f"\nValidation Summary: {passed}/{total} documents passed")

    return validation_results

# Usage
results = batch_validation('originals/', 'output/batch/', 'output/validation_reports/')
```

### Font Validation for Batch

Validate fonts across all documents:

```python
from src.font.font_validator import FontValidator

def batch_font_validation(config_dir):
    """Validate fonts across multiple document configurations"""

    config_path = Path(config_dir)
    validator = FontValidator()

    all_fonts = set()
    font_issues = []

    for config_file in config_path.glob('*.json'):
        print(f"Checking fonts in {config_file.name}...")

        try:
            result = validator.validate_document_fonts(str(config_file))

            # Collect all fonts used
            for font_name in result.fonts_used:
                all_fonts.add(font_name)

            # Collect issues
            if result.font_warnings:
                font_issues.extend([
                    f"{config_file.name}: {warning}"
                    for warning in result.font_warnings
                ])

        except Exception as e:
            font_issues.append(f"{config_file.name}: Error validating fonts - {e}")

    # Report results
    print(f"\nFont Validation Summary:")
    print(f"  Total unique fonts: {len(all_fonts)}")
    print(f"  Documents with issues: {len(font_issues)}")

    if font_issues:
        print("\nFont Issues Found:")
        for issue in font_issues:
            print(f"  - {issue}")

    return all_fonts, font_issues

# Usage
fonts, issues = batch_font_validation('output/batch/')
```

## Performance Optimization

### Memory-Efficient Batch Processing

Handle large batches without memory issues:

```python
import gc
import psutil

def memory_efficient_batch(input_dir, output_dir, batch_size=10):
    """Process documents in memory-efficient batches"""

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    pdf_files = list(input_path.glob('*.pdf'))
    total_files = len(pdf_files)

    print(f"Processing {total_files} files in batches of {batch_size}")

    for i in range(0, total_files, batch_size):
        batch_files = pdf_files[i:i+batch_size]
        batch_num = i // batch_size + 1

        print(f"\nProcessing batch {batch_num} ({len(batch_files)} files)...")

        # Monitor memory before batch
        memory_before = psutil.virtual_memory().percent
        print(f"Memory usage before batch: {memory_before:.1f}%")

        # Process batch
        for pdf_file in batch_files:
            try:
                output_file = output_path / f"{pdf_file.stem}_processed.pdf"

                # Process single file
                subprocess.run([
                    'python', 'main.py',
                    '--input', str(pdf_file),
                    '--output', str(output_file)
                ], check=True, capture_output=True)

                print(f"  ✓ {pdf_file.name}")

            except subprocess.CalledProcessError as e:
                print(f"  ✗ {pdf_file.name}: {e}")

        # Force garbage collection after batch
        gc.collect()

        # Monitor memory after batch
        memory_after = psutil.virtual_memory().percent
        print(f"Memory usage after batch: {memory_after:.1f}%")

        # Optional: pause between batches for memory recovery
        if memory_after > 80:  # If memory usage is high
            print("High memory usage detected, pausing for recovery...")
            time.sleep(5)

# Usage
memory_efficient_batch('input/', 'output/batch/', batch_size=5)
```

### Caching for Repeated Operations

Cache results for efficiency:

```python
import hashlib
import pickle
from pathlib import Path

class BatchProcessingCache:
    """Cache for batch processing operations"""

    def __init__(self, cache_dir='cache/batch'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, pdf_path, operation_type, parameters):
        """Generate cache key for operation"""
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()

        param_hash = hashlib.md5(
            str(sorted(parameters.items())).encode(), usedforsecurity=False
        ).hexdigest()

        return f"{operation_type}_{file_hash}_{param_hash}.cache"

    def get_cached_result(self, pdf_path, operation_type, parameters):
        """Get cached result if available"""
        cache_key = self.get_cache_key(pdf_path, operation_type, parameters)
        cache_file = self.cache_dir / cache_key

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                # Remove corrupted cache file
                cache_file.unlink()

        return None

    def cache_result(self, pdf_path, operation_type, parameters, result):
        """Cache operation result"""
        cache_key = self.get_cache_key(pdf_path, operation_type, parameters)
        cache_file = self.cache_dir / cache_key

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            print(f"Warning: Could not cache result: {e}")

# Usage with caching
cache = BatchProcessingCache()

def cached_batch_processing(input_dir, output_dir):
    """Batch processing with caching"""

    input_path = Path(input_dir)

    for pdf_file in input_path.glob('*.pdf'):
        operation_params = {
            'extract_text': True,
            'extract_images': True,
            'extract_drawings': True
        }

        # Check cache first
        cached_config = cache.get_cached_result(
            str(pdf_file), 'extraction', operation_params
        )

        if cached_config:
            print(f"Using cached extraction for {pdf_file.name}")
            config = cached_config
        else:
            print(f"Extracting {pdf_file.name}")
            # Perform extraction
            content = parse_document(str(pdf_file), operation_params)
            config = content.to_dict()

            # Cache result
            cache.cache_result(
                str(pdf_file), 'extraction', operation_params, config
            )

        # Continue with processing...
```

This batch processing guide provides comprehensive coverage of batch operations, from simple multi-document processing to sophisticated template-based generation and quality control systems.
