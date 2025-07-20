#!/usr/bin/env python3
"""
Migration Validation Script

Comprehensive validation script to test the migration from src/ to src/pdfrebuilder/
structure. Tests imports, CLI functionality, examples, and package installation.
"""

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path


class MigrationValidator:
    """Validates the project structure migration."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {
            "import_tests": [],
            "cli_tests": [],
            "example_tests": [],
            "package_tests": [],
            "overall_success": False,
        }

    def test_import_resolution(self) -> bool:
        """Test that all imports resolve correctly."""
        print("🔍 Testing import resolution...")

        success = True
        test_imports = [
            "pdfrebuilder",
            "pdfrebuilder.cli",
            "pdfrebuilder.settings",
            "pdfrebuilder.core.compare_pdfs_visual",
            "pdfrebuilder.core.generate_debug_pdf_layers",
            "pdfrebuilder.core.pdf_engine",
            "pdfrebuilder.core.recreate_pdf_from_config",
            "pdfrebuilder.core.render",
            "pdfrebuilder.engine.document_parser",
            "pdfrebuilder.models.universal_idm",
            "pdfrebuilder.config.manager",
            "pdfrebuilder.tools.generic",
            "pdfrebuilder.utils.directory_utils",
            "pdfrebuilder.security.path_utils",
            "pdfrebuilder.font.font_validator",
        ]

        for module_name in test_imports:
            try:
                # Try to import the module
                importlib.import_module(module_name)
                self.results["import_tests"].append({"module": module_name, "status": "success", "error": None})
                print(f"  ✅ {module_name}")
            except ImportError as e:
                self.results["import_tests"].append({"module": module_name, "status": "failed", "error": str(e)})
                print(f"  ❌ {module_name}: {e}")
                success = False
            except Exception as e:
                self.results["import_tests"].append({"module": module_name, "status": "error", "error": str(e)})
                print(f"  ⚠️  {module_name}: {e}")
                success = False

        return success

    def test_cli_functionality(self) -> bool:
        """Test CLI commands work correctly."""
        print("🖥️  Testing CLI functionality...")

        success = True
        cli_tests = [
            ["python", "-m", "pdfrebuilder.cli", "--help"],
            ["python", "-m", "pdfrebuilder.cli", "--show-config"],
            ["python", "-m", "pdfrebuilder.cli", "--generate-config"],
        ]

        for cmd in cli_tests:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root,
                )

                if result.returncode == 0:
                    self.results["cli_tests"].append({"command": " ".join(cmd), "status": "success", "error": None})
                    print(f"  ✅ {' '.join(cmd)}")
                else:
                    self.results["cli_tests"].append(
                        {
                            "command": " ".join(cmd),
                            "status": "failed",
                            "error": result.stderr,
                        }
                    )
                    print(f"  ❌ {' '.join(cmd)}: {result.stderr}")
                    success = False

            except subprocess.TimeoutExpired:
                self.results["cli_tests"].append(
                    {
                        "command": " ".join(cmd),
                        "status": "timeout",
                        "error": "Command timed out",
                    }
                )
                print(f"  ⏰ {' '.join(cmd)}: Timeout")
                success = False
            except Exception as e:
                self.results["cli_tests"].append({"command": " ".join(cmd), "status": "error", "error": str(e)})
                print(f"  ⚠️  {' '.join(cmd)}: {e}")
                success = False

        return success

    def test_examples(self) -> bool:
        """Test that examples can be imported and run."""
        print("📚 Testing examples...")

        success = True
        examples_dir = self.project_root / "examples"

        if not examples_dir.exists():
            print("  ⚠️  Examples directory not found")
            return True  # Not a failure if examples don't exist

        # Test key example files
        example_files = [
            "comprehensive_example.py",
            "pdf_processing_examples.py",
            "batch_processing_examples.py",
        ]

        for example_file in example_files:
            example_path = examples_dir / example_file
            if not example_path.exists():
                continue

            try:
                # Try to compile the example (syntax check)
                with open(example_path) as f:
                    content = f.read()

                compile(content, str(example_path), "exec")

                self.results["example_tests"].append({"file": str(example_path), "status": "success", "error": None})
                print(f"  ✅ {example_file}")

            except SyntaxError as e:
                self.results["example_tests"].append(
                    {
                        "file": str(example_path),
                        "status": "syntax_error",
                        "error": str(e),
                    }
                )
                print(f"  ❌ {example_file}: Syntax error - {e}")
                success = False
            except Exception as e:
                self.results["example_tests"].append({"file": str(example_path), "status": "error", "error": str(e)})
                print(f"  ⚠️  {example_file}: {e}")
                success = False

        return success

    def test_package_structure(self) -> bool:
        """Test that the package structure is correct."""
        print("📦 Testing package structure...")

        success = True
        required_files = [
            "src/pdfrebuilder/__init__.py",
            "src/pdfrebuilder/cli.py",
            "src/pdfrebuilder/settings.py",
            "src/pdfrebuilder/core/__init__.py",
            "src/pdfrebuilder/engine/__init__.py",
            "src/pdfrebuilder/models/__init__.py",
            "src/pdfrebuilder/config/__init__.py",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.results["package_tests"].append({"file": file_path, "status": "exists", "error": None})
                print(f"  ✅ {file_path}")
            else:
                self.results["package_tests"].append(
                    {
                        "file": file_path,
                        "status": "missing",
                        "error": "File does not exist",
                    }
                )
                print(f"  ❌ {file_path}: Missing")
                success = False

        # Test that old structure is cleaned up
        old_files_to_check = [
            "src/cli.py",
            "src/compare_pdfs_visual.py",
            "src/generate_debug_pdf_layers.py",
            "src/pdf_engine.py",
            "src/recreate_pdf_from_config.py",
            "src/render.py",
        ]

        for file_path in old_files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.results["package_tests"].append(
                    {
                        "file": file_path,
                        "status": "should_be_removed",
                        "error": "Old file still exists",
                    }
                )
                print(f"  ⚠️  {file_path}: Should be removed (old structure)")
                # Don't mark as failure since this might be intentional during migration

        return success

    def test_public_api(self) -> bool:
        """Test that the public API is accessible."""
        print("🔌 Testing public API...")

        success = True

        try:
            # Test main package import
            import pdfrebuilder

            # Test that key functions are available
            expected_attributes = ["cli_main", "__version__"]

            for attr in expected_attributes:
                if hasattr(pdfrebuilder, attr):
                    print(f"  ✅ pdfrebuilder.{attr}")
                else:
                    print(f"  ❌ pdfrebuilder.{attr}: Not available")
                    success = False

        except ImportError as e:
            print(f"  ❌ Cannot import pdfrebuilder: {e}")
            success = False
        except Exception as e:
            print(f"  ⚠️  Error testing public API: {e}")
            success = False

        return success

    def run_full_validation(self) -> dict:
        """Run all validation tests."""
        print("🚀 Running full migration validation...\n")

        tests = [
            ("Package Structure", self.test_package_structure),
            ("Import Resolution", self.test_import_resolution),
            ("Public API", self.test_public_api),
            ("CLI Functionality", self.test_cli_functionality),
            ("Examples", self.test_examples),
        ]

        all_passed = True

        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                result = test_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ❌ Test failed with exception: {e}")
                all_passed = False

        self.results["overall_success"] = all_passed

        print(f"\n{'=' * 50}")
        print(f"🎯 Overall Result: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        print(f"{'=' * 50}")

        return self.results

    def save_results(self, output_file: str = "migration_validation_results.json"):
        """Save validation results to file."""
        output_path = self.project_root / output_file
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to: {output_path}")


def main():
    """Main function to run migration validation."""
    parser = argparse.ArgumentParser(description="Validate project structure migration")
    parser.add_argument(
        "--output",
        default="migration_validation_results.json",
        help="Output file for results",
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    validator = MigrationValidator(args.project_root)
    results = validator.run_full_validation()
    validator.save_results(args.output)

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)


if __name__ == "__main__":
    main()
