"""
PDF recreation from configuration file.

This module provides functions for generating PDFs from JSON configuration
using the engine selection system.
"""

import json
import logging
from typing import Any

from pdfrebuilder.engine.config_loader import load_engine_config
from pdfrebuilder.engine.pdf_engine_selector import get_default_pdf_engine, get_pdf_engine

logger = logging.getLogger(__name__)


def recreate_pdf_from_config(
    config_path: str,
    output_pdf_path: str,
    engine_name: str | None = None,
    engine_config: dict[str, Any] | None = None,
    original_pdf_for_template: str | None = None,
    engine: Any = None,
) -> None:
    """
    Generate a PDF from a JSON configuration file.

    Args:
        config_path: Path to the JSON configuration file
        output_pdf_path: Path where the generated PDF should be saved
        engine_name: Optional engine name to use (defaults to configured default)
        engine_config: Optional engine configuration dictionary
        original_pdf_for_template: Optional path to original PDF for template mode
    """
    try:
        # Load the document configuration
        with open(config_path) as f:
            config = json.load(f)

        # Load engine configuration if not provided
        if engine_config is None:
            engine_config = load_engine_config()

        # Select and create the PDF engine
        if engine is None:
            if engine_name:
                try:
                    engine = get_pdf_engine(engine_name, engine_config)
                    logger.info(f"Using specified engine: {engine_name}")
                except Exception as e:
                    logger.warning(f"Could not create engine {engine_name}: {e}")
                    logger.info("Falling back to default engine")
                    engine = get_default_pdf_engine(engine_config)
            else:
                engine = get_default_pdf_engine(engine_config)
                logger.info(f"Using default engine: {engine.engine_name}")

        # Generate the PDF
        engine.generate(config, output_pdf_path, original_pdf_for_template)

        logger.info(f"Successfully generated PDF: {output_pdf_path}")

    except Exception as e:
        logger.error(f"Failed to generate PDF from config {config_path}: {e}")
        raise e


def recreate_pdf_with_engine(
    config_path: str,
    output_pdf_path: str,
    engine_name: str,
    engine_config: dict[str, Any] | None = None,
) -> None:
    """
    Generate a PDF using a specific engine.

    Args:
        config_path: Path to the JSON configuration file
        output_pdf_path: Path where the generated PDF should be saved
        engine_name: Name of the engine to use
        engine_config: Optional engine configuration dictionary
    """
    recreate_pdf_from_config(config_path, output_pdf_path, engine_name, engine_config)


def get_available_engines() -> dict[str, dict[str, Any]]:
    """
    Get information about all available engines.

    Returns:
        Dictionary containing information about available engines
    """
    try:
        from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector

        selector = get_engine_selector()
        return selector.list_available_engines()
    except Exception as e:
        logger.error(f"Error getting available engines: {e}")
        return {}


def validate_engine_configuration(engine_name: str, config: dict[str, Any]) -> dict[str, Any]:
    """
    Validate configuration for a specific engine.

    Args:
        engine_name: Name of the engine to validate for
        config: Configuration dictionary to validate

    Returns:
        Validation result dictionary
    """
    try:
        from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector

        selector = get_engine_selector()
        return selector.validate_engine_config(engine_name, config)
    except Exception as e:
        return {"valid": False, "error": str(e), "engine": engine_name}


def compare_engine_capabilities(engine1: str, engine2: str) -> dict[str, Any]:
    """
    Compare capabilities of two engines.

    Args:
        engine1: Name of the first engine
        engine2: Name of the second engine

    Returns:
        Comparison result dictionary
    """
    try:
        from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector

        selector = get_engine_selector()
        return selector.compare_engines(engine1, engine2)
    except Exception as e:
        return {"error": f"Could not compare engines: {e}"}
