"""
Tests for directory structure setup utilities.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pdfrebuilder.utils.directory_utils import (
    ensure_directories_exist,
    get_target_directories,
    setup_project_directories,
    validate_directory_exists,
    validate_directory_for_operations,
    validate_directory_writable,
)


class TestEnsureDirectoriesExist:
    """Test the ensure_directories_exist function."""

    def test_create_single_directory(self, tmp_path):
        """Test creating a single directory."""
        test_dir = tmp_path / "test_dir"
        ensure_directories_exist([test_dir])

        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_create_multiple_directories(self, tmp_path):
        """Test creating multiple directories."""
        test_dirs = [tmp_path / "dir1", tmp_path / "dir2", tmp_path / "dir3"]
        ensure_directories_exist(test_dirs)

        for test_dir in test_dirs:
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_create_nested_directories(self, tmp_path):
        """Test creating nested directory structure."""
        nested_dir = tmp_path / "parent" / "child" / "grandchild"
        ensure_directories_exist([nested_dir])

        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert nested_dir.parent.exists()
        assert nested_dir.parent.parent.exists()

    def test_directory_already_exists(self, tmp_path):
        """Test that existing directories are handled gracefully."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        # Should not raise an error
        ensure_directories_exist([existing_dir])
        assert existing_dir.exists()

    def test_permission_error(self, tmp_path):
        """Test handling of permission errors."""
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = OSError("Permission denied")

            with pytest.raises(OSError, match="Cannot create directory"):
                ensure_directories_exist([tmp_path / "test"])


class TestValidateDirectoryExists:
    """Test the validate_directory_exists function."""

    def test_existing_directory(self, tmp_path):
        """Test validation of existing directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        assert validate_directory_exists(test_dir) is True

    def test_nonexistent_directory(self, tmp_path):
        """Test validation of non-existent directory."""
        test_dir = tmp_path / "nonexistent"

        assert validate_directory_exists(test_dir) is False

    def test_file_instead_of_directory(self, tmp_path):
        """Test validation when path points to a file."""
        test_file = tmp_path / "test_file.txt"
        test_file.touch()

        assert validate_directory_exists(test_file) is False


class TestValidateDirectoryWritable:
    """Test the validate_directory_writable function."""

    def test_writable_directory(self, tmp_path):
        """Test validation of writable directory."""
        assert validate_directory_writable(tmp_path) is True

    def test_nonexistent_directory(self, tmp_path):
        """Test validation of non-existent directory."""
        nonexistent = tmp_path / "nonexistent"
        assert validate_directory_writable(nonexistent) is False

    def test_file_instead_of_directory(self, tmp_path):
        """Test validation when path points to a file."""
        test_file = tmp_path / "test_file.txt"
        test_file.touch()

        assert validate_directory_writable(test_file) is False

    def test_permission_error_on_write_test(self, tmp_path):
        """Test handling of permission errors during write test."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        with patch("pathlib.Path.touch") as mock_touch:
            mock_touch.side_effect = PermissionError("Permission denied")

            assert validate_directory_writable(test_dir) is False


class TestValidateDirectoryForOperations:
    """Test the validate_directory_for_operations function."""

    def test_valid_directory(self, tmp_path):
        """Test validation of a valid directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        assert validate_directory_for_operations(test_dir) is True

    def test_nonexistent_directory(self, tmp_path):
        """Test validation of non-existent directory."""
        nonexistent = tmp_path / "nonexistent"
        assert validate_directory_for_operations(nonexistent) is False

    def test_non_writable_directory(self, tmp_path):
        """Test validation of non-writable directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        with patch("src.utils.directory_utils.validate_directory_writable") as mock_writable:
            mock_writable.return_value = False

            assert validate_directory_for_operations(test_dir) is False


class TestGetTargetDirectories:
    """Test the get_target_directories function."""

    def test_returns_expected_directories(self):
        """Test that the function returns the expected directory list."""
        expected_dirs = [
            "demos",
            "scripts",
            "output/logs",
            "output/debug",
            "tests/fixtures",
        ]

        result = get_target_directories()
        assert result == expected_dirs
        assert len(result) == 5


class TestSetupProjectDirectories:
    """Test the setup_project_directories function."""

    def test_successful_setup(self, tmp_path):
        """Test successful setup of all directories."""
        # Change to temp directory for test
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = setup_project_directories()
            assert result is True

            # Verify all directories were created
            expected_dirs = get_target_directories()
            for directory in expected_dirs:
                assert Path(directory).exists()
                assert Path(directory).is_dir()

        finally:
            os.chdir(original_cwd)

    def test_setup_with_creation_failure(self, tmp_path):
        """Test setup when directory creation fails."""
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            with patch("src.utils.directory_utils.ensure_directories_exist") as mock_ensure:
                mock_ensure.side_effect = OSError("Creation failed")

                result = setup_project_directories()
                assert result is False

        finally:
            os.chdir(original_cwd)

    def test_setup_with_validation_failure(self, tmp_path):
        """Test setup when directory validation fails."""
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            with patch("src.utils.directory_utils.validate_directory_for_operations") as mock_validate:
                mock_validate.return_value = False

                result = setup_project_directories()
                assert result is False

        finally:
            os.chdir(original_cwd)
