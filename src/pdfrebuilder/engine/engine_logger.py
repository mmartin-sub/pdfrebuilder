"""
Engine logging infrastructure for centralized engine version and status logging.

This module provides centralized logging functionality for PDF engines, handling
version information display, engine selection logging, and fallback scenarios
with appropriate log level awareness.
"""

import logging
import os
import sys
from typing import Any

logger = logging.getLogger(__name__)


class EngineLogger:
    """Centralized engine logging with version information management."""

    @staticmethod
    def log_engine_info(
        engine_name: str,
        engine_version: str,
        load_path: str | None = None,
        log_level: int = logging.DEBUG,
        python_executable: str | None = None,
    ) -> None:
        """
        Log engine version information at appropriate level.

        Args:
            engine_name: Name of the engine (e.g., 'pymupdf', 'reportlab')
            engine_version: Version string of the engine
            load_path: Optional path where the engine library is loaded from
            log_level: Log level to use for the message
            python_executable: Optional Python executable path
        """
        current_logger = logging.getLogger(f"engine.{engine_name}")

        # Always log basic engine info at the specified level
        current_logger.log(log_level, f"{engine_name} engine version: {engine_version}")

        # Log additional details only at DEBUG level
        if current_logger.isEnabledFor(logging.DEBUG):
            if load_path:
                current_logger.debug(f"{engine_name} loaded from: {load_path}")
            if python_executable:
                current_logger.debug(f"Python executable: {python_executable}")

    @staticmethod
    def log_engine_selection(engine_name: str, reason: str = "user_selected") -> None:
        """
        Log engine selection at INFO level.

        Args:
            engine_name: Name of the selected engine
            reason: Reason for selection (user_selected, auto_detected, fallback)
        """
        selection_logger = logging.getLogger("engine.selection")

        if reason == "user_selected":
            selection_logger.info(f"Using {engine_name} engine")
        elif reason == "auto_detected":
            selection_logger.info(f"Auto-detected {engine_name} engine")
        elif reason == "fallback":
            selection_logger.warning(f"Falling back to {engine_name} engine")
        else:
            selection_logger.info(f"Using {engine_name} engine ({reason})")

    @staticmethod
    def log_engine_fallback(from_engine: str, to_engine: str, reason: str) -> None:
        """
        Log engine fallback with version info regardless of log level.

        Args:
            from_engine: Name of the engine that failed
            to_engine: Name of the fallback engine
            reason: Reason for the fallback
        """
        fallback_logger = logging.getLogger("engine.fallback")

        # Always log fallback at WARNING level
        fallback_logger.warning(f"Engine fallback: {from_engine} -> {to_engine}")
        fallback_logger.warning(f"Fallback reason: {reason}")

    @staticmethod
    def log_engine_initialization(engine_name: str, config: dict[str, Any]) -> None:
        """
        Log engine initialization at DEBUG level.

        Args:
            engine_name: Name of the engine being initialized
            config: Engine configuration dictionary
        """
        init_logger = logging.getLogger(f"engine.{engine_name}.init")

        if init_logger.isEnabledFor(logging.DEBUG):
            init_logger.debug(f"Initializing {engine_name} engine")
            init_logger.debug(f"Engine configuration: {config}")

    @staticmethod
    def log_engine_error(engine_name: str, error: Exception, show_version: bool = True) -> None:
        """
        Log engine errors with optional version information.

        Args:
            engine_name: Name of the engine that encountered an error
            error: The exception that occurred
            show_version: Whether to display version information for troubleshooting
        """
        error_logger = logging.getLogger(f"engine.{engine_name}.error")

        error_logger.error(f"{engine_name} engine error: {error!s}")

        if show_version:
            # For errors, we want to show version info to help with troubleshooting
            try:
                version_info = EngineLogger._get_engine_version_info(engine_name)
                if version_info:
                    error_logger.error(f"Engine version info: {version_info}")
            except Exception as e:
                error_logger.debug(f"Could not retrieve version info: {e}")

    @staticmethod
    def _get_engine_version_info(engine_name: str) -> dict[str, str] | None:
        """
        Get version information for a specific engine.

        Args:
            engine_name: Name of the engine

        Returns:
            Dictionary with version information or None if unavailable
        """
        try:
            if engine_name.lower() in ["pymupdf", "fitz"]:
                import fitz

                return {
                    "engine": "pymupdf",
                    "version": fitz.__version__,
                    "load_path": os.path.dirname(fitz.__file__),
                    "python_executable": sys.executable,
                }
            elif engine_name.lower() == "reportlab":
                import reportlab

                return {
                    "engine": "reportlab",
                    "version": getattr(reportlab, "__version__", "unknown"),
                    "load_path": os.path.dirname(reportlab.__file__),
                    "python_executable": sys.executable,
                }
            elif engine_name.lower() == "wand":
                from wand import version as wand_version

                return {
                    "engine": "wand",
                    "version": wand_version.VERSION,
                    "load_path": os.path.dirname(wand_version.__file__),
                    "python_executable": sys.executable,
                }
        except ImportError:
            return None
        except Exception:
            return None

        return None

    @staticmethod
    def should_show_version_info(log_level: int | None = None) -> bool:
        """
        Determine if version information should be displayed based on current log level.

        Args:
            log_level: Optional specific log level to check against

        Returns:
            True if version info should be shown, False otherwise
        """
        if log_level is None:
            # Check the root logger's effective level
            root_logger = logging.getLogger()
            return root_logger.isEnabledFor(logging.DEBUG)
        else:
            return log_level <= logging.DEBUG

    @staticmethod
    def log_available_engines() -> None:
        """Log information about available engines at INFO level."""
        engines_logger = logging.getLogger("engine.available")

        available_engines = []

        # Check PyMuPDF
        try:
            import fitz

            available_engines.append(f"pymupdf ({fitz.__version__})")
        except ImportError:
            pass

        # Check ReportLab
        try:
            import reportlab

            version = getattr(reportlab, "__version__", "unknown")
            available_engines.append(f"reportlab ({version})")
        except ImportError:
            pass

        # Check Wand
        try:
            from wand import version as wand_version

            available_engines.append(f"wand ({wand_version.VERSION})")
        except ImportError:
            pass

        if available_engines:
            engines_logger.info(f"Available engines: {', '.join(available_engines)}")
        else:
            engines_logger.warning("No PDF engines available")
