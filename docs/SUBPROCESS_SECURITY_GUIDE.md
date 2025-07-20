# Subprocess Security Guide

## Table of Contents

1. [Overview](#overview)
2. [Security Risks and Vulnerabilities](#security-risks-and-vulnerabilities)
3. [Secure Subprocess Patterns](#secure-subprocess-patterns)
4. [Migration Guide](#migration-guide)
5. [Security Testing and Validation](#security-testing-and-validation)
6. [Troubleshooting and Common Issues](#troubleshooting-and-common-issues)
7. [Best Practices](#best-practices)
8. [Reference](#reference)

## Overview

This guide provides comprehensive information on secure subprocess usage in Python applications, with specific focus on preventing command injection vulnerabilities and following security best practices. The guide covers both traditional subprocess security measures and modern secure alternatives like the plumbum library.

### Why Subprocess Security Matters

Subprocess operations are a common attack vector in Python applications. Improper use can lead to:

- **Command Injection**: Attackers can execute arbitrary commands
- **Path Traversal**: Unauthorized file system access
- **Resource Exhaustion**: Uncontrolled process execution
- **Information Disclosure**: Sensitive data exposure through command output
- **Privilege Escalation**: Running commands with elevated privileges

### Security Philosophy

Our approach to subprocess security follows these principles:

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal permissions and capabilities
3. **Input Validation**: Strict validation of all inputs
4. **Audit Logging**: Comprehensive logging for security monitoring
5. **Fail Secure**: Secure defaults and graceful failure handling

## Security Risks and Vulnerabilities

### Common Vulnerability Patterns

#### 1. Shell Injection (CWE-78)

**Vulnerable Code:**

```python
import subprocess

# DANGEROUS: User input directly in shell command
user_input = request.form['filename']
subprocess.run(f"cat {user_input}", shell=True)  # VULNERABLE

# DANGEROUS: String formatting with user input
subprocess.run("python script.py --file {}".format(user_input), shell=True)  # VULNERABLE
```

**Attack Example:**

```python
# Attacker provides: "file.txt; rm -rf /"
# Resulting command: "cat file.txt; rm -rf /"
```

#### 2. Argument Injection (CWE-88)

**Vulnerable Code:**

```python
# DANGEROUS: User input as arguments without validation
subprocess.run(["python", "script.py", user_input])  # POTENTIALLY VULNERABLE

# Attack example: user_input = "--eval=__import__('os').system('rm -rf /')"
```

#### 3. Path Traversal (CWE-22)

**Vulnerable Code:**

```python
# DANGEROUS: No path validation
file_path = request.form['path']
subprocess.run(["cat", file_path])  # VULNERABLE

# Attack example: file_path = "../../../../etc/passwd"
```

#### 4. Resource Exhaustion (CWE-400)

**Vulnerable Code:**

```python
# DANGEROUS: No timeout or resource limits
subprocess.run(["python", "script.py"])  # VULNERABLE TO RESOURCE EXHAUSTION
```

### Bandit Security Warnings

Our codebase uses bandit for security analysis. Key warnings to address:

- **B404**: `subprocess` module import - Consider security implications
- **B603**: `subprocess` call - Check for execution of untrusted input
- **B602**: `subprocess` with `shell=True` - High risk of command injection

##

 Secure Subprocess Patterns

### 1. Traditional Secure Subprocess Usage

#### Basic Secure Pattern

```python
import subprocess
import shlex
from pathlib import Path

def secure_subprocess_call(cmd_args, cwd=None, timeout=300):
    """
    Execute subprocess call with security controls.

    Args:
        cmd_args: List of command arguments (not string)
        cwd: Working directory (validated)
        timeout: Execution timeout in seconds

    Returns:
        subprocess.CompletedProcess result
    """
    # Validate arguments
    if not isinstance(cmd_args, list):
        raise ValueError("Command must be a list, not string")

    if not cmd_args:
        raise ValueError("Command cannot be empty")

    # Validate executable
    allowed_executables = ['python', 'python3', 'hatch', 'pytest', 'git']
    if cmd_args[0] not in allowed_executables:
        raise ValueError(f"Executable '{cmd_args[0]}' not allowed")

    # Validate working directory
    if cwd:
        cwd_path = Path(cwd).resolve()
        base_path = Path.cwd().resolve()
        try:
            cwd_path.relative_to(base_path)
        except ValueError:
            raise ValueError("Working directory outside allowed path")

    # Execute with security controls
    try:
        result = subprocess.run(
            cmd_args,                    # List, not string
            cwd=cwd,                    # Validated working directory
            timeout=timeout,            # Prevent hanging
            shell=False,                # Never use shell=True
            capture_output=True,        # Capture output for logging
            text=True,                  # Handle text encoding
            check=False                 # Handle errors manually
        )
        return result
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {timeout} seconds")
```

### 2. Modern Secure Alternative: Plumbum

#### Why Plumbum?

Plumbum provides a security-first approach to subprocess operations:

- **Type-safe command construction** prevents injection
- **Automatic argument escaping** handles complex inputs safely
- **No shell execution** by default eliminates shell injection risks
- **Rich error handling** provides better security context
- **Built-in validation** reduces manual security checks

#### Basic Plumbum Usage

```python
from plumbum import local, ProcessExecutionError
from plumbum.cmd import python, hatch, pytest
import logging

logger = logging.getLogger(__name__)

def execute_with_plumbum(executable_name: str, args: List[str], timeout: int = 300) -> str:
    """
    Execute command securely using plumbum.

    Args:
        executable_name: Name of executable to run
        args: List of arguments
        timeout: Timeout in seconds

    Returns:
        Command output as string

    Raises:
        ProcessExecutionError: If command fails
    """
    try:
        # Get command object (type-safe)
        cmd = local[executable_name]

        # Execute with arguments (automatically escaped)
        if args:
            result = cmd[args](timeout=timeout)
        else:
            result = cmd(timeout=timeout)

        logger.info(f"Command succeeded: {executable_name} {' '.join(args)}")
        return result

    except ProcessExecutionError as e:
        logger.error(f"Command failed: {e}")
        raise

# Usage examples
try:
    # Simple command
    version = execute_with_plumbum("python", ["--version"])

    # Complex command with multiple arguments
    test_result = execute_with_plumbum("pytest", [
        "tests/",
        "-v",
        "--tb=short",
        f"--maxfail=5"
    ])

except ProcessExecutionError as e:
    print(f"Command failed: {e}")
```

### 3. Using Our Secure Execution Module

Our project includes a comprehensive secure execution module at `src/security/secure_execution.py`:

```python
from src.security.secure_execution import (
    SecureExecutor, SecurityContext, execute_secure_command
)

# Basic usage
result = execute_secure_command(['python', '--version'])
print(f"Python version: {result.stdout}")

# Advanced usage with custom security context
context = SecurityContext(
    allowed_executables=['python', 'hatch', 'pytest'],
    timeout=600,
    base_path=Path('/safe/directory')
)

executor = SecureExecutor(context)
result = executor.execute_command(['pytest', 'tests/', '-v'])

if result.success:
    print("Tests passed!")
else:
    print(f"Tests failed: {result.stderr}")
```

## Migration Guide

### Phase 1: Assessment and Planning

#### 1. Audit Current Subprocess Usage

Use this script to find all subprocess usage in your codebase:

```bash
# Find all subprocess imports and calls
grep -r "import subprocess" src/
grep -r "from subprocess" src/
grep -r "subprocess\." src/
grep -r "shell=True" src/

# Find bandit suppressions
grep -r "# nosec B404" src/
grep -r "# nosec B603" src/
```

#### 2. Categorize Usage by Risk Level

**High Risk (Immediate Migration Required):**

- Any usage with `shell=True`
- User input in commands
- No timeout specified
- No input validation

**Medium Risk (Priority Migration):**

- Hardcoded commands without validation
- Missing error handling
- No audit logging

**Low Risk (Gradual Migration):**

- Well-validated internal commands
- Development/testing scripts
- Commands with comprehensive security controls

### Phase 2: High-Risk Migration

#### Replace shell=True Usage

**Before (Vulnerable):**

```python
import subprocess

# DANGEROUS
result = subprocess.run(f"python script.py --input {user_file}", shell=True)
```

**After (Secure with our module):**

```python
from src.security.secure_execution import execute_secure_command

def execute_python_script(script_name: str, input_file: str):
    # Validate inputs
    allowed_scripts = ['script.py', 'process.py']
    if script_name not in allowed_scripts:
        raise ValueError(f"Script '{script_name}' not allowed")

    # Validate file path
    input_path = Path(input_file).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Execute securely
    result = execute_secure_command([
        'python', script_name, '--input', str(input_path)
    ], timeout=300)

    return result

# Usage
result = execute_python_script('script.py', 'input.pdf')
```

### Phase 3: Remove Bandit Suppressions

After migrating code, remove `# nosec` suppressions:

```python
# Before migration
subprocess.run(['python', 'script.py'])  # nosec B603

# After migration (remove suppression)
from src.security.secure_execution import execute_secure_command
execute_secure_command(['python', 'script.py'])
```## Sec
urity Testing and Validation

### 1. Security Test Suite

Our project includes comprehensive security tests in `tests/test_secure_execution.py`. Key test categories:

#### Command Injection Prevention Tests
```python
def test_command_injection_prevention():
    """Test that our secure execution prevents command injection."""
    executor = SecureExecutor()

    # Malicious input that would cause injection with shell=True
    malicious_input = "; rm -rf /"

    # Should be safe with our secure executor
    result = executor.validate_command(['python', '-c', f'print("{malicious_input}")'])
    assert result.is_valid  # Should be valid but with warnings
    assert len(result.warnings) > 0  # Should warn about dangerous characters
```

#### Path Traversal Prevention Tests

```python
def test_path_traversal_prevention():
    """Test that path traversal is prevented."""
    executor = SecureExecutor()

    # Attempt path traversal
    with pytest.raises(SecureExecutionError):
        executor.execute_command(
            ['python', '--version'],
            cwd=Path('../../../../etc')
        )
```

#### Resource Limit Tests

```python
def test_timeout_enforcement():
    """Test that timeouts are enforced."""
    context = SecurityContext(allowed_executables=['python'], timeout=1)
    executor = SecureExecutor(context)

    # Command that would run longer than timeout
    with pytest.raises(SecureExecutionError):
        executor.execute_command([
            'python', '-c', 'import time; time.sleep(5)'
        ])
```

### 2. Running Security Tests

Use these commands to run security tests:

```bash
# Run all security tests
hatch run security-test

# Run specific subprocess security tests
hatch run pytest tests/test_secure_execution.py -v

# Run bandit security scan
hatch run security-scan

# Validate security configuration
hatch run security-validate
```

### 3. Bandit Configuration Validation

Test that bandit configuration is working correctly:

```python
def test_bandit_scan_runs_successfully():
    """Test that bandit scan runs without errors."""
    result = subprocess.run([
        'python', '-m', 'bandit',
        '-r', 'src/',
        '-f', 'json'
    ], capture_output=True, text=True, timeout=60)

    # Should complete successfully
    assert result.returncode in [0, 1]  # 0 = no issues, 1 = issues found

    # Should produce valid JSON
    if result.stdout:
        report = json.loads(result.stdout)
        assert 'results' in report
```

## Troubleshooting and Common Issues

### 1. Command Not Found Errors

**Problem:** `SecureExecutionError: Failed to get command 'xyz': CommandNotFound`

**Cause:** Executable not in PATH or not installed

**Solution:**

```python
from plumbum import local

def check_command_exists(cmd_name: str) -> bool:
    """Check if command exists in PATH."""
    try:
        local[cmd_name]
        return True
    except Exception:
        return False

# Usage
if check_command_exists('mutool'):
    result = executor.execute_command(['mutool', 'info', 'file.pdf'])
else:
    print("mutool not found, please install mupdf-tools")
```

### 2. Permission Denied Errors

**Problem:** `ProcessExecutionError: Command failed with exit code 126: Permission denied`

**Cause:** Insufficient permissions to execute command or access files

**Solution:**

```python
import os
from pathlib import Path

def check_executable_permissions(cmd_path: str) -> bool:
    """Check if file has executable permissions."""
    path = Path(cmd_path)
    if not path.exists():
        return False

    return os.access(path, os.X_OK)

# Usage
cmd_path = '/usr/local/bin/mutool'
if not check_executable_permissions(cmd_path):
    print("Command not executable, check permissions")
```

### 3. Timeout Issues

**Problem:** Commands timing out unexpectedly

**Solution:**

```python
def get_adaptive_timeout(cmd: List[str]) -> int:
    """Get appropriate timeout based on command type."""
    timeout_map = {
        'python': 300,      # 5 minutes for Python scripts
        'pytest': 1800,     # 30 minutes for tests
        'hatch': 600,       # 10 minutes for hatch commands
        'git': 120,         # 2 minutes for git operations
        'mutool': 180,      # 3 minutes for PDF operations
    }

    executable = cmd[0]
    return timeout_map.get(executable, 300)  # Default 5 minutes

# Usage
executor = SecureExecutor()
timeout = get_adaptive_timeout(['pytest', 'tests/'])
result = executor.execute_command(['pytest', 'tests/'], timeout=timeout)
```

### 4. Environment Variable Issues

**Problem:** Commands failing due to missing environment variables

**Solution:**

```python
import os

def execute_with_required_env(cmd: List[str], required_env: List[str] = None):
    """Execute command with required environment variables."""
    required_env = required_env or []

    # Check required environment variables
    missing_env = []
    for env_var in required_env:
        if env_var not in os.environ:
            missing_env.append(env_var)

    if missing_env:
        raise ValueError(f"Missing required environment variables: {missing_env}")

    # Build environment dict
    env = {var: os.environ[var] for var in required_env if var in os.environ}

    # Add common safe environment variables
    safe_env_vars = ['PATH', 'HOME', 'USER', 'LANG', 'LC_ALL']
    for var in safe_env_vars:
        if var in os.environ:
            env[var] = os.environ[var]

    executor = SecureExecutor()
    return executor.execute_command(cmd, env=env)
```

## Best Practices

### 1. Security-First Development

#### Always Use Lists for Commands

```python
# ✅ GOOD: List format prevents injection
cmd = ['python', 'script.py', '--input', user_file]

# ❌ BAD: String format vulnerable to injection
cmd = f"python script.py --input {user_file}"
```

#### Never Use shell=True

```python
# ✅ GOOD: Direct execution
subprocess.run(['python', 'script.py'], shell=False)

# ❌ BAD: Shell execution vulnerable to injection
subprocess.run('python script.py', shell=True)
```

#### Validate All Inputs

```python
import re

def validate_filename(filename: str) -> str:
    """Validate filename for security."""
    # Check format
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise ValueError("Invalid filename format")

    # Check length
    if len(filename) > 255:
        raise ValueError("Filename too long")

    # Check for dangerous patterns
    dangerous_patterns = ['..', '/', '\\', '|', ';', '&']
    for pattern in dangerous_patterns:
        if pattern in filename:
            raise ValueError(f"Dangerous pattern '{pattern}' in filename")

    return filename
```

### 2. Error Handling and Logging

#### Comprehensive Error Handling

```python
import logging

logger = logging.getLogger(__name__)

def execute_with_error_handling(cmd: List[str], **kwargs):
    """Execute command with comprehensive error handling."""
    try:
        executor = SecureExecutor()
        result = executor.execute_command(cmd, **kwargs)

        if not result.success:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Return code: {result.returncode}")
            logger.error(f"Error output: {result.stderr}")

            # Handle specific error codes
            if result.returncode == 127:
                raise FileNotFoundError(f"Command not found: {cmd[0]}")
            elif result.returncode == 126:
                raise PermissionError(f"Permission denied: {cmd[0]}")
            else:
                raise RuntimeError(f"Command failed with code {result.returncode}")

        return result

    except SecureExecutionError as e:
        logger.error(f"Security error executing command: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error executing command: {e}")
        raise
```

### 3. Resource Management

#### Timeout Management

```python
class TimeoutManager:
    """Manage timeouts for different command types."""

    DEFAULT_TIMEOUTS = {
        'python': 300,      # 5 minutes
        'pytest': 1800,     # 30 minutes
        'git': 120,         # 2 minutes
        'hatch': 600,       # 10 minutes
        'mutool': 180,      # 3 minutes
        'qpdf': 180,        # 3 minutes
    }

    @classmethod
    def get_timeout(cls, cmd: List[str]) -> int:
        """Get appropriate timeout for command."""
        if not cmd:
            return 300

        executable = cmd[0]
        return cls.DEFAULT_TIMEOUTS.get(executable, 300)

    @classmethod
    def execute_with_timeout(cls, cmd: List[str], **kwargs):
        """Execute command with appropriate timeout."""
        if 'timeout' not in kwargs:
            kwargs['timeout'] = cls.get_timeout(cmd)

        executor = SecureExecutor()
        return executor.execute_command(cmd, **kwargs)
```

## Reference

### Security Libraries and Tools

#### Plumbum

- **Documentation**: <https://plumbum.readthedocs.io/>
- **Security Features**: Type-safe commands, automatic escaping, no shell execution
- **Installation**: `pip install plumbum`

#### Bandit

- **Documentation**: <https://bandit.readthedocs.io/>
- **Purpose**: Security linting for Python code
- **Installation**: `pip install bandit`

### Security Standards and Guidelines

#### CWE (Common Weakness Enumeration)

- **CWE-78**: OS Command Injection
- **CWE-88**: Argument Injection
- **CWE-22**: Path Traversal
- **CWE-400**: Resource Exhaustion

#### OWASP Guidelines

- **Command Injection Prevention**: <https://owasp.org/www-community/attacks/Command_Injection>
- **Input Validation**: <https://owasp.org/www-project-proactive-controls/v3/en/c5-validate-inputs>

### Command Reference

#### Secure Execution Commands

```bash
# Security scanning
hatch run security-scan              # Scan source code
hatch run security-scan-json         # Generate JSON report
hatch run security-validate          # Validate security configuration

# Testing
hatch run security-test              # Run security tests
hatch run test-subprocess-security   # Run subprocess-specific tests

# Validation
python scripts/security_validation.py    # Validate security measures
python scripts/validate_bandit_config.py # Validate bandit configuration
```

#### Migration Commands

```bash
# Find subprocess usage
grep -r "import subprocess" src/
grep -r "subprocess\." src/
grep -r "shell=True" src/

# Find bandit suppressions
grep -r "# nosec B404" src/
grep -r "# nosec B603" src/

# Run migration validation
python scripts/migration_validation.py
```

---

**Document Version**: 1.0
**Last Updated**: August 3, 2025
**Next Review**: February 3, 2026

For questions or updates to this guide, please contact the security team or create an issue with the `security` label.
