"""
Documentation coverage reporting system.

This module provides comprehensive reporting on documentation coverage,
including API documentation, code examples, and guide completeness.
"""

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CoverageMetrics:
    """Documentation coverage metrics."""

    total_modules: int
    documented_modules: int
    total_classes: int
    documented_classes: int
    total_functions: int
    documented_functions: int
    total_methods: int
    documented_methods: int
    coverage_percentage: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_modules": self.total_modules,
            "documented_modules": self.documented_modules,
            "total_classes": self.total_classes,
            "documented_classes": self.documented_classes,
            "total_functions": self.total_functions,
            "documented_functions": self.documented_functions,
            "total_methods": self.total_methods,
            "documented_methods": self.documented_methods,
            "coverage_percentage": self.coverage_percentage,
        }


@dataclass
class ModuleCoverage:
    """Coverage information for a single module."""

    module_path: Path
    module_name: str
    has_module_docstring: bool
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    coverage_score: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module_path": str(self.module_path),
            "module_name": self.module_name,
            "has_module_docstring": self.has_module_docstring,
            "classes": self.classes,
            "functions": self.functions,
            "coverage_score": self.coverage_score,
        }


class DocumentationCoverageReporter:
    """Generates comprehensive documentation coverage reports."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the coverage reporter."""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.src_dir = self.project_root / "src"
        self.docs_dir = self.project_root / "docs"

    def generate_coverage_report(self) -> dict[str, Any]:
        """Generate a comprehensive coverage report."""
        print("📊 Generating documentation coverage report...")

        # Analyze source code coverage
        api_coverage = self._analyze_api_coverage()

        # Analyze documentation completeness
        docs_completeness = self._analyze_docs_completeness()

        # Analyze code examples coverage
        examples_coverage = self._analyze_examples_coverage()

        # Generate overall metrics
        overall_metrics = self._calculate_overall_metrics(api_coverage)

        report = {
            "timestamp": str(Path.cwd()),  # Placeholder for actual timestamp
            "project_root": str(self.project_root),
            "overall_metrics": overall_metrics.to_dict(),
            "api_coverage": api_coverage,
            "documentation_completeness": docs_completeness,
            "examples_coverage": examples_coverage,
            "recommendations": self._generate_recommendations(overall_metrics, api_coverage),
        }

        return report

    def _analyze_api_coverage(self) -> list[dict[str, Any]]:
        """Analyze API documentation coverage."""
        coverage_data: list[dict[str, Any]] = []

        if not self.src_dir.exists():
            return coverage_data

        # Find all Python files
        python_files = list(self.src_dir.rglob("*.py"))

        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue

            try:
                module_coverage = self._analyze_module_coverage(py_file)
                coverage_data.append(module_coverage.to_dict())
            except Exception as e:
                print(f"  Warning: Could not analyze {py_file}: {e}")

        return coverage_data

    def _analyze_module_coverage(self, py_file: Path) -> ModuleCoverage:
        """Analyze coverage for a single module."""
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except Exception as e:
            raise ValueError(f"Could not parse {py_file}: {e}")

        # Get module name
        module_name = py_file.stem

        # Check for module docstring
        has_module_docstring = ast.get_docstring(tree) is not None

        # Analyze classes
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._analyze_class_coverage(node)
                classes.append(class_info)

        # Analyze functions (not methods)
        functions = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function_coverage(node)
                functions.append(func_info)

        # Calculate coverage score
        coverage_score = self._calculate_module_coverage_score(has_module_docstring, classes, functions)

        return ModuleCoverage(
            module_path=py_file,
            module_name=module_name,
            has_module_docstring=has_module_docstring,
            classes=classes,
            functions=functions,
            coverage_score=coverage_score,
        )

    def _analyze_class_coverage(self, class_node: ast.ClassDef) -> dict[str, Any]:
        """Analyze documentation coverage for a class."""
        has_docstring = ast.get_docstring(class_node) is not None

        # Analyze methods
        methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_info = self._analyze_function_coverage(node, is_method=True)
                methods.append(method_info)

        return {
            "name": class_node.name,
            "has_docstring": has_docstring,
            "methods": methods,
            "line_number": class_node.lineno,
        }

    def _analyze_function_coverage(self, func_node: ast.FunctionDef, is_method: bool = False) -> dict[str, Any]:
        """Analyze documentation coverage for a function or method."""
        has_docstring = ast.get_docstring(func_node) is not None

        # Get function arguments
        args = []
        if func_node.args.args:
            for arg in func_node.args.args:
                args.append(arg.arg)

        # Check for type annotations
        has_return_annotation = func_node.returns is not None
        has_arg_annotations = any(arg.annotation is not None for arg in func_node.args.args)

        return {
            "name": func_node.name,
            "has_docstring": has_docstring,
            "has_return_annotation": has_return_annotation,
            "has_arg_annotations": has_arg_annotations,
            "args": args,
            "line_number": func_node.lineno,
            "is_method": is_method,
        }

    def _calculate_module_coverage_score(
        self,
        has_module_docstring: bool,
        classes: list[dict[str, Any]],
        functions: list[dict[str, Any]],
    ) -> float:
        """Calculate coverage score for a module."""
        total_items = 1 + len(classes) + len(functions)  # +1 for module docstring
        documented_items = 0

        if has_module_docstring:
            documented_items += 1

        # Count documented classes and their methods
        for class_info in classes:
            if class_info["has_docstring"]:
                documented_items += 1
            for method in class_info["methods"]:
                total_items += 1
                if method["has_docstring"]:
                    documented_items += 1

        # Count documented functions
        for func_info in functions:
            if func_info["has_docstring"]:
                documented_items += 1

        return (documented_items / total_items * 100) if total_items > 0 else 0.0

    def _analyze_docs_completeness(self) -> dict[str, Any]:
        """Analyze completeness of documentation files."""
        completeness = {
            "required_files": [],
            "optional_files": [],
            "missing_files": [],
            "empty_files": [],
        }

        # Required documentation files
        required_files = [
            "README.md",
            "INSTALLATION.md",
            "ARCHITECTURE.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
        ]

        for file_name in required_files:
            file_path = self.docs_dir / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8").strip()
                    if len(content) > 100:  # Minimum content threshold
                        completeness["required_files"].append(
                            {
                                "name": file_name,
                                "status": "complete",
                                "size": len(content),
                            }
                        )
                    else:
                        completeness["empty_files"].append(file_name)
                except Exception:
                    completeness["empty_files"].append(file_name)
            else:
                completeness["missing_files"].append(file_name)

        # Check for guides
        guides_dir = self.docs_dir / "guides"
        if guides_dir.exists():
            guide_files = list(guides_dir.rglob("*.md"))
            completeness["guides_count"] = len(guide_files)
            completeness["guides"] = [str(f.relative_to(guides_dir)) for f in guide_files]
        else:
            completeness["guides_count"] = 0
            completeness["guides"] = []

        # Check for API documentation
        api_dir = self.docs_dir / "api"
        if api_dir.exists():
            api_files = list(api_dir.rglob("*.md"))
            completeness["api_docs_count"] = len(api_files)
            completeness["api_docs"] = [str(f.relative_to(api_dir)) for f in api_files]
        else:
            completeness["api_docs_count"] = 0
            completeness["api_docs"] = []

        return completeness

    def _analyze_examples_coverage(self) -> dict[str, Any]:
        """Analyze code examples coverage."""
        examples_coverage = {
            "total_examples": 0,
            "working_examples": 0,
            "broken_examples": 0,
            "examples_by_file": [],
        }

        if not self.docs_dir.exists():
            return examples_coverage

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                examples = self._extract_code_examples_for_coverage(content)

                file_examples = {
                    "file": str(md_file.relative_to(self.docs_dir)),
                    "total": len(examples),
                    "examples": examples,
                }

                examples_coverage["examples_by_file"].append(file_examples)
                examples_coverage["total_examples"] += len(examples)

            except Exception as e:
                print(f"  Warning: Could not analyze examples in {md_file}: {e}")

        return examples_coverage

    def _extract_code_examples_for_coverage(self, content: str) -> list[dict[str, Any]]:
        """Extract code examples for coverage analysis."""
        examples = []

        # Pattern to match code blocks
        code_block_pattern = r"```(?:python|bash|shell|json)\n(.*?)\n```"
        matches = re.finditer(code_block_pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            code = match.group(1).strip()
            if code and not code.startswith("#"):  # Skip empty or comment-only blocks
                examples.append(
                    {
                        "index": i,
                        "code": code[:100] + "..." if len(code) > 100 else code,
                        "line_number": content[: match.start()].count("\n") + 1,
                        "length": len(code),
                    }
                )

        return examples

    def _calculate_overall_metrics(self, api_coverage: list[dict[str, Any]]) -> CoverageMetrics:
        """Calculate overall coverage metrics."""
        total_modules = len(api_coverage)
        documented_modules = 0
        total_classes = 0
        documented_classes = 0
        total_functions = 0
        documented_functions = 0
        total_methods = 0
        documented_methods = 0

        for module in api_coverage:
            if module["has_module_docstring"]:
                documented_modules += 1

            # Count classes
            for class_info in module["classes"]:
                total_classes += 1
                if class_info["has_docstring"]:
                    documented_classes += 1

                # Count methods
                for method in class_info["methods"]:
                    total_methods += 1
                    if method["has_docstring"]:
                        documented_methods += 1

            # Count functions
            for func_info in module["functions"]:
                total_functions += 1
                if func_info["has_docstring"]:
                    documented_functions += 1

        # Calculate overall coverage percentage
        total_items = total_modules + total_classes + total_functions + total_methods
        documented_items = documented_modules + documented_classes + documented_functions + documented_methods
        coverage_percentage = (documented_items / total_items * 100) if total_items > 0 else 0.0

        return CoverageMetrics(
            total_modules=total_modules,
            documented_modules=documented_modules,
            total_classes=total_classes,
            documented_classes=documented_classes,
            total_functions=total_functions,
            documented_functions=documented_functions,
            total_methods=total_methods,
            documented_methods=documented_methods,
            coverage_percentage=coverage_percentage,
        )

    def _generate_recommendations(self, metrics: CoverageMetrics, api_coverage: list[dict[str, Any]]) -> list[str]:
        """Generate recommendations for improving documentation coverage."""
        recommendations = []

        if metrics.coverage_percentage < 50:
            recommendations.append(
                "📝 Overall documentation coverage is below 50%. Consider adding docstrings to key modules, classes, and functions."
            )

        if metrics.documented_modules / metrics.total_modules < 0.8:
            recommendations.append(
                "📄 Many modules lack module-level docstrings. Add descriptive docstrings to explain module purpose."
            )

        if metrics.documented_classes / metrics.total_classes < 0.7:
            recommendations.append("🏗️  Many classes lack docstrings. Document class purpose and usage patterns.")

        if metrics.documented_functions / metrics.total_functions < 0.6:
            recommendations.append(
                "⚙️  Many functions lack docstrings. Document function parameters, return values, and behavior."
            )

        # Find modules with lowest coverage
        low_coverage_modules = [module for module in api_coverage if module["coverage_score"] < 30]

        if low_coverage_modules:
            module_names = [m["module_name"] for m in low_coverage_modules[:3]]
            recommendations.append(f"🎯 Focus on improving documentation for: {', '.join(module_names)}")

        if metrics.coverage_percentage > 80:
            recommendations.append(
                "🎉 Excellent documentation coverage! Consider adding more code examples and usage guides."
            )

        return recommendations

    def export_coverage_report(self, output_path: Path, report: dict[str, Any]) -> None:
        """Export coverage report to JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📊 Coverage report exported to: {output_path}")
        except Exception:
            print("❌ Failed to export coverage report.")

    def print_coverage_summary(self, report: dict[str, Any]) -> None:
        """Print a summary of the coverage report."""
        print("\n" + "=" * 60)
        print("📊 DOCUMENTATION COVERAGE SUMMARY")
        print("=" * 60)

        metrics = report["overall_metrics"]
        print(f"📈 Overall Coverage: {metrics['coverage_percentage']:.1f}%")
        print(f"📁 Modules: {metrics['documented_modules']}/{metrics['total_modules']} documented")
        print(f"🏗️  Classes: {metrics['documented_classes']}/{metrics['total_classes']} documented")
        print(f"⚙️  Functions: {metrics['documented_functions']}/{metrics['total_functions']} documented")
        print(f"🔧 Methods: {metrics['documented_methods']}/{metrics['total_methods']} documented")

        # Documentation completeness
        completeness = report["documentation_completeness"]
        print("\n📚 Documentation Files:")
        print(f"  Required files: {len(completeness['required_files'])}")
        print(f"  Missing files: {len(completeness['missing_files'])}")
        print(f"  API docs: {completeness['api_docs_count']}")
        print(f"  Guides: {completeness['guides_count']}")

        # Examples coverage
        examples = report["examples_coverage"]
        print(f"\n💡 Code Examples: {examples['total_examples']} found")

        # Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print("\n🎯 Recommendations:")
            for rec in recommendations:
                print(f"  {rec}")

        print("=" * 60)
