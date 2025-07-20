# Logging Guide

This guide explains the logging system in the Multi-Format Document Engine, including how to control output verbosity and access engine version information.

## Log Levels

The application supports standard Python logging levels:

- **ERROR**: Only error messages
- **WARNING**: Warnings and errors
- **INFO**: General information, warnings, and errors (default)
- **DEBUG**: Detailed information including engine versions and paths

## Basic Usage

### Default Behavior (Clean Output)

By default, the application runs at INFO level with clean output to console:

```bash
python main.py --input sample.pdf
```

Output:

```
⚙️  Output directory: ./output
⚙️  Images directory: ./output/images
ℹ️  Entering full mode...
ℹ️  Parsing document: sample.pdf
ℹ️  Using input engine: auto
ℹ️  Using output engine: reportlab
✅ PDF generation complete.
```

### Debug Mode (Detailed Information)

To see engine version information and detailed logging:

```bash
python main.py --log-level DEBUG --input sample.pdf
```

Output:

```
⚙️  Output directory: ./output
⚙️  Images directory: ./output/images
ℹ️  Entering full mode...
ℹ️  Parsing document: sample.pdf
ℹ️  Using input engine: auto
🔧 Input engine selected: auto
DEBUG:engine.pymupdf.init:Initializing pymupdf engine
DEBUG:engine.pymupdf:pymupdf engine version: 1.26.3
DEBUG:engine.pymupdf:pymupdf loaded from: /path/to/fitz
DEBUG:engine.pymupdf:Python executable: /usr/bin/python
ℹ️  Using output engine: reportlab
DEBUG:engine.reportlab.init:Initializing reportlab engine
DEBUG:engine.reportlab:reportlab engine version: 4.4.3
✅ PDF generation complete.
```

### Quiet Mode (Errors Only)

To see only errors:

```bash
python main.py --log-level ERROR --input sample.pdf
```

### Logging to File

To save logs to a file instead of displaying them in the console:

```bash
python main.py --log-file output/logs/app.log --input sample.pdf
```

The log file directory will be created automatically if it doesn't exist. You can combine this with any log level:

```bash
# Debug level logs to file
python main.py --log-level DEBUG --log-file output/logs/debug.log --input sample.pdf

# Error level logs to file for production
python main.py --log-level ERROR --log-file /var/log/pdf-engine/errors.log --input sample.pdf
```

## Engine-Specific Logging

### Engine Selection

Engine selection is always logged at INFO level:

```
INFO:engine.selection:Using pymupdf engine
INFO:engine.selection:Auto-detected reportlab engine
```

### Engine Fallback

When an engine fails and fallback occurs, it's logged at WARNING level:

```
WARNING:engine.fallback:Engine fallback: pymupdf -> reportlab
WARNING:engine.fallback:Fallback reason: PyMuPDF initialization failed
```

### Engine Errors

Engine errors are always logged with version information for troubleshooting:

```
ERROR:engine.pymupdf.error:pymupdf engine error: Failed to create document
ERROR:engine.pymupdf.error:Engine version info: {'engine': 'pymupdf', 'version': '1.26.3', ...}
```

## Version Information

### When Version Info is Displayed

Engine version information is displayed only when:

1. **Log level is DEBUG** - Shows version info for engines being used
2. **Engine errors occur** - Always shows version info for troubleshooting
3. **Engine fallback happens** - Shows version info for both engines

### What Version Info Includes

For each engine, version information includes:

- Engine name and version
- Library version (e.g., PyMuPDF version)
- Load path (where the library is installed)
- Python executable path

Example:

```
DEBUG:engine.pymupdf:pymupdf engine version: 1.26.3
DEBUG:engine.pymupdf:pymupdf loaded from: /home/user/venv/lib/python3.11/site-packages/fitz
DEBUG:engine.pymupdf:Python executable: /home/user/venv/bin/python
```

## Configuration

### Logging Settings

You can configure logging behavior in `src/settings.py`:

```python
CONFIG = {
    "logging": {
        "show_engine_versions": False,      # Only at DEBUG level
        "show_load_paths": False,           # Only at DEBUG level
        "show_python_executable": False,    # Only at DEBUG level
        "engine_selection_level": "INFO",   # Level for engine selection messages
        "engine_fallback_level": "WARNING", # Level for fallback messages
        "engine_error_level": "ERROR",      # Level for error messages
    }
}
```

### Environment Variables

Control logging through environment variables:

```bash
# Override engine logging level
export PDF_ENGINE_LOG_LEVEL=DEBUG

# Force version display
export PDF_ENGINE_SHOW_VERSIONS=true

# Suppress all engine logging
export PDF_ENGINE_QUIET=true
```

## Examples

### Troubleshooting Engine Issues

When experiencing engine problems, use DEBUG level and save to a log file:

```bash
python main.py --log-level DEBUG --log-file troubleshoot.log --input problematic.pdf
```

This will save detailed information to the log file including:

- Which engines are available
- Engine initialization details
- Version information for troubleshooting
- Detailed error messages

### Production/Automated Use

For production or automated workflows, log errors to a file:

```bash
python main.py --log-level ERROR --log-file /var/log/pdf-engine/production.log --input batch_file.pdf
```

This captures only errors in a persistent log file for monitoring.

### Development and Testing

During development, save DEBUG logs to track all activity:

```bash
python main.py --log-level DEBUG --log-file development.log --mode extract --input test.pdf
```

### Batch Processing with Logging

For batch processing, use log files to track progress:

```bash
# Process multiple files with detailed logging
for file in *.pdf; do
    python main.py --log-level INFO --log-file "logs/process_${file%.pdf}.log" --input "$file"
done
```

## Integration with Rich Console

The application uses Rich console when available for enhanced output:

- ✅ Success messages in green
- ❌ Error messages in red
- ⚠️ Warning messages in yellow
- ℹ️ Info messages in blue
- ⚙️ Configuration messages in cyan
- 🔧 Debug messages in dim style

When Rich is not available, it falls back to plain text with emoji prefixes.

## Best Practices

1. **Use INFO level by default** - Provides good balance of information
2. **Use DEBUG for troubleshooting** - Shows engine details when needed
3. **Use WARNING/ERROR for automation** - Reduces noise in scripts
4. **Use log files for production** - Persistent logging for monitoring and debugging
5. **Check engine versions** - Use DEBUG when reporting issues
6. **Monitor fallback messages** - WARNING level shows when engines fail
7. **Organize log files by purpose** - Use descriptive names and directory structure

## Common Scenarios

### "Which engine is being used?"

```bash
python main.py --input file.pdf  # Shows at INFO level
```

### "What version of PyMuPDF is installed?"

```bash
python main.py --log-level DEBUG --input file.pdf  # Shows version details
```

### "Why did my engine fail?"

```bash
python main.py --log-level DEBUG --input file.pdf  # Shows initialization details
```

### "Clean output for scripts"

```bash
python main.py --log-level ERROR --input file.pdf  # Only errors
```

### "Save detailed logs for later analysis"

```bash
python main.py --log-level DEBUG --log-file logs/detailed-$(date +%Y%m%d-%H%M%S).log --input file.pdf
```

### "Production logging with rotation"

```bash
# Log to dated files for easy rotation
python main.py --log-level INFO --log-file /var/log/pdf-engine/$(date +%Y-%m-%d).log --input file.pdf
```
