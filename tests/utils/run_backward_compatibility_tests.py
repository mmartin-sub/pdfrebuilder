#!/usr/bin/env python3
"""
Backward Compatibility Test Runner for XML Security Fix

This script runs comprehensive backward compatibility tests to ensure that the XML security fix
maintains backward compatibility across all aspects of the validation report system.

The script validates:
1. XML output format compatibility (JUnit, HTML structure)
2. Function signature compatibility (all existing APIs unchanged)
3. Configuration file compatibility (existing configs work without changes)
4. Performance compatibility (no significant degradation)

Requirements covered: 2.1, 2.2, 2.3, 2.4

Usage:
    python tests/run_backward_compatibility_tests.py [--verbose] [--performance] [--output-dir DIR]

Options:
    --verbose       Enable verbose output with detailed test results
    --performance   Run performance tests (may take longer)
    --output-dir    Directory to save test reports (default: tests/backward_compatibility_reports)
"""

import argparse
import json
import os
import sys
import tempfile
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pdfrebuilder.engine.validation_report import (
    ValidationReport,
    ValidationResult,
    create_validation_report,
    create_validation_result,
    secure_xml_parse,
    secure_xml_pretty_print,
)


class BackwardCompatibilityTester:
    """Main class for running backward compatibility tests"""

    def __init__(self, verbose: bool = False, output_dir: str | None = None):
        self.verbose = verbose
        self.output_dir = output_dir or "tests/backward_compatibility_reports"
        self.test_results = []
        self.start_time = time.time()

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "FAIL"]:
            print(f"[{timestamp}] {level}: {message}")

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        self.log(f"Running test: {test_name}")
        start_time = time.time()

        try:
            test_func()
            duration = time.time() - start_time
            self.test_results.append(
                {
                    "name": test_name,
                    "status": "PASS",
                    "duration": duration,
                    "error": None,
                }
            )
            self.log(f"✓ {test_name} PASSED ({duration:.3f}s)", "PASS")
            return True
        except Exception as e:
            duration = time.time() - start_time
            self.test_results.append(
                {
                    "name": test_name,
                    "status": "FAIL",
                    "duration": duration,
                    "error": str(e),
                }
            )
            self.log(f"✗ {test_name} FAILED: {e}", "FAIL")
            return False

    def create_reference_report(self) -> ValidationReport:
        """Create a reference validation report for testing"""
        results = [
            ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original1.pdf",
                generated_path="generated1.pdf",
            ),
            ValidationResult(
                passed=False,
                ssim_score=0.75,
                threshold=0.9,
                original_path="original2.pdf",
                generated_path="generated2.pdf",
                diff_image_path="diff2.png",
                failure_analysis={
                    "failure_reason": "moderate_visual_difference",
                    "severity": "high",
                    "recommendations": ["Check element positioning"],
                },
            ),
        ]

        return ValidationReport(
            document_name="backward_compatibility_test",
            results=results,
            metadata={
                "version": "1.0",
                "engine": "test",
                "test_type": "backward_compatibility",
            },
        )

    def test_junit_xml_structure(self):
        """Test that JUnit XML structure remains unchanged"""
        report = self.create_reference_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            junit_path = os.path.join(temp_dir, "junit_report.xml")
            report.generate_junit_report(junit_path)

            # Verify file exists
            assert os.path.exists(junit_path), "JUnit XML file was not created"

            # Parse and verify structure
            with open(junit_path, encoding="utf-8") as f:
                xml_content = f.read()

            parsed_xml = secure_xml_parse(xml_content)

            # Verify root structure
            assert parsed_xml.tag == "testsuites", f"Expected root tag 'testsuites', got '{parsed_xml.tag}'"
            assert parsed_xml.get("name") == "Document Validation: backward_compatibility_test"
            assert parsed_xml.get("tests") == "2"
            assert parsed_xml.get("failures") == "1"

            # Verify testsuite structure
            testsuites = parsed_xml.findall("testsuite")
            assert len(testsuites) == 1, f"Expected 1 testsuite, found {len(testsuites)}"

            testsuite = testsuites[0]
            assert testsuite.get("name") == "backward_compatibility_test"
            assert testsuite.get("tests") == "2"
            assert testsuite.get("failures") == "1"

            # Verify testcase structure
            testcases = testsuite.findall("testcase")
            assert len(testcases) == 2, f"Expected 2 testcases, found {len(testcases)}"

            # Verify passed test case
            passed_case = testcases[0]
            assert passed_case.get("name") == "Validation 1"
            classname = passed_case.get("classname")
            assert classname is not None and "original1" in classname
            assert len(passed_case.findall("failure")) == 0

            # Verify failed test case
            failed_case = testcases[1]
            assert failed_case.get("name") == "Validation 2"
            failures = failed_case.findall("failure")
            assert len(failures) == 1, "Failed test case should have failure element"

            failure = failures[0]
            assert failure.get("type") == "moderate_visual_difference"
            message = failure.get("message")
            assert message is not None and "0.75" in message

    def test_html_report_structure(self):
        """Test that HTML report structure remains unchanged"""
        report = self.create_reference_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = os.path.join(temp_dir, "report.html")
            report.generate_html_report(html_path)

            assert os.path.exists(html_path), "HTML report file was not created"

            with open(html_path, encoding="utf-8") as f:
                html_content = f.read()

            # Verify basic HTML structure
            assert "<!DOCTYPE html>" in html_content, "HTML should contain DOCTYPE"
            assert "<title>Validation Report: backward_compatibility_test</title>" in html_content
            assert "<h1>Validation Report: backward_compatibility_test</h1>" in html_content
            assert '<div class="summary">' in html_content
            assert "<h2>Summary</h2>" in html_content
            assert "<h2>Results</h2>" in html_content

            # Verify status indicators
            assert 'class="failed">FAILED</span>' in html_content
            assert 'class="passed">PASSED</span>' in html_content

    def test_json_report_structure(self):
        """Test that JSON report structure remains unchanged"""
        report = self.create_reference_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = os.path.join(temp_dir, "report.json")
            report.save_report(json_path)

            assert os.path.exists(json_path), "JSON report file was not created"

            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            # Verify required fields
            required_fields = [
                "document_name",
                "report_id",
                "results",
                "metadata",
                "timestamp",
                "overall_passed",
                "result_count",
                "pass_count",
                "fail_count",
                "average_ssim",
                "min_ssim",
                "max_ssim",
            ]

            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            assert data["document_name"] == "backward_compatibility_test"
            assert len(data["results"]) == 2
            assert data["result_count"] == 2
            assert data["pass_count"] == 1
            assert data["fail_count"] == 1

    def test_function_signatures(self):
        """Test that all function signatures remain unchanged"""
        # Test ValidationResult constructor
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="test.pdf",
            generated_path="test_gen.pdf",
            diff_image_path="diff.png",
            details={"test": "value"},
            failure_analysis={"reason": "test"},
            additional_metrics={"metric": 0.8},
        )

        assert result.passed is True
        assert result.ssim_score == 0.95

        # Test ValidationResult methods
        data = result.to_dict()
        assert isinstance(data, dict)

        loaded_result = ValidationResult.from_dict(data)
        assert isinstance(loaded_result, ValidationResult)

        exit_code = result.get_exit_code()
        assert isinstance(exit_code, int)

        # Test ValidationReport constructor
        report = ValidationReport(
            document_name="test_document",
            results=[result],
            metadata={"version": "1.0"},
            report_id="test_report_123",
        )

        assert report.document_name == "test_document"
        assert len(report.results) == 1

        # Test helper functions
        helper_result = create_validation_result(
            ssim_score=0.95,
            threshold=0.9,
            original_path="test.pdf",
            generated_path="test_gen.pdf",
        )
        assert isinstance(helper_result, ValidationResult)

        helper_report = create_validation_report(document_name="test_document", results=[helper_result])
        assert isinstance(helper_report, ValidationReport)

    def test_xml_security_functions(self):
        """Test that XML security functions work correctly"""
        # Test secure XML parsing
        xml_content = "<root><child>content</child></root>"
        parsed = secure_xml_parse(xml_content)
        assert parsed.tag == "root"
        child = parsed.find("child")
        assert child is not None and child.text == "content"

        # Test secure XML pretty printing
        from xml.etree.ElementTree import Element, SubElement

        root = Element("testsuites")
        root.set("name", "Test Suite")

        testsuite = SubElement(root, "testsuite")
        testsuite.set("name", "test")

        pretty_xml = secure_xml_pretty_print(root)
        assert isinstance(pretty_xml, str)
        assert "<?xml version=" in pretty_xml
        assert 'name="Test Suite"' in pretty_xml

    def test_configuration_compatibility(self):
        """Test that existing configuration formats work unchanged"""
        # Test various metadata formats
        metadata_formats = [
            {"version": "1.0", "engine": "test"},
            {
                "system_info": {"os": "linux", "python_version": "3.8"},
                "validation_config": {"threshold": 0.9, "strict_mode": True},
            },
            {
                "supported_formats": ["pdf", "png"],
                "validation_steps": ["extract", "compare", "report"],
            },
        ]

        for metadata in metadata_formats:
            result = ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="test.pdf",
                generated_path="test_gen.pdf",
            )

            report = ValidationReport(document_name="config_test", results=[result], metadata=metadata)

            # Test serialization/deserialization
            with tempfile.TemporaryDirectory() as temp_dir:
                json_path = os.path.join(temp_dir, "config_test.json")
                report.save_report(json_path)

                loaded_report = ValidationReport.load_report(json_path)
                assert loaded_report.metadata == metadata

    def test_performance_compatibility(self):
        """Test that performance remains acceptable"""
        # Create large report for performance testing
        results = []
        for i in range(50):  # Reduced from 100 for faster testing
            result = ValidationResult(
                passed=(i % 2 == 0),
                ssim_score=0.8 + (i % 20) * 0.01,
                threshold=0.9,
                original_path=f"original_{i}.pdf",
                generated_path=f"generated_{i}.pdf",
                details={"test_id": i},
            )
            results.append(result)

        report = ValidationReport(
            document_name="performance_test",
            results=results,
            metadata={"test_type": "performance", "result_count": len(results)},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test JUnit generation performance
            junit_path = os.path.join(temp_dir, "perf_junit.xml")
            start_time = time.time()
            report.generate_junit_report(junit_path)
            junit_time = time.time() - start_time

            assert junit_time < 3.0, f"JUnit generation took {junit_time:.2f}s, expected < 3.0s"
            assert os.path.exists(junit_path)

            # Test HTML generation performance
            html_path = os.path.join(temp_dir, "perf_report.html")
            start_time = time.time()
            report.generate_html_report(html_path)
            html_time = time.time() - start_time

            assert html_time < 2.0, f"HTML generation took {html_time:.2f}s, expected < 2.0s"
            assert os.path.exists(html_path)

            # Test JSON serialization performance
            json_path = os.path.join(temp_dir, "perf_report.json")
            start_time = time.time()
            report.save_report(json_path)
            json_time = time.time() - start_time

            assert json_time < 1.0, f"JSON serialization took {json_time:.2f}s, expected < 1.0s"
            assert os.path.exists(json_path)

    def run_all_tests(self, include_performance: bool = False) -> dict:
        """Run all backward compatibility tests"""
        self.log("Starting backward compatibility test suite")

        # Core compatibility tests
        tests = [
            ("XML Structure Compatibility", self.test_junit_xml_structure),
            ("HTML Structure Compatibility", self.test_html_report_structure),
            ("JSON Structure Compatibility", self.test_json_report_structure),
            ("Function Signature Compatibility", self.test_function_signatures),
            ("XML Security Functions", self.test_xml_security_functions),
            ("Configuration Compatibility", self.test_configuration_compatibility),
        ]

        # Add performance tests if requested
        if include_performance:
            tests.append(("Performance Compatibility", self.test_performance_compatibility))

        # Run all tests
        passed = 0
        failed = 0

        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1

        # Generate summary
        total_time = time.time() - self.start_time
        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(tests) * 100,
            "total_time": total_time,
            "test_results": self.test_results,
        }

        self.log(f"Test suite completed in {total_time:.2f}s")
        self.log(f"Results: {passed} passed, {failed} failed ({summary['success_rate']:.1f}% success rate)")

        return summary

    def save_report(self, summary: dict):
        """Save test report to file"""
        report_path = os.path.join(self.output_dir, "backward_compatibility_report.json")

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        self.log(f"Test report saved to: {report_path}")

        # Also create a simple text summary
        text_report_path = os.path.join(self.output_dir, "backward_compatibility_summary.txt")
        with open(text_report_path, "w", encoding="utf-8") as f:
            f.write("Backward Compatibility Test Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Passed: {summary['passed']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Success Rate: {summary['success_rate']:.1f}%\n")
            f.write(f"Total Time: {summary['total_time']:.2f}s\n\n")

            f.write("Test Results:\n")
            f.write("-" * 20 + "\n")
            for result in summary["test_results"]:
                status_symbol = "✓" if result["status"] == "PASS" else "✗"
                f.write(f"{status_symbol} {result['name']}: {result['status']} ({result['duration']:.3f}s)\n")
                if result["error"]:
                    f.write(f"  Error: {result['error']}\n")

        self.log(f"Text summary saved to: {text_report_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run backward compatibility tests for XML security fix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument(
        "--performance",
        "-p",
        action="store_true",
        help="Include performance tests (may take longer)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default="tests/backward_compatibility_reports",
        help="Directory to save test reports",
    )

    args = parser.parse_args()

    # Create tester and run tests
    tester = BackwardCompatibilityTester(verbose=args.verbose, output_dir=args.output_dir)

    try:
        summary = tester.run_all_tests(include_performance=args.performance)
        tester.save_report(summary)

        # Exit with appropriate code
        exit_code = 0 if summary["failed"] == 0 else 1
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Test run failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
