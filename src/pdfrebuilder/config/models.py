"""Configuration data models for pdfrebuilder."""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, validator


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EngineType(str, Enum):
    """Available processing engines."""

    AUTO = "auto"
    FITZ = "fitz"
    REPORTLAB = "reportlab"
    WAND = "wand"
    PSD_TOOLS = "psd-tools"


class ExtractionConfig(BaseModel):
    """Configuration for PDF/document extraction."""

    include_text: bool = True
    include_images: bool = True
    include_drawings: bool = True
    include_raw_backgrounds: bool = False
    engine: EngineType = EngineType.AUTO
    normalize_text_spacing: bool = True
    extract_fonts: bool = True
    preserve_layers: bool = True

    class Config:
        env_prefix = "PDFREBUILDER_EXTRACTION_"


class RebuildConfig(BaseModel):
    """Configuration for PDF/document rebuilding."""

    engine: EngineType = EngineType.AUTO
    compression: bool = True
    embed_fonts: bool = True
    output_dpi: int = 300
    preserve_quality: bool = True
    use_original_as_template: bool = False
    optimize_output: bool = True

    class Config:
        env_prefix = "PDFREBUILDER_REBUILD_"


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: LogLevel = LogLevel.INFO
    format_type: str = "standard"  # "standard" or "json"
    log_file: Path | None = None
    enable_console: bool = True
    enable_file_logging: bool = False
    log_rotation: bool = True
    max_log_size: str = "10MB"
    backup_count: int = 5

    class Config:
        env_prefix = "PDFREBUILDER_LOGGING_"


class PathConfig(BaseModel):
    """Configuration for paths and directories."""

    output_dir: Path | None = None
    debug_output_dir: Path | None = None
    test_output_dir: Path | None = None
    reports_output_dir: Path | None = None
    temp_dir: Path | None = None
    cache_dir: Path | None = None
    config_dir: Path | None = None
    font_dir: Path | None = None
    image_dir: Path | None = None
    log_dir: Path | None = None

    class Config:
        env_prefix = "PDFREBUILDER_PATHS_"


class SecurityConfig(BaseModel):
    """Configuration for security settings."""

    validate_paths: bool = True
    secure_temp_files: bool = True
    max_file_size: str = "100MB"
    allowed_extensions: list[str] = Field(default_factory=lambda: [".pdf", ".psd", ".png", ".jpg", ".jpeg"])
    sanitize_filenames: bool = True
    restrict_output_paths: bool = True

    class Config:
        env_prefix = "PDFREBUILDER_SECURITY_"


class PerformanceConfig(BaseModel):
    """Configuration for performance settings."""

    max_memory_usage: str = "1GB"
    parallel_processing: bool = True
    max_workers: int | None = None
    chunk_size: int = 1024 * 1024  # 1MB
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour

    class Config:
        env_prefix = "PDFREBUILDER_PERFORMANCE_"


class PDFRebuilderConfig(BaseModel):
    """Main configuration model for pdfrebuilder."""

    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    rebuild: RebuildConfig = Field(default_factory=RebuildConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    # Environment-specific settings
    environment: str = "production"  # development, testing, production
    debug: bool = False
    verbose: bool = False

    # CLI-specific settings
    quiet: bool = False
    force: bool = False
    dry_run: bool = False

    class Config:
        env_prefix = "PDFREBUILDER_"
        case_sensitive = False

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "testing", "production", "ci"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v

    @validator("debug")
    def set_debug_defaults(cls, v, values):
        """Set debug-related defaults when debug mode is enabled."""
        if v and "logging" in values:
            values["logging"].level = LogLevel.DEBUG
            values["logging"].enable_console = True
        return v


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""


def validate_config(config: PDFRebuilderConfig) -> None:
    """Validate configuration and raise errors for invalid settings."""
    # Validate path configurations
    if config.paths.output_dir and not config.paths.output_dir.parent.exists():
        raise ConfigValidationError(f"Output directory parent does not exist: {config.paths.output_dir.parent}")

    # Validate security settings
    if config.security.max_file_size:
        try:
            _parse_size(config.security.max_file_size)
        except ValueError as e:
            raise ConfigValidationError(f"Invalid max_file_size format: {e}")

    # Validate performance settings
    if config.performance.max_memory_usage:
        try:
            _parse_size(config.performance.max_memory_usage)
        except ValueError as e:
            raise ConfigValidationError(f"Invalid max_memory_usage format: {e}")


def _parse_size(size_str: str) -> int:
    """Parse size string like '100MB' to bytes."""
    if not isinstance(size_str, str):
        return int(size_str)

    size_str = size_str.upper().strip()

    multipliers = {
        "TB": 1024**4,
        "GB": 1024**3,
        "MB": 1024**2,
        "KB": 1024,
        "B": 1,
    }

    # Check suffixes in order of length (longest first)
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            number_str = size_str[: -len(suffix)].strip()
            try:
                if not number_str:
                    raise ValueError(f"No number found in size string: {size_str}")
                number = float(number_str)
                return int(number * multiplier)
            except ValueError as e:
                if "could not convert" in str(e) or "invalid literal" in str(e):
                    raise ValueError(f"Invalid number in size format: {size_str}")
                raise ValueError(f"Invalid size format: {size_str}")

    # Try parsing as plain number (bytes)
    try:
        return int(float(size_str))
    except ValueError:
        raise ValueError(f"Invalid size format: {size_str}")
