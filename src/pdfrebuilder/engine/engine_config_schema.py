"""
Engine Configuration Schema

This module defines JSON schemas for validating engine-specific configurations
and provides validation utilities for engine settings.
"""

import logging
from typing import Any, TypedDict, cast

import jsonschema

try:
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

logger = logging.getLogger(__name__)

# Main engine configuration schema
ENGINE_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "default_engine": {
            "type": "string",
            "enum": ["reportlab", "pymupdf", "fitz"],
            "default": "reportlab",
            "description": "Default PDF rendering engine to use",
        },
        "reportlab": {
            "type": "object",
            "properties": {
                "compression": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 9,
                    "default": 1,
                    "description": "PDF compression level (0=none, 9=maximum)",
                },
                "page_mode": {
                    "type": "string",
                    "enum": ["portrait", "landscape"],
                    "default": "portrait",
                    "description": "Default page orientation",
                },
                "embed_fonts": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to embed fonts in the PDF",
                },
                "font_subsetting": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to subset embedded fonts",
                },
                "image_compression": {
                    "type": "string",
                    "enum": ["none", "jpeg", "flate"],
                    "default": "jpeg",
                    "description": "Image compression method",
                },
                "color_space": {
                    "type": "string",
                    "enum": ["rgb", "cmyk", "gray"],
                    "default": "rgb",
                    "description": "Default color space",
                },
                "precision": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 10.0,
                    "default": 1.0,
                    "description": "Coordinate precision multiplier",
                },
            },
            "additionalProperties": False,
        },
        "pymupdf": {
            "type": "object",
            "properties": {
                "overlay_mode": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to use overlay mode for rendering",
                },
                "annotation_mode": {
                    "type": "string",
                    "enum": ["preserve", "ignore", "remove"],
                    "default": "ignore",
                    "description": "How to handle existing annotations",
                },
                "compression": {
                    "type": "string",
                    "enum": ["none", "flate", "lzw"],
                    "default": "flate",
                    "description": "PDF compression method",
                },
                "image_quality": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 85,
                    "description": "JPEG image quality (1-100)",
                },
                "text_rendering_mode": {
                    "type": "string",
                    "enum": ["fill", "stroke", "fill_stroke", "invisible"],
                    "default": "fill",
                    "description": "Text rendering mode",
                },
                "anti_aliasing": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to use anti-aliasing",
                },
                "optimize_for_web": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to optimize PDF for web viewing",
                },
            },
            "additionalProperties": False,
        },
        "performance": {
            "type": "object",
            "properties": {
                "enable_caching": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to enable engine caching",
                },
                "cache_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 100,
                    "description": "Maximum number of cached engines",
                },
                "parallel_rendering": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to enable parallel rendering",
                },
                "max_workers": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 32,
                    "default": 4,
                    "description": "Maximum number of worker threads",
                },
            },
            "additionalProperties": False,
        },
        "debugging": {
            "type": "object",
            "properties": {
                "enable_metrics": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to collect performance metrics",
                },
                "log_rendering_details": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to log detailed rendering information",
                },
                "save_intermediate_files": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to save intermediate rendering files",
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

# Default configuration values
DEFAULT_ENGINE_CONFIG = {
    "default_engine": "reportlab",
    "reportlab": {
        "compression": 1,
        "page_mode": "portrait",
        "embed_fonts": True,
        "font_subsetting": True,
        "image_compression": "jpeg",
        "color_space": "rgb",
        "precision": 1.0,
    },
    "pymupdf": {
        "overlay_mode": False,
        "annotation_mode": "ignore",
        "compression": "flate",
        "image_quality": 85,
        "text_rendering_mode": "fill",
        "anti_aliasing": True,
        "optimize_for_web": False,
    },
    "performance": {
        "enable_caching": True,
        "cache_size": 100,
        "parallel_rendering": False,
        "max_workers": 4,
    },
    "debugging": {
        "enable_metrics": False,
        "log_rendering_details": False,
        "save_intermediate_files": False,
    },
}


class EngineConfigValidator:
    """Validator for engine configuration."""

    def __init__(self):
        """Initialize the validator."""
        self.schema = ENGINE_CONFIG_SCHEMA
        self.defaults = DEFAULT_ENGINE_CONFIG

    class ValidationResult(TypedDict):
        """Type definition for validation results."""

        valid: bool
        errors: list[str]
        warnings: list[str]

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """
        Validate engine configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validation result with 'valid', 'errors', and 'warnings' keys
        """
        result: EngineConfigValidator.ValidationResult = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Apply defaults first
        config = self.apply_defaults(config)

        # Validate against schema if jsonschema is available
        if HAS_JSONSCHEMA:
            try:
                jsonschema.validate(config, self.schema)
            except jsonschema.ValidationError as e:
                result["valid"] = False
                result["errors"].append(f"Schema validation error: {e.message}")
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Validation error: {e!s}")

        # Additional validations
        self._validate_engine_compatibility(config, result)
        self._validate_performance_settings(config, result)

        return result

    def _validate_engine_compatibility(self, config: dict[str, Any], result: ValidationResult) -> None:
        """Validate engine-specific compatibility."""
        warnings = result.get("warnings", [])
        default_engine = config.get("default_engine", "reportlab")

        # Check if default engine configuration exists
        if default_engine not in config:
            warnings.append(f"No configuration found for default engine '{default_engine}', using defaults")

        # Validate ReportLab specific settings
        reportlab_config = config.get("reportlab", {})
        if isinstance(reportlab_config, dict) and reportlab_config.get("precision", 1.0) > 5.0:
            warnings.append("High precision values may impact performance")

        # Validate PyMuPDF specific settings
        pymupdf_config = config.get("pymupdf", {})
        if isinstance(pymupdf_config, dict) and pymupdf_config.get("image_quality", 85) < 50:
            warnings.append("Low image quality may result in poor visual output")

        result["warnings"] = warnings

    def _validate_performance_settings(self, config: dict[str, Any], result: ValidationResult) -> None:
        """Validate performance-related settings."""
        warnings = result.get("warnings", [])
        perf_config = config.get("performance", {})

        if not isinstance(perf_config, dict):
            return

        if perf_config.get("parallel_rendering", False) and perf_config.get("max_workers", 4) > 8:
            warnings.append("High worker count may cause resource contention")

        if perf_config.get("cache_size", 100) > 500:
            warnings.append("Large cache size may consume significant memory")

        result["warnings"] = warnings

    def apply_defaults(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Apply default values to configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        result = self.defaults.copy()

        # Deep merge the provided config
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Create a new dict with the updated values
                if isinstance(value, dict):
                    result[key] = {**result[key], **value}
                else:
                    result[key] = value
            else:
                result[key] = value

        return cast(dict[str, Any], result)

    def get_engine_config(self, config: dict[str, Any], engine_name: str) -> dict[str, Any]:
        """
        Get configuration for a specific engine.

        Args:
            config: Full configuration dictionary
            engine_name: Name of the engine

        Returns:
            Engine-specific configuration
        """
        full_config = self.apply_defaults(config)
        return full_config.get(engine_name, {})

    def validate_engine_config(self, config: dict[str, Any], engine_name: str) -> ValidationResult:
        """
        Validate configuration for a specific engine.

        Args:
            config: Configuration dictionary
            engine_name: Name of the engine to validate for

        Returns:
            Validation result with 'valid', 'errors', and 'warnings' keys
        """
        result: EngineConfigValidator.ValidationResult = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        schema_properties = self.schema.get("properties", {})
        if engine_name not in schema_properties:
            result["valid"] = False
            result["errors"].append(f"Unknown engine: {engine_name}")
            return result

        engine_schema = {
            "type": "object",
            "properties": {engine_name: schema_properties[engine_name]},
            "additionalProperties": False,
        }

        engine_config = {engine_name: config.get(engine_name, {})}

        if HAS_JSONSCHEMA:
            try:
                jsonschema.validate(engine_config, engine_schema)
            except jsonschema.ValidationError as e:
                result["valid"] = False
                result["errors"].append(f"Engine {engine_name} validation error: {e.message}")
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Validation error: {e!s}")

        return result


# Global validator instance
_validator: EngineConfigValidator | None = None


def get_config_validator() -> EngineConfigValidator:
    """Get the global configuration validator."""
    global _validator
    if _validator is None:
        _validator = EngineConfigValidator()
    return _validator


def validate_engine_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate engine configuration using the global validator."""
    validator = get_config_validator()
    return validator.validate(config)


def apply_config_defaults(config: dict[str, Any]) -> dict[str, Any]:
    """Apply default values to configuration using the global validator."""
    validator = get_config_validator()
    return validator.apply_defaults(config)


def get_engine_specific_config(config: dict[str, Any], engine_name: str) -> dict[str, Any]:
    """Get engine-specific configuration using the global validator."""
    validator = get_config_validator()
    return validator.get_engine_config(config, engine_name)
