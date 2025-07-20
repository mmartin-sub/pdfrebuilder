# Hash Algorithm Security Guidelines

This document provides comprehensive guidelines for secure hash algorithm usage in the Multi-Format Document Engine.

## Overview

Hash algorithms serve different purposes in our system, from file integrity checking to cryptographic security. Using the wrong algorithm or improper security flags can create security vulnerabilities or trigger false positive security warnings.

## Security Context

### Recent Security Fix

**Issue**: MD5 usage in `src/font_utils.py` triggered security warning B324
**Root Cause**: Missing `usedforsecurity=False` flag for non-cryptographic MD5 usage
**Resolution**: Added security flag to indicate non-cryptographic purpose

```python
# Before (triggered security warning)
checksum = hashlib.md5(f.read()).hexdigest()

# After (security compliant)
checksum = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
```

## Hash Algorithm Guidelines

### 1. Non-Cryptographic Uses

For file integrity, caching, and unique identifiers where security is not a concern:

#### ✅ Acceptable: MD5 with Security Flag

```python
import hashlib

def generate_file_checksum(file_path: str) -> str:
    """Generate file checksum for integrity verification (non-cryptographic)."""
    with open(file_path, "rb") as f:
        # MD5 is acceptable for non-cryptographic file integrity checking
        return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()

def create_cache_key(data: str) -> str:
    """Create cache key from string data (non-cryptographic)."""
    # MD5 provides good distribution for cache keys
    return hashlib.md5(data.encode(), usedforsecurity=False).hexdigest()

def generate_unique_id(content: bytes) -> str:
    """Generate unique identifier for content (non-cryptographic)."""
    # MD5 is sufficient for generating unique IDs
    return hashlib.md5(content, usedforsecurity=False).hexdigest()[:8]
```

#### ❌ Incorrect: MD5 without Security Flag

```python
# This will trigger security warning B324
def bad_checksum(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()  # Missing usedforsecurity=False
```

### 2. Cryptographic Uses

For security-sensitive operations where hash collision resistance is critical:

#### ✅ Required: SHA-256 or Stronger

```python
import hashlib
import secrets

def secure_hash(data: bytes) -> str:
    """Generate cryptographically secure hash."""
    return hashlib.sha256(data).hexdigest()

def hash_password(password: str) -> tuple[str, str]:
    """Hash password with random salt (cryptographic)."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def verify_integrity(data: bytes, expected_hash: str) -> bool:
    """Verify data integrity using secure hash (cryptographic)."""
    actual_hash = hashlib.sha256(data).hexdigest()
    return actual_hash == expected_hash
```

#### ❌ Incorrect: MD5 for Security

```python
# Never use MD5 for cryptographic purposes
def insecure_password_hash(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()  # Vulnerable to attacks
```

## Use Case Matrix

| Purpose | Algorithm | Security Flag | Example |
|---------|-----------|---------------|---------|
| File checksums | MD5 | `usedforsecurity=False` | Font file integrity |
| Cache keys | MD5 | `usedforsecurity=False` | Operation result caching |
| Unique IDs | MD5 | `usedforsecurity=False` | Element identification |
| Password hashing | SHA-256+ | N/A | User authentication |
| Digital signatures | SHA-256+ | N/A | Document signing |
| Cryptographic tokens | SHA-256+ | N/A | API tokens |

## Implementation Examples

### Font System Example

```python
class FontMetadata:
    """Font metadata with secure checksum generation."""

    def __init__(self, font_path: str):
        self.font_path = font_path
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate font file checksum for caching and integrity."""
        try:
            with open(self.font_path, "rb") as f:
                # MD5 used for non-cryptographic file integrity checking
                return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
        except IOError as e:
            raise FontError(f"Cannot calculate checksum for {self.font_path}: {e}")

    def verify_integrity(self) -> bool:
        """Verify font file hasn't changed since metadata creation."""
        current_checksum = self._calculate_checksum()
        return current_checksum == self.checksum
```

### Cache System Example

```python
class DocumentCache:
    """Document processing cache with secure key generation."""

    def generate_cache_key(self, file_path: str, options: dict) -> str:
        """Generate cache key from file and processing options."""
        # Combine file path and options for unique key
        key_data = f"{file_path}:{sorted(options.items())}"

        # MD5 provides good distribution for cache keys (non-cryptographic)
        return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()

    def get_file_hash(self, file_path: str) -> str:
        """Get file content hash for cache validation."""
        with open(file_path, "rb") as f:
            # MD5 for file content identification (non-cryptographic)
            return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
```

## Code Review Checklist

When reviewing hash-related code, verify:

### ✅ Security Compliance

- [ ] MD5 usage includes `usedforsecurity=False` for non-cryptographic purposes
- [ ] Cryptographic operations use SHA-256 or stronger algorithms
- [ ] No MD5 usage for security-sensitive operations

### ✅ Documentation

- [ ] Code comments explain the purpose of hashing
- [ ] Security flags are documented when used
- [ ] Algorithm choice is justified for the use case

### ✅ Error Handling

- [ ] Hash generation failures are properly handled
- [ ] File I/O errors are caught and reported
- [ ] Invalid hash values are validated

### ✅ Performance

- [ ] Large files are processed in chunks when appropriate
- [ ] Hash results are cached when beneficial
- [ ] Unnecessary hash recalculation is avoided

## Testing Guidelines

### Unit Tests for Hash Functions

```python
import unittest
import hashlib

class TestHashSecurity(unittest.TestCase):
    """Test hash algorithm security compliance."""

    def test_md5_security_flag(self):
        """Test that MD5 includes security flag for non-cryptographic use."""
        test_data = b"test data"

        # Both methods should produce identical results
        with_flag = hashlib.md5(test_data, usedforsecurity=False).hexdigest()
        without_flag = hashlib.md5(test_data).hexdigest()

        self.assertEqual(with_flag, without_flag)

    def test_source_code_compliance(self):
        """Test that source code follows hash security guidelines."""
        with open('src/font_utils.py', 'r') as f:
            source = f.read()

        # Verify MD5 usage includes security flag
        self.assertIn('usedforsecurity=False', source)

        # Verify no bare MD5 calls
        import re
        bare_md5_pattern = r'hashlib\.md5\([^)]*\)\.hexdigest\(\)'
        bare_md5_matches = re.findall(bare_md5_pattern, source)

        # Filter out calls that include usedforsecurity
        problematic_calls = [
            match for match in bare_md5_matches
            if 'usedforsecurity' not in match
        ]

        self.assertEqual(len(problematic_calls), 0,
                        f"Found MD5 calls without security flag: {problematic_calls}")
```

## Security Scanner Integration

### Bandit Configuration

Ensure your `.bandit` configuration allows proper MD5 usage:

```yaml
# .bandit
tests: [B324]
skips: []

# B324: hashlib - Allow MD5 with usedforsecurity=False
```

### Pre-commit Hooks

Add hash security validation to pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: hash-security-check
        name: Hash Security Check
        entry: python scripts/validate_hash_usage.py
        language: system
        files: '\.py$'
```

## Migration Guide

### Updating Existing MD5 Usage

1. **Identify MD5 Usage**: Search for `hashlib.md5` in codebase
2. **Assess Purpose**: Determine if usage is cryptographic or non-cryptographic
3. **Add Security Flag**: For non-cryptographic uses, add `usedforsecurity=False`
4. **Replace Algorithm**: For cryptographic uses, replace with SHA-256
5. **Test Changes**: Verify functionality remains unchanged
6. **Update Tests**: Ensure tests cover the security improvements

### Example Migration

```python
# Before migration
def old_function(data):
    return hashlib.md5(data).hexdigest()

# After migration (non-cryptographic)
def new_function(data):
    # MD5 used for non-cryptographic data identification
    return hashlib.md5(data, usedforsecurity=False).hexdigest()

# After migration (cryptographic)
def secure_function(data):
    # SHA-256 for cryptographic security
    return hashlib.sha256(data).hexdigest()
```

## Conclusion

Proper hash algorithm usage is critical for both security and compliance. By following these guidelines, developers can:

- Avoid security vulnerabilities
- Prevent false positive security warnings
- Maintain code clarity and documentation
- Ensure appropriate algorithm selection for each use case

Remember: **When in doubt, use SHA-256 for security purposes and MD5 with `usedforsecurity=False` for non-cryptographic purposes.**
