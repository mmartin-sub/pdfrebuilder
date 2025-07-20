"""
API reference validation system.

This module provides comprehensive validation of API references in documentation
against the actual codebase, ensuring that all documented APIs exist and are accurate.
"""

import ast
import importlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .validation import ValidationResult, ValidationStatus


@dataclass
class APIReference:
    """Represents an API reference found in documentation."""

    reference: str
    reference_type: str  # 'module', 'class', 'function', 'method', 'attribute'
    file_path: str
    line_number: int
    context: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "reference": self.reference,
            "reference_type": self.reference_type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "context": self.context,
        }


@dataclass
class APIDefinition:
    """Represents an API definition found in the codebase."""

    name: str
    full_name: str
    definition_type: str  # 'module', 'class', 'function', 'method', 'attribute'
    file_path: str
    line_number: int
    docstring: str | None
    signature: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "full_name": self.full_name,
            "definition_type": self.definition_type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "docstring": self.docstring,
            "signature": self.signature,
        }


class APIReferenceValidator:
    """Validates API references against actual codebase."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the API reference validator."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.src_dir = self.project_root / "src"
        self.docs_dir = self.project_root / "docs"

        # Cache for discovered APIs
        self._api_definitions: dict[str, APIDefinition] = {}
        self._modules_scanned: set[str] = set()

        # Add src to Python path for imports
        if str(self.src_dir) not in sys.path:
            sys.path.insert(0, str(self.src_dir))

    def validate_all_api_references(self) -> list[ValidationResult]:
        """Validate all API references in documentation."""
        print("🔍 Validating API references against codebase...")

        # First, scan the codebase to build API definitions
        self._scan_codebase()

        # Then validate references in documentation
        results = []

        if not self.docs_dir.exists():
            return [
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message="Documentation directory not found",
                    file_path=str(self.docs_dir),
                )
            ]

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))

        for md_file in md_files:
            try:
                file_results = self._validate_file_api_references(md_file)
                results.extend(file_results)
            except Exception as e:
                results.append(
                    ValidationResult(
                        status=ValidationStatus.FAILED,
                        message=f"Error validating API references: {e!s}",
                        file_path=str(md_file),
                    )
                )

        return results

    def _scan_codebase(self) -> None:
        """Scan the codebase to build API definitions."""
        print("  Scanning codebase for API definitions...")

        if not self.src_dir.exists():
            print(f"    Warning: src directory does not exist: {self.src_dir}")
            return

        # Find all Python files
        python_files = list(self.src_dir.rglob("*.py"))
        print(f"    Found {len(python_files)} Python files: {[f.name for f in python_files]}")

        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue

            try:
                print(f"    Scanning {py_file}")
                self._scan_module_file(py_file)
            except Exception as e:
                print(f"    Warning: Could not scan {py_file}: {e}")

    def _scan_module_file(self, py_file: Path) -> None:
        """Scan a single Python file for API definitions."""
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            raise ValueError(f"Could not parse {py_file}: {e}")

        # Calculate module name
        relative_path = py_file.relative_to(self.src_dir)
        module_name = str(relative_path.with_suffix("")).replace("/", ".")

        # Add module itself as an API definition
        module_docstring = ast.get_docstring(tree)
        self._api_definitions[module_name] = APIDefinition(
            name=module_name.split(".")[-1],
            full_name=module_name,
            definition_type="module",
            file_path=str(py_file),
            line_number=1,
            docstring=module_docstring,
            signature=None,
        )

        # Scan for classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._scan_class_definition(node, module_name, py_file)
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions (not methods)
                if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    self._scan_function_definition(node, module_name, py_file)

    def _scan_class_definition(self, class_node: ast.ClassDef, module_name: str, py_file: Path) -> None:
        """Scan a class definition for API information."""
        class_name = class_node.name
        full_class_name = f"{module_name}.{class_name}"

        # Add class definition
        class_docstring = ast.get_docstring(class_node)
        self._api_definitions[full_class_name] = APIDefinition(
            name=class_name,
            full_name=full_class_name,
            definition_type="class",
            file_path=str(py_file),
            line_number=class_node.lineno,
            docstring=class_docstring,
            signature=None,
        )

        # Scan methods
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                self._scan_method_definition(node, full_class_name, py_file)

    def _scan_function_definition(self, func_node: ast.FunctionDef, module_name: str, py_file: Path) -> None:
        """Scan a function definition for API information."""
        func_name = func_node.name
        full_func_name = f"{module_name}.{func_name}"

        # Get function signature
        signature = self._get_function_signature(func_node)

        # Add function definition
        func_docstring = ast.get_docstring(func_node)
        self._api_definitions[full_func_name] = APIDefinition(
            name=func_name,
            full_name=full_func_name,
            definition_type="function",
            file_path=str(py_file),
            line_number=func_node.lineno,
            docstring=func_docstring,
            signature=signature,
        )

    def _scan_method_definition(self, method_node: ast.FunctionDef, class_name: str, py_file: Path) -> None:
        """Scan a method definition for API information."""
        method_name = method_node.name
        full_method_name = f"{class_name}.{method_name}"

        # Get method signature
        signature = self._get_function_signature(method_node)

        # Add method definition
        method_docstring = ast.get_docstring(method_node)
        self._api_definitions[full_method_name] = APIDefinition(
            name=method_name,
            full_name=full_method_name,
            definition_type="method",
            file_path=str(py_file),
            line_number=method_node.lineno,
            docstring=method_docstring,
            signature=signature,
        )

    def _get_function_signature(self, func_node: ast.FunctionDef) -> str:
        """Get function signature as string."""
        args = []

        # Regular arguments
        for arg in func_node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # *args
        if func_node.args.vararg:
            vararg_str = f"*{func_node.args.vararg.arg}"
            if func_node.args.vararg.annotation:
                vararg_str += f": {ast.unparse(func_node.args.vararg.annotation)}"
            args.append(vararg_str)

        # **kwargs
        if func_node.args.kwarg:
            kwarg_str = f"**{func_node.args.kwarg.arg}"
            if func_node.args.kwarg.annotation:
                kwarg_str += f": {ast.unparse(func_node.args.kwarg.annotation)}"
            args.append(kwarg_str)

        signature = f"{func_node.name}({', '.join(args)})"

        # Return annotation
        if func_node.returns:
            signature += f" -> {ast.unparse(func_node.returns)}"

        return signature

    def _validate_file_api_references(self, md_file: Path) -> list[ValidationResult]:
        """Validate API references in a single documentation file."""
        results = []

        try:
            # Ensure codebase is scanned first
            if not self._api_definitions:
                self._scan_codebase()

            content = md_file.read_text(encoding="utf-8")
            references = self._extract_api_references(content, str(md_file))

            print(f"    Extracted {len(references)} references: {[ref.reference for ref in references]}")

            for ref in references:
                result = self._validate_single_api_reference(ref)
                print(f"      Result for {ref.reference}: {result.status} - {result.message}")
                results.append(result)

        except Exception as e:
            results.append(
                ValidationResult(
                    status=ValidationStatus.FAILED,
                    message=f"Error reading file: {e!s}",
                    file_path=str(md_file),
                )
            )

        return results

    def _extract_api_references(self, content: str, file_path: str) -> list[APIReference]:
        """Extract API references from documentation content."""
        references = []

        # Patterns to match different types of API references
        patterns = [
            # Code blocks with imports and function calls
            (r"```python\n(.*?)\n```", "code_block"),
            # Inline code references
            (
                r"`([a-zA-Z_][a-zA-Z0-9_.]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*(?:\([^)]*\))?)`",
                "inline_code",
            ),
            # Import statements in text
            (
                r"from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,\s]*)",
                "import_statement",
            ),
            (r"import\s+([a-zA-Z_][a-zA-Z0-9_.]*)", "import_statement"),
        ]

        for pattern, ref_type in patterns:
            matches = re.finditer(pattern, content, re.DOTALL if ref_type == "code_block" else 0)

            for match in matches:
                line_number = content[: match.start()].count("\n") + 1

                if ref_type == "code_block":
                    # Extract API references from code block
                    code_content = match.group(1)
                    code_refs = self._extract_references_from_code(code_content, file_path, line_number)
                    references.extend(code_refs)

                elif ref_type == "inline_code":
                    reference = match.group(1)
                    # Clean up function calls
                    if "(" in reference:
                        reference = reference.split("(")[0]

                    references.append(
                        APIReference(
                            reference=reference,
                            reference_type="inline_code",
                            file_path=file_path,
                            line_number=line_number,
                            context=match.group(0),
                        )
                    )

                elif ref_type == "import_statement":
                    if "from" in match.group(0):
                        module_name = match.group(1)
                        imported_items = [item.strip() for item in match.group(2).split(",")]

                        # Add the module reference
                        references.append(
                            APIReference(
                                reference=module_name,
                                reference_type="module",
                                file_path=file_path,
                                line_number=line_number,
                                context=match.group(0),
                            )
                        )

                        # Add the full qualified names for imported items
                        for item in imported_items:
                            full_name = f"{module_name}.{item}"
                            references.append(
                                APIReference(
                                    reference=full_name,
                                    reference_type="import",
                                    file_path=file_path,
                                    line_number=line_number,
                                    context=match.group(0),
                                )
                            )
                    else:
                        module_name = match.group(1)
                        references.append(
                            APIReference(
                                reference=module_name,
                                reference_type="module",
                                file_path=file_path,
                                line_number=line_number,
                                context=match.group(0),
                            )
                        )

        return references

    def _extract_references_from_code(self, code: str, file_path: str, base_line: int) -> list[APIReference]:
        """Extract API references from code content."""
        references = []

        try:
            # Parse the code to find function calls and attribute access
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    # Handle 'from module import item' statements
                    module_name = node.module
                    if module_name:
                        # Add the module reference
                        references.append(
                            APIReference(
                                reference=module_name,
                                reference_type="module",
                                file_path=file_path,
                                line_number=base_line + getattr(node, "lineno", 1) - 1,
                                context=f"Import from: {module_name}",
                            )
                        )

                        # Add the full qualified names for imported items
                        for alias in node.names:
                            item_name = alias.name
                            full_name = f"{module_name}.{item_name}"
                            references.append(
                                APIReference(
                                    reference=full_name,
                                    reference_type="import",
                                    file_path=file_path,
                                    line_number=base_line + getattr(node, "lineno", 1) - 1,
                                    context=f"Imported: {full_name}",
                                )
                            )

                elif isinstance(node, ast.Import):
                    # Handle 'import module' statements
                    for alias in node.names:
                        module_name = alias.name
                        references.append(
                            APIReference(
                                reference=module_name,
                                reference_type="module",
                                file_path=file_path,
                                line_number=base_line + getattr(node, "lineno", 1) - 1,
                                context=f"Import: {module_name}",
                            )
                        )

                elif isinstance(node, ast.Call):
                    # Function calls
                    if isinstance(node.func, ast.Name):
                        references.append(
                            APIReference(
                                reference=node.func.id,
                                reference_type="function_call",
                                file_path=file_path,
                                line_number=base_line + getattr(node, "lineno", 1) - 1,
                                context=f"Function call: {node.func.id}()",
                            )
                        )
                    elif isinstance(node.func, ast.Attribute):
                        # Method calls like obj.method()
                        full_name = self._get_full_attribute_name(node.func)
                        if full_name is None:
                            continue  # Skip if we can't determine the full name
                        references.append(
                            APIReference(
                                reference=full_name,  # type: ignore[arg-type]  # We've already checked for None
                                reference_type="method_call",
                                file_path=file_path,
                                line_number=base_line + getattr(node, "lineno", 1) - 1,
                                context=f"Method call: {full_name}()",
                            )
                        )

                elif isinstance(node, ast.Attribute):
                    # Attribute access
                    full_name = self._get_full_attribute_name(node)
                    if full_name is None:
                        continue  # Skip if we can't determine the full name
                    references.append(
                        APIReference(
                            reference=full_name,  # type: ignore[arg-type]  # We've already checked for None
                            reference_type="attribute_access",
                            file_path=file_path,
                            line_number=base_line + getattr(node, "lineno", 1) - 1,
                            context=f"Attribute access: {full_name}",
                        )
                    )

        except SyntaxError:
            # If code doesn't parse, try to extract references with regex
            simple_refs = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_.]*)\b", code)
            for ref in simple_refs:
                if "." in ref:  # Only interested in qualified names
                    references.append(
                        APIReference(
                            reference=ref,
                            reference_type="text_reference",
                            file_path=file_path,
                            line_number=base_line,
                            context=f"Text reference: {ref}",
                        )
                    )

        return references

    def _get_full_attribute_name(self, node: ast.expr) -> str | None:
        """Get the full name of an attribute access."""
        parts = []
        current = node

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))

        # Handle the case where we have a call like func().attr
        if isinstance(current, ast.Call) and isinstance(current.func, ast.Name):
            parts.append(f"{current.func.id}()")
            return ".".join(reversed(parts))

        return None

    def _validate_single_api_reference(self, reference: APIReference) -> ValidationResult:
        """Validate a single API reference."""
        ref_name = reference.reference

        print(f"    Validating reference: {ref_name}")

        # Skip certain types of references that are not API references
        if self._should_skip_reference(ref_name):
            print(f"      Skipping reference: {ref_name}")
            return ValidationResult(
                status=ValidationStatus.SKIPPED,
                message=f"Skipped reference: {ref_name}",
                file_path=reference.file_path,
                line_number=reference.line_number,
            )

        # Check if reference exists in our API definitions
        if ref_name in self._api_definitions:
            api_def = self._api_definitions[ref_name]
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"Valid API reference: {ref_name}",
                file_path=reference.file_path,
                line_number=reference.line_number,
                details={
                    "definition_type": api_def.definition_type,
                    "definition_file": api_def.file_path,
                    "definition_line": api_def.line_number,
                },
            )

        # Try partial matches for nested references
        partial_matches = self._find_partial_matches(ref_name)
        if partial_matches:
            # Only treat as warning if the partial match is very close (same module + similar name)
            module_name = ref_name.split(".")[0] if "." in ref_name else ref_name
            close_matches = [m for m in partial_matches if m.startswith(module_name + ".")]

            if close_matches:
                return ValidationResult(
                    status=ValidationStatus.WARNING,
                    message=f"Partial match for API reference: {ref_name}",
                    file_path=reference.file_path,
                    line_number=reference.line_number,
                    details={"partial_matches": close_matches},
                )

        # Check if it's a standard library or external module
        if self._is_external_reference(ref_name):
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message=f"External API reference: {ref_name}",
                file_path=reference.file_path,
                line_number=reference.line_number,
                details={"external": True},
            )

        # Reference not found
        return ValidationResult(
            status=ValidationStatus.FAILED,
            message=f"API reference not found: {ref_name}",
            file_path=reference.file_path,
            line_number=reference.line_number,
            details={
                "reference_type": reference.reference_type,
                "context": reference.context,
            },
        )

    def _should_skip_reference(self, ref_name: str) -> bool:
        """Check if a reference should be skipped."""
        skip_patterns = [
            # Built-in functions and types
            "print",
            "len",
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "tuple",
            "set",
            "range",
            "enumerate",
            "zip",
            "map",
            "filter",
            "sorted",
            "reversed",
            # Common variables and generic names
            "self",
            "cls",
            "args",
            "kwargs",
            "result",
            "data",
            "value",
            "item",
            # Single character or very short names
        ]

        # Skip single characters or very short names
        if len(ref_name) <= 2:
            return True

        # Skip if it's in the skip patterns
        if ref_name in skip_patterns:
            return True

        # Skip if it looks like a variable (all lowercase, no dots)
        if ref_name.islower() and "." not in ref_name:
            return True

        return False

    def _find_partial_matches(self, ref_name: str) -> list[str]:
        """Find partial matches for a reference."""
        matches = []

        for api_name in self._api_definitions.keys():
            if ref_name in api_name or api_name in ref_name:
                matches.append(api_name)

        return matches[:5]  # Return up to 5 matches

    def _is_external_reference(self, ref_name: str) -> bool:
        """Check if a reference is to an external module."""
        external_modules = [
            "json",
            "os",
            "sys",
            "pathlib",
            "re",
            "datetime",
            "time",
            "math",
            "collections",
            "itertools",
            "functools",
            "typing",
            "dataclasses",
            "unittest",
            "pytest",
            "logging",
            "argparse",
            "subprocess",
            "tempfile",
            "shutil",
            "glob",
            "csv",
            "sqlite3",
            "urllib",
            # Common third-party modules
            "numpy",
            "pandas",
            "matplotlib",
            "requests",
            "flask",
            "django",
            "pillow",
            "opencv",
            "scipy",
            "sklearn",
            "tensorflow",
            "torch",
        ]

        # Check if the reference starts with any external module
        for module in external_modules:
            if ref_name.startswith(module):
                return True

        # Try to import the module to see if it's available
        if "." in ref_name:
            module_name = ref_name.split(".")[0]

            # First check if this module is in our scanned API definitions
            if module_name in self._api_definitions:
                return False  # It's a local module, not external

            try:
                importlib.import_module(module_name)
                return True
            except ImportError:
                pass

        return False

    def get_api_coverage_report(self) -> dict[str, Any]:
        """Generate an API coverage report."""
        if not self._api_definitions:
            self._scan_codebase()

        # Count definitions by type
        type_counts: dict[str, int] = {}
        for api_def in self._api_definitions.values():
            type_counts[api_def.definition_type] = type_counts.get(api_def.definition_type, 0) + 1

        # Find undocumented APIs
        undocumented = []
        for api_def in self._api_definitions.values():
            if not api_def.docstring or len(api_def.docstring.strip()) < 10:
                undocumented.append(api_def.to_dict())

        return {
            "total_apis": len(self._api_definitions),
            "api_types": type_counts,
            "undocumented_count": len(undocumented),
            "undocumented_apis": undocumented[:20],  # First 20 undocumented
            "documentation_coverage": (
                (len(self._api_definitions) - len(undocumented)) / len(self._api_definitions) * 100
                if self._api_definitions
                else 0
            ),
        }
