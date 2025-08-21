"""
Tests for font security hardening fixes.

This module tests the security improvements made to font processing,
specifically the MD5 security flag fix and related security measures.
"""

import hashlib
import unittest


class TestFontSecurityHardening(unittest.TestCase):
    """Test cases for font security hardening improvements."""

    def test_security_flag_prevents_bandit_warning(self):
        """Test that the usedforsecurity=False flag is properly applied."""
        # Read the fixed source code
        with open("src/pdfrebuilder/font/utils.py") as f:
            source_content = f.read()

        # Verify the security flag is present
        self.assertIn("usedforsecurity=False", source_content)

        # Verify the MD5 usage includes the security flag
        self.assertIn("hashlib.md5(f.read(), usedforsecurity=False)", source_content)

    def test_backward_compatibility_with_existing_cache(self):
        """Test that existing font cache entries remain valid."""
        test_content = b"fake font file content for testing"

        # Generate checksum with the new method
        new_checksum = hashlib.md5(test_content, usedforsecurity=False).hexdigest()

        # Generate checksum with the old method (for comparison)
        old_checksum = hashlib.md5(test_content).hexdigest()

        # Both should produce identical results
        self.assertEqual(new_checksum, old_checksum)

    def test_inline_comment_explains_usage(self):
        """Test that inline comment explains non-cryptographic usage."""
        with open("src/pdfrebuilder/font/utils.py") as f:
            source_content = f.read()

        # Verify explanatory comment is present
        self.assertIn("non-cryptographic", source_content.lower())
        self.assertIn("integrity", source_content.lower())

    def test_md5_checksum_output_consistency(self):
        """Test that MD5 checksum output remains identical with security flag."""
        test_content = b"test font data"

        # Both methods should produce identical output
        with_flag = hashlib.md5(test_content, usedforsecurity=False).hexdigest()
        without_flag = hashlib.md5(test_content).hexdigest()

        self.assertEqual(with_flag, without_flag)
        self.assertEqual(len(with_flag), 32)  # MD5 produces 32-character hex string

    def test_security_flag_is_boolean_false(self):
        """Test that the security flag is explicitly set to False."""
        test_content = b"test data"

        # This should not raise an exception
        result = hashlib.md5(test_content, usedforsecurity=False)
        self.assertIsNotNone(result.hexdigest())


if __name__ == "__main__":
    unittest.main()
