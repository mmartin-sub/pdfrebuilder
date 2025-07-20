#!/usr/bin/env python3
"""
Example script demonstrating advanced configuration options.
Shows how to configure engines for different use cases.
"""

import json
import os
from typing import Any

from pdfrebuilder.settings import (
    configure_output_directories,
    get_config_value,
    get_nested_config_value,
    set_nested_config_value,
)


def show_current_configuration():
    """Display the current configuration"""

    print("=== Current Configuration ===\n")

    # Engine configurations
    print("Input Engines:")
    input_engines = get_nested_config_value("engines.input", {})
    for engine, config in input_engines.items():
        if engine != "default":
            print(f"  {engine}:")
            for key, value in config.items():
                print(f"    {key}: {value}")

    print(f"\nDefault Input Engine: {get_nested_config_value('engines.input.default')}")

    print("\nOutput Engines:")
    output_engines = get_nested_config_value("engines.output", {})
    for engine, config in output_engines.items():
        if engine != "default":
            print(f"  {engine}:")
            for key, value in config.items():
                print(f"    {key}: {value}")

    print(f"\nDefault Output Engine: {get_nested_config_value('engines.output.default')}")

    # Other important configurations
    print("\nFont Management:")
    font_config = get_nested_config_value("font_management", {})
    for key, value in font_config.items():
        print(f"  {key}: {value}")

    print("\nValidation Settings:")
    validation_config = get_nested_config_value("validation", {})
    for key, value in validation_config.items():
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

    # Apply engine configurations
    if "engines" in config:
        for engine_type, engines in config["engines"].items():
            for engine_name, engine_config in engines.items():
                config_path = f"engines.{engine_type}.{engine_name}"
                if isinstance(engine_config, dict):
                    for key, value in engine_config.items():
                        set_nested_config_value(f"{config_path}.{key}", value)
                else:
                    set_nested_config_value(config_path, engine_config)

    # Apply processing configuration
    if "processing" in config:
        for key, value in config["processing"].items():
            set_nested_config_value(f"processing.{key}", value)

    # Apply validation configuration
    if "validation" in config:
        for key, value in config["validation"].items():
            set_nested_config_value(f"validation.{key}", value)

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
    print(f"  Base: {get_config_value('test_output_dir')}")
    print(f"  Reports: {get_config_value('reports_output_dir')}")
    print(f"  Logs: {get_config_value('logs_output_dir')}")

    # Configure custom directories
    configure_output_directories(
        base_dir="custom_output",
        test_dir="custom_output/testing",
        reports_dir="custom_output/reports",
    )

    print("\nAfter Custom Configuration:")
    print(f"  Base: {get_config_value('test_output_dir')}")
    print(f"  Reports: {get_config_value('reports_output_dir')}")
    print(f"  Logs: {get_config_value('logs_output_dir')}")


def demonstrate_font_configuration():
    """Demonstrate font management configuration"""

    print("\n=== Font Management Configuration ===\n")

    # Show current font configuration
    font_config = get_nested_config_value("font_management")
    print("Current Font Configuration:")
    for key, value in font_config.items():
        print(f"  {key}: {value}")

    # Modify font configuration
    set_nested_config_value("font_management.enable_google_fonts", False)
    set_nested_config_value("font_management.fallback_font", "Times-Roman")

    print("\nAfter Modifications:")
    print(f"  Google Fonts: {get_nested_config_value('font_management.enable_google_fonts')}")
    print(f"  Fallback Font: {get_nested_config_value('font_management.fallback_font')}")


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
    print(f"\nNew default input engine: {get_nested_config_value('engines.input.default')}")
    print(f"New default output engine: {get_nested_config_value('engines.output.default')}")
    print(f"Parallel processing: {get_nested_config_value('processing.enable_parallel_processing')}")

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
    print("  3. Or modify settings directly with set_nested_config_value()")


if __name__ == "__main__":
    main()
