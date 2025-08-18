#!/usr/bin/env python3
"""
Font Management Test Runner

This script provides a comprehensive test runner for the Font Management System
with configurable output directories and detailed reporting capabilities.

Usage:
    python tests/run_font_tests.py [options]

Examples:
    # Run all tests with default output
    python tests/run_font_tests.py

    # Run tests with custom output directory
    python tests/run_font_tests.py --output-dir /tmp/font_tests

    # Run specific test suite with HTML reports
    python tests/run_font_tests.py --suite font_manager --report-format html

    # Run tests with coverage reporting
    python tests/run_font_tests.py --coverage --output-dir ./test_results
"""

import argparse
import os
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path

# Import test configuration and settings
from pdfrebuilder.settings import configure_output_directories
from tests.config import configure_test_output, generate_test_report, get_test_output_dir

# Import test suites
from ..font.test_font_manager import (
    TestFontCoverage,
    TestFontDiscovery,
    TestFontManagerIntegration,
    TestFontRegistration,
    TestGoogleFontsIntegration,
)
from ..font.test_font_substitution import TestFontFallbackChain, TestFontSubstitutionEngine
from ..font.test_google_fonts_integration import TestGoogleFontsAPI, TestGoogleFontsIntegrationEdgeCases

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class FontTestRunner:
    """Comprehensive test runner for font management tests"""

    def __init__(self, output_dir=None, report_format="json", verbose=True):
        self.output_dir = output_dir or os.path.join(".", "tests", "output")
        self.report_format = report_format
        self.verbose = verbose
        self.test_results = {}

        # Configure output directories
        if output_dir:
            configure_output_directories(base_dir=output_dir)
            configure_test_output(os.path.join(output_dir, "tests"))
        else:
            configure_test_output(self.output_dir)

    def create_test_suite(self, suite_name="all"):
        """Create a test suite based on the specified name"""
        suite = unittest.TestSuite()

        if suite_name in ["all", "font_manager"]:
            suite.addTest(unittest.makeSuite(TestFontDiscovery))
            suite.addTest(unittest.makeSuite(TestFontCoverage))
            suite.addTest(unittest.makeSuite(TestFontRegistration))
            suite.addTest(unittest.makeSuite(TestGoogleFontsIntegration))
            suite.addTest(unittest.makeSuite(TestFontManagerIntegration))

        if suite_name in ["all", "font_substitution"]:
            suite.addTest(unittest.makeSuite(TestFontSubstitutionEngine))
            suite.addTest(unittest.makeSuite(TestFontFallbackChain))

        if suite_name in ["all", "google_fonts"]:
            suite.addTest(unittest.makeSuite(TestGoogleFontsAPI))
            suite.addTest(unittest.makeSuite(TestGoogleFontsIntegrationEdgeCases))

        return suite

    def run_tests(self, suite_name="all", coverage=False):
        """Run the specified test suite with optional coverage"""
        print("🚀 Starting Font Management Test Suite")
        print(f"📁 Output directory: {get_test_output_dir()}")
        print(f"📊 Report format: {self.report_format}")
        print(f"🧪 Test suite: {suite_name}")
        print("=" * 80)

        start_time = time.time()

        # Set up coverage if requested
        cov = None
        if coverage:
            try:
                import coverage

                cov = coverage.Coverage(source=["src"])
                cov.start()
                print("📈 Coverage tracking enabled")
            except ImportError:
                print("⚠️  Coverage package not available, skipping coverage tracking")

        # Create and run test suite
        suite = self.create_test_suite(suite_name)
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1, stream=sys.stdout, buffer=True)

        result = runner.run(suite)

        # Stop coverage and generate report
        if cov:
            cov.stop()
            cov.save()

            # Generate coverage report
            coverage_dir = os.path.join(get_test_output_dir(), "coverage")
            os.makedirs(coverage_dir, exist_ok=True)

            # HTML coverage report
            cov.html_report(directory=coverage_dir)
            print(f"📈 Coverage HTML report: {coverage_dir}/index.html")

            # Console coverage report
            print("\n" + "=" * 80)
            print("COVERAGE REPORT")
            print("=" * 80)
            cov.report()

        end_time = time.time()
        duration = end_time - start_time

        # Collect test results
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "suite_name": suite_name,
            "duration": duration,
            "total_tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(getattr(result, "skipped", [])),
            "success_rate": (
                ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
                if result.testsRun > 0
                else 0
            ),
            "failures": [{"test": str(test), "error": error} for test, error in result.failures],
            "errors": [{"test": str(test), "error": error} for test, error in result.errors],  # noqa: F601
            "output_directory": get_test_output_dir(),
            "coverage_enabled": coverage and cov is not None,
        }

        # Generate test report
        report_file = generate_test_report(
            f"font_tests_{suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            self.test_results,
            self.report_format,
        )

        # Print summary
        self._print_summary(result, duration, report_file)

        return result.wasSuccessful()

    def _print_summary(self, result, duration, report_file):
        """Print a detailed test summary"""
        print("\n" + "=" * 80)
        print("FONT MANAGEMENT TEST SUMMARY")
        print("=" * 80)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🧪 Tests run: {result.testsRun}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"💥 Errors: {self.test_results['errors']}")
        print(f"⏭️  Skipped: {self.test_results['skipped']}")
        print(f"📊 Success rate: {self.test_results['success_rate']:.1f}%")
        print(f"📁 Output directory: {get_test_output_dir()}")
        print(f"📄 Test report: {report_file}")

        if result.failures:
            print(f"\n❌ FAILURES ({len(result.failures)}):")
            for test, _traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print(f"\n💥 ERRORS ({len(result.errors)}):")
            for test, _traceback in result.errors:
                print(f"  - {test}")

        print("=" * 80)

        if result.wasSuccessful():
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the report for details.")


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(
        description="Font Management Test Runner with configurable output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run all tests with default output
  %(prog)s --output-dir /tmp/font_tests       # Custom output directory
  %(prog)s --suite font_manager               # Run specific test suite
  %(prog)s --report-format html --coverage    # HTML reports with coverage
  %(prog)s --quiet --suite google_fonts       # Quiet mode, specific suite
        """,
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help="Base output directory for test results and reports (default: ./tests/output)",
    )

    parser.add_argument(
        "--suite",
        choices=["all", "font_manager", "font_substitution", "google_fonts"],
        default="all",
        help="Test suite to run (default: all)",
    )

    parser.add_argument(
        "--report-format",
        choices=["json", "html", "txt"],
        default="json",
        help="Format for test reports (default: json)",
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Enable code coverage reporting (requires coverage package)",
    )

    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")

    parser.add_argument("--list-tests", action="store_true", help="List available test suites and exit")

    args = parser.parse_args()

    if args.list_tests:
        print("Available test suites:")
        print("  all              - Run all font management tests")
        print("  font_manager     - Core font management functionality")
        print("  font_substitution - Font substitution and fallback")
        print("  google_fonts     - Google Fonts integration")
        return 0

    # Create and run test runner
    runner = FontTestRunner(
        output_dir=args.output_dir,
        report_format=args.report_format,
        verbose=not args.quiet,
    )

    success = runner.run_tests(suite_name=args.suite, coverage=args.coverage)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
