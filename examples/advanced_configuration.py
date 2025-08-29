#!/usr/bin/env python3
"""
Example script demonstrating advanced configuration options.
Shows how to configure engines for different use cases.
"""

import json
import os
from typing import Any

from pdfrebuilder.settings import settings


def show_current_configuration():
    """Display the current configuration"""

    print("=== Current Configuration ===\n")

    # Engine configurations
    print("Input Engines:")
    for engine, config in settings.engines.input.model_dump().items():
        if engine != "default":
            print(f"  {engine}:")
            for key, value in config.items():
                print(f"    {key}: {value}")

    print(f"\nDefault Input Engine: {settings.engines.input.default}")

    print("\nOutput Engines:")
    for engine, config in settings.engines.output.model_dump().items():
        if engine != "default":
            print(f"  {engine}:")
            for key, value in config.items():
                print(f"    {key}: {value}")

    print(f"\nDefault Output Engine: {settings.engines.output.default}")

    # Other important configurations
    print("\nFont Management:")
    for key, value in settings.font_management.model_dump().items():
        print(f"  {key}: {value}")

    print("\nValidation Settings:")
    for key, value in settings.validation.model_dump().items():
        print(f"  {key}: {value}")


def create_high_performance_config():
    """Create a configuration optimized for high performance"""

    print("\n=== High Performance Configuration ===\n")

    config = {
        "engines": {
            "input": {
                "default": "wand",
                "wand": {
                    "density": 300,
                    "memory_limit_mb": 2048,
                    "color_management": True,
                    "use_ocr": False,  # Disable OCR for speed
                },
                "fitz": {
                    "extract_text": True,
                    "extract_images": True,
                    "extract_drawings": True,
                    "extract_raw_backgrounds": False,
                },
            },
            "output": {
                "default": "pymupdf",
                "pymupdf": {
                    "overlay_mode": False,
                    "compression": "flate",
                    "embed_fonts": True,
                },
                "reportlab": {"compression": 1, "output_dpi": 300, "embed_fonts": True},
            },
        },
        "processing": {"enable_parallel_processing": True, "max_memory_mb": 4096},
        "validation": {
            "ssim_threshold": 0.95,  # Slightly lower for speed
            "rendering_dpi": 300,
            "generate_diff_images": False,  # Disable for speed
        },
    }

    print("High Performance Configuration:")
    print(json.dumps(config, indent=2))

    return config


def create_quality_focused_config():
    """Create a configuration optimized for quality"""

    print("\n=== Quality Focused Configuration ===\n")

    config = {
        "engines": {
            "input": {
                "default": "psd-tools",  # Better layer fidelity
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
                    "extract_raw_backgrounds": True,  # Extract everything
                },
            },
            "output": {
                "default": "reportlab",  # Better text precision
                "reportlab": {
                    "compression": 0,  # No compression for quality
                    "output_dpi": 600,  # High DPI
                    "embed_fonts": True,
                    "color_space": "RGB",
                },
            },
        },
        "processing": {
            "enable_parallel_processing": False,  # Single-threaded for consistency
            "max_memory_mb": 2048,
        },
        "validation": {
            "ssim_threshold": 0.99,  # Very high threshold
            "rendering_dpi": 600,
            "generate_diff_images": True,
            "fail_on_font_substitution": True,
        },
    }

    print("Quality Focused Configuration:")
    print(json.dumps(config, indent=2))

    return config


def create_memory_efficient_config():
    """Create a configuration optimized for low memory usage"""

    print("\n=== Memory Efficient Configuration ===\n")

    config = {
        "engines": {
            "input": {
                "default": "fitz",  # More memory efficient than Wand
                "wand": {
                    "density": 150,  # Lower DPI
                    "memory_limit_mb": 256,
                    "color_management": False,
                    "use_ocr": False,
                },
                "fitz": {
                    "extract_text": True,
                    "extract_images": False,  # Skip images to save memory
                    "extract_drawings": True,
                    "extract_raw_backgrounds": False,
                },
            },
            "output": {
                "default": "reportlab",
                "reportlab": {
                    "compression": 9,  # Maximum compression
                    "output_dpi": 150,  # Lower DPI
                    "embed_fonts": False,  # Don't embed fonts
                },
            },
        },
        "processing": {"enable_parallel_processing": False, "max_memory_mb": 512},
        "validation": {
            "ssim_threshold": 0.90,  # Lower threshold
            "rendering_dpi": 150,
            "generate_diff_images": False,
        },
    }

    print("Memory Efficient Configuration:")
    print(json.dumps(config, indent=2))

    return config


def apply_configuration(config: dict[str, Any]):
    """Apply a configuration to the system"""

    print("\n=== Applying Configuration ===\n")

    for category, cat_config in config.items():
        if hasattr(settings, category):
            for key, value in cat_config.items():
                setattr(getattr(settings, category), key, value)

    print("Configuration applied successfully!")


def save_configuration_to_file(config: dict[str, Any], filename: str):
    """Save configuration to a JSON file"""

    with open(filename, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Configuration saved to: {filename}")


def load_configuration_from_file(filename: str) -> dict[str, Any]:
    """Load configuration from a JSON file"""

    if not os.path.exists(filename):
        print(f"Configuration file not found: {filename}")
        return {}

    with open(filename) as f:
        config = json.load(f)

    print(f"Configuration loaded from: {filename}")
    return config


def demonstrate_output_directory_configuration():
    """Demonstrate output directory configuration"""

    print("\n=== Output Directory Configuration ===\n")

    # Show current directories
    print("Current Output Directories:")
    print(f"  Base: {settings.test_framework.test_output_dir}")
    print(f"  Reports: {settings.test_framework.test_reports_dir}")
    print(f"  Logs: {settings.logging.debug_logs_dir}")

    # Configure custom directories
    settings.test_framework.test_output_dir = "custom_output/testing"
    settings.test_framework.test_reports_dir = "custom_output/reports"
    settings.logging.debug_logs_dir = "custom_output/logs"

    print("\nAfter Custom Configuration:")
    print(f"  Base: {settings.test_framework.test_output_dir}")
    print(f"  Reports: {settings.test_framework.test_reports_dir}")
    print(f"  Logs: {settings.logging.debug_logs_dir}")


def demonstrate_font_configuration():
    """Demonstrate font management configuration"""

    print("\n=== Font Management Configuration ===\n")

    # Show current font configuration
    font_config = settings.font_management.model_dump()
    print("Current Font Configuration:")
    for key, value in font_config.items():
        print(f"  {key}: {value}")

    # Modify font configuration
    settings.font_management.enable_google_fonts = False
    settings.font_management.fallback_font = "Times-Roman"

    print("\nAfter Modifications:")
    print(f"  Google Fonts: {settings.font_management.enable_google_fonts}")
    print(f"  Fallback Font: {settings.font_management.fallback_font}")


def main():
    """Main demonstration function"""

    print("Multi-Format Document Engine - Advanced Configuration Example")
    print("=" * 70)

    # Show current configuration
    show_current_configuration()

    # Create different configuration profiles
    high_perf_config = create_high_performance_config()
    quality_config = create_quality_focused_config()
    memory_config = create_memory_efficient_config()

    # Save configurations to files
    os.makedirs("examples/configs", exist_ok=True)
    save_configuration_to_file(high_perf_config, "examples/configs/high_performance.json")
    save_configuration_to_file(quality_config, "examples/configs/quality_focused.json")
    save_configuration_to_file(memory_config, "examples/configs/memory_efficient.json")

    # Demonstrate applying a configuration
    print("\n=== Applying High Performance Configuration ===")
    apply_configuration(high_perf_config)

    # Show the changes
    print(f"\nNew default input engine: {settings.engines.input.default}")
    print(f"New default output engine: {settings.engines.output.default}")
    print(f"Parallel processing: {settings.processing.enable_parallel_processing}")

    # Demonstrate other configuration features
    demonstrate_output_directory_configuration()
    demonstrate_font_configuration()

    print("\n" + "=" * 70)
    print("Advanced configuration demonstration complete!")
    print("\nConfiguration files created in examples/configs/:")
    print("  - high_performance.json")
    print("  - quality_focused.json")
    print("  - memory_efficient.json")
    print("\nTo use a configuration:")
    print("  1. Load it with load_configuration_from_file()")
    print("  2. Apply it with apply_configuration()")
    print("  3. Or modify settings directly on the `settings` object.")


if __name__ == "__main__":
    main()
