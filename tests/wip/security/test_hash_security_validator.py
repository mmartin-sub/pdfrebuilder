"""
Tests for the hash security validator script.

This module tests the hash usage validation functionality to ensure
it correctly identifies and fixes security issues with hash algorithms.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.validate_hash_usage import HashUsageValidator


class TestHashSecurityValidator(unittest.TestCase):
    """Test cases for hash security validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = HashUsageValidator(fix_mode=False)
        self.fix_validator = HashUsageValidator(fix_mode=True)

    def test_detects_md5_without_security_flag(self):
        """Test that validator detects MD5 usage without security flag."""
        test_code = """
import hashlib

def bad_function():
    return hashlib.md5(b"test").hexdigest()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            f.flush()

            errors = self.validator.validate_file(Path(f.name))

            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0][1], "md5_missing_flag")
            self.assertIn("usedforsecurity=False", errors[0][2])

        Path(f.name).unlink()

    def test_accepts_md5_with_security_flag(self):
        """Test that validator accepts MD5 with proper security flag."""
        test_code = """
import hashlib

def good_function():
    return hashlib.md5(b"test", usedforsecurity=False).hexdigest()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            f.flush()

            errors = self.validator.validate_file(Path(f.name))

            self.assertEqual(len(errors), 0)

        Path(f.name).unlink()

    def test_ignores_comments(self):
        """Test that validator ignores MD5 usage in comments."""
        test_code = """
import hashlib

# This is a comment with hashlib.md5(data).hexdigest()
def function():
    return hashlib.md5(b"test", usedforsecurity=False).hexdigest()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            f.flush()

            errors = self.validator.validate_file(Path(f.name))

            self.assertEqual(len(errors), 0)

        Path(f.name).unlink()

    def test_fix_mode_applies_corrections(self):
        """Test that fix mode automatically corrects MD5 usage."""
        test_code = """
import hashlib

def function():
    return hashlib.md5(b"test").hexdigest()
"""

        expected_fixed_code = """
import hashlib

def function():
    return hashlib.md5(b"test", usedforsecurity=False).hexdigest()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            f.flush()

            # Apply fixes
            errors = self.fix_validator.validate_file(Path(f.name))

            # Read the fixed content
            with open(f.name) as fixed_file:
                fixed_content = fixed_file.read()

            self.assertEqual(fixed_content.strip(), expected_fixed_code.strip())
            self.assertEqual(len(errors), 0)  # No errors after fixing

        Path(f.name).unlink()

    def test_detects_violations_in_regular_code(self):
        """Test that validator detects violations in regular code."""
        test_code = """
import hashlib

def regular_function():
    return hashlib.md5(b"data").hexdigest()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            f.flush()

            errors = self.validator.validate_file(Path(f.name))

            # Should detect this violation
            self.assertEqual(len(errors), 1)

        Path(f.name).unlink()

    def test_handles_multiple_violations_in_file(self):
        """Test that validator handles multiple violations in a single file."""
        test_code = """
import hashlib

def function1():
    return hashlib.md5(b"test1").hexdigest()

def function2():
    return hashlib.md5(b"test2").hexdigest()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_code)
            f.flush()

            errors = self.validator.validate_file(Path(f.name))

            self.assertEqual(len(errors), 2)
            self.assertTrue(all(error[1] == "md5_missing_flag" for error in errors))

        Path(f.name).unlink()

    def test_validates_non_python_files_are_skipped(self):
        """Test that non-Python files are skipped."""
        test_content = "hashlib.md5(data).hexdigest()"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(test_content)
            f.flush()

            errors = self.validator.validate_file(Path(f.name))

            self.assertEqual(len(errors), 0)

        Path(f.name).unlink()


if __name__ == "__main__":
    unittest.main()
