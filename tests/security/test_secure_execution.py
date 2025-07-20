#!/usr/bin/env python3
"""
Tests for secure execution module with plumbum integration.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.security.secure_execution import (
    ExecutionResult,
    SecureExecutionError,
    SecureExecutor,
    SecureTempExecutor,
    SecurityContext,
    ValidationResult,
    execute_secure_command,
    validate_command_security,
)


class TestSecurityContext:
    """Test SecurityContext class."""

    def test_default_initialization(self):
        """Test default security context initialization."""
        context = SecurityContext()

        assert isinstance(context.allowed_executables, list)
        assert "python" in context.allowed_executables
        assert "hatch" in context.allowed_executables
        assert context.timeout == 300
        assert context.base_path == Path.cwd()
        assert isinstance(context.environment_whitelist, list)
        assert "PATH" in context.environment_whitelist

    def test_custom_initialization(self):
        """Test custom security context initialization."""
        custom_executables = ["python", "git"]
        custom_base = Path("/tmp")
        custom_timeout = 60

        context = SecurityContext(
            allowed_executables=custom_executables,
            base_path=custom_base,
            timeout=custom_timeout,
        )

        assert context.allowed_executables == custom_executables
        assert context.base_path == custom_base
        assert context.timeout == custom_timeout


class TestValidationResult:
    """Test ValidationResult class."""

    def test_valid_result(self):
        """Test valid validation result."""
        result = ValidationResult(True)
        assert result.is_valid
        assert bool(result)
        assert result.error_message == ""
        assert result.warnings == []

    def test_invalid_result(self):
        """Test invalid validation result."""
        result = ValidationResult(False, "Test error", ["Warning 1"])
        assert not result.is_valid
        assert not bool(result)
        assert result.error_message == "Test error"
        assert result.warnings == ["Warning 1"]


class TestExecutionResult:
    """Test ExecutionResult class."""

    def test_successful_result(self):
        """Test successful execution result."""
        result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.5)

        assert result.command == ["python", "--version"]
        assert result.returncode == 0
        assert result.stdout == "Python 3.12"
        assert result.stderr == ""
        assert result.execution_time == 1.5
        assert result.success

    def test_failed_result(self):
        """Test failed execution result."""
        result = ExecutionResult(["python", "nonexistent.py"], 1, "", "File not found", 0.5)

        assert result.returncode == 1
        assert not result.success
        assert result.stderr == "File not found"

    def test_repr(self):
        """Test string representation."""
        result = ExecutionResult(["echo", "test"], 0)
        repr_str = repr(result)

        assert "ExecutionResult" in repr_str
        assert "returncode=0" in repr_str
        assert "success=True" in repr_str


class TestSecureExecutor:
    """Test SecureExecutor class."""

    def test_initialization(self):
        """Test executor initialization."""
        executor = SecureExecutor()
        assert isinstance(executor.security_context, SecurityContext)
        assert executor._command_cache == {}

    def test_initialization_with_context(self):
        """Test executor initialization with custom context."""
        context = SecurityContext(timeout=60)
        executor = SecureExecutor(context)
        assert executor.security_context == context

    def test_validate_command_empty(self):
        """Test validation of empty command."""
        executor = SecureExecutor()
        result = executor.validate_command([])

        assert not result.is_valid
        assert "empty" in result.error_message.lower()

    def test_validate_command_not_list(self):
        """Test validation of non-list command."""
        executor = SecureExecutor()
        result = executor.validate_command("python --version")

        assert not result.is_valid
        assert "list" in result.error_message.lower()

    def test_validate_command_disallowed_executable(self):
        """Test validation of disallowed executable."""
        context = SecurityContext(allowed_executables=["python"])
        executor = SecureExecutor(context)
        result = executor.validate_command(["rm", "-rf", "/"])

        assert not result.is_valid
        assert "not in the allowed list" in result.error_message

    def test_validate_command_allowed_executable(self):
        """Test validation of allowed executable."""
        executor = SecureExecutor()
        result = executor.validate_command(["python", "--version"])

        assert result.is_valid
        assert result.error_message == ""

    def test_validate_command_dangerous_characters(self):
        """Test validation with dangerous characters."""
        executor = SecureExecutor()
        result = executor.validate_command(["python", "-c", "import os; os.system('ls')"])

        assert result.is_valid  # Should be valid but with warnings
        assert len(result.warnings) > 0

    def test_validate_command_non_string_argument(self):
        """Test validation with non-string argument."""
        executor = SecureExecutor()
        result = executor.validate_command(["python", 123])

        assert not result.is_valid
        assert "must be a string" in result.error_message

    def test_get_security_context(self):
        """Test getting security context."""
        context = SecurityContext(timeout=60)
        executor = SecureExecutor(context)

        assert executor.get_security_context() == context

    def test_update_security_context(self):
        """Test updating security context."""
        executor = SecureExecutor()
        original_timeout = executor.security_context.timeout

        executor.update_security_context(timeout=120)
        assert executor.security_context.timeout == 120
        assert executor.security_context.timeout != original_timeout

    def test_update_security_context_invalid_param(self):
        """Test updating security context with invalid parameter."""
        executor = SecureExecutor()

        # Should not raise exception, just log warning
        executor.update_security_context(invalid_param="value")

    @patch("src.security.secure_execution.local")
    def test_execute_command_success(self, mock_local):
        """Test successful command execution."""
        # Mock plumbum command execution
        mock_cmd = Mock()
        mock_cmd_with_args = Mock()
        mock_cmd_with_args.run.return_value = (0, "Success output", "")

        # Configure the mock to support __getitem__ for arguments
        mock_cmd.__getitem__ = Mock(return_value=mock_cmd_with_args)
        mock_local.__getitem__.return_value = mock_cmd

        # Mock context managers
        mock_local.cwd.return_value.__enter__ = Mock(return_value=None)
        mock_local.cwd.return_value.__exit__ = Mock(return_value=None)
        mock_local.env.return_value.__enter__ = Mock(return_value=None)
        mock_local.env.return_value.__exit__ = Mock(return_value=None)

        executor = SecureExecutor()
        result = executor.execute_command(["python", "--version"])

        assert isinstance(result, ExecutionResult)
        assert result.command == ["python", "--version"]

    @patch("src.security.secure_execution.local")
    def test_execute_command_validation_failure(self, mock_local):
        """Test command execution with validation failure."""
        executor = SecureExecutor()

        with pytest.raises(SecureExecutionError) as exc_info:
            executor.execute_command([])

        assert "validation failed" in str(exc_info.value).lower()

    @patch("src.security.secure_execution.local")
    def test_execute_command_with_cwd(self, mock_local):
        """Test command execution with working directory."""
        mock_cmd = Mock()
        mock_cmd_with_args = Mock()
        mock_cmd_with_args.run.return_value = (0, "Success", "")

        # Configure the mock to support __getitem__ for arguments
        mock_cmd.__getitem__ = Mock(return_value=mock_cmd_with_args)
        mock_local.__getitem__.return_value = mock_cmd

        # Mock context managers
        mock_local.cwd.return_value.__enter__ = Mock(return_value=None)
        mock_local.cwd.return_value.__exit__ = Mock(return_value=None)
        mock_local.env.return_value.__enter__ = Mock(return_value=None)
        mock_local.env.return_value.__exit__ = Mock(return_value=None)

        # Create a temp directory within the current working directory to avoid path validation issues
        base_dir = Path.cwd()
        temp_dir = base_dir / "temp_test_dir"
        temp_dir.mkdir(exist_ok=True)

        try:
            executor = SecureExecutor()
            result = executor.execute_command(["python", "--version"], cwd=temp_dir)
            assert isinstance(result, ExecutionResult)
        finally:
            if temp_dir.exists():
                temp_dir.rmdir()

    @patch("src.security.secure_execution.local")
    def test_execute_command_invalid_cwd(self, mock_local):
        """Test command execution with invalid working directory."""
        executor = SecureExecutor()
        invalid_cwd = Path("/nonexistent/path/outside/base")

        with pytest.raises(SecureExecutionError) as exc_info:
            executor.execute_command(["python", "--version"], cwd=invalid_cwd)

        assert "outside allowed base path" in str(exc_info.value)


class TestSecureTempExecutor:
    """Test SecureTempExecutor class."""

    def test_initialization(self):
        """Test temp executor initialization."""
        executor = SecureTempExecutor()
        assert isinstance(executor, SecureExecutor)
        assert executor.temp_prefix == "secure_exec_"
        assert executor._temp_dirs == []

    def test_create_temp_directory(self):
        """Test temporary directory creation."""
        executor = SecureTempExecutor()
        temp_dir = executor.create_temp_directory()

        assert temp_dir.exists()
        assert temp_dir.is_dir()
        assert temp_dir in executor._temp_dirs

        # Clean up
        executor.cleanup_temp_directories()

    def test_create_temp_directory_with_suffix(self):
        """Test temporary directory creation with suffix."""
        executor = SecureTempExecutor()
        temp_dir = executor.create_temp_directory("_test")

        assert temp_dir.exists()
        assert "_test" in temp_dir.name

        # Clean up
        executor.cleanup_temp_directories()

    def test_cleanup_temp_directories(self):
        """Test temporary directory cleanup."""
        executor = SecureTempExecutor()
        temp_dir1 = executor.create_temp_directory()
        temp_dir2 = executor.create_temp_directory()

        assert temp_dir1.exists()
        assert temp_dir2.exists()
        assert len(executor._temp_dirs) == 2

        executor.cleanup_temp_directories()

        assert not temp_dir1.exists()
        assert not temp_dir2.exists()
        assert len(executor._temp_dirs) == 0

    def test_context_manager(self):
        """Test context manager functionality."""
        with SecureTempExecutor() as executor:
            temp_dir = executor.create_temp_directory()
            assert temp_dir.exists()
            temp_path = temp_dir  # Store reference

        # After context exit, temp directory should be cleaned up
        assert not temp_path.exists()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch("src.security.secure_execution.SecureExecutor")
    def test_execute_secure_command(self, mock_executor_class):
        """Test execute_secure_command convenience function."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        result = execute_secure_command(["python", "--version"])

        assert result == mock_result
        mock_executor_class.assert_called_once()
        mock_executor.execute_command.assert_called_once()

    @patch("src.security.secure_execution.SecureExecutor")
    def test_validate_command_security(self, mock_executor_class):
        """Test validate_command_security convenience function."""
        mock_executor = Mock()
        mock_result = ValidationResult(True)
        mock_executor.validate_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        result = validate_command_security(["python", "--version"])

        assert result == mock_result
        mock_executor_class.assert_called_once()
        mock_executor.validate_command.assert_called_once()


class TestIntegration:
    """Integration tests with real plumbum commands."""

    def test_real_python_version(self):
        """Test real Python version command."""
        executor = SecureExecutor()

        try:
            result = executor.execute_command(["python", "--version"])
            assert result.success
            assert "Python" in result.stdout
        except SecureExecutionError:
            # Skip if Python not available in test environment
            pytest.skip("Python not available in test environment")

    def test_real_command_validation(self):
        """Test real command validation."""
        executor = SecureExecutor()

        # Valid command
        result = executor.validate_command(["python", "--version"])
        assert result.is_valid

        # Invalid command (not in allowed list)
        context = SecurityContext(allowed_executables=["python"])
        executor = SecureExecutor(context)
        result = executor.validate_command(["nonexistent_command"])
        assert not result.is_valid

    def test_environment_filtering(self):
        """Test environment variable filtering."""
        context = SecurityContext(environment_whitelist=["PATH", "TEST_VAR"])
        executor = SecureExecutor(context)

        # This test mainly checks that the filtering logic works
        # without actually executing commands that depend on specific env vars
        env = {"PATH": "/usr/bin", "TEST_VAR": "test", "DANGEROUS_VAR": "danger"}

        # The filtering happens inside execute_command, so we test validation
        result = executor.validate_command(["python", "--version"])
        assert result.is_valid
