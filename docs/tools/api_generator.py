"""
API Documentation Generator for Multi-Format Document Engine

This module provides automated generation of API documentation from Python source code,
extracting docstrings, type annotations, and generating markdown documentation.
"""

import ast
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ParameterInfo:
    """Information about a function/method parameter"""

    name: str
    type_annotation: str | None = None
    default_value: str | None = None
    description: str | None = None


@dataclass
class MethodInfo:
    """Information about a class method"""

    name: str
    docstring: str | None = None
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: str | None = None
    is_abstract: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    is_property: bool = False

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


@dataclass
class ClassInfo:
    """Information about a Python class"""

    name: str
    docstring: str | None = None
    base_classes: list[str] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)
    properties: list[MethodInfo] = field(default_factory=list)
    class_variables: list[tuple[str, str]] = field(default_factory=list)  # (name, type)
    is_abstract: bool = False

    def __post_init__(self):
        if self.base_classes is None:
            self.base_classes = []
        if self.methods is None:
            self.methods = []
        if self.properties is None:
            self.properties = []
        if self.class_variables is None:
            self.class_variables = []


@dataclass
class FunctionInfo:
    """Information about a standalone function"""

    name: str
    docstring: str | None = None
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: str | None = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


@dataclass
class ModuleInfo:
    """Information about a Python module"""

    name: str
    path: str
    docstring: str | None = None
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    constants: list[tuple[str, str, Any]] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.classes is None:
            self.classes = []
        if self.functions is None:
            self.functions = []
        if self.constants is None:
            self.constants = []
        if self.imports is None:
            self.imports = []


class APIDocumentationGenerator:
    """Generates API documentation from Python source code"""

    def __init__(self, source_root: str = "src"):
        self.source_root = Path(source_root)
        self.output_root = Path("docs/api")

    def extract_module_info(self, module_path: Path) -> ModuleInfo:
        """Extract comprehensive information from a Python module"""
        try:
            with open(module_path, encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # Get module docstring
            module_docstring = ast.get_docstring(tree)

            # Extract module information
            module_info = ModuleInfo(
                name=self._get_module_name(module_path),
                path=str(module_path),
                docstring=module_docstring,
            )

            # Process AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node)
                    module_info.classes.append(class_info)
                elif isinstance(node, ast.FunctionDef) and not self._is_method(node, tree):
                    function_info = self._extract_function_info(node)
                    module_info.functions.append(function_info)
                elif isinstance(node, ast.Assign):
                    constants = self._extract_constants(node)
                    module_info.constants.extend(constants)
                elif isinstance(node, ast.Import | ast.ImportFrom):
                    imports = self._extract_imports(node)
                    module_info.imports.extend(imports)

            return module_info

        except Exception as e:
            logger.error(f"Error extracting module info from {module_path}: {e}")
            return ModuleInfo(
                name=self._get_module_name(module_path),
                path=str(module_path),
                docstring=f"Error extracting documentation: {e}",
            )

    def _get_module_name(self, module_path: Path) -> str:
        """Get the module name from its path"""
        relative_path = module_path.relative_to(self.source_root)
        module_name = str(relative_path.with_suffix(""))
        return module_name.replace(os.sep, ".")

    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from a class definition"""
        class_info = ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            base_classes=[self._get_name(base) for base in node.bases],
            is_abstract=self._is_abstract_class(node),
        )

        # Extract methods and properties
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method_info(item)
                if method_info.is_property:
                    class_info.properties.append(method_info)
                else:
                    class_info.methods.append(method_info)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Class variable with type annotation
                var_name = item.target.id
                var_type = self._get_annotation_string(item.annotation)
                class_info.class_variables.append((var_name, var_type))

        return class_info

    def _extract_method_info(self, node: ast.FunctionDef) -> MethodInfo:
        """Extract information from a method definition"""
        method_info = MethodInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            parameters=self._extract_parameters(node),
            return_type=(self._get_annotation_string(node.returns) if node.returns else None),
            is_abstract=self._has_decorator(node, "abstractmethod"),
            is_classmethod=self._has_decorator(node, "classmethod"),
            is_staticmethod=self._has_decorator(node, "staticmethod"),
            is_property=self._has_decorator(node, "property"),
        )

        return method_info

    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract information from a function definition"""
        return FunctionInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            parameters=self._extract_parameters(node),
            return_type=(self._get_annotation_string(node.returns) if node.returns else None),
        )

    def _extract_parameters(self, node: ast.FunctionDef) -> list[ParameterInfo]:
        """Extract parameter information from a function/method"""
        parameters = []

        # Regular arguments
        for i, arg in enumerate(node.args.args):
            param_info = ParameterInfo(
                name=arg.arg,
                type_annotation=(self._get_annotation_string(arg.annotation) if arg.annotation else None),
            )

            # Check for default values
            defaults_offset = len(node.args.args) - len(node.args.defaults)
            if i >= defaults_offset:
                default_index = i - defaults_offset
                param_info.default_value = self._get_default_value_string(node.args.defaults[default_index])

            parameters.append(param_info)

        # Keyword-only arguments
        for i, arg in enumerate(node.args.kwonlyargs):
            param_info = ParameterInfo(
                name=arg.arg,
                type_annotation=(self._get_annotation_string(arg.annotation) if arg.annotation else None),
            )

            # Check for default values in kw_defaults
            if i < len(node.args.kw_defaults) and node.args.kw_defaults[i] is not None:
                param_info.default_value = self._get_default_value_string(node.args.kw_defaults[i])

            parameters.append(param_info)

        return parameters

    def _extract_constants(self, node: ast.Assign) -> list[tuple[str, str, Any]]:
        """Extract constants from assignment nodes"""
        constants = []

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                # This looks like a constant
                const_name = target.id
                const_type = "Any"  # We can't easily determine type from AST
                const_value = self._get_value_string(node.value)
                constants.append((const_name, const_type, const_value))

        return constants

    def _extract_imports(self, node: ast.Import | ast.ImportFrom) -> list[str]:
        """Extract import statements"""
        imports = []

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"from {module} import {alias.name}")

        return imports

    def _get_annotation_string(self, annotation: ast.AST) -> str:
        """Convert an AST annotation to a string"""
        try:
            return ast.unparse(annotation)
        except (ValueError, SyntaxError):
            return "Any"

    def _get_default_value_string(self, default: ast.expr | None) -> str:
        """Convert a default value AST to a string"""
        if default is None:
            return "..."
        try:
            return ast.unparse(default)
        except (ValueError, SyntaxError):
            return "..."

    def _get_value_string(self, value: ast.AST) -> str:
        """Convert a value AST to a string"""
        try:
            return ast.unparse(value)
        except (ValueError, SyntaxError):
            return "..."

    def _get_name(self, node: ast.AST) -> str:
        """Get name from an AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            try:
                return ast.unparse(node)
            except (ValueError, SyntaxError):
                return "Unknown"

    def _is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method (inside a class)"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False

    def _is_abstract_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is abstract"""
        # Check if it inherits from ABC
        for base in node.bases:
            if self._get_name(base) in ["ABC", "abc.ABC"]:
                return True

        # Check if it has abstract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and self._has_decorator(item, "abstractmethod"):
                return True

        return False

    def _has_decorator(self, node: ast.FunctionDef, decorator_name: str) -> bool:
        """Check if a function has a specific decorator"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == decorator_name:
                return True
        return False

    def generate_markdown_documentation(self, module_info: ModuleInfo) -> str:
        """Generate markdown documentation for a module"""
        lines = []

        # Module header
        lines.append(f"# {module_info.name}")
        lines.append("")

        if module_info.docstring:
            lines.append(module_info.docstring)
            lines.append("")

        # Module path
        lines.append(f"**Module Path:** `{module_info.path}`")
        lines.append("")

        # Imports section
        if module_info.imports:
            lines.append("## Imports")
            lines.append("")
            lines.append("```python")
            for imp in sorted(set(module_info.imports)):
                lines.append(imp)
            lines.append("```")
            lines.append("")

        # Constants section
        if module_info.constants:
            lines.append("## Constants")
            lines.append("")
            for const_name, const_type, const_value in module_info.constants:
                lines.append(f"### {const_name}")
                lines.append("")
                lines.append(f"**Type:** `{const_type}`")
                lines.append("")
                lines.append(f"**Value:** `{const_value}`")
                lines.append("")

        # Classes section
        if module_info.classes:
            lines.append("## Classes")
            lines.append("")

            for class_info in module_info.classes:
                lines.extend(self._generate_class_documentation(class_info))
                lines.append("")

        # Functions section
        if module_info.functions:
            lines.append("## Functions")
            lines.append("")

            for function_info in module_info.functions:
                lines.extend(self._generate_function_documentation(function_info))
                lines.append("")

        return "\n".join(lines)

    def _generate_class_documentation(self, class_info: ClassInfo) -> list[str]:
        """Generate documentation for a class"""
        lines = []

        # Class header
        class_title = f"### {class_info.name}"
        if class_info.is_abstract:
            class_title += " (Abstract)"
        lines.append(class_title)
        lines.append("")

        # Base classes
        if class_info.base_classes:
            base_classes_str = ", ".join(f"`{base}`" for base in class_info.base_classes)
            lines.append(f"**Inherits from:** {base_classes_str}")
            lines.append("")

        # Class docstring
        if class_info.docstring:
            lines.append(class_info.docstring)
            lines.append("")

        # Class variables
        if class_info.class_variables:
            lines.append("#### Class Variables")
            lines.append("")
            for var_name, var_type in class_info.class_variables:
                lines.append(f"- **{var_name}**: `{var_type}`")
            lines.append("")

        # Properties
        if class_info.properties:
            lines.append("#### Properties")
            lines.append("")
            for prop in class_info.properties:
                lines.extend(self._generate_method_documentation(prop, is_property=True))
                lines.append("")

        # Methods
        if class_info.methods:
            lines.append("#### Methods")
            lines.append("")
            for method in class_info.methods:
                lines.extend(self._generate_method_documentation(method))
                lines.append("")

        return lines

    def _generate_method_documentation(self, method_info: MethodInfo, is_property: bool = False) -> list[str]:
        """Generate documentation for a method"""
        lines = []

        # Method signature
        method_type = ""
        if method_info.is_abstract:
            method_type += "Abstract "
        if method_info.is_classmethod:
            method_type += "Class Method"
        elif method_info.is_staticmethod:
            method_type += "Static Method"
        elif is_property:
            method_type += "Property"
        else:
            method_type += "Method"

        lines.append(f"##### {method_info.name} ({method_type})")
        lines.append("")

        # Method signature
        params = []
        for param in method_info.parameters:
            param_str = param.name
            if param.type_annotation:
                param_str += f": {param.type_annotation}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            params.append(param_str)

        signature = f"{method_info.name}({', '.join(params)})"
        if method_info.return_type:
            signature += f" -> {method_info.return_type}"

        lines.append("```python")
        lines.append(signature)
        lines.append("```")
        lines.append("")

        # Method docstring
        if method_info.docstring:
            lines.append(method_info.docstring)
            lines.append("")

        # Parameters
        if method_info.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            for param in method_info.parameters:
                param_line = f"- **{param.name}**"
                if param.type_annotation:
                    param_line += f" (`{param.type_annotation}`)"
                if param.default_value:
                    param_line += f" = `{param.default_value}`"
                if param.description:
                    param_line += f": {param.description}"
                lines.append(param_line)
            lines.append("")

        # Return type
        if method_info.return_type:
            lines.append(f"**Returns:** `{method_info.return_type}`")
            lines.append("")

        return lines

    def _generate_function_documentation(self, function_info: FunctionInfo) -> list[str]:
        """Generate documentation for a standalone function"""
        lines = []

        lines.append(f"### {function_info.name}")
        lines.append("")

        # Function signature
        params = []
        for param in function_info.parameters:
            param_str = param.name
            if param.type_annotation:
                param_str += f": {param.type_annotation}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            params.append(param_str)

        signature = f"{function_info.name}({', '.join(params)})"
        if function_info.return_type:
            signature += f" -> {function_info.return_type}"

        lines.append("```python")
        lines.append(signature)
        lines.append("```")
        lines.append("")

        # Function docstring
        if function_info.docstring:
            lines.append(function_info.docstring)
            lines.append("")

        # Parameters
        if function_info.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            for param in function_info.parameters:
                param_line = f"- **{param.name}**"
                if param.type_annotation:
                    param_line += f" (`{param.type_annotation}`)"
                if param.default_value:
                    param_line += f" = `{param.default_value}`"
                lines.append(param_line)
            lines.append("")

        # Return type
        if function_info.return_type:
            lines.append(f"**Returns:** `{function_info.return_type}`")
            lines.append("")

        return lines

    def generate_api_documentation(self, output_dir: str | None = None) -> None:
        """Generate complete API documentation for all modules"""
        if output_dir:
            self.output_root = Path(output_dir)

        # Ensure output directory exists
        self.output_root.mkdir(parents=True, exist_ok=True)

        # Find all Python modules
        python_files = list(self.source_root.rglob("*.py"))
        python_files = [f for f in python_files if not f.name.startswith("__") and "test" not in str(f)]

        logger.info(f"Found {len(python_files)} Python modules to document")

        # Generate documentation for each module
        for module_path in python_files:
            try:
                module_info = self.extract_module_info(module_path)
                markdown_content = self.generate_markdown_documentation(module_info)

                # Determine output path
                relative_path = module_path.relative_to(self.source_root)
                output_path = self.output_root / relative_path.with_suffix(".md")

                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Write documentation
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                logger.info(f"Generated documentation for {module_info.name} -> {output_path}")

            except Exception as e:
                logger.error(f"Failed to generate documentation for {module_path}: {e}")

        # Generate index files
        self._generate_index_files()

        logger.info("API documentation generation complete")

    def _generate_index_files(self) -> None:
        """Generate index files for API documentation"""
        # Generate main API index
        self._generate_main_api_index()

        # Generate category indices
        categories = ["core", "engines", "models", "tools"]
        for category in categories:
            category_path = self.output_root / category
            if category_path.exists():
                self._generate_category_index(category)

    def _generate_main_api_index(self) -> None:
        """Generate the main API documentation index"""
        lines = [
            "# API Documentation",
            "",
            "This section contains comprehensive API documentation for the Multi-Format Document Engine.",
            "",
            "## Categories",
            "",
            "- [Core Modules](core/) - Core functionality and base classes",
            "- [Engines](engines/) - Document parsing and rendering engines",
            "- [Models](models/) - Data models and schemas",
            "- [Tools](tools/) - Utility functions and helpers",
            "",
            "## Quick Reference",
            "",
            "### Key Classes",
            "",
            "- [`UniversalDocument`](models/universal_idm.md#UniversalDocument) - Main document model",
            "- [`DocumentParser`](engines/document_parser.md#DocumentParser) - Abstract parser interface",
            "- [`DocumentRenderer`](engines/document_renderer.md#DocumentRenderer) - Abstract renderer interface",
            "",
            "### Key Functions",
            "",
            "- [`extract_pdf_content`](engines/extract_pdf_content_fitz.md#extract_pdf_content) - PDF content extraction",
            "- [`recreate_pdf_from_config`](../recreate_pdf_from_config.md#recreate_pdf_from_config) - PDF reconstruction",
            "",
            "## Usage Examples",
            "",
            "See the [examples directory](../examples/) for complete usage examples.",
        ]

        index_path = self.output_root / "README.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _generate_category_index(self, category: str) -> None:
        """Generate index for a specific category"""
        category_path = self.output_root / category
        if not category_path.exists():
            return

        # Find all markdown files in the category
        md_files = list(category_path.rglob("*.md"))
        md_files = [f for f in md_files if f.name != "README.md"]

        lines = [
            f"# {category.title()} API Documentation",
            "",
            f"This section contains API documentation for {category} modules.",
            "",
            "## Modules",
            "",
        ]

        for md_file in sorted(md_files):
            relative_path = md_file.relative_to(category_path)
            module_name = str(relative_path.with_suffix(""))
            lines.append(f"- [{module_name}]({relative_path})")

        index_path = category_path / "README.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Generate API documentation
    generator = APIDocumentationGenerator()
    generator.generate_api_documentation()
