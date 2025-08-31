"""
Test logging configuration to suppress verbose output from third-party libraries.

This module provides utilities to configure logging for test environments,
specifically to reduce verbosity from libraries like fontTools.
"""

import logging
import os


def configure_test_logging(
    level: int = logging.WARNING,
    suppress_fonttools: bool = True,
    suppress_other_libs: bool = True,
) -> None:
    """
    Configure logging for test environments to reduce verbosity.

    Args:
        level: Base logging level for the application
        suppress_fonttools: Whether to suppress fontTools debug output
        suppress_other_libs: Whether to suppress other verbose libraries
    """
    # Set base logging level
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )

    # Suppress fontTools logging
    if suppress_fonttools:
        fonttools_loggers = [
            "fontTools.ttLib.ttFont",
            "fontTools.ttLib",
            "fontTools",
        ]
        for logger_name in fonttools_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Suppress other verbose libraries
    if suppress_other_libs:
        verbose_loggers = [
            "PIL",
            "Pillow",
            "fitz",
            "PyMuPDF",
        ]
        for logger_name in verbose_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)


def setup_quiet_test_environment() -> None:
    """
    Set up a quiet test environment with minimal logging output.

    This function configures logging to suppress verbose output from
    third-party libraries commonly used in this project.
    """
    # Check environment variable for logging level
    log_level_env = os.environ.get("FONTTOOLS_LOG_LEVEL", "WARNING").upper()

    if log_level_env == "WARNING":
        # Default quiet mode
        configure_test_logging(
            level=logging.WARNING,
            suppress_fonttools=True,
            suppress_other_libs=True,
        )
    elif log_level_env == "INFO":
        # Verbose mode - show more output but still suppress fontTools
        configure_test_logging(
            level=logging.INFO,
            suppress_fonttools=False,
            suppress_other_libs=False,
        )
    elif log_level_env == "DEBUG":
        # Full debug mode - show everything
        configure_test_logging(
            level=logging.DEBUG,
            suppress_fonttools=False,
            suppress_other_libs=False,
        )
    else:
        # Default to quiet mode
        configure_test_logging(
            level=logging.WARNING,
            suppress_fonttools=True,
            suppress_other_libs=True,
        )


# Auto-configure when imported
if __name__ != "__main__":
    setup_quiet_test_environment()
