#!/usr/bin/env python3
"""
Demonstration of directory structure setup utilities.

This script shows how to use the directory utilities to set up
the project structure for file organization.
"""

import logging
from pathlib import Path

from pdfrebuilder.utils.directory_utils import (
    ensure_directories_exist,
    get_target_directories,
    setup_project_directories,
    validate_directory_exists,
    validate_directory_for_operations,
    validate_directory_writable,
)

# Configure logging to see the utility functions in action
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def demo_individual_functions():
    """Demonstrate individual directory utility functions."""
    logger.info("=== Demonstrating Individual Directory Functions ===")

    # Demo directory creation
    test_dirs = ["demo_temp/subdir1", "demo_temp/subdir2/nested"]
    logger.info(f"Creating test directories: {test_dirs}")
    ensure_directories_exist(test_dirs)

    # Demo directory validation
    for test_dir in test_dirs:
        exists = validate_directory_exists(test_dir)
        writable = validate_directory_writable(test_dir)
        ready = validate_directory_for_operations(test_dir)

        logger.info(f"Directory {test_dir}: exists={exists}, writable={writable}, ready={ready}")

    # Clean up demo directories
    import shutil

    if Path("demo_temp").exists():
        shutil.rmtree("demo_temp")
        logger.info("Cleaned up demo directories")


def demo_project_setup():
    """Demonstrate the complete project directory setup."""
    logger.info("=== Demonstrating Project Directory Setup ===")

    # Show what directories will be created
    target_dirs = get_target_directories()
    logger.info(f"Target directories for project: {target_dirs}")

    # Check current state
    logger.info("Current directory state:")
    for directory in target_dirs:
        exists = validate_directory_exists(directory)
        logger.info(f"  {directory}: {'EXISTS' if exists else 'MISSING'}")

    # Set up all project directories
    logger.info("Setting up project directories...")
    success = setup_project_directories()

    if success:
        logger.info("✅ Project directory setup completed successfully!")

        # Verify final state
        logger.info("Final directory state:")
        for directory in target_dirs:
            ready = validate_directory_for_operations(directory)
            logger.info(f"  {directory}: {'READY' if ready else 'NOT READY'}")
    else:
        logger.error("❌ Project directory setup failed!")


def main():
    """Run the directory setup demonstration."""
    logger.info("Starting Directory Setup Utilities Demo")

    try:
        demo_individual_functions()
        print()  # Add spacing between demos
        demo_project_setup()

    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise

    logger.info("Demo completed successfully!")


if __name__ == "__main__":
    main()
