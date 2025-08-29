"""
Font Management System Test Suite

This module provides a comprehensive test suite for the Font Management System,
demonstrating all the key functionality and integration points.

Test Coverage:
- FontManager functionality (via font_utils.py)
- Font discovery and scanning
- Font substitution and fallback mechanisms
- Google Fonts integration
- Glyph coverage analysis
- Error handling and edge cases

Output Configuration:
- All test outputs can be configured via TEST_OUTPUT_DIR environment variable
- Default output directory: tests/resources/ (configurable)
- CLI support for specifying custom output directories
"""

import argparse
import sys
import unittest

# Import test configuration
from tests.config import cleanup_all_test_output, configure_test_output, get_test_output_dir
from tests.font.test_font_cache_integration import (
    TestCacheIntegrationPerformance,
    TestFontDownloadCache,
    TestFontRegistrationCache,
    TestFontValidatorCache,
)

# Import new integration test classes
from tests.font.test_font_integration_workflows import (
    TestEndToEndFontWorkflow,
    TestFontCachePerformanceWorkflow,
    TestFontDiscoveryWorkflow,
    TestFontSubstitutionWorkflow,
    TestFontValidationIntegrationWorkflow,
)

# Import all test classes from the individual test modules
from tests.font.test_font_manager import (
    TestFontCoverage,
    TestFontDiscovery,
    TestFontManagerIntegration,
    TestFontRegistration,
    TestGoogleFontsIntegration,
)
from tests.font.test_font_substitution import TestFontFallbackChain, TestFontSubstitutionEngine
from tests.font.test_google_fonts_integration import TestGoogleFontsAPI, TestGoogleFontsIntegrationEdgeCases


class FontManagementTestSuite:
    """
    Comprehensive test suite for the Font Management System

    This class provides a unified interface to run all font management tests
    and provides detailed reporting on test coverage and results.
    """

    @staticmethod
    def create_test_suite():
        """Create a comprehensive test suite for font management"""
        suite = unittest.TestSuite()

        # Font Discovery Tests
        suite.addTest(unittest.makeSuite(TestFontDiscovery))

        # Font Coverage Tests
        suite.addTest(unittest.makeSuite(TestFontCoverage))

        # Font Registration Tests
        suite.addTest(unittest.makeSuite(TestFontRegistration))

        # Font Substitution Tests
        suite.addTest(unittest.makeSuite(TestFontSubstitutionEngine))

        # Font Fallback Tests
        suite.addTest(unittest.makeSuite(TestFontFallbackChain))

        # Google Fonts Integration Tests
        suite.addTest(unittest.makeSuite(TestGoogleFontsAPI))
        suite.addTest(unittest.makeSuite(TestGoogleFontsIntegration))
        suite.addTest(unittest.makeSuite(TestGoogleFontsIntegrationEdgeCases))

        # Font Manager Integration Tests
        suite.addTest(unittest.makeSuite(TestFontManagerIntegration))

        # New Integration Tests
        # Font workflow integration tests
        suite.addTest(unittest.makeSuite(TestFontDiscoveryWorkflow))
        suite.addTest(unittest.makeSuite(TestFontSubstitutionWorkflow))
        suite.addTest(unittest.makeSuite(TestFontValidationIntegrationWorkflow))
        suite.addTest(unittest.makeSuite(TestFontCachePerformanceWorkflow))
        suite.addTest(unittest.makeSuite(TestEndToEndFontWorkflow))

        # Font cache integration tests
        suite.addTest(unittest.makeSuite(TestFontRegistrationCache))
        suite.addTest(unittest.makeSuite(TestFontDownloadCache))
        suite.addTest(unittest.makeSuite(TestFontValidatorCache))
        suite.addTest(unittest.makeSuite(TestCacheIntegrationPerformance))

        return suite

    @staticmethod
    def run_all_tests(verbosity=2, output_dir=None):
        """Run all font management tests with detailed output"""
        # Configure output directory if specified
        if output_dir:
            configure_test_output(output_dir)

        # Print configuration info
        current_output_dir = get_test_output_dir()
        print(f"Test output directory: {current_output_dir}")

        suite = FontManagementTestSuite.create_test_suite()
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)

        # Print summary
        print("\n" + "=" * 80)
        print("FONT MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 80)
        print(f"Test output directory: {current_output_dir}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(
            f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
        )

        if result.failures:
            print(f"\nFAILURES ({len(result.failures)}):")
            for test, _traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print(f"\nERRORS ({len(result.errors)}):")
            for test, _traceback in result.errors:
                print(f"  - {test}")

        print("=" * 80)

        return result.wasSuccessful()


def parse_arguments():
    """Parse command line arguments for test configuration"""
    parser = argparse.ArgumentParser(
        description="Font Management System Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tests.test_font_management_suite
  python -m tests.test_font_management_suite --output-dir /tmp/test_output
  python -m tests.test_font_management_suite --output-dir ./custom_output --verbose
  python -m tests.test_font_management_suite --clean-output

Environment Variables:
  TEST_OUTPUT_DIR    Set default output directory for all test outputs
        """,
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        help="Directory for test outputs (default: from tests/config.py or TEST_OUTPUT_DIR env var)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose test output")

    parser.add_argument(
        "--clean-output",
        "-c",
        action="store_true",
        help="Clean output directory before running tests",
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output (only show summary)")

    return parser.parse_args()


def run_font_management_tests():
    """Entry point for running font management tests with CLI support"""
    args = parse_arguments()

    # Configure output directory
    if args.output_dir:
        configure_test_output(args.output_dir)

    # Clean output directory if requested
    if args.clean_output:
        print("Cleaning test output directory...")
        cleanup_all_test_output()

    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    if not args.quiet:
        print("Running Font Management System Test Suite...")
        print("This comprehensive suite tests all aspects of font management:")
        print("- Font discovery and scanning")
        print("- Font registration and caching")
        print("- Glyph coverage analysis")
        print("- Font substitution and fallback")
        print("- Google Fonts integration")
        print("- Error handling and edge cases")
        print("- End-to-end workflow integration")
        print("- Cache performance and behavior")
        print("- Document processing integration")
        print("- Validation system integration")
        print("\n" + "=" * 80)

    success = FontManagementTestSuite.run_all_tests(verbosity=verbosity, output_dir=args.output_dir)

    if success:
        if not args.quiet:
            print("✅ All font management tests passed!")
        return 0
    else:
        if not args.quiet:
            print("❌ Some font management tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_font_management_tests())
