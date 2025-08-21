#!/usr/bin/env python3
"""
Simple test runner for the failing tests.
"""

import os
import sys

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_documentation_builder_tests():
    """Run documentation builder tests."""
    print("Running documentation builder tests...")
    from tests.wip.documentation.test_documentation_builder import TestDocumentationBuilder

    t = TestDocumentationBuilder()
    t.setup_method()

    # Run all test methods (exclude properties)
    test_methods = [method for method in dir(t) if method.startswith("test_") and callable(getattr(t, method))]

    for method_name in test_methods:
        print(f"Running {method_name}...")
        try:
            method = getattr(t, method_name)
            method()
            print(f"✅ {method_name} passed")
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")

    t.teardown_method()
    print("Documentation builder tests completed.")


def run_documentation_validation_tests():
    """Run documentation validation tests."""
    print("Running documentation validation tests...")
    from tests.wip.documentation.test_documentation_validation import TestDocumentationValidator

    t = TestDocumentationValidator()
    t.setup_method()

    # Run all test methods (exclude properties)
    test_methods = [method for method in dir(t) if method.startswith("test_") and callable(getattr(t, method))]

    for method_name in test_methods:
        print(f"Running {method_name}...")
        try:
            method = getattr(t, method_name)
            method()
            print(f"✅ {method_name} passed")
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")

    print("Documentation validation tests completed.")


def run_font_cache_tests():
    """Run font cache integration tests."""
    print("Running font cache integration tests...")
    from tests.font.test_font_cache_integration import (
        TestCacheIntegrationPerformance,
        TestFontDownloadCache,
        TestFontRegistrationCache,
        TestFontValidatorCache,
    )

    test_classes = [
        TestFontRegistrationCache,
        TestFontDownloadCache,
        TestFontValidatorCache,
        TestCacheIntegrationPerformance,
    ]

    for test_class in test_classes:
        print(f"Running {test_class.__name__}...")
        t = test_class()
        t.setUp()

        # Run all test methods (exclude properties)
        test_methods = [method for method in dir(t) if method.startswith("test_") and callable(getattr(t, method))]

        for method_name in test_methods:
            print(f"  Running {method_name}...")
            try:
                method = getattr(t, method_name)
                method()
                print(f"  ✅ {method_name} passed")
            except Exception as e:
                print(f"  ❌ {method_name} failed: {e}")

        t.tearDown()

    print("Font cache integration tests completed.")


def run_e2e_tests():
    """Run E2E PDF regeneration tests."""
    print("Running E2E PDF regeneration tests...")
    from tests.wip.e2e.test_e2e_pdf_regeneration import (
        test_full_pdf_regeneration_pipeline,
        test_generate_debug_pdfs_for_outputs,
    )

    # Create a mock request object for pytest fixtures
    class MockRequest:
        def __init__(self):
            self.config = type("obj", (object,), {})
            self.config.getoption = lambda x: None

    # Create a mock setup fixture
    def mock_setup_e2e_test():
        return None

    print("Running test_full_pdf_regeneration_pipeline...")
    try:
        test_full_pdf_regeneration_pipeline(mock_setup_e2e_test(), MockRequest())
        print("✅ test_full_pdf_regeneration_pipeline passed")
    except Exception as e:
        print(f"❌ test_full_pdf_regeneration_pipeline failed: {e}")

    print("Running test_generate_debug_pdfs_for_outputs...")
    try:
        test_generate_debug_pdfs_for_outputs()
        print("✅ test_generate_debug_pdfs_for_outputs passed")
    except Exception as e:
        print(f"❌ test_generate_debug_pdfs_for_outputs failed: {e}")

    print("E2E PDF regeneration tests completed.")


if __name__ == "__main__":
    print("Running specific failing tests...")

    try:
        run_documentation_builder_tests()
        print()
        run_documentation_validation_tests()
        print()
        run_font_cache_tests()
        print()
        run_e2e_tests()
        print()
        print("All tests completed!")
    except Exception as e:
        print(f"Test runner failed: {e}")
        import traceback

        traceback.print_exc()
