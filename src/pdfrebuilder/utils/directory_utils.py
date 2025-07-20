"""
Directory structure setup utilities for project organization.

This module provides utilities to ensure target directories exist before file operations
and validate directory permissions for file migrations.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_directories_exist(directories: list[str | Path]) -> None:
    """
    Create directories if they don't exist.

    Args:
        directories: List of directory paths to create

    Raises:
        OSError: If directory creation fails due to permissions or other issues
    """
    for directory in directories:
        directory_path = Path(directory)

        try:
            # Create directory and any necessary parent directories
            directory_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory_path}")

        except OSError as e:
            logger.error(f"Failed to create directory {directory_path}: {e}")
            raise OSError(f"Cannot create directory {directory_path}: {e}") from e


def validate_directory_exists(directory: str | Path) -> bool:
    """
    Check if a directory exists.

    Args:
        directory: Directory path to check

    Returns:
        True if directory exists, False otherwise
    """
    directory_path = Path(directory)
    exists = directory_path.exists() and directory_path.is_dir()

    if exists:
        logger.debug(f"Directory exists: {directory_path}")
    else:
        logger.debug(f"Directory does not exist: {directory_path}")

    return exists


def validate_directory_writable(directory: str | Path) -> bool:
    """
    Check if a directory is writable.

    Args:
        directory: Directory path to check

    Returns:
        True if directory is writable, False otherwise
    """
    directory_path = Path(directory)

    if not directory_path.exists():
        logger.warning(f"Directory does not exist: {directory_path}")
        return False

    if not directory_path.is_dir():
        logger.warning(f"Path is not a directory: {directory_path}")
        return False

    # Test write permissions by attempting to create a temporary file
    try:
        test_file = directory_path / ".write_test_temp"
        test_file.touch()
        test_file.unlink()  # Clean up test file
        logger.debug(f"Directory is writable: {directory_path}")
        return True

    except (OSError, PermissionError) as e:
        logger.warning(f"Directory is not writable {directory_path}: {e}")
        return False


def validate_directory_for_operations(directory: str | Path) -> bool:
    """
    Validate that a directory exists and is writable for file operations.

    Args:
        directory: Directory path to validate

    Returns:
        True if directory is ready for file operations, False otherwise
    """
    directory_path = Path(directory)

    # Check if directory exists
    if not validate_directory_exists(directory_path):
        logger.error(f"Directory validation failed - does not exist: {directory_path}")
        return False

    # Check if directory is writable
    if not validate_directory_writable(directory_path):
        logger.error(f"Directory validation failed - not writable: {directory_path}")
        return False

    logger.info(f"Directory validation passed: {directory_path}")
    return True


def get_target_directories() -> list[str | Path]:
    """
    Get the list of target directories that need to be created for project structure cleanup.

    Returns:
        List of directory paths that should be created
    """
    return ["demos", "scripts", "output/logs", "output/debug", "tests/fixtures"]


def setup_project_directories() -> bool:
    """
    Set up all required directories for the project structure cleanup.

    Returns:
        True if all directories were created successfully, False otherwise
    """
    target_directories = get_target_directories()

    try:
        ensure_directories_exist(target_directories)

        # Validate all directories are ready for operations
        all_valid = True
        for directory in target_directories:
            if not validate_directory_for_operations(directory):
                all_valid = False

        if all_valid:
            logger.info("All project directories set up successfully")
            return True
        else:
            logger.error("Some directories failed validation after creation")
            return False

    except OSError as e:
        logger.error(f"Failed to set up project directories: {e}")
        return False
