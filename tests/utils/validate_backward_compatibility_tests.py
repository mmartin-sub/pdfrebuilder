#!/usr/bin/env python3
"""
Validation Script for Backward Compatibility Tests

This script validates that the backward compatibility test suite is working correctly
by running a subset of tests and verifying the expected behavior.

Usage:
    python tests/validate_backward_compatibility_tests.py
"""

import os
import sys
import tempfile
import traceback

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")

    try:
        from pdfrebuilder.engine.validation_report import (
            ValidationReport,
            ValidationResult,
            secure_xml_parse,
            secure_xml_pretty_print,
        )

        print("✓ Core imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic validation report functionality"""
    print("Testing basic functionality...")

    try:
        from pdfrebuilder.engine.validation_report import ValidationReport, ValidationResult

        # Create a simple validation result
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="test.pdf",
            generated_path="test_gen.pdf",
        )

        # Create a validation report
        report = ValidationReport("test_document", [result])

        # Test basic properties
        assert report.document_name == "test_document"
        assert report.result_count == 1
        assert report.pass_count == 1
        assert report.fail_count == 0
        assert report.overall_passed is True

        print("✓ Basic functionality test passed")
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_xml_generation():
    """Test XML generation functionality"""
    print("Testing XML generation...")

    try:
        from pdfrebuilder.engine.validation_report import ValidationReport, ValidationResult, secure_xml_parse

        # Create test data
        result = ValidationResult(
            passed=False,
            ssim_score=0.75,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            failure_analysis={"failure_reason": "test_failure", "severity": "medium"},
        )

        report = ValidationReport("xml_test_document", [result])

        # Test JUnit XML generation
        with tempfile.TemporaryDirectory() as temp_dir:
            junit_path = os.path.join(temp_dir, "test_junit.xml")
            report.generate_junit_report(junit_path)

            # Verify file exists
            assert os.path.exists(junit_path), "JUnit XML file not created"

            # Verify content can be parsed
            with open(junit_path, encoding="utf-8") as f:
                xml_content = f.read()

            parsed_xml = secure_xml_parse(xml_content)
            assert parsed_xml.tag == "testsuites"

            # Verify structure
            testsuites = parsed_xml.findall("testsuite")
            assert len(testsuites) == 1

            testsuite = testsuites[0]
            assert testsuite.get("name") == "xml_test_document"

            testcases = testsuite.findall("testcase")
            assert len(testcases) == 1

            # Verify failure information
            failures = testcases[0].findall("failure")
            assert len(failures) == 1

            failure = failures[0]
            assert failure.get("type") == "test_failure"

        print("✓ XML generation test passed")
        return True
    except Exception as e:
        print(f"✗ XML generation test failed: {e}")
        traceback.print_exc()
        return False


def test_html_generation():
    """Test HTML generation functionality"""
    print("Testing HTML generation...")

    try:
        from pdfrebuilder.engine.validation_report import ValidationReport, ValidationResult

        # Create test data
        result = ValidationResult(
            passed=True,
            ssim_score=0.92,
            threshold=0.9,
            original_path="test.pdf",
            generated_path="test_gen.pdf",
        )

        report = ValidationReport("html_test_document", [result])

        # Test HTML generation
        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = os.path.join(temp_dir, "test_report.html")
            report.generate_html_report(html_path)

            # Verify file exists
            assert os.path.exists(html_path), "HTML report file not created"

            # Verify basic HTML structure
            with open(html_path, encoding="utf-8") as f:
                html_content = f.read()

            assert "<!DOCTYPE html>" in html_content
            assert "<title>Validation Report: html_test_document</title>" in html_content
            assert "<h1>Validation Report: html_test_document</h1>" in html_content
            assert 'class="passed">PASSED</span>' in html_content

        print("✓ HTML generation test passed")
        return True
    except Exception as e:
        print(f"✗ HTML generation test failed: {e}")
        traceback.print_exc()
        return False


def test_json_serialization():
    """Test JSON serialization functionality"""
    print("Testing JSON serialization...")

    try:
        import json

        from pdfrebuilder.engine.validation_report import ValidationReport, ValidationResult

        # Create test data with various data types
        result = ValidationResult(
            passed=False,
            ssim_score=0.85,
            threshold=0.9,
            original_path="test.pdf",
            generated_path="test_gen.pdf",
            details={"test_key": "test_value", "number": 42},
            additional_metrics={"metric1": 0.8, "metric2": 0.9},
        )

        report = ValidationReport(
            "json_test_document",
            [result],
            metadata={"version": "1.0", "test_mode": True},
        )

        # Test JSON serialization
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = os.path.join(temp_dir, "test_report.json")
            report.save_report(json_path)

            # Verify file exists
            assert os.path.exists(json_path), "JSON report file not created"

            # Verify JSON can be loaded
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            # Verify structure
            assert data["document_name"] == "json_test_document"
            assert data["result_count"] == 1
            assert data["pass_count"] == 0
            assert data["fail_count"] == 1
            assert data["overall_passed"] is False

            # Verify result data
            result_data = data["results"][0]
            assert result_data["passed"] is False
            assert result_data["ssim_score"] == 0.85
            assert result_data["details"]["test_key"] == "test_value"
            assert result_data["additional_metrics"]["metric1"] == 0.8

        print("✓ JSON serialization test passed")
        return True
    except Exception as e:
        print(f"✗ JSON serialization test failed: {e}")
        traceback.print_exc()
        return False


def test_secure_xml_functions():
    """Test secure XML functions"""
    print("Testing secure XML functions...")

    try:
        from xml.etree.ElementTree import Element, SubElement

        from pdfrebuilder.engine.validation_report import secure_xml_parse, secure_xml_pretty_print

        # Test secure XML parsing
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Test Suite">
    <testsuite name="test_suite" tests="1">
        <testcase name="test1" classname="TestClass">
            <system-out>Test output</system-out>
        </testcase>
    </testsuite>
</testsuites>"""

        parsed_xml = secure_xml_parse(xml_content)
        assert parsed_xml.tag == "testsuites"
        assert parsed_xml.get("name") == "Test Suite"

        # Test secure XML pretty printing
        root = Element("testsuites")
        root.set("name", "Pretty Print Test")

        testsuite = SubElement(root, "testsuite")
        testsuite.set("name", "test_suite")

        testcase = SubElement(testsuite, "testcase")
        testcase.set("name", "test1")

        pretty_xml = secure_xml_pretty_print(root)
        assert isinstance(pretty_xml, str)
        assert "<?xml version=" in pretty_xml
        assert 'name="Pretty Print Test"' in pretty_xml

        print("✓ Secure XML functions test passed")
        return True
    except Exception as e:
        print(f"✗ Secure XML functions test failed: {e}")
        traceback.print_exc()
        return False


def test_backward_compatibility_runner():
    """Test that the backward compatibility test runner can be imported and initialized"""
    print("Testing backward compatibility test runner...")

    try:
        from tests.run_backward_compatibility_tests import BackwardCompatibilityTester

        # Test initialization
        tester = BackwardCompatibilityTester(verbose=False)
        assert tester.verbose is False
        assert tester.test_results == []

        # Test reference report creation
        report = tester.create_reference_report()
        assert report.document_name == "backward_compatibility_test"
        assert len(report.results) == 2
        assert report.result_count == 2
        assert report.pass_count == 1
        assert report.fail_count == 1

        print("✓ Backward compatibility test runner test passed")
        return True
    except Exception as e:
        print(f"✗ Backward compatibility test runner test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("Validating Backward Compatibility Test Suite")
    print("=" * 50)

    tests = [
        test_imports,
        test_basic_functionality,
        test_xml_generation,
        test_html_generation,
        test_json_serialization,
        test_secure_xml_functions,
        test_backward_compatibility_runner,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            failed += 1
        print()  # Add blank line between tests

    print("=" * 50)
    print(f"Validation Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✓ All validation tests passed! The backward compatibility test suite is ready to use.")
        return 0
    else:
        print("✗ Some validation tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
