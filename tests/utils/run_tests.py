#!/usr/bin/env python3
"""
Convenience script to run tests with different verbosity levels.

Usage:
    python scripts/run_tests.py                    # Default quiet mode
    python scripts/run_tests.py --verbose         # Verbose mode
    python scripts/run_tests.py --debug           # Full debug mode
    python scripts/run_tests.py --coverage        # Run with coverage
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for security utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from security.subprocess_utils import SecureSubprocessRunner, SecurityError


def run_tests(verbose_level: str = "quiet", coverage: bool = False) -> int:
    """
    Run tests with specified verbosity level.

    Args:
        verbose_level: One of "quiet", "verbose", or "debug"
        coverage: Whether to run with coverage reporting

    Returns:
        Exit code from the test run
    """
    # Set environment variable based on verbose level
    if verbose_level == "quiet":
        env_var = "WARNING"
    elif verbose_level == "verbose":
        env_var = "INFO"
    elif verbose_level == "debug":
        env_var = "DEBUG"
    else:
        print(f"Unknown verbose level: {verbose_level}")
        return 1

    # Set environment variable
    os.environ["FONTTOOLS_LOG_LEVEL"] = env_var

    # Build command
    if coverage:
        cmd = ["hatch", "run", "test-cov"]
    else:
        cmd = ["hatch", "run", "test"]

    # Add any additional arguments
    if len(sys.argv) > 1:
        # Filter out our script arguments
        additional_args = [
            arg
            for arg in sys.argv[1:]
            if not arg.startswith("--verbose") and not arg.startswith("--debug") and not arg.startswith("--coverage")
        ]
        cmd.extend(additional_args)

    print(f"Running tests with {verbose_level} verbosity (FONTTOOLS_LOG_LEVEL={env_var})")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)

    # Run the command securely
    try:
        runner = SecureSubprocessRunner(base_path=Path.cwd())
        result = runner.run(cmd, capture_output=False)
        return result.returncode
    except SecurityError as e:
        print(f"Security error: {e}")
        return 1
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run tests with different verbosity levels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tests/run_tests.py                    # Default quiet mode
    python tests/run_tests.py --verbose         # Verbose mode
    python tests/run_tests.py --debug           # Full debug mode
    python tests/run_tests.py --coverage        # Run with coverage
    python tests/run_tests.py tests/test_specific.py  # Run specific test
        """,
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests in verbose mode (INFO level logging)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run tests in debug mode (DEBUG level logging)",
    )
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage reporting")

    args = parser.parse_args()

    # Determine verbose level
    if args.debug:
        verbose_level = "debug"
    elif args.verbose:
        verbose_level = "verbose"
    else:
        verbose_level = "quiet"

    # Run tests
    exit_code = run_tests(verbose_level, args.coverage)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
