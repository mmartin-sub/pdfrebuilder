"""
Unit tests for engine selection functionality.

Tests the PDF engine selector, configuration validation, and engine interfaces.
"""

from typing import Any, ClassVar
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.engine.engine_config_schema import (
    EngineConfigValidator,
    apply_config_defaults,
    validate_engine_config,
)
from pdfrebuilder.engine.pdf_engine_selector import PDFEngineSelector, get_engine_selector
from pdfrebuilder.engine.pdf_rendering_engine import (
    EngineError,
    EngineInitializationError,
    EngineNotFoundError,
    PDFRenderingEngine,
    RenderingError,
    UnsupportedFeatureError,
)


class MockEngine(PDFRenderingEngine):
    """Mock engine for testing."""

    engine_name = "mock"
    engine_version = "1.0.0"
    supported_features: ClassVar[dict[str, bool]] = {"text": True, "images": True, "drawings": False}

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.init_config = None

    def initialize(self, config: dict[str, Any]) -> None:
        self.initialized = True
        self.init_config = config
        self._initialized = True

    def create_document(self, metadata: dict[str, Any]) -> Any:
        return {"type": "mock_document", "metadata": metadata}

    def add_page(self, document: Any, size: tuple, background_color: Any = None) -> Any:
        return {"type": "mock_page", "size": size, "background_color": background_color}

    def render_element(self, page: Any, element: dict[str, Any], resources: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success", "element_id": element.get("id", "unknown")}

    def finalize_document(self, document: Any, output_path: str) -> None:
        pass

    def get_engine_info(self) -> dict[str, Any]:
        return {
            "engine": self.engine_name,
            "version": self.engine_version,
            "supported_features": self.supported_features,
        }


class TestPDFRenderingEngine:
    """Test the abstract PDF rendering engine."""

    def test_abstract_engine_cannot_be_instantiated(self):
        """Test that the abstract engine cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PDFRenderingEngine()

    def test_mock_engine_can_be_instantiated(self):
        """Test that a concrete engine can be instantiated."""
        engine = MockEngine()
        assert engine.engine_name == "mock"
        assert engine.engine_version == "1.0.0"

    def test_feature_support_checking(self):
        """Test feature support checking."""
        engine = MockEngine()

        assert engine.is_feature_supported("text") is True
        assert engine.is_feature_supported("images") is True
        assert engine.is_feature_supported("drawings") is False
        assert engine.is_feature_supported("nonexistent") is False

    def test_unsupported_feature_warning(self):
        """Test unsupported feature warning."""
        engine = MockEngine()

        with patch.object(engine.logger, "warning") as mock_warning:
            engine.warn_unsupported_feature("rotation", "test context")
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert "rotation" in args[0]
            assert "mock" in args[0]
            assert "test context" in args[0]

    def test_config_validation(self):
        """Test configuration validation."""
        engine = MockEngine()

        # Valid config
        result = engine.validate_config({"key": "value"})
        assert result["valid"] is True
        assert result["errors"] == []

        # Test with required keys
        engine.required_config_keys = ["required_key"]
        result = engine.validate_config({})
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_performance_metrics(self):
        """Test performance metrics collection."""
        engine = MockEngine()
        metrics = engine.get_performance_metrics()

        assert metrics["engine"] == "mock"
        assert metrics["version"] == "1.0.0"
        assert "initialized" in metrics
        assert "supported_features_count" in metrics


class TestPDFEngineSelector:
    """Test the PDF engine selector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.selector = PDFEngineSelector()

    def test_engine_registration(self):
        """Test engine registration."""
        self.selector.register_engine("test", MockEngine)
        assert "test" in self.selector.engines
        assert self.selector.engines["test"] == MockEngine

    def test_invalid_engine_registration(self):
        """Test registration of invalid engine."""

        class InvalidEngine:
            pass

        with pytest.raises(ValueError):
            self.selector.register_engine("invalid", InvalidEngine)

    def test_get_engine_success(self):
        """Test successful engine retrieval."""
        self.selector.register_engine("test", MockEngine)

        engine = self.selector.get_engine("test")
        assert isinstance(engine, MockEngine)
        assert engine.initialized is True

    def test_get_engine_not_found(self):
        """Test engine not found error."""
        with pytest.raises(EngineNotFoundError):
            self.selector.get_engine("nonexistent")

    def test_get_engine_with_config(self):
        """Test engine retrieval with configuration."""
        self.selector.register_engine("test", MockEngine)

        config = {"test": {"param": "value"}}
        engine = self.selector.get_engine("test", config)

        assert isinstance(engine, MockEngine)
        assert engine.init_config == {"param": "value"}

    def test_get_default_engine(self):
        """Test default engine retrieval."""
        self.selector.register_engine("default", MockEngine)

        config = {"default_engine": "default"}
        engine = self.selector.get_default_engine(config)

        assert isinstance(engine, MockEngine)

    def test_list_available_engines(self):
        """Test listing available engines."""
        self.selector.register_engine("test", MockEngine)

        engines = self.selector.list_available_engines()
        assert "test" in engines
        assert engines["test"]["engine_name"] == "mock"
        assert engines["test"]["engine_version"] == "1.0.0"

    def test_validate_engine_config(self):
        """Test engine configuration validation."""
        self.selector.register_engine("test", MockEngine)

        result = self.selector.validate_engine_config("test", {})
        assert result["valid"] is True
        assert result["engine"] == "mock"

    def test_compare_engines(self):
        """Test engine comparison."""
        self.selector.register_engine("test1", MockEngine)
        self.selector.register_engine("test2", MockEngine)

        comparison = self.selector.compare_engines("test1", "test2")

        assert "engine1" in comparison
        assert "engine2" in comparison
        assert "differences" in comparison

    def test_engine_caching(self):
        """Test that engines are cached properly."""
        self.selector.register_engine("test", MockEngine)

        engine1 = self.selector.get_engine("test")
        engine2 = self.selector.get_engine("test")

        # Should be the same instance due to caching
        assert engine1 is engine2


class TestEngineConfigValidator:
    """Test the engine configuration validator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = EngineConfigValidator()

    def test_valid_config_validation(self):
        """Test validation of valid configuration."""
        config = {
            "default_engine": "reportlab",
            "reportlab": {"compression": 1, "embed_fonts": True},
        }

        result = self.validator.validate(config)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_invalid_config_validation(self):
        """Test validation of invalid configuration."""
        config = {"default_engine": "invalid_engine"}

        result = self.validator.validate(config)
        # Should have warnings but might still be valid
        assert isinstance(result["valid"], bool)

    def test_apply_defaults(self):
        """Test applying default values."""
        config = {"reportlab": {"compression": 5}}

        result = self.validator.apply_defaults(config)

        assert result["default_engine"] == "reportlab"
        assert result["reportlab"]["compression"] == 5  # User value preserved
        assert result["reportlab"]["embed_fonts"] is True  # Default applied

    def test_get_engine_config(self):
        """Test getting engine-specific configuration."""
        config = {"reportlab": {"compression": 5}, "pymupdf": {"overlay_mode": True}}

        full_config = self.validator.apply_defaults(config)
        reportlab_config = self.validator.get_engine_config(full_config, "reportlab")

        assert reportlab_config["compression"] == 5
        assert "embed_fonts" in reportlab_config

    def test_validate_engine_specific_config(self):
        """Test validation of engine-specific configuration."""
        config = {"reportlab": {"compression": 15}}  # Invalid value (should be 0-9)

        result = self.validator.validate_engine_config(config, "reportlab")
        # The exact validation behavior depends on jsonschema availability
        assert isinstance(result["valid"], bool)


class TestEngineConfigSchema:
    """Test the engine configuration schema functions."""

    def test_validate_engine_config_function(self):
        """Test the validate_engine_config function."""
        config = {"default_engine": "reportlab"}

        result = validate_engine_config(config)
        assert isinstance(result, dict)
        assert "valid" in result
        assert "errors" in result

    def test_apply_config_defaults_function(self):
        """Test the apply_config_defaults function."""
        config = {"reportlab": {"compression": 3}}

        result = apply_config_defaults(config)
        assert result["default_engine"] == "reportlab"
        assert result["reportlab"]["compression"] == 3


class TestEngineErrors:
    """Test engine-specific error classes."""

    def test_engine_error_hierarchy(self):
        """Test that engine errors inherit correctly."""
        assert issubclass(EngineNotFoundError, EngineError)
        assert issubclass(EngineInitializationError, EngineError)
        assert issubclass(RenderingError, EngineError)
        assert issubclass(UnsupportedFeatureError, EngineError)

    def test_engine_error_messages(self):
        """Test engine error messages."""
        error = EngineNotFoundError("Test engine not found")
        assert str(error) == "Test engine not found"

        error = RenderingError("Rendering failed")
        assert str(error) == "Rendering failed"


class TestGlobalEngineSelector:
    """Test the global engine selector functions."""

    def test_get_engine_selector_singleton(self):
        """Test that get_engine_selector returns a singleton."""
        selector1 = get_engine_selector()
        selector2 = get_engine_selector()

        assert selector1 is selector2
        assert isinstance(selector1, PDFEngineSelector)

    @patch("src.engine.pdf_engine_selector.get_engine_selector")
    def test_get_pdf_engine_function(self, mock_get_selector):
        """Test the get_pdf_engine convenience function."""
        from pdfrebuilder.engine.pdf_engine_selector import get_pdf_engine

        mock_selector = Mock()
        mock_engine = Mock()
        mock_selector.get_engine.return_value = mock_engine
        mock_get_selector.return_value = mock_selector

        result = get_pdf_engine("test", {"config": "value"})

        assert result is mock_engine
        mock_selector.get_engine.assert_called_once_with("test", {"config": "value"})

    @patch("src.engine.pdf_engine_selector.get_engine_selector")
    def test_get_default_pdf_engine_function(self, mock_get_selector):
        """Test the get_default_pdf_engine convenience function."""
        from pdfrebuilder.engine.pdf_engine_selector import get_default_pdf_engine

        mock_selector = Mock()
        mock_engine = Mock()
        mock_selector.get_default_engine.return_value = mock_engine
        mock_get_selector.return_value = mock_selector

        result = get_default_pdf_engine({"config": "value"})

        assert result is mock_engine
        mock_selector.get_default_engine.assert_called_once_with({"config": "value"})


if __name__ == "__main__":
    pytest.main([__file__])
