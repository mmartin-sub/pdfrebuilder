"""
PDF Engine Selector

This module provides a factory pattern for selecting and instantiating
the appropriate PDF rendering engine based on configuration.
"""

import logging
from typing import Any, cast

from pdfrebuilder.engine.pdf_rendering_engine import EngineInitializationError, EngineNotFoundError, PDFRenderingEngine

logger = logging.getLogger(__name__)


class PDFEngineSelector:
    """Factory for PDF rendering engines."""

    def __init__(self):
        """Initialize the engine selector."""
        self.engines: dict[str, type[PDFRenderingEngine]] = {}
        self._engine_cache: dict[str, PDFRenderingEngine] = {}
        self.register_default_engines()

    def register_engine(self, name: str, engine_class: type[PDFRenderingEngine]) -> None:
        """
        Register a new engine.

        Args:
            name: Engine name (case-insensitive)
            engine_class: Engine class that implements PDFRenderingEngine

        Raises:
            ValueError: If engine_class doesn't implement PDFRenderingEngine
        """
        if not issubclass(engine_class, PDFRenderingEngine):
            raise ValueError(f"Engine class {engine_class} must implement PDFRenderingEngine")

        self.engines[name.lower()] = engine_class
        logger.info(f"Registered PDF engine: {name}")

    def register_default_engines(self) -> None:
        """Register the default engines."""
        from pdfrebuilder.engine.engine_logger import EngineLogger

        try:
            # Import engines dynamically to avoid circular imports
            from pdfrebuilder.engine.pymupdf_engine import PyMuPDFEngine
            from pdfrebuilder.engine.reportlab_engine import ReportLabEngine

            self.register_engine("reportlab", ReportLabEngine)
            self.register_engine("pymupdf", PyMuPDFEngine)
            self.register_engine("fitz", PyMuPDFEngine)  # Alias for PyMuPDF
        except ImportError as e:
            logger.warning(f"Could not register some default engines: {e}")
            # Register what we can
            try:
                from pdfrebuilder.engine.reportlab_engine import ReportLabEngine

                self.register_engine("reportlab", ReportLabEngine)
            except ImportError:
                logger.warning("ReportLab engine not available")

            try:
                from pdfrebuilder.pdf_engine import FitzPDFEngine

                # Create a wrapper for the old FitzPDFEngine
                self.register_engine("pymupdf", cast(type[PDFRenderingEngine], FitzPDFEngine))
                self.register_engine("fitz", cast(type[PDFRenderingEngine], FitzPDFEngine))
            except ImportError:
                logger.warning("PyMuPDF engine not available")

        # Log available engines at DEBUG level
        if logger.isEnabledFor(logging.DEBUG):
            EngineLogger.log_available_engines()

    def get_engine(self, name: str, config: dict[str, Any] | None = None) -> PDFRenderingEngine:
        """
        Get an instance of the specified engine.

        Args:
            name: Engine name
            config: Optional configuration dictionary

        Returns:
            Configured engine instance

        Raises:
            EngineNotFoundError: If engine is not registered
            EngineInitializationError: If engine initialization fails
        """
        from pdfrebuilder.engine.engine_logger import EngineLogger

        name = name.lower()
        if name not in self.engines:
            available = ", ".join(self.engines.keys())
            raise EngineNotFoundError(f"Unknown PDF rendering engine: {name}. Available engines: {available}")

        # Check cache first
        cache_key = f"{name}_{hash(str(sorted((config or {}).items())))}"
        if cache_key in self._engine_cache:
            cached_engine = self._engine_cache[cache_key]
            EngineLogger.log_engine_selection(cached_engine.engine_name, "cached")
            return cached_engine

        try:
            engine_class = self.engines[name]
            engine = engine_class()

            # Log engine selection
            EngineLogger.log_engine_selection(engine.engine_name, "user_selected")

            # Initialize with configuration
            if config:
                engine_config = config.get(name, {})
                engine.initialize(engine_config)
            else:
                engine.initialize({})

            # Cache the engine
            self._engine_cache[cache_key] = engine

            return engine

        except Exception as e:
            # Log engine error with version info for troubleshooting
            EngineLogger.log_engine_error(name, e, show_version=True)
            raise EngineInitializationError(f"Failed to initialize engine {name}: {e!s}")

    def get_default_engine(self, config: dict[str, Any] | None = None) -> PDFRenderingEngine:
        """
        Get the default engine based on configuration.

        Args:
            config: Optional configuration dictionary

        Returns:
            Default engine instance
        """
        from pdfrebuilder.engine.engine_logger import EngineLogger

        if config is None:
            config = {}

        default_engine = config.get("default_engine", "reportlab").lower()

        try:
            engine = self.get_engine(default_engine, config)
            EngineLogger.log_engine_selection(engine.engine_name, "auto_detected")
            return engine
        except Exception as e:
            # Try fallback engines
            fallback_engines = ["reportlab", "pymupdf", "fitz"]
            for fallback in fallback_engines:
                if fallback != default_engine and fallback in self.engines:
                    try:
                        engine = self.get_engine(fallback, config)
                        EngineLogger.log_engine_fallback(default_engine, engine.engine_name, str(e))
                        return engine
                    except Exception as fallback_error:  # nosec B112 - Intentional fallback pattern with logging
                        logger.debug(f"Fallback engine {fallback} also failed: {fallback_error}")
                        continue

            # If all fallbacks fail, re-raise the original error
            raise

    def list_available_engines(self) -> dict[str, dict[str, Any]]:
        """List all available engines with their capabilities."""
        engines_info = {}

        for name, engine_class in self.engines.items():
            # Create a temporary instance to get engine info
            try:
                engine = engine_class()
                engine.initialize({})  # Initialize with empty config for info gathering

                engines_info[name] = {
                    "engine_name": engine.engine_name,
                    "engine_version": engine.engine_version,
                    "supported_features": engine.supported_features,
                }
            except Exception as e:
                logger.warning(f"Could not get info for engine {name}: {e}")
                engines_info[name] = {"error": str(e)}

        return engines_info

    def validate_engine_config(self, engine_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate configuration for a specific engine."""
        try:
            engine = self.get_engine(engine_name, config)
            return {
                "valid": True,
                "engine": engine.engine_name,
                "version": engine.engine_version,
                "supported_features": engine.supported_features,
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "engine": engine_name,
            }

    def compare_engines(self, engine1: str, engine2: str) -> dict[str, Any]:
        """Compare capabilities of two engines."""
        try:
            eng1 = self.get_engine(engine1)
            eng2 = self.get_engine(engine2)

            comparison = {
                "engine1": {
                    "name": eng1.engine_name,
                    "version": eng1.engine_version,
                    "features": eng1.supported_features,
                },
                "engine2": {
                    "name": eng2.engine_name,
                    "version": eng2.engine_version,
                    "features": eng2.supported_features,
                },
                "differences": {},
            }

            # Compare features
            all_features = set(eng1.supported_features.keys()) | set(eng2.supported_features.keys())
            for feature in all_features:
                eng1_supports = eng1.supported_features.get(feature, False)
                eng2_supports = eng2.supported_features.get(feature, False)

                if eng1_supports != eng2_supports:
                    comparison["differences"][feature] = {
                        "engine1": eng1_supports,
                        "engine2": eng2_supports,
                    }

            return comparison

        except Exception as e:
            return {"error": f"Could not compare engines: {e}"}


# Global engine selector instance
_engine_selector: PDFEngineSelector | None = None


def get_engine_selector() -> PDFEngineSelector:
    """Get the global engine selector instance."""
    global _engine_selector
    if _engine_selector is None:
        _engine_selector = PDFEngineSelector()
    return _engine_selector


def get_pdf_engine(engine_name: str, config: dict[str, Any] | None = None) -> PDFRenderingEngine:
    """Get a PDF engine instance."""
    selector = get_engine_selector()
    return selector.get_engine(engine_name, config)


def get_default_pdf_engine(config: dict[str, Any] | None = None) -> PDFRenderingEngine:
    """Get the default PDF engine."""
    selector = get_engine_selector()
    return selector.get_default_engine(config)
