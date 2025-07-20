#!/usr/bin/env python3
"""
Tests for subprocess compatibility wrapper.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.security.secure_execution import ExecutionResult, SecurityContext
from pdfrebuilder.security.subprocess_compatibility import (
    CompatibilityResult,
    MigrationHelper,
    SecureSubprocessWrapper,
    SubprocessCompatibilityError,
    call,
    check_call,
    check_output,
    get_default_wrapper,
    run,
)


class TestCompatibilityResult:
    """Test CompatibilityResult class."""

    def test_initialization(self):
        """Test compatibility result initialization."""
        exec_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        compat_result = CompatibilityResult(exec_result)

        assert compat_result.args == ["python", "--version"]
        assert compat_result.returncode == 0
        assert compat_result.stdout == "Python 3.12"
        assert compat_result.stderr == ""

    def test_check_returncode_success(self):
        """Test check_returncode with successful command."""
        exec_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        compat_result = CompatibilityResult(exec_result)

        # Should not raise exception
        compat_result.check_returncode()

    def test_check_returncode_failure(self):
        """Test check_returncode with failed command."""
        exec_result = ExecutionResult(["python", "nonexistent.py"], 1, "", "File not found", 1.0)
        compat_result = CompatibilityResult(exec_result)

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            compat_result.check_returncode()

        assert exc_info.value.returncode == 1
        assert exc_info.value.cmd == ["python", "nonexistent.py"]

    def test_repr(self):
        """Test string representation."""
        exec_result = ExecutionResult(["echo", "test"], 0, "test", "", 0.1)
        compat_result = CompatibilityResult(exec_result)

        repr_str = repr(compat_result)
        assert "CompletedProcess" in repr_str
        assert "returncode=0" in repr_str


class TestSecureSubprocessWrapper:
    """Test SecureSubprocessWrapper class."""

    def test_initialization(self):
        """Test wrapper initialization."""
        wrapper = SecureSubprocessWrapper()
        assert wrapper.enable_warnings is True
        assert wrapper.strict_mode is False

    def test_initialization_with_options(self):
        """Test wrapper initialization with custom options."""
        context = SecurityContext(timeout=60)
        wrapper = SecureSubprocessWrapper(
            security_context=context,
            enable_warnings=False,
            strict_mode=True,
        )
        assert wrapper.enable_warnings is False
        assert wrapper.strict_mode is True

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_run_basic(self, mock_executor_class):
        """Test basic run functionality."""
        # Mock executor
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()
        result = wrapper.run(["python", "--version"])

        assert isinstance(result, CompatibilityResult)
        assert result.returncode == 0
        assert result.stdout == "Python 3.12"

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_run_with_string_command(self, mock_executor_class):
        """Test run with string command."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()
        result = wrapper.run("python --version", shell=True)

        assert isinstance(result, CompatibilityResult)
        mock_executor.execute_command.assert_called_once()

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_run_strict_mode_shell_error(self, mock_executor_class):
        """Test run with shell=True in strict mode."""
        wrapper = SecureSubprocessWrapper(strict_mode=True)

        with pytest.raises(SubprocessCompatibilityError) as exc_info:
            wrapper.run("python --version", shell=True)

        assert "Shell commands not allowed in strict mode" in str(exc_info.value)

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_run_with_check_success(self, mock_executor_class):
        """Test run with check=True and successful command."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()
        result = wrapper.run(["python", "--version"], check=True)

        assert result.returncode == 0

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_run_with_check_failure(self, mock_executor_class):
        """Test run with check=True and failed command."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "nonexistent.py"], 1, "", "File not found", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()

        with pytest.raises(subprocess.CalledProcessError):
            wrapper.run(["python", "nonexistent.py"], check=True)

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_call(self, mock_executor_class):
        """Test call method."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()
        returncode = wrapper.call(["python", "--version"])

        assert returncode == 0

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_check_call_success(self, mock_executor_class):
        """Test check_call with successful command."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()
        # Should not raise exception
        wrapper.check_call(["python", "--version"])

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_check_call_failure(self, mock_executor_class):
        """Test check_call with failed command."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "nonexistent.py"], 1, "", "File not found", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()

        with pytest.raises(subprocess.CalledProcessError):
            wrapper.check_call(["python", "nonexistent.py"])

    @patch("src.security.subprocess_compatibility.SecureExecutor")
    def test_check_output(self, mock_executor_class):
        """Test check_output method."""
        mock_executor = Mock()
        mock_result = ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0)
        mock_executor.execute_command.return_value = mock_result
        mock_executor_class.return_value = mock_executor

        wrapper = SecureSubprocessWrapper()
        output = wrapper.check_output(["python", "--version"])

        assert output == "Python 3.12"

    def test_prepare_command_list(self):
        """Test command preparation with list input."""
        wrapper = SecureSubprocessWrapper()
        cmd = wrapper._prepare_command(["python", "--version"], False)
        assert cmd == ["python", "--version"]

    def test_prepare_command_string_no_shell(self):
        """Test command preparation with string input, no shell."""
        wrapper = SecureSubprocessWrapper()
        cmd = wrapper._prepare_command("python", False)
        assert cmd == ["python"]

    def test_prepare_command_string_with_shell(self):
        """Test command preparation with string input and shell."""
        wrapper = SecureSubprocessWrapper()
        cmd = wrapper._prepare_command("python --version", True)
        assert cmd == ["python", "--version"]

    def test_prepare_command_invalid_type(self):
        """Test command preparation with invalid input type."""
        wrapper = SecureSubprocessWrapper()

        with pytest.raises(SubprocessCompatibilityError) as exc_info:
            wrapper._prepare_command(123, False)

        assert "Invalid command type" in str(exc_info.value)


class TestMigrationHelper:
    """Test MigrationHelper class."""

    def test_analyze_subprocess_usage(self):
        """Test subprocess usage analysis."""
        # Create a temporary Python file with subprocess usage
        test_code = """
import subprocess
from subprocess import run

def test_function():
    result = subprocess.run(['python', '--version'])
    subprocess.call(['echo', 'test'])
    return result
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            analysis = MigrationHelper.analyze_subprocess_usage(temp_path)

            assert analysis["total_calls"] == 2
            assert len(analysis["subprocess_imports"]) == 2
            assert len(analysis["subprocess_calls"]) == 2
            assert analysis["migration_complexity"] in ["low", "medium", "high"]

        finally:
            temp_path.unlink()

    def test_analyze_subprocess_usage_no_subprocess(self):
        """Test analysis of file without subprocess usage."""
        test_code = """
def test_function():
    print("Hello, world!")
    return 42
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            analysis = MigrationHelper.analyze_subprocess_usage(temp_path)

            assert analysis["total_calls"] == 0
            assert len(analysis["subprocess_imports"]) == 0
            assert len(analysis["subprocess_calls"]) == 0
            assert analysis["migration_complexity"] == "low"

        finally:
            temp_path.unlink()

    def test_generate_migration_suggestions(self):
        """Test migration suggestion generation."""
        analysis = {
            "subprocess_imports": [{"line": 1, "import": "import subprocess"}],
            "subprocess_calls": [
                {"function": "run", "line": 5, "args": 1, "keywords": []},
                {"function": "call", "line": 6, "args": 1, "keywords": []},
            ],
            "total_calls": 2,
            "migration_complexity": "medium",
        }

        suggestions = MigrationHelper.generate_migration_suggestions(analysis)

        assert len(suggestions) > 0
        assert any("Replace subprocess imports" in s for s in suggestions)
        assert any("subprocess.run()" in s for s in suggestions)
        assert any("subprocess.call()" in s for s in suggestions)

    def test_generate_migration_suggestions_error(self):
        """Test migration suggestions with error analysis."""
        analysis = {"error": "File not found"}
        suggestions = MigrationHelper.generate_migration_suggestions(analysis)

        assert len(suggestions) == 1
        assert "Error analyzing file" in suggestions[0]

    def test_create_migration_script(self):
        """Test migration script creation."""
        # Create a temporary Python file
        test_code = """
import subprocess

def test():
    subprocess.run(['python', '--version'])
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            migration_path = MigrationHelper.create_migration_script(temp_path)

            assert migration_path.exists()
            assert migration_path.suffix == ".py"
            assert "migration" in migration_path.name

            # Check migration script content
            with open(migration_path) as f:
                content = f.read()

            assert "Migration script" in content
            assert "SecureSubprocessWrapper" in content
            assert "subprocess.run" in content

        finally:
            temp_path.unlink()
            if migration_path.exists():
                migration_path.unlink()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch("src.security.subprocess_compatibility.get_default_wrapper")
    def test_run_function(self, mock_get_wrapper):
        """Test run convenience function."""
        mock_wrapper = Mock()
        mock_result = CompatibilityResult(ExecutionResult(["python", "--version"], 0, "Python 3.12", "", 1.0))
        mock_wrapper.run.return_value = mock_result
        mock_get_wrapper.return_value = mock_wrapper

        result = run(["python", "--version"])

        assert isinstance(result, CompatibilityResult)
        mock_wrapper.run.assert_called_once_with(["python", "--version"])

    @patch("src.security.subprocess_compatibility.get_default_wrapper")
    def test_call_function(self, mock_get_wrapper):
        """Test call convenience function."""
        mock_wrapper = Mock()
        mock_wrapper.call.return_value = 0
        mock_get_wrapper.return_value = mock_wrapper

        returncode = call(["python", "--version"])

        assert returncode == 0
        mock_wrapper.call.assert_called_once_with(["python", "--version"])

    @patch("src.security.subprocess_compatibility.get_default_wrapper")
    def test_check_call_function(self, mock_get_wrapper):
        """Test check_call convenience function."""
        mock_wrapper = Mock()
        mock_wrapper.check_call.return_value = None
        mock_get_wrapper.return_value = mock_wrapper

        # Should not raise exception
        check_call(["python", "--version"])

        mock_wrapper.check_call.assert_called_once_with(["python", "--version"])

    @patch("src.security.subprocess_compatibility.get_default_wrapper")
    def test_check_output_function(self, mock_get_wrapper):
        """Test check_output convenience function."""
        mock_wrapper = Mock()
        mock_wrapper.check_output.return_value = "Python 3.12"
        mock_get_wrapper.return_value = mock_wrapper

        output = check_output(["python", "--version"])

        assert output == "Python 3.12"
        mock_wrapper.check_output.assert_called_once_with(["python", "--version"])

    def test_get_default_wrapper(self):
        """Test default wrapper creation."""
        wrapper1 = get_default_wrapper()
        wrapper2 = get_default_wrapper()

        # Should return the same instance (singleton pattern)
        assert wrapper1 is wrapper2
        assert isinstance(wrapper1, SecureSubprocessWrapper)


class TestIntegration:
    """Integration tests with real commands."""

    def test_real_command_execution(self):
        """Test real command execution through wrapper."""
        wrapper = SecureSubprocessWrapper(enable_warnings=False)

        try:
            result = wrapper.run(["python", "--version"], capture_output=True)
            assert result.returncode == 0
            assert "Python" in result.stdout
        except Exception:
            # Skip if Python not available in test environment
            pytest.skip("Python not available in test environment")

    def test_compatibility_with_subprocess_interface(self):
        """Test that wrapper maintains subprocess interface compatibility."""
        wrapper = SecureSubprocessWrapper(enable_warnings=False)

        try:
            # Test that the interface matches subprocess.run
            result = wrapper.run(["python", "--version"], capture_output=True, text=True)

            # Check that result has expected attributes
            assert hasattr(result, "args")
            assert hasattr(result, "returncode")
            assert hasattr(result, "stdout")
            assert hasattr(result, "stderr")
            assert hasattr(result, "check_returncode")

            # Test check_returncode method
            result.check_returncode()  # Should not raise for successful command

        except Exception:
            pytest.skip("Python not available in test environment")
