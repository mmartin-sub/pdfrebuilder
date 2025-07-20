"""
Configuration Loader for Engine Selection

This module provides utilities for loading and validating engine configurations
from various sources including JSON files, environment variables, and CLI arguments.
"""

import json
import logging
import os
from typing import Any

from pdfrebuilder.engine.engine_config_schema import (
    EngineConfigValidator,
    apply_config_defaults,
    get_config_validator,
    validate_engine_config,
)

logger = logging.getLogger(__name__)


class EngineConfigLoader:
    """Loader for engine configurations."""

    def __init__(self):
        """Initialize the configuration loader."""
        self.validator = get_config_validator()

    def load_from_file(self, config_path: str) -> dict[str, Any]:
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid JSON
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                config = json.load(f)

            logger.info(f"Loaded configuration from: {config_path}")
            return config

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration file {config_path}: {e}")

    def load_from_env(self, prefix: str = "PDF_ENGINE_") -> dict[str, Any]:
        """
        Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix

        Returns:
            Configuration dictionary
        """
        config: dict[str, Any] = {}

        # Load general settings
        default_engine = os.getenv(f"{prefix}DEFAULT", "reportlab")
        config["default_engine"] = default_engine

        # Load ReportLab settings
        reportlab_config: dict[str, Any] = {}
        _val = os.getenv(f"{prefix}REPORTLAB_COMPRESSION")
        if _val is not None:
            reportlab_config["compression"] = int(_val)
        _val = os.getenv(f"{prefix}REPORTLAB_PAGE_MODE")
        if _val is not None:
            reportlab_config["page_mode"] = _val
        _val = os.getenv(f"{prefix}REPORTLAB_EMBED_FONTS")
        if _val is not None:
            reportlab_config["embed_fonts"] = _val.lower() == "true"

        if reportlab_config:
            config["reportlab"] = reportlab_config

        # Load PyMuPDF settings
        pymupdf_config: dict[str, Any] = {}
        _val = os.getenv(f"{prefix}PYMUPDF_OVERLAY_MODE")
        if _val is not None:
            pymupdf_config["overlay_mode"] = _val.lower() == "true"
        _val = os.getenv(f"{prefix}PYMUPDF_ANNOTATION_MODE")
        if _val is not None:
            pymupdf_config["annotation_mode"] = _val
        _val = os.getenv(f"{prefix}PYMUPDF_COMPRESSION")
        if _val is not None:
            pymupdf_config["compression"] = _val
        _val = os.getenv(f"{prefix}PYMUPDF_IMAGE_QUALITY")
        if _val is not None:
            pymupdf_config["image_quality"] = int(_val)

        if pymupdf_config:
            config["pymupdf"] = pymupdf_config

        if config:
            logger.info(f"Loaded configuration from environment variables with prefix: {prefix}")

        return config

    def merge_configs(self, *configs: dict[str, Any]) -> dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Args:
            *configs: Configuration dictionaries to merge

        Returns:
            Merged configuration dictionary
        """
        merged: dict[str, Any] = {}

        for config in configs:
            if not config:
                continue

            for key, value in config.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    # Deep merge dictionaries
                    merged[key] = {**merged[key], **value}
                else:
                    merged[key] = value

        return merged

    def load_complete_config(
        self,
        config_file: str | None = None,
        cli_args: dict[str, Any] | None = None,
        env_prefix: str = "PDF_ENGINE_",
    ) -> dict[str, Any]:
        """
        Load complete configuration from all sources.

        Args:
            config_file: Optional path to configuration file
            cli_args: Optional CLI arguments dictionary
            env_prefix: Environment variable prefix

        Returns:
            Complete configuration dictionary with defaults applied
        """
        configs = []

        # 1. Start with defaults
        configs.append(apply_config_defaults({}))

        # 2. Load from environment variables
        env_config = self.load_from_env(env_prefix)
        if env_config:
            configs.append(env_config)

        # 3. Load from file
        if config_file and os.path.exists(config_file):
            try:
                file_config = self.load_from_file(config_file)
                configs.append(file_config)
            except Exception as e:
                logger.warning(f"Could not load config file {config_file}: {e}")

        # 4. Apply CLI arguments
        if cli_args:
            cli_config = self._cli_args_to_config(cli_args)
            if cli_config:
                configs.append(cli_config)

        # Merge all configurations
        merged_config = self.merge_configs(*configs)

        # Validate the final configuration
        validation_result = validate_engine_config(merged_config)
        if not validation_result["valid"]:
            logger.warning(f"Configuration validation errors: {validation_result['errors']}")

        if validation_result.get("warnings"):
            for warning in validation_result["warnings"]:
                logger.warning(f"Configuration warning: {warning}")

        return merged_config

    def _cli_args_to_config(self, cli_args: dict[str, Any]) -> dict[str, Any]:
        """
        Convert CLI arguments to configuration format.

        Args:
            cli_args: CLI arguments dictionary

        Returns:
            Configuration dictionary
        """
        config = {}

        # Map CLI arguments to configuration
        if "output_engine" in cli_args and cli_args["output_engine"] != "auto":
            config["default_engine"] = cli_args["output_engine"]

        # Add other CLI-to-config mappings as needed

        return config

    def save_config(self, config: dict[str, Any], output_path: str) -> None:
        """
        Save configuration to a JSON file.

        Args:
            config: Configuration dictionary to save
            output_path: Path where to save the configuration
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(config, f, indent=2, sort_keys=True)

            logger.info(f"Configuration saved to: {output_path}")

        except Exception as e:
            logger.error(f"Error saving configuration to {output_path}: {e}")
            raise

    def get_engine_config(self, config: dict[str, Any], engine_name: str) -> dict[str, Any]:
        """
        Get configuration for a specific engine.

        Args:
            config: Complete configuration dictionary
            engine_name: Name of the engine

        Returns:
            Engine-specific configuration
        """
        return self.validator.get_engine_config(config, engine_name)

    def validate_config(self, config: dict[str, Any]) -> "EngineConfigValidator.ValidationResult":
        """
        Validate a configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            Dictionary containing validation results with 'valid', 'errors', and 'warnings' keys
        """
        validation_result = self.validator.validate(config)
        # ValidationResult is already a TypedDict with the correct structure
        return validation_result


# Global configuration loader instance
_config_loader: EngineConfigLoader | None = None


def get_config_loader() -> EngineConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = EngineConfigLoader()
    return _config_loader


def load_engine_config(config_file: str | None = None, cli_args: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Load engine configuration from all sources.

    Args:
        config_file: Optional path to configuration file
        cli_args: Optional CLI arguments dictionary

    Returns:
        Complete configuration dictionary
    """
    loader = get_config_loader()
    return loader.load_complete_config(config_file, cli_args)


def get_engine_specific_config(config: dict[str, Any], engine_name: str) -> dict[str, Any]:
    """
    Get engine-specific configuration.

    Args:
        config: Complete configuration dictionary
        engine_name: Name of the engine

    Returns:
        Engine-specific configuration
    """
    loader = get_config_loader()
    return loader.get_engine_config(config, engine_name)
