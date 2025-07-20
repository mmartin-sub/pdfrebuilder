# Font Management Scripts

## Essential Font Downloader

The `download_essential_fonts.py` script helps you download high-quality, free fonts for the PDF rebuilder system.

### Quick Start

```bash
# Download all essential fonts
python scripts/download_essential_fonts.py

# Download only high priority fonts (recommended for most users)
python scripts/download_essential_fonts.py --priority high

# List available fonts
python scripts/download_essential_fonts.py --list
```

### Font Priorities

- **High Priority**: Essential fonts for basic functionality
  - Noto Sans (free Helvetica alternative)
  - Open Sans (free Arial alternative)
  - Roboto (modern sans-serif)

- **Medium Priority**: Important fonts for common use cases
  - Source Sans Pro (technical documents)
  - Noto Serif (formal documents)
  - Roboto Mono (code/technical content)

- **Low Priority**: Specialized fonts for specific needs
  - Noto Sans Mono, Lato, Montserrat, Inter

### System Fonts vs Downloaded Fonts

The system prioritizes fonts in this order:

1. **Downloaded fonts** (from Google Fonts) - stored in `fonts/auto/`
2. **System fonts** (if available) - Nimbus Sans, Liberation Sans, DejaVu Sans
3. **PyMuPDF built-in fonts** - helv, tiro, cour
4. **Standard PDF fonts** - Times-Roman, Courier, Symbol, etc.
5. **Non-free fonts** (last resort) - Helvetica, Arial

### Default Font Configuration

The system uses **Noto Sans** as the default font because:

- It's free and available on Google Fonts
- Excellent Unicode support for international text
- Good alternative to Helvetica
- Works well across different document types

### Installation Notes

Some fonts like Nimbus Sans and Liberation Sans are system fonts that come with Linux distributions. If you need these fonts and they're not available, you can install them via your package manager:

```bash
# Ubuntu/Debian
sudo apt install fonts-liberation fonts-dejavu

# Fedora/RHEL
sudo dnf install liberation-fonts dejavu-fonts

# Arch Linux
sudo pacman -S ttf-liberation ttf-dejavu
```

### Troubleshooting

If font downloads fail:

1. Check your internet connection
2. Some fonts may not be available on Google Fonts
3. Use `--verbose` flag to see detailed error messages
4. Try downloading individual priority levels

### Advanced Usage

```bash
# Download to custom directory
python scripts/download_essential_fonts.py --fonts-dir ./my-fonts

# Force redownload existing fonts
python scripts/download_essential_fonts.py --force

# Verbose output for debugging
python scripts/download_essential_fonts.py --verbose
```
