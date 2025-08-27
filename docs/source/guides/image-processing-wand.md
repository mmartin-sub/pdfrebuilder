# Image Processing with Wand

The Multi-Format Document Engine includes a powerful image processing engine based on the [Wand](https://docs.wand-py.org/en/latest/) library, which is a Python binding for the renowned [ImageMagick](https://imagemagick.org/) image processing software. This guide provides a comprehensive overview of how to use the `wand` engine for image extraction and processing.

## Overview

The `wand` engine is designed to handle a wide variety of image formats, with a special focus on complex, layered formats like PSD (Adobe Photoshop Document). It can extract layers, text, and metadata from these files and represent them in the Universal Document Model.

### Key Capabilities

*   **Broad Format Support:** Process a wide range of image formats, including PSD, PSB, TIFF, PNG, JPEG, GIF, and BMP.
*   **Layer Extraction:** Extract individual layers from PSD files, preserving their hierarchy, blend modes, and opacity.
*   **Metadata Extraction:** Extract rich metadata from images, including EXIF and Photoshop-specific information.
*   **Optional OCR:** Use Tesseract OCR to extract text from rasterized text layers.
*   **Image Enhancement:** Apply various image enhancements, such as auto-level, auto-gamma, sharpening, and noise reduction.
*   **Color Management:** Ensure consistent color reproduction with color profile management.

## Installation

The `wand` engine is an optional dependency. To use it, you need to install the `wand` extra and the ImageMagick system library.

### 1. Install ImageMagick

ImageMagick is a system-level dependency. You need to install it on your operating system before installing the `wand` Python library.

**On macOS (using Homebrew):**
```bash
brew install imagemagick
```

**On Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install libmagickwand-dev
```

**On CentOS/RHEL:**
```bash
sudo yum install ImageMagick-devel
```

**On Windows:**
Download and run the installer from the [ImageMagick website](https://imagemagick.org/script/download.php). Make sure to install the "development headers and libraries" and to check the box to "Install legacy utilities (e.g., convert)".

### 2. Install the `wand` extra

Once ImageMagick is installed, you can install the `wand` extra for this project:

```bash
pip install "pdfrebuilder[wand]"
```

Or, if you are using `hatch`:

```bash
hatch run uv sync --extra wand
```

## Using the `wand` Engine

The main function for using the `wand` engine is `extract_wand_content`. This function takes the path to an image file and returns a `UniversalDocument` object.

### Basic Usage

Here's a simple example of how to extract the content of a PSD file:

```python
from pdfrebuilder.engine.extract_wand_content import extract_wand_content, check_wand_availability

# First, check if the wand engine is available
is_available, info = check_wand_availability()

if is_available:
    try:
        # Extract the content of the PSD file
        document = extract_wand_content("path/to/your/image.psd")

        # Now you can work with the document object
        print(f"Extracted {len(document.document_structure)} canvas(es).")
        for canvas in document.document_structure:
            print(f" - Canvas '{canvas.canvas_name}' has {len(canvas.layers)} layers.")

    except (ImportError, FileNotFoundError, RuntimeError) as e:
        print(f"An error occurred: {e}")
else:
    print(f"The wand engine is not available: {info.get('error')}")

```

### OCR (Optical Character Recognition)

The `wand` engine can use Tesseract OCR to extract text from images. This is particularly useful for images that contain rasterized text.

To use this feature, you need to install `pytesseract` and the Tesseract OCR engine.

**1. Install Tesseract OCR:**
Follow the installation instructions for your operating system on the [Tesseract OCR website](https://github.com/tesseract-ocr/tesseract).

**2. Install the `pytesseract` library:**
```bash
pip install pytesseract
```

Once installed, you can enable OCR in the `wand` engine's configuration.

## Configuration

The `wand` engine can be configured through the `[engines.input.wand]` section in your `pdfrebuilder.toml` file or directly in your Python code.

Here are the available configuration options:

| Option | Type | Default | Description |
|---|---|---|---|
| `density` | integer | 300 | The resolution (DPI) for processing images. |
| `use_ocr` | boolean | `False` | Enable or disable OCR for text extraction. |
| `tesseract_lang` | string | `"eng"` | The language to use for OCR (e.g., "eng+fra" for English and French). |
| `image_format` | string | `"png"` | The output format for extracted images (e.g., "png", "jpeg"). |
| `color_management`| boolean | `True` | Enable or disable color profile management. |
| `memory_limit_mb` | integer | 1024 | The memory limit for ImageMagick in megabytes. |
| `enhance_images` | boolean | `False` | Enable or disable image enhancements. |
| `auto_level` | boolean | `False` | Automatically adjust image levels for better contrast. |
| `auto_gamma` | boolean | `False` | Automatically adjust image gamma. |
| `sharpen` | boolean | `False` | Apply a sharpening filter to the image. |
| `noise_reduction`| boolean | `False` | Apply a noise reduction filter to the image. |
| `normalize_colors`| boolean | `False` | Normalize the image's colors. |
| `enhance_contrast`| boolean | `False` | Enhance the image's contrast. |
| `strip_metadata` | boolean | `False` | Strip metadata from the image to reduce file size. |
| `jpeg_quality` | integer | 90 | The quality for JPEG images (1-100). |
| `png_compression`| integer | 95 | The compression level for PNG images (0-100). |
| `webp_quality` | integer | 85 | The quality for WebP images (1-100). |
