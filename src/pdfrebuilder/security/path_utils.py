#!/usr/bin/env python3
"""
Secure path utilities.

This module provides secure path handling utilities to prevent path traversal attacks
and ensure safe file operations.
"""

import logging
import tempfile
from pathlib import Path
from typing import ClassVar

logger = logging.getLogger(__name__)


class PathSecurityError(Exception):
    """Raised when a path security violation is detected."""


class SecurePathManager:
    """Manages secure path operations."""

    # Dangerous path components that could indicate path traversal
    DANGEROUS_PATH_COMPONENTS: ClassVar[list[str]] = ["..", "~", "$", "`", ";", "&", "|", ">", "<"]

    @classmethod
    def validate_path(
        cls,
        path: str | Path,
        base_path: Path | None = None,
        must_exist: bool = False,
        allow_creation: bool = True,
    ) -> Path:
        """
        Validate a path for security issues.

        Args:
            path: Path to validate
            base_path: Base path to restrict access to
            must_exist: Whether the path must exist
            allow_creation: Whether to allow creation of non-existent paths

        Returns:
            Validated Path object

        Raises:
            PathSecurityError: If path is unsafe
        """
        if not path:
            raise PathSecurityError("Path cannot be empty")

        path_obj = Path(path)
        base_path = base_path or Path.cwd()

        # Check for dangerous path components
        path_str = str(path)
        for dangerous_component in cls.DANGEROUS_PATH_COMPONENTS:
            if dangerous_component in path_str:
                raise PathSecurityError(f"Path contains potentially dangerous component: '{dangerous_component}'")

        try:
            # Resolve paths to handle symlinks and relative paths
            if path_obj.exists() or path_obj.is_absolute():
                resolved_path = path_obj.resolve()
            else:
                # For non-existent relative paths, resolve against base_path
                resolved_path = (base_path / path_obj).resolve()

            resolved_base = base_path.resolve()

            # Check if path is within base directory
            try:
                resolved_path.relative_to(resolved_base)
            except ValueError:
                raise PathSecurityError(f"Path '{path}' resolves outside allowed directory '{base_path}'")

        except (OSError, RuntimeError) as e:
            raise PathSecurityError(f"Failed to resolve path '{path}': {e}")

        # Check existence requirements
        if must_exist and not resolved_path.exists():
            raise PathSecurityError(f"Path '{path}' does not exist")

        if not allow_creation and not resolved_path.exists() and not resolved_path.parent.exists():
            raise PathSecurityError(f"Path '{path}' cannot be created (parent directory missing)")

        return resolved_path

    @classmethod
    def create_secure_temp_directory(
        cls,
        prefix: str = "secure_temp_",
        suffix: str = "",
        base_dir: Path | None = None,
    ) -> Path:
        """
        Create a secure temporary directory.

        Args:
            prefix: Directory name prefix
            suffix: Directory name suffix
            base_dir: Base directory for temp directory

        Returns:
            Path to created directory
        """
        # Use system temp directory if base_dir not specified
        if base_dir is None:
            base_dir = Path(tempfile.gettempdir())

        # For system temp directory, skip validation (it's outside project bounds but safe)
        # For custom base_dir, validate it
        if base_dir != Path(tempfile.gettempdir()):
            base_dir = cls.validate_path(base_dir, must_exist=True)

        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=base_dir))

        # Set secure permissions (owner read/write/execute only)
        temp_dir.chmod(0o700)

        logger.debug(f"Created secure temporary directory: {temp_dir}")
        return temp_dir

    @classmethod
    def create_secure_temp_file(
        cls,
        prefix: str = "secure_temp_",
        suffix: str = "",
        base_dir: Path | None = None,
        text: bool = True,
    ) -> tuple[int, Path]:
        """
        Create a secure temporary file.

        Args:
            prefix: File name prefix
            suffix: File name suffix
            base_dir: Base directory for temp file
            text: Whether file is for text content

        Returns:
            Tuple of (file_descriptor, path)
        """
        # Use system temp directory if base_dir not specified
        if base_dir is None:
            base_dir = Path(tempfile.gettempdir())

        # For system temp directory, skip validation (it's outside project bounds but safe)
        # For custom base_dir, validate it
        if base_dir != Path(tempfile.gettempdir()):
            base_dir = cls.validate_path(base_dir, must_exist=True)

        # Create temporary file
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=base_dir, text=text)

        temp_path = Path(temp_path)

        # Set secure permissions (owner read/write only)
        temp_path.chmod(0o600)

        logger.debug(f"Created secure temporary file: {temp_path}")
        return fd, temp_path

    @classmethod
    def ensure_directory_exists(cls, path: Path, mode: int = 0o755) -> Path:
        """
        Ensure a directory exists with secure permissions.

        Args:
            path: Directory path
            mode: Directory permissions

        Returns:
            Path to directory
        """
        validated_path = cls.validate_path(path, allow_creation=True)

        if not validated_path.exists():
            validated_path.mkdir(parents=True, exist_ok=True)
            validated_path.chmod(mode)
            logger.debug(f"Created directory: {validated_path}")

        return validated_path

    @classmethod
    def safe_file_write(
        cls,
        path: Path,
        content: str | bytes,
        mode: str = "w",
        encoding: str = "utf-8",
        file_mode: int = 0o644,
    ) -> None:
        """
        Safely write content to a file.

        Args:
            path: File path
            content: Content to write
            mode: File open mode
            encoding: Text encoding (for text mode)
            file_mode: File permissions
        """
        validated_path = cls.validate_path(path, allow_creation=True)

        # Ensure parent directory exists
        cls.ensure_directory_exists(validated_path.parent)

        # Write content
        if "b" in mode:
            with open(validated_path, mode) as f:
                f.write(content)
        else:
            with open(validated_path, mode, encoding=encoding) as f:
                f.write(content)

        # Set secure permissions
        validated_path.chmod(file_mode)

        logger.debug(f"Safely wrote to file: {validated_path}")


# Convenience functions
def validate_path(path: str | Path, base_path: Path | None = None) -> Path:
    """Validate a path for security issues."""
    return SecurePathManager.validate_path(path, base_path)


def create_secure_temp_dir(prefix: str = "secure_temp_") -> Path:
    """Create a secure temporary directory."""
    return SecurePathManager.create_secure_temp_directory(prefix=prefix)


def create_secure_temp_file(prefix: str = "secure_temp_") -> tuple[int, Path]:
    """Create a secure temporary file."""
    return SecurePathManager.create_secure_temp_file(prefix=prefix)


def sanitize_path(path: str) -> str:
    """Sanitize a path by removing dangerous components."""
    import re
    import urllib.parse

    # Decode URL encoding
    path = urllib.parse.unquote(path)

    # Remove multiple slashes
    path = re.sub(r"/+", "/", path)

    # Remove path traversal attempts
    path = path.replace("../", "").replace("..\\", "")

    return path


def is_safe_path(path: str) -> bool:
    """Check if a path is safe (no traversal attempts or dangerous locations)."""
    dangerous_patterns = ["../", "..\\", "/etc/", "/proc/", "/dev/", "\\\\", "%2e%2e"]

    path_lower = path.lower()
    for pattern in dangerous_patterns:
        if pattern in path_lower:
            return False

    return True


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
    """Validate that a filename has an allowed extension."""
    import os

    _, ext = os.path.splitext(filename.lower())
    return ext in [e.lower() for e in allowed_extensions]


def get_safe_filename(filename: str) -> str:
    """Get a safe filename by removing dangerous characters and path components."""
    import os

    # Remove path components
    filename = os.path.basename(filename)

    # Remove dangerous characters
    dangerous_chars = '<>:"|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, "")

    # Remove path traversal attempts
    filename = filename.replace("../", "").replace("..\\", "")

    return filename
