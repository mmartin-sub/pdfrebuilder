# Quick Installation Guide

Choose the installation method that best fits your needs:

## 🚀 Global Tool (Recommended)

Install PDFRebuilder as a global command-line tool:

```bash
# Install uv (if not already installed)
pip install uv

# Install PDFRebuilder globally
uv tool install pdfrebuilder

# Use anywhere
pdfrebuilder --help
```

## ⚡ One-Time Use

Run without installing:

```bash
# Run directly without installing
uvx pdfrebuilder --help
uvx pdfrebuilder --mode extract --input document.pdf
```

## 📚 As Library

Install for use in Python projects:

```bash
# Add to project
uv add pdfrebuilder

# Use in code
python -c "from pdfrebuilder import extract, rebuild"
```

## 🛠️ Development

For contributing or development:

```bash
# Clone repository
git clone <repository-url>
cd pdfrebuilder

# Setup development environment
hatch env create
hatch shell

# Run from source
hatch run python main.py --help
```

## ✅ Verify Installation

Test your installation:

```bash
# Basic test
pdfrebuilder --help

# Generate sample config
pdfrebuilder --generate-config

# Show current settings
pdfrebuilder --show-config

# Run verification script (development)
hatch run python scripts/verify_installation.py
```

## 🆘 Need Help?

- **Full guide**: [INSTALLATION.md](INSTALLATION.md)
- **Troubleshooting**: [guides/troubleshooting.md](guides/troubleshooting.md)
- **Getting started**: [guides/getting-started.md](guides/getting-started.md)

## 📋 Requirements

- Python 3.11+ (3.12 recommended)
- uv package manager (recommended)
- ~50MB disk space for dependencies
