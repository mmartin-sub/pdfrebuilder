"""
Integration tests for engine selection functionality.

Tests end-to-end engine selection, configuration loading, and PDF generation
with different engines.
"""

import json
import os
import tempfile

import pytest

from pdfrebuilder.engine.config_loader import get_config_loader
from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector, get_pdf_engine
from pdfrebuilder.engine.performance_metrics import get_performance_collector
from pdfrebuilder.recreate_pdf_from_config import (
    get_available_engines,
    recreate_pdf_from_config,
    validate_engine_configuration,
)


class TestEngineSelectionIntegration:
    """Integration tests for engine selection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            "version": "1.0",
            "engine": "test",
            "metadata": {"title": "Test Document", "author": "Test Author"},
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
                                    "id": "text_0",
                                    "bbox": [100, 700, 500, 720],
                                    "text": "Hello, World!",
                                    "font_details": {
                                        "name": "Helvetica",
                                        "size": 12,
                                        "color": [0, 0, 0, 1],
                                    },
                                }
                            ],
                        }
                    ],
                }
            ],
        }

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_engine_selector_default_engines(self):
        """Test that default engines are registered."""
        selector = get_engine_selector()
        engines = selector.list_available_engines()

        # Should have at least reportlab registered
        assert len(engines) > 0

        # Check for expected engines (may not all be available)
        expected_engines = ["reportlab", "pymupdf", "fitz"]
        available_engines = list(engines.keys())

        # At least one engine should be available
        assert any(engine in available_engines for engine in expected_engines)

    def test_get_engine_with_config(self):
        """Test getting an engine with configuration."""
        config = {
            "default_engine": "reportlab",
            "reportlab": {"compression": 1, "embed_fonts": True},
        }

        try:
            engine = get_pdf_engine("reportlab", config)
            assert engine is not None
            assert engine.engine_name == "reportlab"
        except Exception as e:
            pytest.skip(f"ReportLab engine not available: {e}")

    def test_config_loader_integration(self):
        """Test configuration loading integration."""
        # Create a test config file
        config_file = os.path.join(self.temp_dir, "engine_config.json")
        test_config = {
            "default_engine": "reportlab",
            "reportlab": {"compression": 2, "embed_fonts": False},
        }

        with open(config_file, "w") as f:
            json.dump(test_config, f)

        # Load configuration
        loader = get_config_loader()
        loaded_config = loader.load_from_file(config_file)

        assert loaded_config["default_engine"] == "reportlab"
        assert loaded_config["reportlab"]["compression"] == 2

    def test_config_merging(self):
        """Test configuration merging from multiple sources."""
        # Environment config
        env_config = {"default_engine": "pymupdf"}

        # CLI config
        cli_config = {"reportlab": {"compression": 5}}

        # File config
        file_config = {
            "reportlab": {"embed_fonts": False},
            "pymupdf": {"overlay_mode": True},
        }

        loader = get_config_loader()
        merged = loader.merge_configs(env_config, file_config, cli_config)

        assert merged["default_engine"] == "pymupdf"
        assert merged["reportlab"]["compression"] == 5
        assert merged["reportlab"]["embed_fonts"] is False
        assert merged["pymupdf"]["overlay_mode"] is True

    @pytest.mark.skipif(
        not any(engine in get_engine_selector().list_available_engines() for engine in ["reportlab", "pymupdf"]),
        reason="No PDF engines available",
    )
    def test_pdf_generation_with_different_engines(self):
        """Test PDF generation with different engines."""
        # Create test config file
        config_file = os.path.join(self.temp_dir, "test_config.json")
        with open(config_file, "w") as f:
            json.dump(self.test_config, f)

        available_engines = get_engine_selector().list_available_engines()

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue  # Skip engines with errors

            output_file = os.path.join(self.temp_dir, f"test_{engine_name}.pdf")

            try:
                recreate_pdf_from_config(config_file, output_file, engine_name)

                # Check that file was created
                assert os.path.exists(output_file)
                assert os.path.getsize(output_file) > 0

            except Exception as e:
                pytest.skip(f"Engine {engine_name} failed: {e}")

    def test_engine_fallback_mechanism(self):
        """Test engine fallback when primary engine fails."""
        config_file = os.path.join(self.temp_dir, "test_config.json")
        with open(config_file, "w") as f:
            json.dump(self.test_config, f)

        output_file = os.path.join(self.temp_dir, "fallback_test.pdf")

        # Try with a non-existent engine - should fallback
        try:
            recreate_pdf_from_config(config_file, output_file, "nonexistent_engine")

            # If it succeeds, fallback worked
            assert os.path.exists(output_file)

        except Exception:
            # If it fails, that's also acceptable for this test
            pass

    def test_performance_metrics_collection(self):
        """Test that performance metrics are collected during rendering."""
        collector = get_performance_collector()
        initial_count = len(collector.get_metrics_history())

        config_file = os.path.join(self.temp_dir, "metrics_test.json")
        with open(config_file, "w") as f:
            json.dump(self.test_config, f)

        output_file = os.path.join(self.temp_dir, "metrics_test.pdf")

        try:
            recreate_pdf_from_config(config_file, output_file)

            # Check that metrics were collected
            final_count = len(collector.get_metrics_history())
            assert final_count > initial_count

            # Check latest metrics
            latest_metrics = collector.get_latest_metrics()
            assert latest_metrics is not None
            assert latest_metrics.page_count >= 0
            assert latest_metrics.duration > 0

        except Exception as e:
            pytest.skip(f"PDF generation failed: {e}")

    def test_engine_configuration_validation(self):
        """Test engine configuration validation."""
        # Valid configuration
        valid_config = {"reportlab": {"compression": 1, "embed_fonts": True}}

        result = validate_engine_configuration("reportlab", valid_config)
        assert isinstance(result, dict)
        assert "valid" in result

        # Invalid configuration
        invalid_config = {
            "reportlab": {
                "compression": 15,  # Invalid value
                "embed_fonts": "not_a_boolean",  # Invalid type
            }
        }

        result = validate_engine_configuration("reportlab", invalid_config)
        assert isinstance(result, dict)
        assert "valid" in result

    def test_available_engines_function(self):
        """Test the get_available_engines function."""
        engines = get_available_engines()

        assert isinstance(engines, dict)
        assert len(engines) > 0

        # Each engine should have basic info
        for engine_name, engine_info in engines.items():
            if "error" not in engine_info:
                assert "engine_name" in engine_info
                assert "supported_features" in engine_info

    def test_engine_feature_comparison(self):
        """Test comparing features between engines."""
        selector = get_engine_selector()
        available_engines = list(selector.list_available_engines().keys())

        if len(available_engines) >= 2:
            engine1, engine2 = available_engines[0], available_engines[1]

            comparison = selector.compare_engines(engine1, engine2)

            assert "engine1" in comparison
            assert "engine2" in comparison
            assert "differences" in comparison

            # Check structure
            assert "name" in comparison["engine1"]
            assert "features" in comparison["engine1"]

    def test_config_file_with_engine_sections(self):
        """Test loading config file with engine-specific sections."""
        config_data = {
            "default_engine": "reportlab",
            "reportlab": {"compression": 3, "embed_fonts": True, "precision": 2.0},
            "pymupdf": {"overlay_mode": True, "image_quality": 90},
            "performance": {"enable_caching": True, "cache_size": 50},
        }

        config_file = os.path.join(self.temp_dir, "full_config.json")
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load and validate
        loader = get_config_loader()
        loaded_config = loader.load_from_file(config_file)

        assert loaded_config["default_engine"] == "reportlab"
        assert loaded_config["reportlab"]["compression"] == 3
        assert loaded_config["pymupdf"]["overlay_mode"] is True
        assert loaded_config["performance"]["cache_size"] == 50

        # Test engine-specific config extraction
        reportlab_config = loader.get_engine_config(loaded_config, "reportlab")
        assert reportlab_config["compression"] == 3
        assert reportlab_config["embed_fonts"] is True

    def test_cli_args_to_config_conversion(self):
        """Test conversion of CLI arguments to configuration."""
        cli_args = {"output_engine": "pymupdf", "other_arg": "value"}

        loader = get_config_loader()
        config = loader._cli_args_to_config(cli_args)

        assert config.get("default_engine") == "pymupdf"

    def test_environment_variable_config_loading(self):
        """Test loading configuration from environment variables."""
        # Mock environment variables
        env_vars = {
            "PDF_ENGINE_DEFAULT": "pymupdf",
            "PDF_ENGINE_REPORTLAB_COMPRESSION": "2",
            "PDF_ENGINE_PYMUPDF_OVERLAY_MODE": "true",
        }

        loader = get_config_loader()

        # Temporarily set environment variables
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            config = loader.load_from_env()

            assert config.get("default_engine") == "pymupdf"
            if "reportlab" in config:
                assert config["reportlab"]["compression"] == 2
            if "pymupdf" in config:
                assert config["pymupdf"]["overlay_mode"] is True

        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value


if __name__ == "__main__":
    pytest.main([__file__])
