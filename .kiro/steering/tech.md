# Technology Stack

## Core Technologies

- **Language**: Python 3.8+
- **PDF Processing**: PyMuPDF (fitz) >= 1.26.23
- **Image Processing**: Pillow
- **Configuration**: json5 (for commented JSON overrides)
- **Console Output**: rich (optional, for colored output)

## Development Tools

- **Code Formatting**: black (line-length: 120)
- **Linting & Style Enforcement**: `ruff`
- **Testing**: pytest
- **Package Management & Environments**: [Hatch](https://hatch.pypa.io/) with [uv](https://github.com/astral-sh/uv)

---
**Migration Note:**
> As of June 2025, this project uses Hatch and uv for all environment and dependency management. All previous references to `venv`, `venv_pdf_debug`, and `requirements.txt` are deprecated. Use the instructions below.
---

## Key Dependencies

```
PyMuPDF>=1.26.23
json5
Pillow
rich
```

## Common Commands

### Environment Setup

```bash
# Create and activate the default environment
hatch env create
hatch shell
```

### Running the Application

```bash
# Full pipeline (extract + generate)
hatch run python main.py --input input/sample.pdf

# Extract only
hatch run python main.py --mode extract --input sample.pdf --config layout.json

# Generate only
hatch run python main.py --mode generate --config layout.json --output final.pdf

# Debug mode (layer visualization)
hatch run python main.py --mode debug --config layout.json --debugoutput debug_layers.pdf
```

### Development Commands

```bash
# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Code formatting
hatch run style

# Lint and auto-fix
hatch run lint:lint
```

## Configuration Files

- `layout_config.json`: Main extracted layout data
- `manual_overrides.json5`: Manual corrections (supports comments)
- `pyproject.toml`: Black, ruff, and environment configuration

## PDF Optimization Workflow

- To reduce output PDF file size (especially for large or font-heavy files), run:

  ```bash
  mutool clean -ggg input.pdf output.pdf
  qpdf --linearize input.pdf output.pdf
  ```

- This step is recommended if file size is a limitation in your environment.

## Engine Abstraction & Feature Support

- The codebase will use an engine abstraction (PDFEngineBase) to support multiple PDF backends.
- If a feature is not supported by the engine, a warning will be logged and a best-effort fallback will be attempted.
- All extractable objects should capture rotation if present.
