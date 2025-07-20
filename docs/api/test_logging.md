# test_logging

Test logging configuration to suppress verbose output from third-party libraries.

This module provides utilities to configure logging for test environments,
specifically to reduce verbosity from libraries like fontTools.

## Functions

### configure_test_logging(level, suppress_fonttools, suppress_other_libs)

Configure logging for test environments to reduce verbosity.

Args:
    level: Base logging level for the application
    suppress_fonttools: Whether to suppress fontTools debug output
    suppress_other_libs: Whether to suppress other verbose libraries

### setup_quiet_test_environment()

Set up a quiet test environment with minimal logging output.

This function configures logging to suppress verbose output from
third-party libraries commonly used in this project.
