# settings

Configuration management for the Multi-Format Document Engine.

This module provides centralized configuration management with support for dynamic paths,
environment-specific settings, and runtime configuration updates. It manages all system
settings including file paths, font configurations, visual validation thresholds, and
debug options.

Key Features:

- Dynamic path resolution using lambda functions
- Environment-aware configuration
- Centralized configuration dictionary (CONFIG)
- Standard PDF font definitions
- Output directory management

Example:
    from src.settings import CONFIG, get_config_value, set_config_value

    # Get configuration values
    image_dir = get_config_value('image_dir')

    # Set configuration values
    set_config_value('visual_diff_threshold', 10)

## Classes

### OutputConfig

Configuration class for managing output directories

#### Methods

##### __init__()

##### base_output_dir()

Get the base output directory for all outputs

##### base_output_dir(value)

Set the base output directory

##### test_output_dir()

Get the test output directory

##### test_output_dir(value)

Set the test output directory

##### reports_output_dir()

Get the reports output directory

##### reports_output_dir(value)

Set the reports output directory

##### logs_output_dir()

Get the logs output directory

##### get_logs_output_path(filename, subdir)

Get a full logs output path for a file

##### get_output_path(filename, subdir)

Get a full output path for a file

##### get_test_output_path(filename, subdir)

Get a full test output path for a file

##### get_report_output_path(filename, subdir)

Get a full report output path for a file

## Functions

### configure_output_directories(base_dir, test_dir, reports_dir)

Configure output directories programmatically

### get_config_value(key)

Get a configuration value, resolving callable values

### configure_logging(log_file, log_level, log_format)

Configure centralized logging for the application.

Args:
    log_file: Optional path to a log file. If None, logs only to console.
    log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
    log_format: Format string for log messages.

Example:
    >>> from src.settings import configure_logging
    >>> configure_logging("output/app.log", logging.DEBUG)
