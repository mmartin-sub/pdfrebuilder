"""
Documentation validation framework for the Multi-Format Document Engine.

This module provides tools to validate documentation accuracy against the current codebase,
including code example execution, API reference validation, and configuration verification.
"""

import ast
import builtins
import io
import json
import logging
import re
import subprocess  # nosec B404 - Used for TimeoutExpired exception handling in secure sandboxed execution
import sys
import tempfile
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status of validation results."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    status: ValidationStatus
    message: str
    details: dict[str, Any] | None = None
    file_path: str | None = None
    line_number: int | None = None


@dataclass
class CodeExample:
    """Code example with validation metadata."""

    title: str
    description: str
    code: str
    expected_output: str | None = None
    setup_code: str | None = None
    cleanup_code: str | None = None
    validation_status: ValidationStatus = ValidationStatus.SKIPPED
    file_path: str | None = None
    line_number: int | None = None


class SecureCodeExecutor:
    """Secure code execution environment with sandboxing."""

    def __init__(self):
        # Define allowed modules and functions
        self.allowed_modules = {
            "math",
            "random",
            "datetime",
            "json",
            "re",
            "collections",
            "itertools",
            "functools",
            "operator",
            "string",
            "typing",
        }

        # Define forbidden operations
        self.forbidden_operations = {
            "import",
            "from",
            "exec",
            "eval",
            "__import__",
            "compile",
            "open",
            "file",
            "subprocess",
            "os.system",
            "os.popen",
            "input",
            "raw_input",
            "getpass",
            "globals",
            "locals",
        }

        # Define safe builtins
        self.safe_builtins = {
            "abs",
            "all",
            "any",
            "bin",
            "bool",
            "chr",
            "complex",
            "dict",
            "divmod",
            "enumerate",
            "filter",
            "float",
            "format",
            "frozenset",
            "hash",
            "hex",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "map",
            "max",
            "min",
            "next",
            "oct",
            "ord",
            "pow",
            "print",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "slice",
            "sorted",
            "str",
            "sum",
            "tuple",
            "type",
            "zip",
            "True",
            "False",
            "None",
        }

    def validate_code_safety(self, code: str) -> tuple[bool, str]:
        """Validate that code doesn't contain dangerous operations."""
        try:
            # Parse the code
            tree = ast.parse(code)

            # Check for forbidden operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.forbidden_operations:
                            return False, f"Forbidden import: {alias.name}"

                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.forbidden_operations:
                        return False, f"Forbidden import from: {node.module}"

                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.forbidden_operations:
                            return False, f"Forbidden function call: {node.func.id}"
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in self.forbidden_operations:
                            return False, f"Forbidden method call: {node.func.attr}"

                elif isinstance(node, ast.Attribute):
                    if node.attr in self.forbidden_operations:
                        return False, f"Forbidden attribute access: {node.attr}"

            return True, "Code is safe"

        except SyntaxError as e:
            return False, f"Syntax error: {e!s}"
        except Exception as e:
            return False, f"Validation error: {e!s}"

    def create_safe_globals(self) -> dict[str, Any]:
        """Create a safe globals dictionary with restricted access."""
        safe_globals = {}

        # Add safe builtins
        for name in self.safe_builtins:
            if hasattr(builtins, name):
                safe_globals[name] = getattr(builtins, name)

        # Add safe modules
        for module_name in self.allowed_modules:
            try:
                module = __import__(module_name)
                safe_globals[module_name] = module
            except ImportError:
                pass

        return safe_globals

    def execute_safely(self, code: str, timeout: int = 30) -> tuple[bool, str, str, int]:
        """Execute code in a safe environment."""
        # Validate code safety first
        is_safe, safety_message = self.validate_code_safety(code)
        if not is_safe:
            return False, safety_message, "", 1

        # Create safe execution environment
        safe_globals = self.create_safe_globals()
        safe_locals: dict[str, Any] = {}

        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            # Set up execution with timeout
            start_time = time.time()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Compile and execute the code
                compiled_code = compile(code, "<string>", "exec")
                exec(compiled_code, safe_globals, safe_locals)  # nosec B102 - Secure sandboxed execution environment

            execution_time = time.time() - start_time

            if execution_time > timeout:
                return False, f"Execution timed out after {timeout} seconds", "", 1

            return True, stdout_capture.getvalue(), stderr_capture.getvalue(), 0

        except Exception as e:
            return False, str(e), stderr_capture.getvalue(), 1


class DocumentationValidator:
    """Validates documentation content for correctness and safety."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the validator."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.executor = SecureCodeExecutor()
        self.validation_config = self._load_validation_config()

    def _load_validation_config(self) -> dict[str, Any]:
        """Load validation configuration from config file."""
        config_path = self.project_root / "docs" / "validation_config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load validation config: {e}")

        # Return default configuration
        return {
            "validation_settings": {
                "code_examples": {"enabled": True, "timeout_seconds": 30},
                "api_references": {"enabled": True, "ignore_external_modules": True},
                "configuration_examples": {"enabled": True, "validate_json": True},
            }
        }

    def validate_code_examples(self, doc_path: str | Path) -> list[ValidationResult]:
        """Validate code examples in documentation files."""
        results: list[ValidationResult] = []
        doc_path = Path(doc_path)

        if not doc_path.exists():
            return [
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Documentation file not found: {doc_path}",
                    file_path=str(doc_path),
                )
            ]

        try:
            content = doc_path.read_text(encoding="utf-8")
            examples = self._extract_code_examples(content, str(doc_path))

            for example in examples:
                result = self._validate_single_example(example)
                results.append(result)

        except Exception as e:
            results.append(
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Error reading documentation file: {e!s}",
                    file_path=str(doc_path),
                )
            )

        return results

    def validate_api_references(self, doc_path: str | Path) -> list[ValidationResult]:
        """
        Validate that API references match actual implementation.

        Args:
            doc_path: Path to documentation file

        Returns:
            List of validation results
        """
        doc_path = Path(doc_path)
        results: list[ValidationResult] = []

        if not doc_path.exists():
            results.append(
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Documentation file not found: {doc_path}",
                    file_path=str(doc_path),
                )
            )
            return results

        try:
            # Use the enhanced API validator if available
            try:
                from .api_validator import APIReferenceValidator

                api_validator = APIReferenceValidator(self.project_root)
                return api_validator._validate_file_api_references(doc_path)
            except ImportError:
                # Fall back to basic validation
                pass

            content = doc_path.read_text(encoding="utf-8")
            api_refs = self._extract_api_references(content)

            for api_ref in api_refs:
                result = self._validate_api_reference(api_ref, str(doc_path))
                results.append(result)

        except Exception as e:
            results.append(
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Error validating API references: {e!s}",
                    file_path=str(doc_path),
                    details={"exception": str(e)},
                )
            )

        return results

    def validate_configuration_examples(self, doc_path: str | Path) -> list[ValidationResult]:
        """
        Validate that configuration examples are valid.

        Args:
            doc_path: Path to documentation file

        Returns:
            List of validation results
        """
        doc_path = Path(doc_path)
        results: list[ValidationResult] = []

        if not doc_path.exists():
            results.append(
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Documentation file not found: {doc_path}",
                    file_path=str(doc_path),
                )
            )
            return results

        try:
            content = doc_path.read_text(encoding="utf-8")
            config_examples = self._extract_configuration_examples(content)

            for config_example in config_examples:
                result = self._validate_configuration_example(config_example, str(doc_path))
                results.append(result)

        except Exception as e:
            results.append(
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Error validating configuration examples: {e!s}",
                    file_path=str(doc_path),
                    details={"exception": str(e)},
                )
            )

        return results

    def _extract_code_examples(self, content: str, file_path: str) -> list[CodeExample]:
        """Extract code examples from markdown content."""
        examples = []

        # Pattern to match code blocks with language specification
        code_block_pattern = r"```(?:python|bash|shell|json)\n(.*?)\n```"
        matches = re.finditer(code_block_pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            code = match.group(1).strip()

            # Skip if it's empty or just comments (but allow imports for testing)
            if not code or (code.startswith("#") and len(code.split("\n")) == 1):
                continue

            # Try to find a title or description before the code block
            start_pos = match.start()
            preceding_text = content[:start_pos].split("\n")[-5:]  # Last 5 lines before code

            title = f"Code example {i + 1}"
            description = "Code example from documentation"

            # Look for markdown headers or descriptive text
            for line in reversed(preceding_text):
                line = line.strip()
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                    break
                elif line and not line.startswith("```"):
                    description = line

            examples.append(
                CodeExample(
                    title=title,
                    description=description,
                    code=code,
                    file_path=file_path,
                    line_number=content[: match.start()].count("\n") + 1,
                )
            )

        return examples

    def _validate_single_example(self, example: CodeExample) -> ValidationResult:
        """Validate a single code example."""
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                # Add setup code if provided
                if example.setup_code:
                    f.write(example.setup_code + "\n\n")

                # Add the main code
                f.write(example.code)

                # Add cleanup code if provided
                if example.cleanup_code:
                    f.write("\n\n" + example.cleanup_code)

                temp_file = f.name

            try:
                # First, check if the code is syntactically valid
                with open(temp_file) as f:
                    code_content = f.read()

                # Use the secure executor to validate and execute the code
                is_safe, stdout, stderr, return_code = self.executor.execute_safely(code_content)

                if is_safe:
                    # Check expected output if provided
                    if example.expected_output:
                        if example.expected_output.strip() in stdout.strip():
                            return ValidationResult(
                                status=ValidationStatus.PASSED,
                                message=f"Code example '{example.title}' executed successfully with expected output",
                                file_path=example.file_path,
                                line_number=example.line_number,
                            )
                        else:
                            return ValidationResult(
                                status=ValidationStatus.WARNING,
                                message=f"Code example '{example.title}' executed but output doesn't match expected",
                                file_path=example.file_path,
                                line_number=example.line_number,
                                details={
                                    "expected": example.expected_output,
                                    "actual": stdout,
                                },
                            )
                    else:
                        return ValidationResult(
                            status=ValidationStatus.PASSED,
                            message=f"Code example '{example.title}' executed successfully",
                            file_path=example.file_path,
                            line_number=example.line_number,
                        )
                else:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Code example '{example.title}' failed to execute: {stderr}",
                        file_path=example.file_path,
                        line_number=example.line_number,
                        details={
                            "return_code": return_code,
                            "stdout": stdout,
                            "stderr": stderr,
                        },
                    )

            finally:
                # Clean up temporary file
                Path(temp_file).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Code example '{example.title}' timed out",
                file_path=example.file_path,
                line_number=example.line_number,
            )
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Error validating code example '{example.title}': {e!s}",
                file_path=example.file_path,
                line_number=example.line_number,
                details={"exception": str(e)},
            )

    def _extract_api_references(self, content: str) -> list[dict[str, Any]]:
        """Extract API references from documentation content."""
        api_refs = []

        # Pattern to match Python class/function references
        patterns = [
            r"`([a-zA-Z_][a-zA-Z0-9_.]*\.[a-zA-Z_][a-zA-Z0-9_]*(?:\([^)]*\))?)`",  # module.function or module.function()
            r"`([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))`",  # function()
            r"from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import",  # from module import
            r"import\s+([a-zA-Z_][a-zA-Z0-9_.]*)",  # import module
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                reference = match.group(1)
                # Clean up function calls - remove parentheses and parameters
                if "(" in reference:
                    reference = reference.split("(")[0]

                api_refs.append(
                    {
                        "reference": reference,
                        "type": "api_reference",
                        "line_number": content[: match.start()].count("\n") + 1,
                    }
                )

        return api_refs

    def _validate_api_reference(self, api_ref: dict[str, Any], file_path: str) -> ValidationResult:
        """Validate a single API reference."""
        reference = api_ref["reference"]

        try:
            # Try to resolve the reference
            if "." in reference:
                parts = reference.split(".")
                module_name = ".".join(parts[:-1])
                attr_name = parts[-1]

                # Try to import the module and access the attribute
                try:
                    module = __import__(module_name)
                    if hasattr(module, attr_name):
                        return ValidationResult(
                            status=ValidationStatus.PASSED,
                            message=f"API reference '{reference}' is valid",
                            file_path=file_path,
                            line_number=api_ref.get("line_number"),
                        )
                    else:
                        return ValidationResult(
                            status=ValidationStatus.FAILED,
                            message=f"API reference '{reference}' not found",
                            file_path=file_path,
                            line_number=api_ref.get("line_number"),
                        )
                except ImportError:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Module '{module_name}' not found for API reference '{reference}'",
                        file_path=file_path,
                        line_number=api_ref.get("line_number"),
                    )

            else:
                # Try to import as a module
                try:
                    __import__(reference)
                    return ValidationResult(
                        status=ValidationStatus.PASSED,
                        message=f"Module '{reference}' is valid",
                        file_path=file_path,
                        line_number=api_ref.get("line_number"),
                    )
                except ImportError:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Module '{reference}' not found",
                        file_path=file_path,
                        line_number=api_ref.get("line_number"),
                    )

        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Error validating API reference '{reference}': {e!s}",
                file_path=file_path,
                line_number=api_ref.get("line_number"),
                details={"exception": str(e)},
            )

    def _extract_configuration_examples(self, content: str) -> list[dict[str, Any]]:
        """Extract configuration examples from documentation content."""
        config_examples = []

        # Pattern to match only explicitly marked JSON/JSON5 configuration blocks
        patterns = [
            r"```(json|json5)\n(.*?)\n```",  # JSON/JSON5 code blocks only
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                config_type = match.group(1)  # The language type (json or json5)
                config_content = match.group(2).strip()  # The actual content

                # Clean up the content - remove any trailing backticks and following text
                if "```" in config_content:
                    config_content = config_content.split("```")[0].strip()

                if config_content:
                    config_examples.append(
                        {
                            "content": config_content,
                            "type": config_type,
                            "line_number": content[: match.start()].count("\n") + 1,
                        }
                    )

        return config_examples

    def _validate_configuration_example(self, config_example: dict[str, Any], file_path: str) -> ValidationResult:
        """Validate a single configuration example."""
        try:
            content = config_example["content"]
            config_type = config_example.get("type", "json")

            if config_type == "json":
                try:
                    json.loads(content)
                    return ValidationResult(
                        status=ValidationStatus.PASSED,
                        message="JSON configuration example is valid",
                        file_path=file_path,
                        line_number=config_example.get("line_number"),
                    )
                except json.JSONDecodeError as e:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Invalid JSON configuration: {e!s}",
                        file_path=file_path,
                        line_number=config_example.get("line_number"),
                        details={"json_error": str(e)},
                    )

            elif config_type == "json5":
                try:
                    import json5

                    json5.loads(content)
                    return ValidationResult(
                        status=ValidationStatus.PASSED,
                        message="JSON5 configuration example is valid",
                        file_path=file_path,
                        line_number=config_example.get("line_number"),
                    )
                except Exception as e:
                    return ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Invalid JSON5 configuration: {e!s}",
                        file_path=file_path,
                        line_number=config_example.get("line_number"),
                        details={"json5_error": str(e)},
                    )

            else:
                return ValidationResult(
                    status=ValidationStatus.SKIPPED,
                    message=f"Unknown configuration type: {config_type}",
                    file_path=file_path,
                    line_number=config_example.get("line_number"),
                )

        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Error validating configuration example: {e!s}",
                file_path=file_path,
                line_number=config_example.get("line_number"),
                details={"exception": str(e)},
            )


class DocumentationBuilder:
    """Builds complete documentation from sources."""

    def __init__(self, project_root: Path | None = None):
        """Initialize builder with project root directory."""
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.src_dir = self.project_root / "src"
        self.validator = DocumentationValidator(project_root)

    def build_api_docs(self) -> list[ValidationResult]:
        """Generate API documentation from source code."""
        results: list[ValidationResult] = []

        # Find all Python modules in src/
        python_files = list(self.src_dir.rglob("*.py"))

        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue

            try:
                # Extract module documentation
                module_doc = self._extract_module_documentation(py_file)
                if module_doc:
                    # Generate API documentation file
                    api_doc_path = self._generate_api_doc_file(py_file, module_doc)
                    results.append(
                        ValidationResult(
                            status=ValidationStatus.PASSED,
                            message=f"Generated API documentation for {py_file.name}",
                            file_path=str(api_doc_path),
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            status=ValidationStatus.WARNING,
                            message=f"No documentation found for {py_file.name}",
                            file_path=str(py_file),
                        )
                    )
            except Exception as e:
                results.append(
                    ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Error generating API documentation for {py_file.name}: {e!s}",
                        file_path=str(py_file),
                    )
                )

        return results

    def build_user_guides(self) -> list[ValidationResult]:
        """Process and validate user guide content."""
        results: list[ValidationResult] = []

        guides_dir = self.docs_dir / "guides"
        if not guides_dir.exists():
            return results

        guide_files = list(guides_dir.rglob("*.md"))
        for guide_file in guide_files:
            try:
                # Validate code examples in the guide
                code_results = self.validator.validate_code_examples(guide_file)
                results.extend(code_results)

                # Validate API references
                api_results = self.validator.validate_api_references(guide_file)
                results.extend(api_results)

            except Exception as e:
                results.append(
                    ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Error processing guide {guide_file.name}: {e!s}",
                        file_path=str(guide_file),
                    )
                )

        return results

    def build_examples(self) -> list[ValidationResult]:
        """Generate and validate example code."""
        results: list[ValidationResult] = []

        examples_dir = self.docs_dir / "examples"
        examples_dir.mkdir(exist_ok=True)

        # Generate basic examples
        basic_examples = self._generate_basic_examples()
        for example_name, example_content in basic_examples.items():
            try:
                example_file = examples_dir / "basic" / example_name
                example_file.parent.mkdir(exist_ok=True)
                example_file.write_text(example_content, encoding="utf-8")

                results.append(
                    ValidationResult(
                        status=ValidationStatus.PASSED,
                        message=f"Generated example: {example_name}",
                        file_path=str(example_file),
                    )
                )

            except Exception as e:
                results.append(
                    ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Error generating example {example_name}: {e!s}",
                    )
                )

        return results

    def build_complete_docs(self) -> dict[str, list[ValidationResult]]:
        """Build complete documentation set."""
        results = {
            "api_docs": self.build_api_docs(),
            "user_guides": self.build_user_guides(),
            "examples": self.build_examples(),
        }
        return results

    def _extract_module_documentation(self, py_file: Path) -> dict[str, Any] | None:
        """Extract documentation from a Python module."""
        try:
            # Read the Python file
            content = py_file.read_text(encoding="utf-8")

            # Parse the module
            tree = ast.parse(content)

            # Extract module-level docstring
            module_docstring = ast.get_docstring(tree)

            # Find classes and functions
            classes = []
            functions = []

            # First pass: collect all classes and their methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract methods from the class
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            # Get function arguments
                            args = []
                            if child.args.args:
                                for arg in child.args.args:
                                    if arg.arg != "self":  # Skip self parameter
                                        args.append(arg.arg)

                            methods.append(
                                {
                                    "name": child.name,
                                    "docstring": ast.get_docstring(child),
                                    "line_number": child.lineno,
                                    "args": args,
                                }
                            )

                    classes.append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "line_number": node.lineno,
                            "methods": methods,
                        }
                    )

            # Second pass: collect top-level functions (not methods)
            # Look at the module body directly
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    # Get function arguments
                    args = []
                    if node.args.args:
                        for arg in node.args.args:
                            args.append(arg.arg)

                    functions.append(
                        {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "line_number": node.lineno,
                            "args": args,
                        }
                    )

            if module_docstring or classes or functions:
                return {
                    "module_name": py_file.stem,
                    "module_path": str(py_file.relative_to(self.src_dir)),
                    "docstring": module_docstring,
                    "classes": classes,
                    "functions": functions,
                }

            return None

        except Exception as e:
            logger.warning(f"Could not extract documentation from {py_file}: {e}")
            return None

    def _generate_api_doc_file(self, py_file: Path, module_doc: dict[str, Any]) -> Path:
        """Generate API documentation file from module documentation."""
        # Determine the appropriate API docs subdirectory
        relative_path = py_file.relative_to(self.src_dir)
        api_doc_dir = self.docs_dir / "api" / relative_path.parent

        # Create the directory structure
        api_doc_dir.mkdir(parents=True, exist_ok=True)

        # Generate the markdown content
        markdown_content = self._generate_api_markdown(module_doc)

        # Write the file
        api_doc_file = api_doc_dir / f"{module_doc['module_name']}.md"
        api_doc_file.write_text(markdown_content, encoding="utf-8")

        return api_doc_file

    def _generate_api_markdown(self, module_doc: dict[str, Any]) -> str:
        """Generate markdown content for API documentation."""
        lines = []

        # Module header
        lines.append(f"# {module_doc['module_name']}")
        lines.append("")

        # Module docstring
        if module_doc.get("docstring"):
            lines.append(module_doc["docstring"])
            lines.append("")

        # Classes
        if module_doc.get("classes"):
            lines.append("## Classes")
            lines.append("")

            for class_info in module_doc["classes"]:
                lines.append(f"### {class_info['name']}")
                if class_info.get("docstring"):
                    lines.append("")
                    lines.append(class_info["docstring"])
                lines.append("")

                # Methods
                if class_info.get("methods"):
                    lines.append("#### Methods")
                    lines.append("")

                    for method_info in class_info["methods"]:
                        # Format method signature
                        args_str = ", ".join(method_info.get("args", []))
                        lines.append(f"##### {method_info['name']}({args_str})")
                        if method_info.get("docstring"):
                            lines.append("")
                            lines.append(method_info["docstring"])
                        lines.append("")

        # Functions
        if module_doc.get("functions"):
            lines.append("## Functions")
            lines.append("")

            for func_info in module_doc["functions"]:
                args_str = ", ".join(func_info.get("args", []))
                lines.append(f"### {func_info['name']}({args_str})")
                if func_info.get("docstring"):
                    lines.append("")
                    lines.append(func_info["docstring"])
                lines.append("")

        return "\n".join(lines)

    def _generate_basic_examples(self) -> dict[str, str]:
        """Generate basic code examples."""
        examples = {
            "basic_pdf_processing.py": '''"""
Basic PDF processing example for the Multi-Format Document Engine.
"""

import json
import sys
from pathlib import Path

def main():
    """Basic PDF processing example."""
    print("Basic PDF Processing Example")
    print("=" * 35)

    # Example PDF processing configuration
    config = {
        "version": "1.0",
        "engine": "fitz",
        "metadata": {
            "title": "Sample PDF Document",
            "creator": "Multi-Format Document Engine"
        },
        "document_structure": [
            {
                "type": "page",
                "page_number": 1,
                "size": [612.0, 792.0],
                "layers": []
            }
        ]
    }

    print("Example PDF processing configuration:")
    print(json.dumps(config, indent=2))

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
''',
            "basic_usage.py": '''"""
Basic usage example for the Multi-Format Document Engine.
"""

import json
import sys
from pathlib import Path

def main():
    """Basic usage example."""
    print("Basic Usage Example")
    print("=" * 30)

    # Example configuration
    config = {
        "version": "1.0",
        "engine": "fitz",
        "document_structure": []
    }

    print("Example configuration:")
    print(json.dumps(config, indent=2))

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
''',
            "configuration_example.py": '''"""
Configuration example for the Multi-Format Document Engine.
"""

import json
import sys
from pathlib import Path

def main():
    """Configuration example."""
    print("Configuration Example")
    print("=" * 30)

    # Example configuration structure
    config = {
        "version": "1.0",
        "engine": "fitz",
        "metadata": {
            "title": "Example Document"
        },
        "document_structure": []
    }

    print("Example configuration:")
    print(json.dumps(config, indent=2))

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
''',
        }

        return examples


def main():
    """Main entry point for documentation validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate documentation")
    parser.add_argument("--docs-dir", type=Path, default="docs", help="Documentation directory")
    parser.add_argument("--file", type=Path, help="Specific file to validate")
    parser.add_argument("--examples", action="store_true", help="Validate code examples")
    parser.add_argument("--api-refs", action="store_true", help="Validate API references")
    parser.add_argument("--config", action="store_true", help="Validate configuration examples")
    parser.add_argument("--all", action="store_true", help="Run all validations")

    args = parser.parse_args()

    validator = DocumentationValidator()
    all_results = []

    if args.file:
        files_to_check = [args.file]
    else:
        files_to_check = list(args.docs_dir.rglob("*.md"))

    for doc_file in files_to_check:
        if not doc_file.exists():
            continue

        print(f"Validating {doc_file}...")

        if args.examples or args.all:
            results = validator.validate_code_examples(doc_file)
            all_results.extend(results)

        if args.api_refs or args.all:
            results = validator.validate_api_references(doc_file)
            all_results.extend(results)

        if args.config or args.all:
            results = validator.validate_configuration_examples(doc_file)
            all_results.extend(results)

    # Print summary
    passed = sum(1 for r in all_results if r.status == ValidationStatus.PASSED)
    failed = sum(1 for r in all_results if r.status == ValidationStatus.FAILED)
    warnings = sum(1 for r in all_results if r.status == ValidationStatus.WARNING)

    print("\nValidation Summary:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Warnings: {warnings}")
    print(f"  Total: {len(all_results)}")

    # Print failed results
    if failed > 0:
        print("\nFailed validations:")
        for result in all_results:
            if result.status == ValidationStatus.FAILED:
                print(f"  {result.file_path}:{result.line_number} - {result.message}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
