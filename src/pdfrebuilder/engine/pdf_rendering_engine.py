"""
PDF Rendering Engine Interface

This module defines the abstract base class for PDF rendering engines,
providing a common interface for different PDF generation backends.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class EngineError(Exception):
    """Base exception for all engine-related errors"""


class EngineNotFoundError(EngineError):
    """Raised when a requested engine is not available"""


class EngineInitializationError(EngineError):
    """Raised when an engine fails to initialize"""


class RenderingError(EngineError):
    """Raised when an error occurs during rendering"""


class UnsupportedFeatureError(EngineError):
    """Raised when an engine doesn't support a requested feature"""


class PDFRenderingEngine(ABC):
    """Abstract base class for PDF rendering engines"""

    # Engine metadata - must be defined by subclasses
    engine_name: str = "unknown"
    engine_version: str = "unknown"
    supported_features: dict[str, bool] = {}

    def __init__(self):
        """Initialize the engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        self._config: dict[str, Any] = {}

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        """
        Initialize the engine with configuration.

        Args:
            config: Engine-specific configuration dictionary

        Raises:
            EngineInitializationError: If initialization fails
        """

    @abstractmethod
    def create_document(self, metadata: dict[str, Any]) -> Any:
        """
        Create a new document with the given metadata.

        Args:
            metadata: Document metadata dictionary

        Returns:
            Engine-specific document object

        Raises:
            RenderingError: If document creation fails
        """

    @abstractmethod
    def add_page(
        self,
        document: Any,
        size: tuple[float, float],
        background_color: Any | None = None,
    ) -> Any:
        """
        Add a new page to the document.

        Args:
            document: Engine-specific document object
            size: Page size as (width, height) tuple
            background_color: Optional background color

        Returns:
            Engine-specific page object

        Raises:
            RenderingError: If page creation fails
        """

    @abstractmethod
    def render_element(self, page: Any, element: dict[str, Any], resources: dict[str, Any]) -> dict[str, Any]:
        """
        Render an element on the page.

        Args:
            page: Engine-specific page object
            element: Element data dictionary
            resources: Available resources (fonts, images, etc.)

        Returns:
            Rendering result dictionary with status and metrics

        Raises:
            RenderingError: If element rendering fails
            UnsupportedFeatureError: If element type is not supported
        """

    @abstractmethod
    def finalize_document(self, document: Any, output_path: str) -> None:
        """
        Finalize and save the document.

        Args:
            document: Engine-specific document object
            output_path: Path where to save the document

        Raises:
            RenderingError: If document finalization fails
        """

    @abstractmethod
    def generate(
        self,
        config: dict[str, Any],
        output_pdf_path: str,
        original_pdf_for_template: str | None = None,
    ) -> None:
        """
        Generate a PDF from a universal document configuration.

        Args:
            config: Document configuration dictionary
            output_pdf_path: Output PDF file path
            original_pdf_for_template: Optional path to an original PDF for overlay/template

        Raises:
            RenderingError: If PDF generation fails
        """

    @abstractmethod
    def get_engine_info(self) -> dict[str, Any]:
        """
        Get information about the engine.

        Returns:
            Dictionary containing engine information
        """

    def is_feature_supported(self, feature: str) -> bool:
        """
        Check if a feature is supported by this engine.

        Args:
            feature: Feature name to check

        Returns:
            True if feature is supported, False otherwise
        """
        return self.supported_features.get(feature, False)

    def warn_unsupported_feature(self, feature: str, context: str = "") -> None:
        """
        Log a warning for unsupported features.

        Args:
            feature: Name of the unsupported feature
            context: Additional context information
        """
        msg = f"Feature '{feature}' is not supported by {self.engine_name}"
        if context:
            msg += f". Context: {context}"
        self.logger.warning(msg)

    def validate_font_licensing(self, font_name: str) -> dict[str, Any]:
        """
        Validate font licensing for embedding.

        Default implementation returns an unknown status. Engines that support
        font validation (e.g., ReportLab) should override this method.

        Args:
            font_name: Name of the font to validate

        Returns:
            Dictionary with validation details
        """
        return {
            "font_name": font_name,
            "available": False,
            "embeddable": False,
            "status": "unknown",
            "reason": "Font licensing validation not supported by this engine",
        }

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate engine configuration.

        Args:
            config: Configuration to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Basic validation - subclasses can override for specific validation
            required_keys = getattr(self, "required_config_keys", [])
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                return {
                    "valid": False,
                    "errors": [f"Missing required configuration keys: {missing_keys}"],
                }

            return {"valid": True, "errors": []}

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Configuration validation error: {e!s}"],
            }

    def get_performance_metrics(self) -> dict[str, Any]:
        """
        Get performance metrics for this engine.

        Returns:
            Dictionary containing performance metrics
        """
        return {
            "engine": self.engine_name,
            "version": self.engine_version,
            "initialized": self._initialized,
            "supported_features_count": len([f for f, supported in self.supported_features.items() if supported]),
        }

    def __str__(self) -> str:
        """String representation of the engine."""
        return f"{self.engine_name} v{self.engine_version}"

    def log_initialization(self) -> None:
        """Log engine initialization with version info at DEBUG level."""
        from pdfrebuilder.engine.engine_logger import EngineLogger

        EngineLogger.log_engine_initialization(self.engine_name, self._config)

        # Log version information at DEBUG level
        version_info = self.get_version_info()
        if version_info and EngineLogger.should_show_version_info():
            EngineLogger.log_engine_info(
                engine_name=self.engine_name,
                engine_version=version_info.get("engine_version", self.engine_version),
                load_path=version_info.get("load_path"),
                python_executable=version_info.get("python_executable"),
            )

    def get_version_info(self) -> dict[str, Any]:
        """
        Get comprehensive version information for this engine.

        Returns:
            Dictionary containing version information
        """
        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "load_path": None,  # Subclasses should override
            "python_executable": None,  # Subclasses should override
        }

    def __repr__(self) -> str:
        """Detailed string representation of the engine."""
        return f"<{self.__class__.__name__}(name='{self.engine_name}', version='{self.engine_version}')>"
