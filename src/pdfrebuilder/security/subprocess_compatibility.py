#!/usr/bin/env python3
"""
Subprocess compatibility wrapper for secure execution.

This module provides a compatibility layer that translates existing subprocess calls
to secure alternatives using plumbum. It maintains backward compatibility while
adding security features.

The wrapper provides:
- Drop-in replacement for subprocess.run()
- Automatic migration to secure execution
- Gradual transition support
- Compatibility with existing code patterns
"""

import logging
import subprocess  # nosec B404 # Required for subprocess compatibility wrapper implementation
import warnings
from pathlib import Path
from typing import Any

from .secure_execution import ExecutionResult, SecureExecutionError, SecureExecutor, SecurityContext

logger = logging.getLogger(__name__)


class SubprocessCompatibilityError(Exception):
    """Raised when subprocess compatibility operation fails."""


class CompatibilityResult:
    """
    Compatibility wrapper for subprocess.CompletedProcess.

    This class mimics the interface of subprocess.CompletedProcess
    while using our secure execution backend.
    """

    def __init__(self, execution_result: ExecutionResult):
        self._execution_result = execution_result

    @property
    def args(self) -> list[str]:
        """Command that was executed."""
        return self._execution_result.command

    @property
    def returncode(self) -> int:
        """Return code of the process."""
        return self._execution_result.returncode

    @property
    def stdout(self) -> str:
        """Standard output of the process."""
        return self._execution_result.stdout

    @property
    def stderr(self) -> str:
        """Standard error of the process."""
        return self._execution_result.stderr

    def check_returncode(self) -> None:
        """
        Check return code and raise CalledProcessError if non-zero.

        Raises:
            subprocess.CalledProcessError: If returncode is non-zero
        """
        if self.returncode != 0:
            raise subprocess.CalledProcessError(self.returncode, self.args, self.stdout, self.stderr)

    def __repr__(self) -> str:
        return f"CompletedProcess(args={self.args!r}, returncode={self.returncode})"


class SecureSubprocessWrapper:
    """
    Secure subprocess wrapper that provides compatibility with subprocess module.

    This wrapper translates subprocess calls to secure execution while maintaining
    the same interface and behavior.
    """

    def __init__(
        self,
        security_context: SecurityContext | None = None,
        enable_warnings: bool = True,
        strict_mode: bool = False,
    ):
        """
        Initialize the compatibility wrapper.

        Args:
            security_context: Security context for execution
            enable_warnings: Whether to emit deprecation warnings
            strict_mode: Whether to enforce strict security validation
        """
        self.executor = SecureExecutor(security_context)
        self.enable_warnings = enable_warnings
        self.strict_mode = strict_mode

    def run(
        self,
        args: str | list[str],
        *,
        stdin=None,
        input=None,
        stdout=None,
        stderr=None,
        capture_output: bool = False,
        shell: bool = False,
        cwd: str | Path | None = None,
        timeout: float | None = None,
        check: bool = False,
        encoding: str | None = None,
        errors: str | None = None,
        text: bool | None = None,
        env: dict[str, str] | None = None,
        **kwargs,
    ) -> CompatibilityResult:
        """
        Secure replacement for subprocess.run().

        Args:
            args: Command to execute
            stdin: Standard input (not supported in secure mode)
            input: Input data (not supported in secure mode)
            stdout: Standard output handling
            stderr: Standard error handling
            capture_output: Whether to capture output
            shell: Shell usage (always forced to False for security)
            cwd: Working directory
            timeout: Timeout in seconds
            check: Whether to check return code
            encoding: Text encoding
            errors: Error handling
            text: Whether to use text mode
            env: Environment variables
            universal_newlines: Legacy text mode parameter
            **kwargs: Additional arguments

        Returns:
            CompatibilityResult mimicking subprocess.CompletedProcess

        Raises:
            SubprocessCompatibilityError: If operation fails
            subprocess.CalledProcessError: If check=True and command fails
        """
        # Emit deprecation warning if enabled
        if self.enable_warnings:
            warnings.warn(
                "Using subprocess compatibility wrapper. Consider migrating to secure_execution module directly.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Validate and convert arguments
        try:
            cmd = self._prepare_command(args, shell)
            cwd_path = Path(cwd) if cwd else None
            timeout_int = int(timeout) if timeout else None

            # Handle output capture
            should_capture = capture_output or (stdout is not None) or (stderr is not None)

            # Log security-relevant parameters
            if shell:
                logger.warning("Shell=True was requested but forced to False for security")
            if stdin is not None or input is not None:
                logger.warning("stdin/input parameters not supported in secure mode")

            # Execute command securely
            result = self.executor.execute_command(
                cmd=cmd,
                cwd=cwd_path,
                timeout=timeout_int,
                env=env,
                capture_output=should_capture,
            )

            # Create compatibility result
            compat_result = CompatibilityResult(result)

            # Check return code if requested
            if check:
                compat_result.check_returncode()

            return compat_result

        except subprocess.CalledProcessError:
            # Re-raise CalledProcessError as-is for compatibility
            raise
        except SecureExecutionError as e:
            raise SubprocessCompatibilityError(f"Secure execution failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in subprocess compatibility: {e}")
            raise SubprocessCompatibilityError(f"Compatibility wrapper failed: {e}")

    def _prepare_command(self, args: str | list[str], shell: bool) -> list[str]:
        """
        Prepare command arguments for secure execution.

        Args:
            args: Command arguments
            shell: Whether shell was requested (ignored for security)

        Returns:
            List of command arguments

        Raises:
            SubprocessCompatibilityError: If command preparation fails
        """
        if isinstance(args, str):
            if shell and not self.strict_mode:
                # In non-strict mode, try to split shell command
                import shlex

                try:
                    cmd = shlex.split(args)
                    logger.warning(f"Converted shell command to argument list: {cmd}")
                    return cmd
                except ValueError as e:
                    raise SubprocessCompatibilityError(f"Failed to parse shell command: {e}")
            elif shell and self.strict_mode:
                raise SubprocessCompatibilityError("Shell commands not allowed in strict mode")
            else:
                # Single string command without shell
                return [args]
        elif isinstance(args, list):
            return args
        else:
            raise SubprocessCompatibilityError(f"Invalid command type: {type(args)}")

    def call(self, args: str | list[str], **kwargs) -> int:
        """
        Compatibility wrapper for subprocess.call().

        Args:
            args: Command to execute
            **kwargs: Additional arguments

        Returns:
            Return code of the process
        """
        result = self.run(args, **kwargs)
        return result.returncode

    def check_call(self, args: str | list[str], **kwargs) -> None:
        """
        Compatibility wrapper for subprocess.check_call().

        Args:
            args: Command to execute
            **kwargs: Additional arguments

        Raises:
            subprocess.CalledProcessError: If command fails
        """
        self.run(args, check=True, **kwargs)

    def check_output(self, args: str | list[str], **kwargs) -> str:
        """
        Compatibility wrapper for subprocess.check_output().

        Args:
            args: Command to execute
            **kwargs: Additional arguments

        Returns:
            Standard output of the process

        Raises:
            subprocess.CalledProcessError: If command fails
        """
        result = self.run(args, check=True, capture_output=True, **kwargs)
        return result.stdout


class MigrationHelper:
    """Helper class for gradual migration from subprocess to secure execution."""

    @staticmethod
    def analyze_subprocess_usage(file_path: Path) -> dict[str, Any]:
        """
        Analyze subprocess usage in a Python file.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Dictionary with analysis results
        """
        import ast
        import re

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to find subprocess calls
            tree = ast.parse(content)
            subprocess_calls = []

            class SubprocessVisitor(ast.NodeVisitor):
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                            subprocess_calls.append(
                                {
                                    "function": node.func.attr,
                                    "line": node.lineno,
                                    "args": len(node.args),
                                    "keywords": [kw.arg for kw in node.keywords],
                                }
                            )
                    self.generic_visit(node)

            visitor = SubprocessVisitor()
            visitor.visit(tree)

            # Find subprocess imports
            subprocess_imports = []
            import_pattern = r"^(import subprocess|from subprocess import .+)$"
            for i, line in enumerate(content.split("\n"), 1):
                if re.match(import_pattern, line.strip()):
                    subprocess_imports.append({"line": i, "import": line.strip()})

            return {
                "file_path": str(file_path),
                "subprocess_imports": subprocess_imports,
                "subprocess_calls": subprocess_calls,
                "total_calls": len(subprocess_calls),
                "migration_complexity": (
                    "high" if len(subprocess_calls) > 5 else "medium" if len(subprocess_calls) > 2 else "low"
                ),
            }

        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return {"error": str(e)}

    @staticmethod
    def generate_migration_suggestions(analysis: dict[str, Any]) -> list[str]:
        """
        Generate migration suggestions based on analysis.

        Args:
            analysis: Analysis results from analyze_subprocess_usage

        Returns:
            List of migration suggestions
        """
        suggestions = []

        if "error" in analysis:
            return [f"Error analyzing file: {analysis['error']}"]

        # Import suggestions
        if analysis["subprocess_imports"]:
            suggestions.append(
                "Replace subprocess imports with: from pdfrebuilder.security.subprocess_compatibility import SecureSubprocessWrapper"
            )

        # Call-specific suggestions
        for call in analysis["subprocess_calls"]:
            func = call["function"]
            line = call["line"]

            if func == "run":
                suggestions.append(f"Line {line}: Replace subprocess.run() with wrapper.run() for secure execution")
            elif func == "call":
                suggestions.append(f"Line {line}: Replace subprocess.call() with wrapper.call() for secure execution")
            elif func == "check_call":
                suggestions.append(
                    f"Line {line}: Replace subprocess.check_call() with wrapper.check_call() for secure execution"
                )
            elif func == "check_output":
                suggestions.append(
                    f"Line {line}: Replace subprocess.check_output() with wrapper.check_output() for secure execution"
                )
            elif func == "Popen":
                suggestions.append(f"Line {line}: subprocess.Popen() requires manual migration to SecureExecutor")

        # General suggestions
        if analysis["total_calls"] > 0:
            suggestions.append("Consider migrating to SecureExecutor directly for better security control")
            suggestions.append("Test all subprocess calls after migration to ensure compatibility")

        return suggestions

    @staticmethod
    def create_migration_script(file_path: Path, output_path: Path | None = None) -> Path:
        """
        Create a migration script for a file.

        Args:
            file_path: Path to file to migrate
            output_path: Output path for migration script

        Returns:
            Path to created migration script
        """
        analysis = MigrationHelper.analyze_subprocess_usage(file_path)
        suggestions = MigrationHelper.generate_migration_suggestions(analysis)

        if output_path is None:
            output_path = file_path.parent / f"{file_path.stem}_migration.py"

        migration_content = f'''#!/usr/bin/env python3
"""
Migration script for {file_path.name}

This script was generated automatically to help migrate subprocess usage
to secure execution patterns.

Original file: {file_path}
Generated: {__import__("datetime").datetime.now().isoformat()}
"""

# Migration Analysis:
# Total subprocess calls: {analysis.get("total_calls", 0)}
# Migration complexity: {analysis.get("migration_complexity", "unknown")}

# Suggestions:
{chr(10).join(f"# - {suggestion}" for suggestion in suggestions)}

# Example migration pattern:
# OLD:
# import subprocess
# result = subprocess.run(['python', '--version'], capture_output=True, text=True)

# NEW:
from pdfrebuilder.security.subprocess_compatibility import SecureSubprocessWrapper

wrapper = SecureSubprocessWrapper()
result = wrapper.run(['python', '--version'], capture_output=True, text=True)

# Or migrate directly to SecureExecutor for better control:
# from pdfrebuilder.security.secure_execution import SecureExecutor
# executor = SecureExecutor()
# result = executor.execute_command(['python', '--version'])
'''

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(migration_content)

        logger.info(f"Created migration script: {output_path}")
        return output_path


# Global compatibility wrapper instance
_default_wrapper = None


def get_default_wrapper() -> SecureSubprocessWrapper:
    """Get the default compatibility wrapper instance."""
    global _default_wrapper
    if _default_wrapper is None:
        _default_wrapper = SecureSubprocessWrapper()
    return _default_wrapper


# Convenience functions that mimic subprocess module interface
def run(args: str | list[str], **kwargs) -> CompatibilityResult:
    """Secure replacement for subprocess.run()."""
    return get_default_wrapper().run(args, **kwargs)


def call(args: str | list[str], **kwargs) -> int:
    """Secure replacement for subprocess.call()."""
    return get_default_wrapper().call(args, **kwargs)


def check_call(args: str | list[str], **kwargs) -> None:
    """Secure replacement for subprocess.check_call()."""
    return get_default_wrapper().check_call(args, **kwargs)


def check_output(args: str | list[str], **kwargs) -> str:
    """Secure replacement for subprocess.check_output()."""
    return get_default_wrapper().check_output(args, **kwargs)
