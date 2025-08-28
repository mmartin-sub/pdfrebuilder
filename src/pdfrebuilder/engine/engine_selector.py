import logging
from typing import Any

from pdfrebuilder.engine.document_parser import DocumentParser
from pdfrebuilder.engine.document_renderer import DocumentRenderer
from pdfrebuilder.engine.pdf_rendering_engine import (
    EngineInitializationError,
    EngineNotFoundError,
    PDFRenderingEngine,
)

logger = logging.getLogger(__name__)


class EngineSelector:
    def __init__(self):
        self.engines = {}
        self._engine_cache = {}

    def register_engine(self, name, engine_class):
        self.engines[name.lower()] = engine_class
        logger.info(f"Registered engine: {name}")

    def get_engine(self, name: str, config: dict[str, Any] | None = None):
        name = name.lower()
        if name not in self.engines:
            available = ", ".join(self.engines.keys())
            raise EngineNotFoundError(f"Unknown engine: {name}. Available engines: {available}")

        cache_key = f"{name}_{hash(str(sorted((config or {}).items())))}"
        if cache_key in self._engine_cache:
            return self._engine_cache[cache_key]

        try:
            engine_class = self.engines[name]
            engine = engine_class()

            if config:
                engine_config = config.get(name, {})
                engine.initialize(engine_config)
            else:
                engine.initialize({})

            self._engine_cache[cache_key] = engine
            return engine

        except Exception as e:
            raise EngineInitializationError(f"Failed to initialize engine {name}: {e!s}")


class PDFEngineSelector:
    def __init__(self):
        self.engines = {}
        self._engine_cache = {}
        self.register_default_engines()

    def register_engine(self, name, engine_class):
        self.engines[name.lower()] = engine_class
        logger.info(f"Registered PDF engine: {name}")

    def register_default_engines(self):
        try:
            from pdfrebuilder.engine.pymupdf_engine import PyMuPDFEngine
            from pdfrebuilder.engine.reportlab_engine import ReportLabEngine

            self.register_engine("reportlab", ReportLabEngine)
            self.register_engine("pymupdf", PyMuPDFEngine)
            self.register_engine("fitz", PyMuPDFEngine)
        except ImportError as e:
            logger.warning(f"Could not register some default PDF engines: {e}")

    def get_engine(self, name: str, config: dict[str, Any] | None = None):
        name = name.lower()
        if name not in self.engines:
            available = ", ".join(self.engines.keys())
            raise EngineNotFoundError(f"Unknown PDF engine: {name}. Available engines: {available}")

        cache_key = f"{name}_{hash(str(sorted((config or {}).items())))}"
        if cache_key in self._engine_cache:
            return self._engine_cache[cache_key]

        try:
            engine_class = self.engines[name]
            engine = engine_class()

            if config:
                engine_config = config.get(name, {})
                engine.initialize(engine_config)
            else:
                engine.initialize({})

            self._engine_cache[cache_key] = engine
            return engine

        except Exception as e:
            raise EngineInitializationError(f"Failed to initialize PDF engine {name}: {e!s}")

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

    def get_default_engine(self, config: dict[str, Any] | None = None) -> PDFRenderingEngine:
        if config is None:
            config = {}

        default_engine = config.get("default_engine", "reportlab").lower()

        try:
            return self.get_engine(default_engine, config)
        except Exception:
            fallback_engines = ["reportlab", "pymupdf", "fitz"]
            for fallback in fallback_engines:
                if fallback != default_engine and fallback in self.engines:
                    try:
                        return self.get_engine(fallback, config)
                    except Exception:
                        continue
            raise


class InputEngineSelector(EngineSelector):
    def __init__(self):
        super().__init__()
        self.register_default_engines()

    def register_default_engines(self):
        try:
            from pdfrebuilder.engine.krita_engine import KritaInputEngine

            self.register_engine("krita", KritaInputEngine)
        except ImportError as e:
            logger.warning(f"Could not register some default input engines: {e}")


class OutputEngineSelector(EngineSelector):
    def __init__(self):
        super().__init__()
        self.register_default_engines()

    def register_default_engines(self):
        try:
            from pdfrebuilder.engine.krita_engine import KritaOutputEngine
            from pdfrebuilder.engine.wand_image_engine import WandImageOutputEngine

            self.register_engine("krita", KritaOutputEngine)
            self.register_engine("wand_image", WandImageOutputEngine)
        except ImportError as e:
            logger.warning(f"Could not register some default output engines: {e}")


_pdf_engine_selector = None
_input_engine_selector = None
_output_engine_selector = None


def get_pdf_engine_selector():
    global _pdf_engine_selector
    if _pdf_engine_selector is None:
        _pdf_engine_selector = PDFEngineSelector()
    return _pdf_engine_selector


def get_input_engine_selector():
    global _input_engine_selector
    if _input_engine_selector is None:
        _input_engine_selector = InputEngineSelector()
    return _input_engine_selector


def get_output_engine_selector():
    global _output_engine_selector
    if _output_engine_selector is None:
        _output_engine_selector = OutputEngineSelector()
    return _output_engine_selector


def get_input_engine(engine_name: str, config: dict | None = None) -> DocumentParser:
    """Get an input engine instance."""
    selector = get_input_engine_selector()
    return selector.get_engine(engine_name, config)


def get_output_engine(engine_name: str, config: dict | None = None) -> DocumentRenderer:
    """Get an output engine instance."""
    selector = get_output_engine_selector()
    return selector.get_engine(engine_name, config)
