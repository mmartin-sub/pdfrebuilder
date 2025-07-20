"""
Configuration management for the Multi-Format Document Engine.

This module provides centralized configuration management with support for dynamic paths,
environment-specific settings, and runtime configuration updates. It manages all system
settings including file paths, font configurations, visual validation thresholds, and
debug options.

Key Features:
- Dynamic path resolution using lambda functions
- Environment-aware configuration
- Centralized configuration dictionary (CONFIG)
- Standard PDF font definitions
- Output directory management

Example:
    from pdfrebuilder.settings import CONFIG, get_config_value, set_config_value

    # Get configuration values
    image_dir = get_config_value('image_dir')

    # Set configuration values
    set_config_value('visual_diff_threshold', 10)
"""

import logging
import os
from typing import Any


class OutputConfig:
    """Configuration class for managing output directories"""

    def __init__(self) -> None:
        self._base_output_dir: str | None = None
        self._test_output_dir: str | None = None
        self._reports_output_dir: str | None = None

    @property
    def base_output_dir(self) -> str:
        """Get the base output directory for all outputs"""
        if self._base_output_dir is None:
            self._base_output_dir = os.path.join(".", "output")
        os.makedirs(self._base_output_dir, exist_ok=True)
        return self._base_output_dir

    @base_output_dir.setter
    def base_output_dir(self, value: str) -> None:
        """Set the base output directory"""
        self._base_output_dir = value
        os.makedirs(self._base_output_dir, exist_ok=True)

    @property
    def test_output_dir(self) -> str:
        """Get the test output directory"""
        if self._test_output_dir is None:
            self._test_output_dir = os.path.join(self.base_output_dir, "tests")
        os.makedirs(self._test_output_dir, exist_ok=True)
        return self._test_output_dir

    @test_output_dir.setter
    def test_output_dir(self, value: str) -> None:
        """Set the test output directory"""
        self._test_output_dir = value
        os.makedirs(self._test_output_dir, exist_ok=True)

    @property
    def reports_output_dir(self) -> str:
        """Get the reports output directory"""
        if self._reports_output_dir is None:
            self._reports_output_dir = os.path.join(self.base_output_dir, "reports")
        os.makedirs(self._reports_output_dir, exist_ok=True)
        return self._reports_output_dir

    @reports_output_dir.setter
    def reports_output_dir(self, value: str) -> None:
        """Set the reports output directory"""
        self._reports_output_dir = value
        os.makedirs(self._reports_output_dir, exist_ok=True)

    @property
    def logs_output_dir(self) -> str:
        """Get the logs output directory"""
        logs_dir = os.path.join(self.base_output_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

    def get_logs_output_path(self, filename: str, subdir: str = "") -> str:
        """Get a full logs output path for a file"""
        if subdir:
            logs_dir = os.path.join(self.logs_output_dir, subdir)
            os.makedirs(logs_dir, exist_ok=True)
        else:
            logs_dir = self.logs_output_dir
        return os.path.join(logs_dir, filename)

    def get_output_path(self, filename: str, subdir: str = "") -> str:
        """Get a full output path for a file"""
        if subdir:
            output_dir = os.path.join(self.base_output_dir, subdir)
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = self.base_output_dir
        return os.path.join(output_dir, filename)

    def get_test_output_path(self, filename: str, subdir: str = "") -> str:
        """Get a full test output path for a file"""
        if subdir:
            output_dir = os.path.join(self.test_output_dir, subdir)
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = self.test_output_dir
        return os.path.join(output_dir, filename)

    def get_report_output_path(self, filename: str, subdir: str = "") -> str:
        """Get a full report output path for a file"""
        if subdir:
            output_dir = os.path.join(self.reports_output_dir, subdir)
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = self.reports_output_dir
        return os.path.join(output_dir, filename)


# Global output configuration instance
output_config = OutputConfig()


def configure_output_directories(
    base_dir: str | None = None,
    test_dir: str | None = None,
    reports_dir: str | None = None,
) -> None:
    """Configure output directories programmatically"""
    if base_dir:
        output_config.base_output_dir = base_dir
    if test_dir:
        output_config.test_output_dir = test_dir
    if reports_dir:
        output_config.reports_output_dir = reports_dir


CONFIG = {
    # Core paths and files
    "image_dir": lambda: output_config.get_output_path("images"),
    "config_path": "./layout_config.json",
    "override_config_path": "./override_config.json5",
    "rebuilt_pdf": lambda: output_config.get_output_path("rebuilt.pdf"),
    "diff_image": lambda: output_config.get_output_path("visual_diff.png"),
    "debug_pdf": lambda: output_config.get_output_path("debug_layers.pdf"),
    # Engine configurations
    "engines": {
        "input": {
            "default": "auto",  # auto, fitz, psd-tools, wand
            "wand": {
                "density": 300,  # DPI for rasterization
                "use_ocr": False,  # Whether to use OCR for text extraction
                "tesseract_lang": "eng",  # OCR language
                "image_format": "png",  # Format for extracted images
                "color_management": True,  # Whether to use color management
                "memory_limit_mb": 1024,  # Memory limit for Wand operations
                "enhance_images": False,  # Whether to apply image enhancements
                "auto_level": False,  # Auto-adjust levels for better contrast
                "auto_gamma": False,  # Auto-adjust gamma correction
                "sharpen": False,  # Apply sharpening filter
                "noise_reduction": False,  # Apply noise reduction
                "normalize_colors": False,  # Normalize color distribution
                "enhance_contrast": False,  # Enhance contrast
                "strip_metadata": False,  # Strip image metadata to reduce size
                "jpeg_quality": 90,  # JPEG compression quality (1-100)
                "png_compression": 95,  # PNG compression quality (1-100)
                "webp_quality": 85,  # WebP compression quality (1-100)
            },
            "psd_tools": {
                "extract_text_layers": True,
                "extract_image_layers": True,
                "extract_shape_layers": True,
                "preserve_layer_effects": True,
            },
            "fitz": {
                "extract_text": True,
                "extract_images": True,
                "extract_drawings": True,
                "extract_raw_backgrounds": False,
            },
        },
        "output": {
            "default": "reportlab",  # reportlab, pymupdf, fitz
            "reportlab": {
                "compression": 1,
                "page_mode": "portrait",
                "embed_fonts": True,
                "color_space": "RGB",
                "output_dpi": 300,
            },
            "pymupdf": {
                "overlay_mode": False,
                "annotation_mode": "ignore",  # preserve, ignore, remove
                "compression": "flate",  # none, flate, lzw
                "embed_fonts": True,
            },
            "fitz": {
                "overlay_mode": False,
                "annotation_mode": "ignore",
                "compression": "flate",
                "embed_fonts": True,
            },
        },
    },
    # Font management configuration
    "font_management": {
        "font_directory": "fonts",
        "downloaded_fonts_dir": "fonts/auto",
        "manual_fonts_dir": "fonts/manual",
        "enable_google_fonts": True,
        "fallback_font": "Noto Sans",
        "cache_file": "fonts/font_cache.json",
        "default_font": "Noto Sans",
    },
    # Visual validation configuration
    "validation": {
        "ssim_threshold": 0.98,
        "rendering_dpi": 300,
        "comparison_engine": "opencv",
        "generate_diff_images": True,
        "fail_on_font_substitution": False,
        "visual_diff_threshold": 5,
        "ssim_score_display_digits": 3,
    },
    # Logging configuration
    "logging": {
        "show_engine_versions": False,  # Only at DEBUG level
        "show_load_paths": False,  # Only at DEBUG level
        "show_python_executable": False,  # Only at DEBUG level
        "engine_selection_level": "INFO",
        "engine_fallback_level": "WARNING",
        "engine_error_level": "ERROR",
    },
    # Debug configuration
    "debug": {
        "font_name": "cour",  # Courier is a great monospaced font for code/JSON
        "fontsize": 8,  # A smaller, more compact font size
        "line_height": 1.2,  # Line height (1.2 = 120% of font size) for good readability
        "max_height_ratio": 0.8,  # Max height the box can take (80% of page) to prevent huge boxes
        "text_wrap_width": 100,  # Character width for manual text wrapping
        "text_padding": 10,  # Padding inside the black box
        "font": "Lato-Regular",
        "overlay_width_ratio": 0.33,  # Use 33% of the page width
        "overlay_bg_color": [0.1, 0.1, 0.1],  # Dark grey background
        "overlay_text_color": [0.95, 0.95, 0.95],  # Off-white text
        "text_background": True,  # Whether to draw a background for the debug text overlay.
        "number_display_digits": 3,  # Maximum number of digits for debug number display in debug statements
        "overlay_margin": 10,  # Margin for the debug text box.
        "overlay_width": 450,  # Fixed width for the debug text box.
        "overlay_height": 180,  # Fixed height for the debug text box.
    },
    # Processing configuration
    "processing": {
        "space_density_threshold": 0.3,
        "max_memory_mb": 2048,
        "enable_parallel_processing": True,
        "temp_dir": lambda: output_config.get_output_path("temp"),
    },
    # Test configuration settings
    "test_output_dir": lambda: output_config.test_output_dir,
    "test_temp_dir": lambda: output_config.get_test_output_path("temp"),
    "test_fonts_dir": lambda: output_config.get_test_output_path("fonts"),
    "test_reports_dir": lambda: output_config.get_test_output_path("reports"),
    "test_sample_dir": lambda: output_config.get_test_output_path("sample"),
    "test_fixtures_dir": lambda: output_config.get_test_output_path("fixtures"),
    "test_debug_dir": lambda: output_config.get_test_output_path("debug"),
    "reports_output_dir": lambda: output_config.reports_output_dir,
    "font_validation_reports_dir": lambda: output_config.get_report_output_path("font_validation"),
    "test_coverage_reports_dir": lambda: output_config.get_report_output_path("test_coverage"),
    "font_validation_demo_reports_dir": lambda: output_config.get_test_output_path("font_validation_demo_reports"),
    "logs_output_dir": lambda: output_config.logs_output_dir,
    "debug_logs_dir": lambda: output_config.get_logs_output_path("debug"),
    # Legacy compatibility (deprecated - use nested config)
    "fonts_dir": "fonts",
    "downloaded_fonts_dir": "fonts/auto",
    "manual_fonts_dir": "fonts/manual",
    "default_font": "Noto Sans",
    "visual_diff_threshold": 5,
    # Test framework configuration
    "test_framework": {
        "cleanup_after_tests": True,
        "preserve_test_outputs": False,
        "generate_test_reports": True,
        "max_test_output_size_mb": 100,
        "test_timeout_seconds": 300,
        "font_test_timeout_seconds": 60,
        "enable_performance_tracking": True,
        "enable_memory_monitoring": True,
        "test_data_retention_days": 7,
    },
    # Test fixture configuration
    "test_fixtures": {
        "auto_cleanup": True,
        "preserve_on_failure": True,
        "create_debug_outputs": True,
        "mock_external_dependencies": True,
        "use_temporary_directories": True,
        "font_fixture_timeout": 30,
    },
    # Test sample data configuration
    "test_samples": {
        "sample_pdfs_dir": "tests/sample/pdfs",
        "sample_fonts_dir": "tests/sample/fonts",
        "sample_configs_dir": "tests/sample/configs",
        "sample_images_dir": "tests/sample/images",
        "create_missing_samples": True,
        "validate_sample_integrity": True,
    },
}


def get_config_value(key: str) -> Any:
    """Get a configuration value, resolving callable values"""
    value = CONFIG.get(key)
    if callable(value):
        return value()
    return value


def get_nested_config_value(path: str, default: Any = None) -> Any:
    """
    Get a nested configuration value using dot notation.

    Args:
        path: Dot-separated path to the config value (e.g., 'engines.input.wand.density')
        default: Default value if path is not found

    Returns:
        The configuration value or default if not found

    Example:
        >>> get_nested_config_value('engines.input.wand.density')
        300
        >>> get_nested_config_value('engines.output.reportlab.compression')
        1
    """
    keys = path.split(".")
    value: Any = CONFIG

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    # Resolve callable values
    if callable(value):
        return value()
    return value


def set_nested_config_value(path: str, value: Any) -> None:
    """
    Set a nested configuration value using dot notation.

    Args:
        path: Dot-separated path to the config value
        value: Value to set

    Example:
        >>> set_nested_config_value('engines.input.wand.density', 600)
        >>> set_nested_config_value('validation.ssim_threshold', 0.95)
    """
    keys = path.split(".")
    config: Any = CONFIG

    # Navigate to the parent dictionary
    for key in keys[:-1]:
        if key not in config:
            config[key] = {}
        config = config[key]

    # Set the final value
    config[keys[-1]] = value


# Standard PDF fonts that don't need to be embedded (valid PyMuPDF names and variants)
STANDARD_PDF_FONTS = [
    "helv",
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-Oblique",
    "Helvetica-BoldOblique",
    "cour",
    "Courier",
    "Courier-Bold",
    "Courier-Oblique",
    "Courier-BoldOblique",
    "tiro",
    "Times-Roman",
    "Times-Bold",
    "Times-Italic",
    "Times-BoldItalic",
    "Symbol",
    "ZapfDingbats",
]


def configure_logging(
    log_file: str | None = None,
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
) -> None:
    """Configure centralized logging for the application.

    Args:
        log_file: Optional path to a log file. If None, logs only to console.
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
        log_format: Format string for log messages.

    Example:
        >>> from pdfrebuilder.settings import configure_logging
        >>> configure_logging("output/app.log", logging.DEBUG)
    """

    handlers: list[logging.StreamHandler | logging.FileHandler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True,  # Override any prior config
    )
