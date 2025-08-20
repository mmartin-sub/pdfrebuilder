#!/usr/bin/env python3
"""
Comprehensive documentation testing runner.

This script runs all documentation tests including validation, coverage,
API reference checking, and comprehensive testing framework.
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import security utilities
from security.subprocess_utils import SecureSubprocessRunner, SecurityError

from docs.api_validator import APIReferenceValidator
from docs.coverage_reporter import DocumentationCoverageReporter
from docs.validation import DocumentationValidator, ValidationStatus

# Removed _validate_command_components - now handled by SecureSubprocessRunner


class DocumentationTestRunner:
    """Comprehensive documentation test runner."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the test runner."""
        self.project_root = project_root or Path.cwd()
        self.validator = DocumentationValidator(self.project_root)
        self.coverage_reporter = DocumentationCoverageReporter(self.project_root)
        self.api_validator = APIReferenceValidator(self.project_root)
        self.subprocess_runner = SecureSubprocessRunner(base_path=self.project_root)

        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "test_results": {},
        }

    def run_all_tests(self, verbose: bool = False) -> dict:
        """Run all documentation tests."""
        print("🚀 Starting comprehensive documentation testing...")
        print("=" * 70)

        start_time = time.time()

        # Run individual test suites
        test_suites = [
            ("pytest_tests", self.run_pytest_tests),
            ("code_examples", self.run_code_example_tests),
            ("api_references", self.run_api_reference_tests),
            ("configuration", self.run_configuration_tests),
            ("coverage_analysis", self.run_coverage_analysis),
            # ("comprehensive_framework", self.run_comprehensive_framework),  # Moved to WIP
        ]

        for suite_name, test_func in test_suites:
            print(f"\n📋 Running {suite_name.replace('_', ' ').title()}...")
            try:
                suite_results = test_func(verbose)
                self.results["test_results"][suite_name] = suite_results
                self._print_suite_summary(suite_name, suite_results)
            except Exception as e:
                print(f"❌ Error running {suite_name}: {e}")
                self.results["test_results"][suite_name] = {
                    "status": "error",
                    "error": str(e),
                }

        end_time = time.time()
        self.results["execution_time"] = end_time - start_time

        # Print overall summary
        self._print_overall_summary()

        return self.results

    def run_pytest_tests(self, verbose: bool = False) -> dict:
        """Run pytest-based documentation tests."""
        test_files = [
            "tests/test_documentation_validation.py",
            "tests/test_documentation_builder.py",
            "tests/test_comprehensive_documentation.py",
            "tests/test_api_validator.py",
        ]

        results = {"passed": 0, "failed": 0, "errors": 0, "test_files": []}

        for test_file in test_files:
            if not Path(test_file).exists():
                print(f"  ⚠️  Test file not found: {test_file}")
                continue

            try:
                cmd = (
                    [sys.executable, "-m", "pytest", test_file, "-v"]
                    if verbose
                    else [sys.executable, "-m", "pytest", test_file, "-q"]
                )

                result = self.subprocess_runner.run(cmd, capture_output=True, text=True, timeout=300)

                file_result = {
                    "file": test_file,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

                if result.returncode == 0:
                    results["passed"] += 1
                    print(f"  ✅ {test_file}")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_file}")
                    if verbose:
                        print(f"    Error: {result.stderr}")

                results["test_files"].append(file_result)

            except SecurityError as e:
                results["errors"] += 1
                print(f"  🔒 {test_file} (security error: {e})")
            except Exception as e:
                results["errors"] += 1
                if "timeout" in str(e).lower():
                    print(f"  ⏰ {test_file} (timeout)")
                else:
                    print(f"  ❌ {test_file} (error: {e})")

        return results

    def run_code_example_tests(self, verbose: bool = False) -> dict:
        """Run code example validation tests."""
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return {"status": "skipped", "reason": "docs directory not found"}

        md_files = list(docs_dir.rglob("*.md"))
        results = {
            "total_files": len(md_files),
            "total_examples": 0,
            "passed": 0,
            "failed": 0,
            "files": [],
        }

        for md_file in md_files:
            try:
                file_results = self.validator.validate_code_examples(md_file)

                file_summary = {
                    "file": str(md_file.relative_to(docs_dir)),
                    "examples": len(file_results),
                    "passed": sum(1 for r in file_results if r.status == ValidationStatus.PASSED),
                    "failed": sum(1 for r in file_results if r.status == ValidationStatus.FAILED),
                }

                results["total_examples"] += len(file_results)
                results["passed"] += file_summary["passed"]
                results["failed"] += file_summary["failed"]
                results["files"].append(file_summary)

                if verbose and file_summary["failed"] > 0:
                    print(f"    ❌ {file_summary['file']}: {file_summary['failed']} failed examples")

            except Exception as e:
                if verbose:
                    print(f"    ❌ Error processing {md_file}: {e}")

        return results

    def run_api_reference_tests(self, verbose: bool = False) -> dict:
        """Run API reference validation tests."""
        try:
            validation_results = self.api_validator.validate_all_api_references()

            results = {
                "total_references": len(validation_results),
                "passed": sum(1 for r in validation_results if r.status == ValidationStatus.PASSED),
                "failed": sum(1 for r in validation_results if r.status == ValidationStatus.FAILED),
                "warnings": sum(1 for r in validation_results if r.status == ValidationStatus.WARNING),
                "skipped": sum(1 for r in validation_results if r.status == ValidationStatus.SKIPPED),
            }

            # Get API coverage report
            coverage_report = self.api_validator.get_api_coverage_report()
            results["api_coverage"] = coverage_report

            if verbose:
                failed_results = [r for r in validation_results if r.status == ValidationStatus.FAILED]
                for result in failed_results[:5]:  # Show first 5 failures
                    print(f"    ❌ {result.message} ({result.file_path}:{result.line_number})")

            return results

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_configuration_tests(self, verbose: bool = False) -> dict:
        """Run configuration example validation tests."""
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return {"status": "skipped", "reason": "docs directory not found"}

        md_files = list(docs_dir.rglob("*.md"))
        results = {
            "total_files": len(md_files),
            "total_configs": 0,
            "passed": 0,
            "failed": 0,
        }

        for md_file in md_files:
            try:
                file_results = self.validator.validate_configuration_examples(md_file)

                results["total_configs"] += len(file_results)
                results["passed"] += sum(1 for r in file_results if r.status == ValidationStatus.PASSED)
                results["failed"] += sum(1 for r in file_results if r.status == ValidationStatus.FAILED)

            except Exception as e:
                if verbose:
                    print(f"    ❌ Error processing {md_file}: {e}")

        return results

    def run_coverage_analysis(self, verbose: bool = False) -> dict:
        """Run documentation coverage analysis."""
        try:
            coverage_report = self.coverage_reporter.generate_coverage_report()

            if verbose:
                self.coverage_reporter.print_coverage_summary(coverage_report)

            return coverage_report

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_comprehensive_framework(self, verbose: bool = False) -> dict:
        """Run the comprehensive testing framework."""
        try:
            # Use sys.executable to ensure we're using the correct Python interpreter
            cmd = [sys.executable, "scripts/test_docs_framework.py"]
            if verbose:
                cmd.append("--verbose")

            result = self.subprocess_runner.run(cmd, capture_output=True, text=True, timeout=600)

            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "passed" if result.returncode == 0 else "failed",
            }

        except SecurityError as e:
            return {
                "status": "security_error",
                "error": f"Security validation failed: {e}",
            }
        except Exception as e:
            if "timeout" in str(e).lower():
                return {"status": "timeout", "error": "Framework test timed out"}
            return {"status": "error", "error": str(e)}

    def _print_suite_summary(self, suite_name: str, results: dict):
        """Print summary for a test suite."""
        if isinstance(results, dict):
            if "status" in results:
                status = results["status"]
                if status == "error":
                    print(f"  ❌ {suite_name}: Error - {results.get('error', 'Unknown error')}")
                elif status == "skipped":
                    print(f"  ⏭️  {suite_name}: Skipped - {results.get('reason', 'Unknown reason')}")
                elif status == "passed":
                    print(f"  ✅ {suite_name}: Passed")
                elif status == "failed":
                    print(f"  ❌ {suite_name}: Failed")
                else:
                    print(f"  ❓ {suite_name}: {status}")
            elif "passed" in results and "failed" in results:
                total = results.get("passed", 0) + results.get("failed", 0)
                passed = results.get("passed", 0)
                print(f"  📊 {suite_name}: {passed}/{total} passed")
            else:
                print(f"  ✅ {suite_name}: Completed")

    def _print_overall_summary(self):
        """Print overall test summary."""
        print("\n" + "=" * 70)
        print("📊 OVERALL DOCUMENTATION TEST SUMMARY")
        print("=" * 70)

        total_suites = len(self.results["test_results"])
        passed_suites = 0
        failed_suites = 0

        for _suite_name, suite_results in self.results["test_results"].items():
            if isinstance(suite_results, dict):
                if suite_results.get("status") == "passed" or (
                    "failed" in suite_results and suite_results["failed"] == 0
                ):
                    passed_suites += 1
                else:
                    failed_suites += 1

        print(f"📋 Test Suites: {passed_suites}/{total_suites} passed")

        # Coverage summary
        if "coverage_analysis" in self.results["test_results"]:
            coverage = self.results["test_results"]["coverage_analysis"]
            if "overall_metrics" in coverage:
                metrics = coverage["overall_metrics"]
                print(f"📚 Documentation Coverage: {metrics['coverage_percentage']:.1f}%")

        # API reference summary
        if "api_references" in self.results["test_results"]:
            api_results = self.results["test_results"]["api_references"]
            if "total_references" in api_results:
                total_refs = api_results["total_references"]
                passed_refs = api_results.get("passed", 0)
                print(f"🔗 API References: {passed_refs}/{total_refs} valid")

        print(f"⏱️  Execution Time: {self.results['execution_time']:.2f}s")

        # Overall result
        if failed_suites == 0:
            print("\n🎉 ALL DOCUMENTATION TESTS PASSED!")
            return True
        else:
            print(f"\n❌ {failed_suites} test suite(s) failed. See details above.")
            return False

    def export_results(self, output_path: Path):
        """Export test results to JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"📄 Test results exported to: {output_path}")
        except Exception as e:
            print(f"❌ Failed to export results: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive documentation testing runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python scripts/run_documentation_tests.py

  # Run with verbose output
  python scripts/run_documentation_tests.py --verbose

  # Export results to JSON
  python scripts/run_documentation_tests.py --export results.json

  # Run specific test suites
  python scripts/run_documentation_tests.py --pytest-only
  python scripts/run_documentation_tests.py --coverage-only
        """,
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--export", type=Path, help="Export results to JSON file")
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest tests")
    parser.add_argument("--coverage-only", action="store_true", help="Run only coverage analysis")
    parser.add_argument("--api-only", action="store_true", help="Run only API reference tests")

    args = parser.parse_args()

    # Initialize test runner
    runner = DocumentationTestRunner()

    # Run tests based on arguments
    if args.pytest_only:
        results = {"test_results": {"pytest_tests": runner.run_pytest_tests(args.verbose)}}
    elif args.coverage_only:
        results = {"test_results": {"coverage_analysis": runner.run_coverage_analysis(args.verbose)}}
    elif args.api_only:
        results = {"test_results": {"api_references": runner.run_api_reference_tests(args.verbose)}}
    else:
        results = runner.run_all_tests(args.verbose)

    # Export results if requested
    if args.export:
        runner.results = results
        runner.export_results(args.export)

    # Return appropriate exit code
    success = runner._print_overall_summary() if not (args.pytest_only or args.coverage_only or args.api_only) else True
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
