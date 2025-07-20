#!/usr/bin/env python3
"""
Example Validation System

This module provides functionality to validate that all code examples
in the documentation and examples directory execute correctly against
the current codebase.
"""

import ast
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

# Add src to path for security utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from security.path_utils import PathSecurityError, SecurePathManager
from security.subprocess_utils import SecureSubprocessRunner, SecurityError


class ExampleValidationResult:
    """Result of validating a single example."""

    def __init__(
        self,
        example_path: str,
        success: bool,
        error: str | None = None,
        output: str | None = None,
        execution_time: float | None = None,
    ):
        self.example_path = example_path
        self.success = success
        self.error = error
        self.output = output
        self.execution_time = execution_time


class ExampleValidator:
    """Validates code examples to ensure they work with current codebase."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.validation_results: list[ExampleValidationResult] = []
        self.subprocess_runner = SecureSubprocessRunner(base_path=self.project_root)

    def validate_python_file(self, file_path: Path) -> ExampleValidationResult:
        """
        Validate a Python file by executing it and checking for errors.

        Args:
            file_path: Path to the Python file to validate

        Returns:
            ExampleValidationResult with validation outcome
        """
        import time

        start_time = time.time()

        try:
            # First, check if the file can be parsed
            with open(file_path, encoding="utf-8") as f:
                source_code = f.read()

            try:
                ast.parse(source_code)
            except SyntaxError as e:
                return ExampleValidationResult(
                    str(file_path),
                    False,
                    f"Syntax error: {e}",
                    execution_time=time.time() - start_time,
                )

            # Validate file path using secure path manager
            try:
                validated_path = SecurePathManager.validate_path(
                    file_path, base_path=self.project_root, must_exist=True
                )
            except PathSecurityError as e:
                raise ValueError(f"Path security validation failed: {e}")

            # Execute the file in a subprocess to isolate it
            cmd = [sys.executable, str(validated_path)]

            try:
                result = self.subprocess_runner.run(
                    cmd,
                    cwd=self.project_root,
                    timeout=300,  # 5 minute timeout for complex examples
                    capture_output=True,
                    text=True,
                )
            except SecurityError as e:
                raise ValueError(f"Security validation failed: {e}")

            execution_time = time.time() - start_time

            if result.returncode == 0:
                return ExampleValidationResult(
                    str(file_path),
                    True,
                    output=result.stdout,
                    execution_time=execution_time,
                )
            else:
                return ExampleValidationResult(
                    str(file_path),
                    False,
                    f"Exit code {result.returncode}: {result.stderr}",
                    output=result.stdout,
                    execution_time=execution_time,
                )

        except Exception as e:
            if "timeout" in str(e).lower():
                return ExampleValidationResult(
                    str(file_path),
                    False,
                    "Execution timeout (300 seconds)",
                    execution_time=300.0,
                )
            else:
                return ExampleValidationResult(
                    str(file_path),
                    False,
                    f"Validation error: {e}",
                    execution_time=time.time() - start_time,
                )

    def validate_code_snippet(self, code: str, description: str = "") -> ExampleValidationResult:
        """
        Validate a code snippet by executing it.

        Args:
            code: Python code to validate
            description: Description of the code snippet

        Returns:
            ExampleValidationResult with validation outcome
        """
        import time

        start_time = time.time()

        try:
            # Create a secure temporary file with the code
            fd, temp_path = SecurePathManager.create_secure_temp_file(prefix="code_snippet_", suffix=".py")

            try:
                # Add project root to path
                setup_code = f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

{code}
"""
                # Write to the temporary file
                with os.fdopen(fd, "w") as f:
                    f.write(setup_code)

                # Execute the temporary file
                cmd = [sys.executable, str(temp_path)]

                try:
                    result = self.subprocess_runner.run(
                        cmd,
                        cwd=self.project_root,
                        timeout=30,
                        capture_output=True,
                        text=True,
                    )
                except SecurityError as e:
                    raise ValueError(f"Security validation failed: {e}")

                execution_time = time.time() - start_time

                if result.returncode == 0:
                    return ExampleValidationResult(
                        description or "Code snippet",
                        True,
                        output=result.stdout,
                        execution_time=execution_time,
                    )
                else:
                    return ExampleValidationResult(
                        description or "Code snippet",
                        False,
                        f"Exit code {result.returncode}: {result.stderr}",
                        output=result.stdout,
                        execution_time=execution_time,
                    )
            finally:
                # Clean up temporary file
                try:
                    temp_path.unlink()
                except OSError:
                    pass  # File may already be deleted

        except Exception as e:
            return ExampleValidationResult(
                description or "Code snippet",
                False,
                f"Validation error: {e}",
                execution_time=time.time() - start_time,
            )

    def validate_import_statements(self, file_path: Path) -> list[str]:
        """
        Check if all import statements in a file are valid.

        Args:
            file_path: Path to the Python file

        Returns:
            List of import errors (empty if all imports are valid)
        """
        errors = []

        try:
            with open(file_path, encoding="utf-8") as f:
                source_code = f.read()

            # Parse the AST to find import statements
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            importlib.import_module(alias.name)
                        except ImportError as e:
                            errors.append(f"Import error for '{alias.name}': {e}")

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            module = importlib.import_module(node.module)
                            for alias in node.names:
                                if not hasattr(module, alias.name):
                                    errors.append(f"Module '{node.module}' has no attribute '{alias.name}'")
                        except ImportError as e:
                            errors.append(f"Import error for '{node.module}': {e}")

        except Exception as e:
            errors.append(f"Error parsing file: {e}")

        return errors

    def validate_all_examples(self) -> dict[str, Any]:
        """
        Validate all example files in the examples directory.

        Returns:
            Dictionary with validation summary and results
        """
        examples_dir = self.project_root / "examples"
        docs_examples_dir = self.project_root / "docs" / "examples"

        all_results = []

        # Find all Python files in examples directories
        python_files = []

        if examples_dir.exists():
            python_files.extend(examples_dir.glob("*.py"))

        if docs_examples_dir.exists():
            python_files.extend(docs_examples_dir.glob("*.py"))

        # Validate each file
        for py_file in python_files:
            if py_file.name == "validation.py":  # Skip this validation file
                continue

            print(f"Validating {py_file.name}...")
            result = self.validate_python_file(py_file)
            all_results.append(result)
            self.validation_results.append(result)

        # Generate summary
        successful = sum(1 for r in all_results if r.success)
        failed = len(all_results) - successful

        summary = {
            "total_examples": len(all_results),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(all_results) if all_results else 0,
            "results": all_results,
        }

        return summary

    def generate_validation_report(self, output_file: Path | None = None) -> str:
        """
        Generate a detailed validation report.

        Args:
            output_file: Optional file to save the report to

        Returns:
            Report content as string
        """
        if not self.validation_results:
            self.validate_all_examples()

        report_lines = [
            "# Example Validation Report",
            "",
            f"Generated on: {Path(__file__).stat().st_mtime}",
            f"Project root: {self.project_root}",
            "",
            "## Summary",
            "",
        ]

        successful = sum(1 for r in self.validation_results if r.success)
        failed = len(self.validation_results) - successful

        report_lines.extend(
            [
                f"- Total examples: {len(self.validation_results)}",
                f"- Successful: {successful}",
                f"- Failed: {failed}",
                (
                    f"- Success rate: {successful / len(self.validation_results) * 100:.1f}%"
                    if self.validation_results
                    else "- Success rate: N/A"
                ),
                "",
                "## Detailed Results",
                "",
            ]
        )

        for result in self.validation_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report_lines.append(f"### {Path(result.example_path).name} - {status}")
            report_lines.append("")

            if result.execution_time:
                report_lines.append(f"**Execution time:** {result.execution_time:.2f}s")

            if result.error:
                report_lines.extend(["**Error:**", "```", result.error, "```", ""])

            if result.output and result.success:
                # Show first few lines of output for successful runs
                output_lines = result.output.strip().split("\n")[:5]
                report_lines.extend(["**Output (first 5 lines):**", "```", *output_lines, "```", ""])

            report_lines.append("")

        report_content = "\n".join(report_lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_content)

        return report_content


def main():
    """Main function to run example validation."""
    print("Example Validation System")
    print("=" * 50)

    validator = ExampleValidator()

    # Validate all examples
    summary = validator.validate_all_examples()

    # Print summary
    print("\nValidation Summary:")
    print(f"  Total examples: {summary['total_examples']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success rate: {summary['success_rate'] * 100:.1f}%")

    # Show failed examples
    if summary["failed"] > 0:
        print("\nFailed examples:")
        for result in summary["results"]:
            if not result.success:
                print(f"  - {Path(result.example_path).name}: {result.error}")

    # Generate detailed report
    report_file = Path("examples/output/validation_report.md")
    validator.generate_validation_report(report_file)
    print(f"\nDetailed report saved to: {report_file}")

    # Return appropriate exit code
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
