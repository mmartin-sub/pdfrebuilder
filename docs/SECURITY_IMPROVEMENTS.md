# Security Improvements

This document outlines the security improvements implemented to address security vulnerabilities identified by static analysis tools.

## Overview

The security improvements focus on three main areas:

1. **Subprocess Security**: Preventing command injection attacks
2. **Path Security**: Preventing path traversal attacks
3. **Temporary File Security**: Secure handling of temporary files and directories

## Security Issues Addressed

### B108: Hardcoded Temporary Directory

**Issue**: Using hardcoded temporary directory paths like `/tmp/test_fonts/debug_test`

**Risk**:

- Predictable file locations that could be exploited
- Potential race conditions in shared temporary directories
- Insufficient access controls

**Solution**:

- Created `SecurePathManager` class with `create_secure_temp_directory()` method
- Uses system `tempfile.mkdtemp()` with secure permissions (0o700)
- Generates unpredictable directory names with secure prefixes

**Files Fixed**:

- `debug_font_registration.py`

### B404: Subprocess Import

**Issue**: Direct import and use of `subprocess` module without security considerations

**Risk**:

- Command injection vulnerabilities
- Execution of untrusted input
- Shell injection attacks

**Solution**:

- Created centralized `SecureSubprocessRunner` class
- Implemented command validation and sanitization
- Enforced `shell=False` for all subprocess calls
- Added input validation and path restrictions

**Files Fixed**:

- `examples/validation.py`
- `scripts/deploy_documentation.py`
- `scripts/generate_final_validation_report.py`
- `scripts/run_documentation_tests.py`
- `scripts/run_tests.py`
- `scripts/update_documentation.py`

### B603: Subprocess Without shell=False

**Issue**: Subprocess calls without explicitly setting `shell=False`

**Risk**:

- Shell injection attacks
- Command injection through shell metacharacters
- Execution of unintended commands

**Solution**:

- All subprocess calls now use `SecureSubprocessRunner`
- Enforced `shell=False` in security utilities
- Added comprehensive input validation
- Implemented command component validation

## Security Architecture

### Core Security Modules

#### `src/security/subprocess_utils.py`

Provides secure subprocess execution with the following features:

- **Command Validation**: Validates all command components for dangerous characters
- **Path Validation**: Ensures file paths are within allowed directories
- **Timeout Enforcement**: Prevents long-running processes
- **Shell Injection Prevention**: Forces `shell=False` for all calls
- **Executable Whitelisting**: Optional whitelist of allowed executables
- **Security Logging**: Logs all subprocess executions for auditing

Key Classes:

- `SubprocessSecurityValidator`: Validates commands and paths
- `SecureSubprocessRunner`: Executes commands securely
- `SecureTempManager`: Manages temporary files and directories

#### `src/security/path_utils.py`

Provides secure path handling with the following features:

- **Path Traversal Prevention**: Validates paths against base directories
- **Dangerous Character Detection**: Blocks paths with suspicious characters
- **Secure Temporary Files**: Creates temporary files with proper permissions
- **Directory Creation**: Ensures directories are created securely
- **File Writing**: Provides secure file writing utilities

Key Classes:

- `SecurePathManager`: Manages all path operations securely
- `PathSecurityError`: Custom exception for path security violations

### Security Best Practices Implemented

#### 1. Input Validation

All user inputs are validated before processing:

```python
# Command validation
def validate_command(cls, cmd: List[str]) -> None:
    for component in cmd:
        if not isinstance(component, str) or not component.strip():
            raise SecurityError("Invalid command component")

        for dangerous_char in cls.DANGEROUS_CHARS:
            if dangerous_char in component:
                raise SecurityError(f"Dangerous character: '{dangerous_char}'")
```

#### 2. Path Restriction

All file operations are restricted to allowed directories:

```python
# Path validation
def validate_path(cls, path: Union[str, Path], base_path: Optional[Path] = None) -> Path:
    resolved_path = path_obj.resolve()
    resolved_base = base_path.resolve()

    # Ensure path is within base directory
    resolved_path.relative_to(resolved_base)
```

#### 3. Secure Temporary Files

Temporary files are created with secure permissions:

```python
# Secure temp directory creation
temp_dir = Path(tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=base_dir))
temp_dir.chmod(0o700)  # Owner read/write/execute only
```

#### 4. Subprocess Hardening

All subprocess calls are hardened against injection:

```python
# Secure subprocess execution
result = subprocess.run(
    cmd,
    cwd=cwd,
    timeout=timeout,
    capture_output=True,
    text=True,
    shell=False,  # Always False for security
    **kwargs
)
```

## Migration Guide

### For Developers

When working with subprocess calls or file operations, use the security utilities:

#### Old Pattern (Insecure)

```python
import subprocess
import tempfile

# Insecure subprocess call
result = subprocess.run(["python", script_path], shell=True)

# Insecure temp directory
temp_dir = "/tmp/my_temp_dir"
```

#### New Pattern (Secure)

```python
from security.subprocess_utils import SecureSubprocessRunner
from security.path_utils import SecurePathManager

# Secure subprocess call
runner = SecureSubprocessRunner()
result = runner.run(["python", script_path])

# Secure temp directory
temp_dir = SecurePathManager.create_secure_temp_directory()
```

### Configuration

The security utilities can be configured through environment variables:

- `SECURITY_LOG_LEVEL`: Set logging level for security events
- `SECURITY_STRICT_MODE`: Enable strict security validation
- `SECURITY_ALLOWED_EXECUTABLES`: Comma-separated list of allowed executables

## Testing

Security improvements include comprehensive tests:

- Command injection prevention tests
- Path traversal attack tests
- Temporary file security tests
- Subprocess execution validation tests

Run security tests with:

```bash
hatch run test tests/test_security/
```

## Monitoring and Auditing

### Security Logging

All security-related operations are logged:

```python
logger.info(f"Executing secure subprocess: {' '.join(shlex.quote(arg) for arg in cmd)}")
logger.warning(f"Executable '{executable}' not in whitelist")
logger.error(f"Security violation: {error_message}")
```

### Audit Trail

The security utilities maintain an audit trail of:

- All subprocess executions
- File path validations
- Security violations
- Temporary file creations

## Compliance

These security improvements help ensure compliance with:

- **CWE-78**: OS Command Injection
- **CWE-377**: Insecure Temporary File
- **CWE-22**: Path Traversal
- **OWASP Top 10**: Injection vulnerabilities

## Future Enhancements

Planned security enhancements include:

1. **Sandboxing**: Container-based execution isolation
2. **Resource Limits**: CPU and memory limits for subprocess calls
3. **Network Restrictions**: Network access controls for subprocess calls
4. **Enhanced Logging**: Structured security event logging
5. **Security Metrics**: Automated security metrics collection

## References

- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
- [CWE-377: Insecure Temporary File](https://cwe.mitre.org/data/definitions/377.html)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [Python Security Best Practices](https://python.org/dev/security/)
