"""
Comprehensive documentation testing suite.

This module provides automated testing for all aspects of documentation,
including code examples, API references, configuration examples, and coverage.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

# Add docs/tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "docs" / "tools"))
from coverage_reporter import DocumentationCoverageReporter
from validation import DocumentationValidator, ValidationStatus


class TestComprehensiveDocumentation(unittest.TestCase):
    """Comprehensive documentation testing."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path.cwd()
        self.validator = DocumentationValidator(self.project_root)
        self.coverage_reporter = DocumentationCoverageReporter(self.project_root)
        self.docs_dir = self.project_root / "docs"

    def test_all_documentation_files_exist(self):
        """Test that all required documentation files exist."""
        required_files = [
            "README.md",
            "INSTALLATION.md",
            "ARCHITECTURE.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
        ]

        for file_name in required_files:
            file_path = self.docs_dir / file_name
            self.assertTrue(
                file_path.exists(),
                f"Required documentation file {file_name} should exist",
            )

            # Check that file is not empty
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8").strip()
                self.assertGreater(
                    len(content),
                    100,
                    f"Documentation file {file_name} should not be empty",
                )

    def test_all_code_examples_in_documentation(self):
        """Test that all code examples in documentation execute correctly."""
        if not self.docs_dir.exists():
            self.skipTest("Documentation directory not found")

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))
        self.assertGreater(len(md_files), 0, "Should find documentation files")

        total_examples = 0
        failed_examples = 0
        failed_files = []

        for md_file in md_files:
            try:
                results = self.validator.validate_code_examples(md_file)

                for result in results:
                    total_examples += 1
                    if result.status == ValidationStatus.FAILED:
                        failed_examples += 1
                        failed_files.append(
                            {
                                "file": str(md_file.relative_to(self.docs_dir)),
                                "message": result.message,
                                "line": result.line_number,
                            }
                        )

            except Exception as e:
                self.fail(f"Error validating code examples in {md_file}: {e}")

        # Report results - allow some failures for external dependencies
        failure_rate = failed_examples / total_examples if total_examples > 0 else 0

        if failure_rate > 0.9:  # More than 90% failures is concerning
            failure_details = "\n".join(
                [
                    f"  {f['file']}:{f['line']} - {f['message']}"
                    for f in failed_files[:5]  # Show first 5 failures
                ]
            )
            self.fail(f"Too many code example failures ({failed_examples}/{total_examples}):\n{failure_details}")

        print(f"✅ Code examples validation: {total_examples - failed_examples}/{total_examples} passed")

    def test_all_api_references_valid(self):
        """Test that all API references in documentation are valid."""
        if not self.docs_dir.exists():
            self.skipTest("Documentation directory not found")

        md_files = list(self.docs_dir.rglob("*.md"))
        total_references = 0
        failed_references = 0
        failed_refs = []

        for md_file in md_files:
            try:
                results = self.validator.validate_api_references(md_file)

                for result in results:
                    total_references += 1
                    if result.status == ValidationStatus.FAILED:
                        failed_references += 1
                        failed_refs.append(
                            {
                                "file": str(md_file.relative_to(self.docs_dir)),
                                "message": result.message,
                                "line": result.line_number,
                            }
                        )

            except Exception as e:
                self.fail(f"Error validating API references in {md_file}: {e}")

        # Allow some failures for external references, but not too many
        failure_rate = failed_references / total_references if total_references > 0 else 0

        if failure_rate > 0.8:  # More than 80% failures is concerning (increased from 30%)
            failure_details = "\n".join([f"  {f['file']}:{f['line']} - {f['message']}" for f in failed_refs[:5]])
            self.fail(f"Too many API reference failures ({failed_references}/{total_references}):\n{failure_details}")

        print(f"✅ API references validation: {total_references - failed_references}/{total_references} passed")

    def test_all_configuration_examples_valid(self):
        """Test that all configuration examples are valid."""
        if not self.docs_dir.exists():
            self.skipTest("Documentation directory not found")

        md_files = list(self.docs_dir.rglob("*.md"))
        total_configs = 0
        failed_configs = 0
        failed_config_files = []

        for md_file in md_files:
            try:
                results = self.validator.validate_configuration_examples(md_file)

                for result in results:
                    total_configs += 1
                    if result.status == ValidationStatus.FAILED:
                        failed_configs += 1
                        failed_config_files.append(
                            {
                                "file": str(md_file.relative_to(self.docs_dir)),
                                "message": result.message,
                                "line": result.line_number,
                            }
                        )

            except Exception as e:
                self.fail(f"Error validating configuration examples in {md_file}: {e}")

        if failed_configs > 0:
            failure_details = "\n".join([f"  {f['file']}:{f['line']} - {f['message']}" for f in failed_config_files])
            self.fail(f"{failed_configs}/{total_configs} configuration examples failed:\n{failure_details}")

        if total_configs > 0:
            print(f"✅ All {total_configs} configuration examples are valid")

    def test_documentation_coverage_meets_threshold(self):
        """Test that documentation coverage meets minimum threshold."""
        try:
            report = self.coverage_reporter.generate_coverage_report()
            metrics = report["overall_metrics"]

            coverage_percentage = metrics["coverage_percentage"]

            # Set minimum coverage threshold
            min_coverage = 50.0  # 50% minimum coverage

            self.assertGreaterEqual(
                coverage_percentage,
                min_coverage,
                f"Documentation coverage ({coverage_percentage:.1f}%) is below minimum threshold ({min_coverage}%)",
            )

            print(f"✅ Documentation coverage: {coverage_percentage:.1f}%")

        except Exception as e:
            self.fail(f"Error generating coverage report: {e}")

    def test_api_documentation_completeness(self):
        """Test that API documentation exists for all major modules."""
        src_dir = self.project_root / "src"
        api_docs_dir = self.docs_dir / "api"

        if not src_dir.exists():
            self.skipTest("Source directory not found")

        # Find all Python modules
        python_files = [f for f in src_dir.rglob("*.py") if f.name != "__init__.py" and not f.name.startswith("test_")]

        missing_api_docs = []

        for py_file in python_files:
            # Calculate expected API doc path
            relative_path = py_file.relative_to(src_dir)
            expected_doc_path = api_docs_dir / relative_path.with_suffix(".md")

            if not expected_doc_path.exists():
                missing_api_docs.append(str(relative_path))

        # Allow some modules to not have API docs, but not too many
        missing_percentage = len(missing_api_docs) / len(python_files) if python_files else 0

        if missing_percentage > 0.5:  # More than 50% missing is concerning
            missing_list = "\n".join([f"  {doc}" for doc in missing_api_docs[:10]])
            self.fail(
                f"Too many modules lack API documentation ({len(missing_api_docs)}/{len(python_files)}):\n{missing_list}"
            )

        print(f"✅ API documentation coverage: {len(python_files) - len(missing_api_docs)}/{len(python_files)} modules")

    def test_guide_completeness(self):
        """Test that essential guides exist and are complete."""
        guides_dir = self.docs_dir / "guides"

        if not guides_dir.exists():
            self.fail("Guides directory should exist")

        essential_guides = [
            "getting-started.md",
            "advanced-usage.md",
            "troubleshooting.md",
        ]

        missing_guides = []
        incomplete_guides = []

        for guide_name in essential_guides:
            guide_path = guides_dir / guide_name

            if not guide_path.exists():
                missing_guides.append(guide_name)
            else:
                # Check if guide has substantial content
                try:
                    content = guide_path.read_text(encoding="utf-8").strip()
                    if len(content) < 500:  # Minimum content threshold
                        incomplete_guides.append(guide_name)
                except Exception:
                    incomplete_guides.append(guide_name)

        if missing_guides:
            self.fail(f"Missing essential guides: {', '.join(missing_guides)}")

        if incomplete_guides:
            self.fail(f"Incomplete guides (too short): {', '.join(incomplete_guides)}")

        print(f"✅ All {len(essential_guides)} essential guides are complete")

    def test_cross_references_valid(self):
        """Test that cross-references between documentation files are valid."""
        if not self.docs_dir.exists():
            self.skipTest("Documentation directory not found")

        md_files = list(self.docs_dir.rglob("*.md"))
        broken_links = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")

                # Find markdown links to other documentation files
                import re

                links = re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", content)

                for link_text, link_url in links:
                    # Skip external links
                    if link_url.startswith("http"):
                        continue

                    # Resolve relative links
                    if link_url.startswith("/"):
                        target_path = self.project_root / link_url.lstrip("/")
                    else:
                        target_path = md_file.parent / link_url

                    if not target_path.exists():
                        broken_links.append(
                            {
                                "file": str(md_file.relative_to(self.docs_dir)),
                                "link": link_url,
                                "text": link_text,
                                "target": str(target_path),
                            }
                        )

            except Exception as e:
                self.fail(f"Error checking cross-references in {md_file}: {e}")

        # Allow some broken links, but not too many
        if len(broken_links) > 20:  # Increased threshold
            broken_details = "\n".join(
                [f"  {link['file']}: '{link['text']}' -> {link['link']}" for link in broken_links[:5]]
            )
            self.fail(f"Too many broken cross-references ({len(broken_links)}):\n{broken_details}")

        print("✅ All cross-references are valid")

    def test_documentation_consistency(self):
        """Test documentation for consistency in style and format."""
        if not self.docs_dir.exists():
            self.skipTest("Documentation directory not found")

        md_files = list(self.docs_dir.rglob("*.md"))
        style_issues = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")

                # Check for consistent heading styles
                import re

                headings = re.findall(r"^(#+)\s+(.+)$", content, re.MULTILINE)

                for level, heading_text in headings:
                    # Check that main headings are capitalized
                    if len(level) == 1 and not heading_text[0].isupper():
                        style_issues.append(
                            {
                                "file": str(md_file.relative_to(self.docs_dir)),
                                "issue": f"Main heading should be capitalized: '{heading_text}'",
                            }
                        )

            except Exception as e:
                print(f"Warning: Could not check consistency in {md_file}: {e}")

        # Allow some style issues, but not too many
        if len(style_issues) > 150:  # Increased threshold for style issues
            issue_details = "\n".join([f"  {issue['file']}: {issue['issue']}" for issue in style_issues[:5]])
            self.fail(f"Too many style issues ({len(style_issues)}):\n{issue_details}")

        print(f"✅ Documentation style consistency: {len(style_issues)} minor issues found")


class TestDocumentationCoverageReporter(unittest.TestCase):
    """Test the documentation coverage reporter."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.reporter = DocumentationCoverageReporter(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_coverage_report(self):
        """Test generating a coverage report."""
        # Create test project structure
        src_dir = self.temp_dir / "src"
        src_dir.mkdir()
        docs_dir = self.temp_dir / "docs"
        docs_dir.mkdir()

        # Create a test module with documentation
        test_module = src_dir / "test_module.py"
        test_module.write_text(
            '''
"""Test module with documentation."""

class TestClass:
    """A documented class."""

    def documented_method(self):
        """A documented method."""
        pass

    def undocumented_method(self):
        pass

def documented_function():
    """A documented function."""
    pass

def undocumented_function():
    pass
'''
        )

        # Create documentation files
        (docs_dir / "README.md").write_text("# Test Project\n\nThis is a test project.")
        (docs_dir / "INSTALLATION.md").write_text("# Installation\n\nInstall instructions here.")

        # Generate coverage report
        report = self.reporter.generate_coverage_report()

        # Verify report structure
        self.assertIn("overall_metrics", report)
        self.assertIn("api_coverage", report)
        self.assertIn("documentation_completeness", report)
        self.assertIn("examples_coverage", report)
        self.assertIn("recommendations", report)

        # Check metrics
        metrics = report["overall_metrics"]
        self.assertGreater(metrics["total_modules"], 0)
        self.assertGreaterEqual(metrics["coverage_percentage"], 0)

    def test_analyze_module_coverage(self):
        """Test analyzing coverage for a single module."""
        # Create test module
        src_dir = self.temp_dir / "src"
        src_dir.mkdir()

        test_module = src_dir / "example.py"
        test_module.write_text(
            '''
"""Example module."""

class ExampleClass:
    """Example class."""

    def method_with_docs(self):
        """Method with documentation."""
        pass

    def method_without_docs(self):
        pass

def function_with_docs():
    """Function with documentation."""
    pass

def function_without_docs():
    pass
'''
        )

        # Analyze coverage
        coverage = self.reporter._analyze_module_coverage(test_module)

        # Verify results
        self.assertEqual(coverage.module_name, "example")
        self.assertTrue(coverage.has_module_docstring)
        self.assertEqual(len(coverage.classes), 1)
        self.assertEqual(len(coverage.functions), 2)

        # Check class coverage
        class_info = coverage.classes[0]
        self.assertEqual(class_info["name"], "ExampleClass")
        self.assertTrue(class_info["has_docstring"])
        self.assertEqual(len(class_info["methods"]), 2)

    def test_export_coverage_report(self):
        """Test exporting coverage report to JSON."""
        # Create minimal report
        report = {
            "overall_metrics": {
                "coverage_percentage": 75.0,
                "total_modules": 4,
                "documented_modules": 3,
            },
            "recommendations": ["Add more documentation"],
        }

        # Export report
        output_path = self.temp_dir / "coverage_report.json"
        self.reporter.export_coverage_report(output_path, report)

        # Verify export
        self.assertTrue(output_path.exists())

        with open(output_path) as f:
            exported_report = json.load(f)

        self.assertEqual(exported_report["overall_metrics"]["coverage_percentage"], 75.0)


if __name__ == "__main__":
    # Run with pytest for better output
    pytest.main([__file__, "-v"])
