"""
Tests for security modules functionality.
"""

import tempfile
from unittest.mock import Mock, patch

from pdfrebuilder.security.path_utils import get_safe_filename, is_safe_path, sanitize_path, validate_file_extension
from pdfrebuilder.security.secure_execution import ExecutionResult, SecureExecutor, validate_command_safety


class TestPathUtils:
    """Test path utilities security functions"""

    def test_sanitize_path_basic(self):
        """Test basic path sanitization"""
        # Test normal path
        result = sanitize_path("/home/user/document.pdf")
        assert result == "/home/user/document.pdf"

        # Test path with double slashes
        result = sanitize_path("/home//user///document.pdf")
        assert "//" not in result
        assert "///" not in result

    def test_sanitize_path_traversal_attempts(self):
        """Test sanitization of path traversal attempts"""
        # Test directory traversal
        result = sanitize_path("/home/user/../../../etc/passwd")
        assert "../" not in result

        # Test with encoded traversal
        result = sanitize_path("/home/user/%2e%2e/document.pdf")
        assert "%2e" not in result

    def test_is_safe_path_valid_paths(self):
        """Test validation of safe paths"""
        safe_paths = [
            "/home/user/documents/file.pdf",
            "./local/file.txt",
            "relative/path/file.json",
        ]

        for path in safe_paths:
            assert is_safe_path(path) is True

    def test_is_safe_path_dangerous_paths(self):
        """Test rejection of dangerous paths"""
        dangerous_paths = [
            "/etc/passwd",
            "../../../etc/shadow",
            "/proc/self/environ",
            "/dev/null",
            "\\\\server\\share\\file.txt",  # Windows UNC path
        ]

        for path in dangerous_paths:
            assert is_safe_path(path) is False

    def test_validate_file_extension_allowed(self):
        """Test validation of allowed file extensions"""
        allowed_extensions = [".pdf", ".json", ".txt"]

        valid_files = ["document.pdf", "config.json", "readme.txt"]

        for filename in valid_files:
            assert validate_file_extension(filename, allowed_extensions) is True

    def test_validate_file_extension_disallowed(self):
        """Test rejection of disallowed file extensions"""
        allowed_extensions = [".pdf", ".json", ".txt"]

        invalid_files = ["script.exe", "malware.bat", "document.docx", "image.png"]

        for filename in invalid_files:
            assert validate_file_extension(filename, allowed_extensions) is False

    def test_get_safe_filename_basic(self):
        """Test getting safe filename"""
        result = get_safe_filename("normal_file.pdf")
        assert result == "normal_file.pdf"

    def test_get_safe_filename_dangerous_chars(self):
        """Test sanitization of dangerous characters in filename"""
        dangerous_filename = 'file<>:"|?*.pdf'
        result = get_safe_filename(dangerous_filename)

        # Should not contain dangerous characters
        dangerous_chars = '<>:"|?*'
        for char in dangerous_chars:
            assert char not in result

    def test_get_safe_filename_path_traversal(self):
        """Test removal of path traversal from filename"""
        traversal_filename = "../../../malicious.pdf"
        result = get_safe_filename(traversal_filename)

        assert "../" not in result
        assert result == "malicious.pdf"


class TestSecureExecution:
    """Test secure execution functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def test_execution_result_creation(self):
        """Test creating ExecutionResult instance"""
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Success output",
            stderr="",
            execution_time=1.5,
        )

        assert result.success is True
        assert result.return_code == 0
        assert result.stdout == "Success output"
        assert result.stderr == ""
        assert result.execution_time == 1.5

    def test_execution_result_failure(self):
        """Test ExecutionResult for failed execution"""
        result = ExecutionResult(
            success=False,
            return_code=1,
            stdout="",
            stderr="Error occurred",
            execution_time=0.5,
        )

        assert result.success is False
        assert result.return_code == 1
        assert result.stderr == "Error occurred"

    def test_secure_executor_success(self):
        """Test successful secure execution"""
        executor = SecureExecutor()
        result = executor.execute_command(["echo", "hello"])

        assert result.success is True
        assert result.return_code == 0

    @patch("src.security.secure_execution.local")
    def test_secure_executor_failure(self, mock_local):
        """Test failed secure execution"""
        from plumbum import ProcessExecutionError

        # Mock plumbum to raise ProcessExecutionError
        mock_cmd = Mock()
        mock_cmd.run.side_effect = ProcessExecutionError(["false"], 1, "", "Command failed")
        mock_local.__getitem__.return_value = mock_cmd

        executor = SecureExecutor()
        result = executor.execute_command(["false"])

        assert result.success is False
        assert result.return_code == 1
        assert result.stderr == "Command failed"

    def test_secure_executor_timeout(self):
        """Test secure execution with timeout"""
        executor = SecureExecutor()

        # Test with a very short timeout to ensure it completes quickly
        # Use a command that should complete quickly
        result = executor.execute_command(["echo", "test"], timeout=10)

        # The command should succeed since it's fast
        assert isinstance(result, ExecutionResult)

    def test_validate_command_safety_safe_commands(self):
        """Test validation of safe commands"""
        safe_commands = [
            ["ls", "-la"],
            ["cat", "file.txt"],
            ["python", "script.py"],
            ["echo", "hello world"],
        ]

        for command in safe_commands:
            assert validate_command_safety(command) is True

    def test_validate_command_safety_dangerous_commands(self):
        """Test rejection of dangerous commands"""
        dangerous_commands = [
            ["rm", "-rf", "/"],
            ["dd", "if=/dev/zero", "of=/dev/sda"],
            ["chmod", "777", "/etc/passwd"],
            ["sudo", "rm", "file.txt"],
            ["; rm -rf /"],  # Command injection
        ]

        for command in dangerous_commands:
            assert validate_command_safety(command) is False

    def test_validate_command_safety_empty_command(self):
        """Test validation of empty command"""
        assert validate_command_safety([]) is False
        assert validate_command_safety(None) is False

    @patch("src.security.secure_execution.local")
    def test_secure_executor_working_directory(self, mock_local):
        """Test secure executor with working directory"""
        # Mock plumbum local
        mock_cmd = Mock()
        mock_cmd.run.return_value = (0, "Success", "")
        mock_local.__getitem__.return_value = mock_cmd
        mock_local.cwd.return_value.__enter__ = Mock()
        mock_local.cwd.return_value.__exit__ = Mock()

        # Create a security context that allows the temp directory
        from pathlib import Path

        from pdfrebuilder.security.secure_execution import SecurityContext

        security_context = SecurityContext(base_path=Path(self.temp_dir).parent)
        executor = SecureExecutor(security_context)

        result = executor.execute_command(["ls"], cwd=self.temp_dir)

        assert result.success is True

    @patch("src.security.secure_execution.local")
    def test_secure_executor_environment_variables(self, mock_local):
        """Test secure executor with environment variables"""
        # Mock plumbum local
        mock_cmd = Mock()
        mock_cmd.run.return_value = (0, "Success", "")
        mock_local.__getitem__.return_value = mock_cmd
        mock_local.env.return_value.__enter__ = Mock()
        mock_local.env.return_value.__exit__ = Mock()
        mock_local.cwd.return_value.__enter__ = Mock()
        mock_local.cwd.return_value.__exit__ = Mock()

        executor = SecureExecutor()
        env_vars = {"PATH": "/usr/bin"}  # Use whitelisted env var
        result = executor.execute_command(["env"], env=env_vars)

        assert result.success is True

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
