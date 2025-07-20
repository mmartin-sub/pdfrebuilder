"""Configuration manager for pdfrebuilder."""

import json
import os
import tomllib
from pathlib import Path
from typing import Any

from platformdirs import user_cache_dir, user_config_dir, user_data_dir

from .models import ConfigValidationError, PDFRebuilderConfig, validate_config


class ConfigManager:
    """Manages hierarchical configuration with platform-appropriate directories."""

    def __init__(self, app_name: str = "pdfrebuilder", config_file: str | Path | None = None):
        """Initialize configuration manager.

        Args:
            app_name: Application name for directory creation
            config_file: Optional path to specific configuration file
        """
        self.app_name = app_name
        self._config_file = Path(config_file) if config_file else None

        # Platform-appropriate directories
        self._config_dir = Path(user_config_dir(app_name))
        self._data_dir = Path(user_data_dir(app_name))
        self._cache_dir = Path(user_cache_dir(app_name))

        # Create directories
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self._config = self._load_config()

    @property
    def config_dir(self) -> Path:
        """Get configuration directory."""
        return self._config_dir

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self._data_dir

    @property
    def cache_dir(self) -> Path:
        """Get cache directory."""
        return self._cache_dir

    @property
    def config(self) -> PDFRebuilderConfig:
        """Get current configuration."""
        return self._config

    def _load_config(self) -> PDFRebuilderConfig:
        """Load configuration from multiple sources in priority order."""
        config_data = {}

        # 1. Load defaults (handled by Pydantic defaults)

        # 2. Load system config (if exists)
        system_config = self._load_system_config()
        if system_config:
            config_data.update(system_config)

        # 3. Load user config
        user_config = self._load_user_config()
        if user_config:
            config_data.update(user_config)

        # 4. Load specific config file (if provided)
        if self._config_file:
            file_config = self._load_config_file(self._config_file)
            if file_config:
                config_data.update(file_config)

        # 5. Load environment variables (handled by Pydantic)

        # Create configuration object
        try:
            config = PDFRebuilderConfig(**config_data)
            validate_config(config)
            return config
        except Exception as e:
            raise ConfigValidationError(f"Failed to load configuration: {e}")

    def _load_system_config(self) -> dict[str, Any] | None:
        """Load system-wide configuration."""
        # System config locations vary by platform
        system_paths = [
            Path("/etc") / self.app_name / "config.toml",
            Path("/usr/local/etc") / self.app_name / "config.toml",
        ]

        for path in system_paths:
            if path.exists():
                return self._load_config_file(path)

        return None

    def _load_user_config(self) -> dict[str, Any] | None:
        """Load user configuration."""
        config_files = [
            self._config_dir / "config.toml",
            self._config_dir / "config.json",
            Path.home() / f".{self.app_name}.toml",
            Path.home() / f".{self.app_name}.json",
        ]

        for config_file in config_files:
            if config_file.exists():
                return self._load_config_file(config_file)

        return None

    def _load_config_file(self, config_path: Path) -> dict[str, Any] | None:
        """Load configuration from a specific file."""
        try:
            if config_path.suffix.lower() == ".toml":
                with open(config_path, "rb") as f:
                    return tomllib.load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path) as f:
                    return json.load(f)
            else:
                # Try to detect format by content
                with open(config_path) as f:
                    content = f.read().strip()
                    if content.startswith("{"):
                        return json.loads(content)
                    else:
                        # Assume TOML
                        return tomllib.loads(content)
        except Exception as e:
            import logging

            logging.getLogger(f"{self.app_name}.config").warning(f"Failed to load config file {config_path}: {e}")
            return None

    def save_user_config(self, config: PDFRebuilderConfig | None = None) -> None:
        """Save configuration to user config file."""
        if config is None:
            config = self._config

        config_file = self._config_dir / "config.toml"
        config_data = config.dict()

        # Convert to TOML format
        try:
            import tomli_w

            with open(config_file, "wb") as f:
                tomli_w.dump(config_data, f)
        except ImportError:
            # Fallback to JSON if tomli_w not available
            config_file = self._config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(config_data, f, indent=2, default=str)

    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
        config_data = self._config.dict()

        # Update nested configuration
        for key, value in kwargs.items():
            if "." in key:
                # Handle nested keys like 'logging.level'
                keys = key.split(".")
                current = config_data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            else:
                config_data[key] = value

        # Recreate configuration object
        try:
            self._config = PDFRebuilderConfig(**config_data)
            validate_config(self._config)
        except Exception as e:
            raise ConfigValidationError(f"Failed to update configuration: {e}")

    def get_effective_config(self) -> dict[str, Any]:
        """Get the effective configuration including all sources."""
        return self._config.dict()

    def generate_sample_config(self, output_path: Path | None = None) -> Path:
        """Generate a sample configuration file with all options documented."""
        if output_path is None:
            output_path = self._config_dir / "sample_config.toml"

        sample_config = self._generate_sample_config_content()

        with open(output_path, "w") as f:
            f.write(sample_config)

        return output_path

    def _generate_sample_config_content(self) -> str:
        """Generate sample configuration content with documentation."""
        return """# PDFRebuilder Configuration File
# This file contains all available configuration options with their default values
# Uncomment and modify the options you want to change

# Environment: development, testing, production, ci
# environment = "production"

# Enable debug mode (sets logging to DEBUG level)
# debug = false

# Enable verbose output
# verbose = false

[extraction]
# Include text elements in extraction
# include_text = true

# Include image elements in extraction
# include_images = true

# Include drawing/vector elements in extraction
# include_drawings = true

# Include raw background elements
# include_raw_backgrounds = false

# Processing engine: auto, fitz, reportlab, wand, psd-tools
# engine = "auto"

# Normalize text spacing issues
# normalize_text_spacing = true

# Extract font information
# extract_fonts = true

# Preserve layer information (for PSD files)
# preserve_layers = true

[rebuild]
# Processing engine for rebuilding: auto, fitz, reportlab, wand
# engine = "auto"

# Enable compression in output files
# compression = true

# Embed fonts in output PDF
# embed_fonts = true

# Output DPI for rasterized elements
# output_dpi = 300

# Preserve original quality
# preserve_quality = true

# Use original document as template background
# use_original_as_template = false

# Optimize output file size
# optimize_output = true

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
# level = "INFO"

# Log format: standard, json
# format_type = "standard"

# Log file path (optional)
# log_file = "/path/to/logfile.log"

# Enable console logging
# enable_console = true

# Enable file logging
# enable_file_logging = false

# Enable log rotation
# log_rotation = true

# Maximum log file size before rotation
# max_log_size = "10MB"

# Number of backup log files to keep
# backup_count = 5

[paths]
# Default output directory
# output_dir = "./output"

# Temporary directory for processing
# temp_dir = "/tmp/pdfrebuilder"

# Cache directory for downloaded resources
# cache_dir = "~/.cache/pdfrebuilder"

# Configuration directory
# config_dir = "~/.config/pdfrebuilder"

# Font directory for custom fonts
# font_dir = "./fonts"

# Image extraction directory
# image_dir = "./images"

[security]
# Validate and sanitize file paths
# validate_paths = true

# Use secure permissions for temporary files
# secure_temp_files = true

# Maximum allowed file size for processing
# max_file_size = "100MB"

# Allowed file extensions
# allowed_extensions = [".pdf", ".psd", ".png", ".jpg", ".jpeg"]

# Sanitize filenames to remove dangerous characters
# sanitize_filenames = true

# Restrict output paths to prevent directory traversal
# restrict_output_paths = true

[performance]
# Maximum memory usage for processing
# max_memory_usage = "1GB"

# Enable parallel processing where possible
# parallel_processing = true

# Maximum number of worker processes (null = auto-detect)
# max_workers = null

# Chunk size for processing large files (bytes)
# chunk_size = 1048576

# Enable caching of processed results
# enable_caching = true

# Cache time-to-live in seconds
# cache_ttl = 3600
"""

    def get_environment_variables(self) -> dict[str, str]:
        """Get all relevant environment variables."""
        env_vars = {}
        prefix = f"{self.app_name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                env_vars[key] = value

        return env_vars

    def validate_current_config(self) -> bool:
        """Validate the current configuration."""
        try:
            validate_config(self._config)
            return True
        except ConfigValidationError:
            return False

    def load_config(
        self,
        config_file: str | Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
    ) -> PDFRebuilderConfig:
        """Load configuration with optional file and CLI overrides.

        Args:
            config_file: Optional path to configuration file
            cli_overrides: Optional dictionary of CLI argument overrides

        Returns:
            Loaded and validated configuration
        """
        # Update config file if provided
        if config_file:
            self._config_file = Path(config_file)

        # Reload configuration
        config_data = {}

        # 1. Load system config
        system_config = self._load_system_config()
        if system_config:
            config_data.update(system_config)

        # 2. Load user config
        user_config = self._load_user_config()
        if user_config:
            config_data.update(user_config)

        # 3. Load specific config file
        if self._config_file and self._config_file.exists():
            file_config = self._load_config_file(self._config_file)
            if file_config:
                config_data.update(file_config)

        # 4. Apply CLI overrides
        if cli_overrides:
            config_data.update(cli_overrides)

        # Create and validate configuration
        try:
            self._config = PDFRebuilderConfig(**config_data)
            validate_config(self._config)
            return self._config
        except Exception as e:
            raise ConfigValidationError(f"Failed to load configuration: {e}")

    def show_config(self) -> str:
        """Return a formatted string showing the current effective configuration."""
        config_dict = self._config.dict()

        output_lines = ["Current PDFRebuilder Configuration:"]
        output_lines.append("=" * 40)

        def format_section(data: dict[str, Any], indent: int = 0) -> None:
            """Recursively format configuration sections."""
            for key, value in data.items():
                prefix = "  " * indent
                if isinstance(value, dict):
                    output_lines.append(f"{prefix}[{key}]")
                    format_section(value, indent + 1)
                else:
                    output_lines.append(f"{prefix}{key} = {value}")

        format_section(config_dict)

        # Add environment variables section
        env_vars = self.get_environment_variables()
        if env_vars:
            output_lines.append("")
            output_lines.append("Environment Variables:")
            output_lines.append("-" * 20)
            for key, value in env_vars.items():
                output_lines.append(f"{key} = {value}")

        return "\n".join(output_lines)
