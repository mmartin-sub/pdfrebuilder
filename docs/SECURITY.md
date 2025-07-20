# Security Guidelines

This document outlines security considerations and best practices for the Multi-Format Document Engine.

## Security Overview

The Multi-Format Document Engine processes potentially untrusted documents and must handle various security concerns including malicious content, resource exhaustion, and data exposure. The system implements multiple layers of security controls to ensure safe processing of documents from unknown sources.

### Security Principles

- **Defense in Depth**: Multiple security layers protect against various attack vectors
- **Secure by Default**: Safe configuration options are used by default
- **Input Validation**: All inputs are validated before processing
- **Resource Management**: Strict limits prevent resource exhaustion attacks
- **Minimal Privileges**: Components operate with minimal required permissions

## Input Validation

### Document Format Validation

All input documents undergo strict validation before processing:

```python
from src.engine.document_parser import parse_document
from src.models.schema_validator import validate_document_schema

def validate_input_document(file_path: str) -> ValidationResult:
    # Check file size limits
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        raise SecurityError("File size exceeds limit")

    # Validate file format and structure
    if not is_supported_format(file_path):
        raise SecurityError("Unsupported file format")

    # Parse with security constraints
    try:
        document = parse_document(file_path, extraction_flags={
            "include_text": True,
            "include_images": True,
            "include_drawings_non_background": True,
            "include_raw_background_drawings": False  # Security: exclude raw backgrounds
        })
    except Exception as e:
        raise SecurityError(f"Document parsing failed: {e}")

    # Validate document schema
    validation_result = validate_document_schema(document)
    if not validation_result.is_valid:
        raise SecurityError("Document schema validation failed")
```

### Content Sanitization

The system implements comprehensive content sanitization:

- **Text Content**: All text is sanitized to prevent injection attacks and malicious scripts
- **Image Data**: Images are validated, re-encoded, and stripped of potentially malicious metadata
- **Vector Graphics**: SVG and other vector content is parsed and sanitized to remove scripts
- **Embedded Objects**: Embedded files, scripts, and external references are removed or sandboxed
- **Font Files**: Font files undergo security validation before use

### XML Security

Special attention is paid to XML-based content security:

```python
from defusedxml import ElementTree as ET

def parse_xml_safely(xml_content: str):
    """Parse XML content with security protections against XXE and other attacks."""
    try:
        # Use defusedxml to prevent XXE attacks
        root = ET.fromstring(xml_content)
        return root
    except ET.ParseError as e:
        raise SecurityError(f"XML parsing failed: {e}")
```

## Resource Management

### Memory Limits

```python
# Memory usage monitoring
import resource

def set_memory_limit(max_memory_mb: int):
    """Set maximum memory usage for document processing"""
    max_memory = max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
```

### Processing Timeouts

All operations have configurable timeouts to prevent resource exhaustion:

```python
from src.settings import CONFIG

# Timeout configuration through settings
PROCESSING_TIMEOUTS = {
    "pdf_extraction": 300,  # 5 minutes
    "psd_processing": 600,  # 10 minutes
    "image_processing": 120,  # 2 minutes
    "font_validation": 60,   # 1 minute
    "visual_comparison": 180  # 3 minutes
}

def with_timeout(func, timeout_seconds: int):
    """Execute function with timeout protection."""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        result = func()
        return result
    finally:
        signal.alarm(0)
```

### File System Access

The system implements strict file system access controls:

- **Restricted Paths**: Access limited to configured output directories
- **Path Validation**: Prevention of directory traversal attacks
- **Temporary Files**: Secure cleanup of temporary files with automatic deletion
- **Permission Checks**: Validate file permissions before access
- **Output Directory Management**: Configurable, sandboxed output directories

```python
from src.settings import output_config, get_config_value

# Secure output directory management
def get_safe_output_path(filename: str, subdir: str = "") -> str:
    """Get a safe output path within configured directories."""
    # Validate filename for security
    if ".." in filename or "/" in filename or "\\" in filename:
        raise SecurityError("Invalid filename: path traversal detected")

    # Use configured output directory
    return output_config.get_output_path(filename, subdir)
```

## Hash Algorithm Security

### Secure Hash Usage Guidelines

The system uses various hash algorithms for different purposes. It's critical to use the appropriate algorithm and security flags for each use case.

#### Non-Cryptographic Hash Usage

For file integrity checking, caching, and other non-security purposes, MD5 is acceptable when properly flagged:

```python
import hashlib

# ✅ CORRECT: MD5 for non-cryptographic purposes
def generate_cache_key(file_path: str) -> str:
    """Generate cache key for file (non-cryptographic use)."""
    with open(file_path, "rb") as f:
        # Use usedforsecurity=False to indicate non-cryptographic usage
        checksum = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
    return checksum

# ❌ INCORRECT: MD5 without security flag (triggers security warnings)
def bad_cache_key(file_path: str) -> str:
    with open(file_path, "rb") as f:
        checksum = hashlib.md5(f.read()).hexdigest()  # Security warning!
    return checksum
```

#### Cryptographic Hash Usage

For security-sensitive operations, use SHA-256 or stronger algorithms:

```python
import hashlib

# ✅ CORRECT: SHA-256 for cryptographic purposes
def generate_secure_hash(data: bytes) -> str:
    """Generate cryptographically secure hash."""
    return hashlib.sha256(data).hexdigest()

# ✅ CORRECT: SHA-256 for password hashing (with salt)
def hash_password(password: str, salt: bytes) -> str:
    """Hash password with salt using secure algorithm."""
    return hashlib.sha256(password.encode() + salt).hexdigest()
```

#### Hash Algorithm Selection Guide

| Use Case | Recommended Algorithm | Security Flag Required |
|----------|----------------------|----------------------|
| File integrity checking | MD5 | `usedforsecurity=False` |
| Cache key generation | MD5 | `usedforsecurity=False` |
| Unique ID generation | MD5 | `usedforsecurity=False` |
| Password hashing | SHA-256 + salt | N/A |
| Digital signatures | SHA-256 or stronger | N/A |
| Cryptographic operations | SHA-256 or stronger | N/A |

#### Code Review Guidelines

When reviewing hash-related code:

1. **Check Algorithm Choice**: Ensure appropriate algorithm for the use case
2. **Verify Security Flags**: MD5 must include `usedforsecurity=False` for non-cryptographic use
3. **Validate Context**: Ensure cryptographic operations use secure algorithms
4. **Review Comments**: Code should clearly indicate the purpose of hashing

#### Example: Font Checksum Generation

```python
def calculate_font_checksum(font_path: str) -> str:
    """
    Calculate font file checksum for caching and integrity verification.

    Uses MD5 for non-cryptographic file integrity checking.
    This is safe for caching purposes and provides good performance.
    """
    with open(font_path, "rb") as f:
        # MD5 used for non-cryptographic file integrity checking
        checksum = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
    return checksum
```

## Font Security

### Font Validation

The system includes comprehensive font security validation:

```python
from src.font.font_validator import FontValidator
from src.settings import get_config_value

def validate_font_file(font_path: str) -> bool:
    """Validate font file for security issues"""
    validator = FontValidator()

    # Check file size limits
    max_font_size = 50 * 1024 * 1024  # 50MB limit
    if os.path.getsize(font_path) > max_font_size:
        raise SecurityError("Font file exceeds size limit")

    # Validate font format and structure
    try:
        validation_result = validator.validate_font_file(font_path)
        if not validation_result.is_valid:
            raise SecurityError(f"Font validation failed: {validation_result.errors}")
    except Exception as e:
        raise SecurityError(f"Font validation error: {e}")

    # Check for embedded scripts or malicious content
    if validator.has_malicious_content(font_path):
        raise SecurityError("Font contains potentially malicious content")

    return True
```

### Font Licensing and Management

The font management system includes security-aware licensing:

- **License Validation**: Comprehensive checking of font licensing before use
- **Usage Tracking**: Monitor font usage for compliance and security auditing
- **Fallback Fonts**: Use safe, system fallback fonts when licensing is unclear
- **Font Directory Security**: Separate directories for auto-downloaded and manual fonts
- **Font Source Validation**: Verify font sources and integrity

```python
from src.font.font_validator import FontValidator

def validate_font_licensing(font_name: str) -> dict:
    """Validate font licensing and usage rights."""
    validator = FontValidator()

    licensing_info = validator.check_font_licensing(font_name)

    return {
        "is_licensed": licensing_info.get("is_licensed", False),
        "license_type": licensing_info.get("license_type", "unknown"),
        "usage_restrictions": licensing_info.get("restrictions", []),
        "commercial_use_allowed": licensing_info.get("commercial_use", False)
    }
```

## Configuration Security

### Secure Defaults

```json
{
  "security": {
    "max_file_size_mb": 100,
    "max_processing_time_seconds": 300,
    "allow_external_resources": false,
    "sandbox_mode": true,
    "validate_all_inputs": true
  }
}
```

### Configuration Validation

All configuration files are validated:

```python
def validate_security_config(config: dict) -> None:
    """Validate security-related configuration"""
    required_keys = ["max_file_size_mb", "max_processing_time_seconds"]

    for key in required_keys:
        if key not in config:
            raise ConfigurationError(f"Missing required security setting: {key}")

    # Validate ranges
    if config["max_file_size_mb"] > 1000:
        raise ConfigurationError("File size limit too high")
```

## Network Security

### External Resources

- **Disabled by Default**: External resource loading disabled
- **Whitelist Approach**: Only approved external resources allowed
- **Proxy Support**: Route external requests through security proxy

### API Security (Future)

When REST API is implemented:

- **Authentication**: Token-based authentication required
- **Rate Limiting**: Request rate limits enforced
- **Input Validation**: All API inputs validated
- **HTTPS Only**: Encrypted communication required

## Threat Model

### Identified Threats

1. **Malicious Documents**: Documents containing exploits or malware
2. **Resource Exhaustion**: Documents designed to consume excessive resources
3. **Data Exfiltration**: Attempts to access unauthorized files
4. **Code Injection**: Embedded scripts or code execution attempts
5. **Font Exploits**: Malicious font files causing system compromise

### Mitigation Strategies

1. **Sandboxing**: Run processing in isolated environments
2. **Input Validation**: Comprehensive validation of all inputs
3. **Resource Limits**: Strict limits on memory, CPU, and time
4. **Monitoring**: Log and monitor all security-relevant events
5. **Regular Updates**: Keep dependencies updated for security patches

## Security Testing

### Automated Security Tests

```python
def test_malicious_pdf_handling():
    """Test handling of potentially malicious PDF files"""
    malicious_samples = [
        "tests/security/malicious_javascript.pdf",
        "tests/security/resource_exhaustion.pdf",
        "tests/security/embedded_files.pdf"
    ]

    for sample in malicious_samples:
        with pytest.raises(SecurityError):
            process_document(sample)
```

### Security Scanning

Regular security scans should include:

- **Dependency Scanning**: Check for vulnerable dependencies
- **Static Analysis**: Code analysis for security issues
- **Dynamic Testing**: Runtime security testing
- **Penetration Testing**: External security assessment

## Incident Response

### Security Incident Handling

1. **Detection**: Monitor for security events
2. **Containment**: Isolate affected systems
3. **Analysis**: Determine scope and impact
4. **Recovery**: Restore normal operations
5. **Lessons Learned**: Update security measures

### Reporting Security Issues

To report security vulnerabilities:

1. **Do not** create public issues for security problems
2. Contact maintainers directly via secure channels
3. Provide detailed information about the vulnerability
4. Allow reasonable time for fixes before disclosure

## Compliance

### Data Protection

- **Data Minimization**: Process only necessary data
- **Retention Limits**: Delete processed data when no longer needed
- **Access Controls**: Restrict access to sensitive data
- **Audit Logging**: Log all data access and processing

### Industry Standards

The system aims to comply with:

- **OWASP Guidelines**: Web application security best practices
- **ISO 27001**: Information security management
- **NIST Framework**: Cybersecurity framework guidelines

## Security Configuration Examples

### Production Security Settings

```json
{
  "security": {
    "max_file_size_mb": 50,
    "max_processing_time_seconds": 180,
    "allow_external_resources": false,
    "sandbox_mode": true,
    "validate_all_inputs": true,
    "log_security_events": true,
    "enable_resource_monitoring": true,
    "font_validation_strict": true
  }
}
```

### Development Security Settings

```json
{
  "security": {
    "max_file_size_mb": 200,
    "max_processing_time_seconds": 600,
    "allow_external_resources": true,
    "sandbox_mode": false,
    "validate_all_inputs": true,
    "log_security_events": true,
    "enable_resource_monitoring": false,
    "font_validation_strict": false
  }
}
```

## Recent Security Improvements

The following security vulnerabilities have been addressed through comprehensive security refactoring:

### Subprocess Security (B404, B603)

**Issues Addressed:**

- Direct subprocess imports without security considerations
- Subprocess calls without explicit `shell=False`
- Lack of input validation for command execution

**Solutions Implemented:**

- Created centralized `SecureSubprocessRunner` class
- Enforced `shell=False` for all subprocess calls
- Added comprehensive command validation
- Implemented executable whitelisting
- Added timeout enforcement and security logging

**Files Refactored:**

- `examples/validation.py`
- `scripts/deploy_documentation.py`
- `scripts/generate_final_validation_report.py`
- `scripts/run_documentation_tests.py`
- `scripts/run_tests.py`
- `scripts/update_documentation.py`

### Temporary File Security (B108)

**Issues Addressed:**

- Hardcoded temporary directory paths
- Predictable temporary file locations
- Insufficient access controls on temporary files

**Solutions Implemented:**

- Created `SecurePathManager` for secure temporary file handling
- Used system `tempfile.mkdtemp()` with secure permissions
- Implemented automatic cleanup of temporary resources
- Added path validation and traversal prevention

**Files Refactored:**

- `debug_font_registration.py`

### Security Architecture

The security improvements introduce two core security modules:

#### `src/security/subprocess_utils.py`

- `SubprocessSecurityValidator`: Command and path validation
- `SecureSubprocessRunner`: Secure subprocess execution
- `SecureTempManager`: Temporary file management

#### `src/security/path_utils.py`

- `SecurePathManager`: Path validation and secure file operations
- Path traversal prevention
- Secure temporary file creation

For detailed information about these security improvements, see [SECURITY_IMPROVEMENTS.md](SECURITY_IMPROVEMENTS.md).

## Regular Security Maintenance

### Monthly Tasks

- Review security logs for anomalies
- Update dependency security scans
- Review and update security configurations
- Test incident response procedures

### Quarterly Tasks

- Conduct security architecture review
- Update threat model based on new features
- Review and update security documentation
- Conduct security training for developers

### Annual Tasks

- Comprehensive security audit
- Penetration testing
- Security policy review and updates
- Compliance assessment and certification
