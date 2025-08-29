#!/usr/bin/env python3
"""
Engine Selection Examples

This script demonstrates various ways to use the engine selection system
for PDF generation with different engines and configurations.
"""

import json
import os
import tempfile

from pdfrebuilder.core.recreate_pdf_from_config import get_available_engines, recreate_pdf_from_config
from pdfrebuilder.engine.config_loader import get_config_loader
from pdfrebuilder.engine.engine_selector import get_pdf_engine_selector
from pdfrebuilder.engine.pdf_engine_selector import get_pdf_engine
from pdfrebuilder.engine.performance_metrics import generate_performance_report, get_performance_collector


def create_sample_document():
    """Create a sample document configuration for testing."""
    return {
        "version": "1.0",
        "engine": "test",
        "metadata": {
            "title": "Engine Selection Example",
            "author": "PDF Engine System",
            "subject": "Demonstration of engine selection capabilities",
        },
        "document_structure": [
            {
                "type": "page",
                "page_number": 0,
                "size": [612, 792],
                "page_background_color": [1.0, 1.0, 1.0],
                "layers": [
                    {
                        "layer_id": "page_0_base_layer",
                        "layer_name": "Page Content",
                        "layer_type": "base",
                        "bbox": [0, 0, 612, 792],
                        "visibility": True,
                        "opacity": 1.0,
                        "blend_mode": "Normal",
                        "children": [],
                        "content": [
                            {
                                "type": "text",
                                "id": "title_text",
                                "bbox": [100, 700, 500, 730],
                                "text": "Engine Selection Example",
                                "font_details": {
                                    "name": "Helvetica-Bold",
                                    "size": 18,
                                    "color": [0, 0, 0, 1],
                                },
                            },
                            {
                                "type": "text",
                                "id": "body_text",
                                "bbox": [100, 650, 500, 680],
                                "text": "This document was generated using the engine selection system.",
                                "font_details": {
                                    "name": "Helvetica",
                                    "size": 12,
                                    "color": [0.2, 0.2, 0.2, 1],
                                },
                            },
                            {
                                "type": "drawing",
                                "id": "sample_rect",
                                "bbox": [100, 600, 200, 640],
                                "color": [0, 0, 1],
                                "fill": [0.8, 0.8, 1.0],
                                "width": 2.0,
                                "drawing_commands": [{"cmd": "rect", "bbox": [100, 600, 200, 640]}],
                            },
                        ],
                    }
                ],
            }
        ],
    }


def example_1_basic_engine_selection():
    """Example 1: Basic engine selection with different engines."""
    print("=" * 60)
    print("Example 1: Basic Engine Selection")
    print("=" * 60)

    # Create sample document
    doc_config = create_sample_document()

    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "sample_config.json")
        with open(config_file, "w") as f:
            json.dump(doc_config, f, indent=2)

        # Get available engines
        available_engines = get_available_engines()
        print(f"Available engines: {list(available_engines.keys())}")

        # Try each available engine
        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                print(f"❌ {engine_name}: {available_engines[engine_name]['error']}")
                continue

            try:
                output_file = os.path.join(temp_dir, f"example1_{engine_name}.pdf")
                print(f"🔄 Generating PDF with {engine_name} engine...")

                recreate_pdf_from_config(config_file, output_file, engine_name)

                file_size = os.path.getsize(output_file)
                print(f"✅ {engine_name}: Generated {output_file} ({file_size} bytes)")

            except Exception as e:
                print(f"❌ {engine_name}: Failed - {e}")


def example_2_configuration_based_selection():
    """Example 2: Configuration-based engine selection."""
    print("\n" + "=" * 60)
    print("Example 2: Configuration-Based Selection")
    print("=" * 60)

    # Create engine configuration
    engine_config = {
        "default_engine": "reportlab",
        "reportlab": {
            "compression": 3,
            "embed_fonts": True,
            "font_subsetting": True,
            "precision": 1.5,
        },
        "pymupdf": {"overlay_mode": False, "image_quality": 90, "anti_aliasing": True},
        "performance": {"enable_caching": True, "cache_size": 50},
        "debugging": {"enable_metrics": True},
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Save engine configuration
        engine_config_file = os.path.join(temp_dir, "engine_config.json")
        with open(engine_config_file, "w") as f:
            json.dump(engine_config, f, indent=2)

        # Save document configuration
        doc_config = create_sample_document()
        doc_config_file = os.path.join(temp_dir, "doc_config.json")
        with open(doc_config_file, "w") as f:
            json.dump(doc_config, f, indent=2)

        # Load configuration using the config loader
        loader = get_config_loader()
        loaded_config = loader.load_from_file(engine_config_file)

        print(f"Default engine: {loaded_config['default_engine']}")
        print(f"ReportLab compression: {loaded_config['reportlab']['compression']}")
        print(f"PyMuPDF image quality: {loaded_config['pymupdf']['image_quality']}")

        # Generate PDF using configuration
        try:
            selector = get_pdf_engine_selector()
            engine = selector.get_default_engine(loaded_config)

            output_file = os.path.join(temp_dir, "example2_configured.pdf")
            print(f"🔄 Generating PDF with configured engine ({engine.engine_name})...")

            # Create document using the engine
            metadata = doc_config.get("metadata", {})
            document = engine.create_document(metadata)

            # Process document structure (simplified)
            for doc_unit in doc_config["document_structure"]:
                if doc_unit.get("type") == "page":
                    page_size = doc_unit.get("size", [612, 792])
                    page = engine.add_page(document, page_size)

                    # Render elements (simplified)
                    for layer in doc_unit.get("layers", []):
                        for element in layer.get("content", []):
                            engine.render_element(page, element, {})

            # Finalize document
            engine.finalize_document(document, output_file)

            file_size = os.path.getsize(output_file)
            print(f"✅ Generated {output_file} ({file_size} bytes)")

        except Exception as e:
            print(f"❌ Configuration-based generation failed: {e}")


def example_3_performance_comparison():
    """Example 3: Performance comparison between engines."""
    print("\n" + "=" * 60)
    print("Example 3: Performance Comparison")
    print("=" * 60)

    # Clear performance metrics
    collector = get_performance_collector()
    collector.clear_history()

    # Create a more complex document for performance testing
    complex_doc = create_sample_document()

    # Add more elements for better performance testing
    additional_elements = []
    for i in range(20):
        additional_elements.append(
            {
                "type": "text",
                "id": f"perf_text_{i}",
                "bbox": [50, 550 - i * 20, 550, 570 - i * 20],
                "text": f"Performance test line {i + 1}: Lorem ipsum dolor sit amet",
                "font_details": {
                    "name": "Helvetica",
                    "size": 10,
                    "color": [0, 0, 0, 1],
                },
            }
        )

    complex_doc["document_structure"][0]["layers"][0]["content"].extend(additional_elements)

    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "complex_config.json")
        with open(config_file, "w") as f:
            json.dump(complex_doc, f, indent=2)

        # Test each available engine
        available_engines = get_available_engines()
        performance_results = {}

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            try:
                output_file = os.path.join(temp_dir, f"perf_{engine_name}.pdf")
                print(f"🔄 Performance testing {engine_name}...")

                import time

                start_time = time.time()

                recreate_pdf_from_config(config_file, output_file, engine_name)

                end_time = time.time()
                duration = end_time - start_time
                file_size = os.path.getsize(output_file)

                performance_results[engine_name] = {
                    "duration": duration,
                    "file_size": file_size,
                }

                print(f"✅ {engine_name}: {duration:.3f}s, {file_size} bytes")

            except Exception as e:
                print(f"❌ {engine_name}: Failed - {e}")

        # Display performance comparison
        if len(performance_results) > 1:
            print("\n📊 Performance Comparison:")
            list(performance_results.keys())

            # Find fastest and smallest
            fastest = min(performance_results.items(), key=lambda x: x[1]["duration"])
            smallest = min(performance_results.items(), key=lambda x: x[1]["file_size"])

            print(f"🏃 Fastest: {fastest[0]} ({fastest[1]['duration']:.3f}s)")
            print(f"📦 Smallest file: {smallest[0]} ({smallest[1]['file_size']} bytes)")

            # Show relative performance
            for engine, stats in performance_results.items():
                speed_ratio = stats["duration"] / fastest[1]["duration"]
                size_ratio = stats["file_size"] / smallest[1]["file_size"]
                print(f"   {engine}: {speed_ratio:.2f}x speed, {size_ratio:.2f}x size")


def example_4_advanced_configuration():
    """Example 4: Advanced configuration with environment variables and CLI args."""
    print("\n" + "=" * 60)
    print("Example 4: Advanced Configuration")
    print("=" * 60)

    # Simulate environment variables
    original_env = {}
    env_vars = {
        "PDF_ENGINE_DEFAULT": "pymupdf",
        "PDF_ENGINE_REPORTLAB_COMPRESSION": "5",
        "PDF_ENGINE_PYMUPDF_IMAGE_QUALITY": "95",
    }

    # Set environment variables
    for key, value in env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Load configuration from multiple sources
        loader = get_config_loader()

        # Simulate CLI arguments
        cli_args = {"output_engine": "reportlab"}  # Override env default

        # Load complete configuration
        config = loader.load_complete_config(cli_args=cli_args, env_prefix="PDF_ENGINE_")

        print("📋 Configuration loaded from multiple sources:")
        print(f"   Default engine: {config.get('default_engine', 'not set')}")
        print(f"   ReportLab compression: {config.get('reportlab', {}).get('compression', 'not set')}")
        print(f"   PyMuPDF image quality: {config.get('pymupdf', {}).get('image_quality', 'not set')}")

        # Validate configuration
        validation_result = loader.validate_config(config)
        if validation_result["valid"]:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration errors:")
            for error in validation_result["errors"]:
                print(f"   - {error}")

        if validation_result.get("warnings"):
            print("⚠️  Configuration warnings:")
            for warning in validation_result["warnings"]:
                print(f"   - {warning}")

        # Use the configuration
        try:
            engine = get_pdf_engine(config["default_engine"], config)
            print(f"✅ Successfully created {engine.engine_name} engine")

            # Get engine info
            info = engine.get_engine_info()
            print(f"   Engine version: {info.get('version', 'unknown')}")
            print(f"   Supported features: {len(info.get('supported_features', {}))}")

        except Exception as e:
            print(f"❌ Failed to create engine: {e}")

    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def example_5_error_handling_and_fallbacks():
    """Example 5: Error handling and engine fallbacks."""
    print("\n" + "=" * 60)
    print("Example 5: Error Handling and Fallbacks")
    print("=" * 60)

    def get_engine_with_fallback(preferred_engine, config, fallback_engines=None):
        """Get an engine with automatic fallback."""
        if fallback_engines is None:
            fallback_engines = ["reportlab", "pymupdf"]

        engines_to_try = [preferred_engine] + [e for e in fallback_engines if e != preferred_engine]

        for engine_name in engines_to_try:
            try:
                engine = get_pdf_engine(engine_name, config)
                if engine_name != preferred_engine:
                    print(f"⚠️  Using fallback engine: {engine_name}")
                else:
                    print(f"✅ Using preferred engine: {engine_name}")
                return engine
            except Exception as e:
                print(f"❌ Engine {engine_name} failed: {e}")

        raise Exception("No engines available")

    # Test with non-existent engine
    config = {"default_engine": "reportlab"}

    print("🔄 Testing fallback mechanism...")

    try:
        # Try non-existent engine first
        engine = get_engine_with_fallback("nonexistent_engine", config)
        print(f"✅ Successfully got fallback engine: {engine.engine_name}")
    except Exception as e:
        print(f"❌ All engines failed: {e}")

    # Test configuration validation with error handling
    print("\n🔄 Testing configuration validation...")

    invalid_configs = [
        {
            "reportlab": {
                "compression": 15,  # Invalid - should be 0-9
                "embed_fonts": "yes",  # Invalid - should be boolean
            }
        },
        {
            "pymupdf": {
                "image_quality": 150,  # Invalid - should be 1-100
                "annotation_mode": "invalid_mode",  # Invalid option
            }
        },
    ]

    from pdfrebuilder.engine.engine_config_schema import validate_engine_config

    for i, config in enumerate(invalid_configs, 1):
        print(f"\n   Testing invalid config {i}:")
        result = validate_engine_config(config)

        if result["valid"]:
            print("   ✅ Configuration passed validation")
        else:
            print("   ❌ Configuration validation failed:")
            for error in result.get("errors", []):
                print(f"      - {error}")


def example_6_performance_monitoring():
    """Example 6: Performance monitoring and reporting."""
    print("\n" + "=" * 60)
    print("Example 6: Performance Monitoring")
    print("=" * 60)

    # Enable performance metrics

    # Clear previous metrics
    collector = get_performance_collector()
    collector.clear_history()

    doc_config = create_sample_document()

    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = os.path.join(temp_dir, "monitor_config.json")
        with open(config_file, "w") as f:
            json.dump(doc_config, f, indent=2)

        # Generate documents with different engines to collect metrics
        available_engines = get_available_engines()

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            try:
                output_file = os.path.join(temp_dir, f"monitor_{engine_name}.pdf")
                print(f"🔄 Generating with {engine_name} for metrics collection...")

                recreate_pdf_from_config(config_file, output_file, engine_name)

            except Exception as e:
                print(f"❌ {engine_name} failed: {e}")

        # Analyze collected metrics
        print("\n📊 Performance Metrics Analysis:")

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            stats = collector.get_engine_stats(engine_name)
            if stats.get("total_runs", 0) > 0:
                print(f"\n   {engine_name} Statistics:")
                print(f"      Total runs: {stats['total_runs']}")
                print(f"      Successful runs: {stats['successful_runs']}")
                print(f"      Success rate: {stats['success_rate']:.2%}")

                if stats["successful_runs"] > 0:
                    print(f"      Average duration: {stats.get('avg_duration_ms', 0):.2f}ms")
                    print(f"      Average memory: {stats.get('avg_memory_mb', 0):.2f}MB")
                    print(f"      Total pages: {stats.get('total_pages', 0)}")
                    print(f"      Total elements: {stats.get('total_elements', 0)}")

        # Generate performance report
        report_file = os.path.join(temp_dir, "performance_report.json")
        report = generate_performance_report(report_file)

        print(f"\n📋 Performance Report Generated: {report_file}")
        print(f"   Total runs: {report['summary'].get('total_runs', 0)}")
        print(f"   Overall success rate: {report['summary'].get('overall_success_rate', 0):.2%}")
        print(f"   Total processing time: {report['summary'].get('total_processing_time_ms', 0):.2f}ms")


def main():
    """Run all examples."""
    print("🚀 PDF Engine Selection Examples")
    print("This script demonstrates various aspects of the engine selection system.\n")

    try:
        example_1_basic_engine_selection()
        example_2_configuration_based_selection()
        example_3_performance_comparison()
        example_4_advanced_configuration()
        example_5_error_handling_and_fallbacks()
        example_6_performance_monitoring()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
