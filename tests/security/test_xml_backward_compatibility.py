"""
Backward compatibility validation tests for XML security fix

This test suite ensures that the XML security fix maintains backward compatibility
by verifying that existing XML output format is maintained, all existing function
signatures remain unchanged, existing configuration files work without changes,
and performance is not significantly degraded.

Requirements covered: 2.1, 2.2, 2.3, 2.4
"""

import json
import os
import tempfile
import time
from xml.etree.ElementTree import Element, SubElement

import pytest

from pdfrebuilder.engine.validation_report import (
    ValidationReport,
    ValidationResult,
    create_validation_report,
    create_validation_result,
    generate_validation_report,
    secure_xml_parse,
    secure_xml_pretty_print,
)


class TestXMLOutputFormatCompatibility:
    """Test that existing XML output format is maintained (Requirement 2.1)"""

    def create_reference_validation_report(self):
        """Create a reference validation report for format comparison"""
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
            document_name="test_document",
            results=results,
            metadata={"version": "1.0", "engine": "test"},
        )

    def test_junit_xml_structure_unchanged(self):
        """Test that JUnit XML structure remains unchanged"""
        report = self.create_reference_validation_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            junit_path = os.path.join(temp_dir, "junit_report.xml")

            # Generate JUnit report
            report.generate_junit_report(junit_path)

            # Verify file was created
            assert os.path.exists(junit_path)

            # Parse and verify XML structure
            with open(junit_path, encoding="utf-8") as f:
                xml_content = f.read()

            # Parse with secure parser to ensure compatibility
            parsed_xml = secure_xml_parse(xml_content)

            # Verify root element structure
            assert parsed_xml.tag == "testsuites"
            assert parsed_xml.get("name") == "Document Validation: test_document"
            assert parsed_xml.get("tests") == "2"
            assert parsed_xml.get("failures") == "1"
            assert parsed_xml.get("errors") == "0"

            # Verify testsuite structure
            testsuites = parsed_xml.findall("testsuite")
            assert len(testsuites) == 1

            testsuite = testsuites[0]
            assert testsuite.get("name") == "test_document"
            assert testsuite.get("tests") == "2"
            assert testsuite.get("failures") == "1"
            assert testsuite.get("errors") == "0"
            assert testsuite.get("timestamp") is not None

            # Verify properties section exists
            properties = testsuite.findall("properties")
            assert len(properties) == 1

            property_elements = properties[0].findall("property")
            assert len(property_elements) > 0

            # Verify testcase structure
            testcases = testsuite.findall("testcase")
            assert len(testcases) == 2

            # Check passed test case
            passed_case = testcases[0]
            assert passed_case.get("name") == "Validation 1"
            assert passed_case.get("classname") == "document.validation.original1"
            assert len(passed_case.findall("failure")) == 0
            assert len(passed_case.findall("system-out")) == 1

            # Check failed test case
            failed_case = testcases[1]
            assert failed_case.get("name") == "Validation 2"
            assert failed_case.get("classname") == "document.validation.original2"

            failures = failed_case.findall("failure")
            assert len(failures) == 1

            failure = failures[0]
            assert failure.get("type") == "moderate_visual_difference"
            assert "SSIM score 0.75" in failure.get("message")
            assert failure.text is not None
            assert "SSIM Score: 0.75" in failure.text
            assert "Threshold: 0.9" in failure.text

            system_outs = failed_case.findall("system-out")
            assert len(system_outs) == 1
            assert "SSIM Score: 0.75" in system_outs[0].text

    def test_junit_xml_content_format_unchanged(self):
        """Test that JUnit XML content format remains unchanged"""
        report = self.create_reference_validation_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            junit_path = os.path.join(temp_dir, "junit_report.xml")

            # Generate JUnit report
            report.generate_junit_report(junit_path)

            # Read and verify XML content format
            with open(junit_path, encoding="utf-8") as f:
                xml_content = f.read()

            # Verify XML declaration
            assert xml_content.startswith('<?xml version="1.0"')

            # Verify proper XML formatting (indentation)
            lines = xml_content.split("\n")
            indented_lines = [line for line in lines if line.startswith("  ")]
            assert len(indented_lines) > 0  # Should have indented content

            # Verify no malformed XML
            parsed_xml = secure_xml_parse(xml_content)
            assert parsed_xml is not None

            # Verify specific content patterns remain unchanged
            assert 'name="Document Validation: test_document"' in xml_content
            assert 'classname="document.validation.' in xml_content
            assert 'type="moderate_visual_difference"' in xml_content

    def test_xml_pretty_printing_format_unchanged(self):
        """Test that XML pretty printing format remains unchanged"""
        # Create test XML element
        root = Element("testsuites")
        root.set("name", "Test Suite")
        root.set("tests", "1")

        testsuite = SubElement(root, "testsuite")
        testsuite.set("name", "test_document")
        testsuite.set("tests", "1")

        testcase = SubElement(testsuite, "testcase")
        testcase.set("name", "Test 1")
        testcase.set("classname", "document.validation.test")

        # Pretty print with secure function
        result = secure_xml_pretty_print(root)

        # Verify format characteristics
        assert result.startswith('<?xml version="1.0"')
        assert "  <testsuite" in result  # Proper indentation
        assert "    <testcase" in result  # Nested indentation
        assert 'name="Test Suite"' in result
        assert 'classname="document.validation.test"' in result

        # Verify it can be parsed back
        parsed = secure_xml_parse(result)
        assert parsed.tag == "testsuites"
        assert parsed.get("name") == "Test Suite"

    def test_html_report_structure_unchanged(self):
        """Test that HTML report structure remains unchanged"""
        report = self.create_reference_validation_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = os.path.join(temp_dir, "report.html")

            # Generate HTML report
            report.generate_html_report(html_path)

            # Verify file was created
            assert os.path.exists(html_path)

            # Read and verify HTML structure
            with open(html_path, encoding="utf-8") as f:
                html_content = f.read()

            # Verify basic HTML structure
            assert html_content.startswith("<!DOCTYPE html>")
            assert "<html>" in html_content
            assert "<head>" in html_content
            assert "<title>Validation Report: test_document</title>" in html_content
            assert "<body>" in html_content

            # Verify key sections exist
            assert "<h1>Validation Report: test_document</h1>" in html_content
            assert '<div class="summary">' in html_content
            assert "<h2>Summary</h2>" in html_content
            assert "<h2>Results</h2>" in html_content
            assert "<h2>Metadata</h2>" in html_content

            # Verify status indicators
            assert 'class="failed">FAILED</span>' in html_content
            assert 'class="passed">PASSED</span>' in html_content

            # Verify metrics display
            assert "SSIM Score:" in html_content
            assert "0.95" in html_content  # Passed test score
            assert "0.75" in html_content  # Failed test score

    def test_json_report_structure_unchanged(self):
        """Test that JSON report structure remains unchanged"""
        report = self.create_reference_validation_report()

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = os.path.join(temp_dir, "report.json")

            # Save JSON report
            report.save_report(json_path)

            # Verify file was created
            assert os.path.exists(json_path)

            # Load and verify JSON structure
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            # Verify top-level structure
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
                "failure_summary",
            ]

            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Verify data types and values
            assert data["document_name"] == "test_document"
            assert isinstance(data["results"], list)
            assert len(data["results"]) == 2
            assert data["result_count"] == 2
            assert data["pass_count"] == 1
            assert data["fail_count"] == 1
            assert data["overall_passed"] is False

            # Verify result structure
            result = data["results"][0]
            result_fields = [
                "passed",
                "ssim_score",
                "threshold",
                "original_path",
                "generated_path",
                "details",
                "failure_analysis",
                "additional_metrics",
                "timestamp",
            ]

            for field in result_fields:
                assert field in result, f"Missing result field: {field}"


class TestFunctionSignatureCompatibility:
    """Test that all existing function signatures remain unchanged (Requirement 2.2)"""

    def test_validation_result_constructor_signature(self):
        """Test ValidationResult constructor signature unchanged"""
        # Test with all parameters
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            diff_image_path="diff.png",
            details={"test": "value"},
            failure_analysis={"reason": "test"},
            additional_metrics={"metric": 0.8},
        )

        assert result.passed is True
        assert result.ssim_score == 0.95
        assert result.threshold == 0.9
        assert result.original_path == "original.pdf"
        assert result.generated_path == "generated.pdf"
        assert result.diff_image_path == "diff.png"
        assert result.details["test"] == "value"
        assert result.failure_analysis["reason"] == "test"
        assert result.additional_metrics["metric"] == 0.8

    def test_validation_result_methods_signature(self):
        """Test ValidationResult methods signatures unchanged"""
        result = ValidationResult(
            passed=True,
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
        )

        # Test to_dict method
        data = result.to_dict()
        assert isinstance(data, dict)

        # Test from_dict class method
        loaded_result = ValidationResult.from_dict(data)
        assert isinstance(loaded_result, ValidationResult)

        # Test save_report method
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = os.path.join(temp_dir, "result.json")
            result.save_report(report_path)
            assert os.path.exists(report_path)

            # Test load_report class method
            loaded_result = ValidationResult.load_report(report_path)
        assert isinstance(loaded_result, ValidationResult)

        # Test get_exit_code method
        exit_code = result.get_exit_code()
        assert isinstance(exit_code, int)
        assert exit_code == 0  # Passed result

    def test_validation_report_constructor_signature(self):
        """Test ValidationReport constructor signature unchanged"""
        results = [
            ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original.pdf",
                generated_path="generated.pdf",
            )
        ]

        # Test with all parameters
        report = ValidationReport(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
            report_id="test_report_123",
        )

        assert report.document_name == "test_document"
        assert len(report.results) == 1
        assert report.metadata["version"] == "1.0"
        assert report.report_id == "test_report_123"

    def test_validation_report_methods_signature(self):
        """Test ValidationReport methods signatures unchanged"""
        results = [
            ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original.pdf",
                generated_path="generated.pdf",
            )
        ]

        report = ValidationReport(document_name="test_document", results=results)

        # Test to_dict method
        data = report.to_dict()
        assert isinstance(data, dict)

        # Test from_dict class method
        loaded_report = ValidationReport.from_dict(data)
        assert isinstance(loaded_report, ValidationReport)

        # Test save_report method
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = os.path.join(temp_dir, "report.json")
            report.save_report(report_path)
            assert os.path.exists(report_path)

            # Test load_report class method
            loaded_report = ValidationReport.load_report(report_path)
        assert isinstance(loaded_report, ValidationReport)

        # Test get_summary method
        summary = report.get_summary()
        assert isinstance(summary, dict)

        # Test get_exit_code method
        exit_code = report.get_exit_code()
        assert isinstance(exit_code, int)

        # Test generate_html_report method
        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = os.path.join(temp_dir, "report.html")
            report.generate_html_report(html_path)
            assert os.path.exists(html_path)

        # Test generate_junit_report method
        with tempfile.TemporaryDirectory() as temp_dir:
            junit_path = os.path.join(temp_dir, "junit.xml")
            report.generate_junit_report(junit_path)
            assert os.path.exists(junit_path)

        # Test generate_markdown_report method
        with tempfile.TemporaryDirectory() as temp_dir:
            md_path = os.path.join(temp_dir, "report.md")
            report.generate_markdown_report(md_path)
            assert os.path.exists(md_path)

    def test_helper_functions_signature(self):
        """Test helper functions signatures unchanged"""
        # Test create_validation_result function
        result = create_validation_result(
            ssim_score=0.95,
            threshold=0.9,
            original_path="original.pdf",
            generated_path="generated.pdf",
            diff_image_path="diff.png",
            details={"test": "value"},
            failure_analysis={"reason": "test"},
            additional_metrics={"metric": 0.8},
        )

        assert isinstance(result, ValidationResult)
        assert result.ssim_score == 0.95

        # Test create_validation_report function
        results = [result]
        report = create_validation_report(
            document_name="test_document",
            results=results,
            metadata={"version": "1.0"},
            report_id="test_report",
        )

        assert isinstance(report, ValidationReport)
        assert report.document_name == "test_document"

        # Test generate_validation_report function
        with tempfile.TemporaryDirectory() as temp_dir:
            report_paths = generate_validation_report(
                original_path="original.pdf",
                generated_path="generated.pdf",
                validation_result=result,
                output_dir=temp_dir,
                report_formats=["json", "html", "ci"],
                font_validation_result={"validation_passed": True},
            )

            assert isinstance(report_paths, dict)
            assert "json" in report_paths
            assert "html" in report_paths
            assert "ci" in report_paths

    def test_secure_xml_functions_signature(self):
        """Test secure XML functions signatures unchanged"""
        # Test secure_xml_parse function
        xml_content = "<root><child>content</child></root>"
        parsed = secure_xml_parse(xml_content)
        assert parsed.tag == "root"

        # Test secure_xml_pretty_print function
        from xml.etree.ElementTree import Element, SubElement

        root = Element("root")
        child = SubElement(root, "child")
        child.text = "content"

        pretty_xml = secure_xml_pretty_print(root)
        assert isinstance(pretty_xml, str)
        assert "<?xml version=" in pretty_xml


class TestConfigurationCompatibility:
    """Test that existing configuration files work without changes (Requirement 2.3)"""

    def test_existing_json_configuration_compatibility(self):
        """Test that existing JSON configuration files work unchanged"""
        # Create a sample configuration that might exist in user systems
        existing_config = {
            "validation_settings": {
                "ssim_threshold": 0.9,
                "generate_diff_images": True,
                "output_formats": ["json", "html", "junit"],
            },
            "report_metadata": {
                "version": "1.0",
                "engine": "test_engine",
                "author": "test_user",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "validation_config.json")

            # Save existing configuration
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(existing_config, f, indent=2)

            # Load and use configuration (should work without changes)
            with open(config_path, encoding="utf-8") as f:
                loaded_config = json.load(f)

            # Verify configuration can be used as before
            assert loaded_config["validation_settings"]["ssim_threshold"] == 0.9
            assert loaded_config["report_metadata"]["version"] == "1.0"

            # Create validation result using configuration
            result = ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=loaded_config["validation_settings"]["ssim_threshold"],
                original_path="original.pdf",
                generated_path="generated.pdf",
            )

            # Create report using configuration metadata
            report = ValidationReport(
                document_name="test_document",
                results=[result],
                metadata=loaded_config["report_metadata"],
            )

            # Generate reports in configured formats
            for format_type in loaded_config["validation_settings"]["output_formats"]:
                if format_type == "json":
                    json_path = os.path.join(temp_dir, "report.json")
                    report.save_report(json_path)
                    assert os.path.exists(json_path)
                elif format_type == "html":
                    html_path = os.path.join(temp_dir, "report.html")
                    report.generate_html_report(html_path)
                    assert os.path.exists(html_path)
                elif format_type == "junit":
                    junit_path = os.path.join(temp_dir, "report.xml")
                    report.generate_junit_report(junit_path)
                    assert os.path.exists(junit_path)

    def test_existing_metadata_format_compatibility(self):
        """Test that existing metadata formats work unchanged"""
        # Test various metadata formats that might exist
        metadata_formats = [
            # Simple string values
            {"version": "1.0", "engine": "test"},
            # Nested objects
            {
                "system_info": {"os": "linux", "python_version": "3.8"},
                "validation_config": {"threshold": 0.9, "strict_mode": True},
            },
            # Arrays
            {
                "supported_formats": ["pdf", "png", "jpg"],
                "validation_steps": [
                    "extract_content",
                    "compare_images",
                    "generate_report",
                ],
            },
            # Mixed types
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "validation_count": 42,
                "success_rate": 0.95,
                "enabled": True,
                "tags": ["test", "validation", "pdf"],
            },
        ]

        for metadata in metadata_formats:
            result = ValidationResult(
                passed=True,
                ssim_score=0.95,
                threshold=0.9,
                original_path="original.pdf",
                generated_path="generated.pdf",
            )

            report = ValidationReport(document_name="test_document", results=[result], metadata=metadata)

            # Test JSON serialization/deserialization
            with tempfile.TemporaryDirectory() as temp_dir:
                json_path = os.path.join(temp_dir, "report.json")
                report.save_report(json_path)

                loaded_report = ValidationReport.load_report(json_path)
                assert loaded_report.metadata == metadata

                # Test HTML generation with metadata
                html_path = os.path.join(temp_dir, "report.html")
                report.generate_html_report(html_path)
                assert os.path.exists(html_path)

                # Test JUnit generation with metadata
                junit_path = os.path.join(temp_dir, "report.xml")
                report.generate_junit_report(junit_path)
                assert os.path.exists(junit_path)

    def test_existing_failure_analysis_format_compatibility(self):
        """Test that existing failure analysis formats work unchanged"""
        # Test various failure analysis formats that might exist
        failure_analysis_formats = [
            # Basic format
            {"failure_reason": "visual_difference", "severity": "high"},
            # Extended format
            {
                "failure_reason": "layout_mismatch",
                "severity": "medium",
                "recommendations": ["Check font rendering", "Verify image positioning"],
                "affected_areas": ["header", "footer"],
                "confidence": 0.85,
            },
            # Custom format
            {
                "failure_reason": "custom_validation_failed",
                "severity": "critical",
                "error_code": "VAL_001",
                "description": "Custom validation logic failed",
                "remediation_steps": [
                    "Step 1: Check input",
                    "Step 2: Verify configuration",
                ],
                "related_issues": ["ISSUE-123", "ISSUE-456"],
            },
        ]

        for failure_analysis in failure_analysis_formats:
            result = ValidationResult(
                passed=False,
                ssim_score=0.75,
                threshold=0.9,
                original_path="original.pdf",
                generated_path="generated.pdf",
                failure_analysis=failure_analysis,
            )

            report = ValidationReport(document_name="test_document", results=[result])

            # Test all report formats work with existing failure analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                # JSON format
                json_path = os.path.join(temp_dir, "report.json")
                report.save_report(json_path)

                loaded_report = ValidationReport.load_report(json_path)
                assert loaded_report.results[0].failure_analysis == failure_analysis

                # HTML format
                html_path = os.path.join(temp_dir, "report.html")
                report.generate_html_report(html_path)
                assert os.path.exists(html_path)

                # JUnit format
                junit_path = os.path.join(temp_dir, "report.xml")
                report.generate_junit_report(junit_path)
                assert os.path.exists(junit_path)

                # Verify JUnit contains failure information
                with open(junit_path, encoding="utf-8") as f:
                    junit_content = f.read()

                assert failure_analysis["failure_reason"] in junit_content
                assert failure_analysis["severity"] in junit_content


class TestPerformanceCompatibility:
    """Test that performance is not significantly degraded (Requirement 2.4)"""

    def create_large_validation_report(self, num_results=100):
        """Create a large validation report for performance testing"""
        results = []
        for i in range(num_results):
            result = ValidationResult(
                passed=(i % 2 == 0),  # Alternate pass/fail
                ssim_score=0.8 + (i % 20) * 0.01,  # Vary scores
                threshold=0.9,
                original_path=f"original_{i}.pdf",
                generated_path=f"generated_{i}.pdf",
                diff_image_path=f"diff_{i}.png" if i % 2 == 1 else None,
                details={"test_id": i, "batch": i // 10},
                failure_analysis=(
                    {
                        "failure_reason": "test_failure",
                        "severity": "medium",
                        "recommendations": [f"Fix issue {i}"],
                    }
                    if i % 2 == 1
                    else {}
                ),
                additional_metrics={"metric_1": i * 0.01, "metric_2": i * 0.02},
            )
            results.append(result)

        return ValidationReport(
            document_name="performance_test_document",
            results=results,
            metadata={
                "test_type": "performance",
                "result_count": num_results,
                "batch_size": 10,
            },
        )

    def test_junit_report_generation_performance(self):
        """Test JUnit report generation performance"""
        report = self.create_large_validation_report(100)

        with tempfile.TemporaryDirectory() as temp_dir:
            junit_path = os.path.join(temp_dir, "performance_junit.xml")

            # Measure generation time
            start_time = time.time()
            report.generate_junit_report(junit_path)
            generation_time = time.time() - start_time

            # Verify file was created
            assert os.path.exists(junit_path)

            # Performance should be reasonable (less than 5 seconds for 100 results)
            assert generation_time < 5.0, f"JUnit generation took {generation_time:.2f}s, expected < 5.0s"

            # Verify file size is reasonable
            file_size = os.path.getsize(junit_path)
            assert file_size > 1000, "JUnit file seems too small"
            assert file_size < 10 * 1024 * 1024, "JUnit file seems too large (>10MB)"

            # Verify content is valid
            with open(junit_path, encoding="utf-8") as f:
                xml_content = f.read()

            parsed_xml = secure_xml_parse(xml_content)
            assert parsed_xml.tag == "testsuites"

    def test_html_report_generation_performance(self):
        """Test HTML report generation performance"""
        report = self.create_large_validation_report(100)

        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = os.path.join(temp_dir, "performance_report.html")

            # Measure generation time
            start_time = time.time()
            report.generate_html_report(html_path)
            generation_time = time.time() - start_time

            # Verify file was created
            assert os.path.exists(html_path)

            # Performance should be reasonable (less than 3 seconds for 100 results)
            assert generation_time < 3.0, f"HTML generation took {generation_time:.2f}s, expected < 3.0s"

            # Verify file size is reasonable
            file_size = os.path.getsize(html_path)
            assert file_size > 5000, "HTML file seems too small"
            assert file_size < 5 * 1024 * 1024, "HTML file seems too large (>5MB)"

            # Verify content is valid HTML
            with open(html_path, encoding="utf-8") as f:
                html_content = f.read()

            assert html_content.startswith("<!DOCTYPE html>")
            assert "performance_test_document" in html_content

    def test_json_report_serialization_performance(self):
        """Test JSON report serialization performance"""
        report = self.create_large_validation_report(100)

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = os.path.join(temp_dir, "performance_report.json")

            # Measure serialization time
            start_time = time.time()
            report.save_report(json_path)
            serialization_time = time.time() - start_time

            # Verify file was created
            assert os.path.exists(json_path)

            # Performance should be reasonable (less than 2 seconds for 100 results)
            assert serialization_time < 2.0, f"JSON serialization took {serialization_time:.2f}s, expected < 2.0s"

            # Measure deserialization time
            start_time = time.time()
            loaded_report = ValidationReport.load_report(json_path)
            deserialization_time = time.time() - start_time

            # Performance should be reasonable (less than 2 seconds for 100 results)
            assert deserialization_time < 2.0, f"JSON deserialization took {deserialization_time:.2f}s, expected < 2.0s"

            # Verify data integrity
            assert loaded_report.document_name == report.document_name
            assert len(loaded_report.results) == len(report.results)
            assert loaded_report.result_count == report.result_count

    def test_xml_parsing_performance(self):
        """Test XML parsing performance with secure functions"""
        # Create large XML content
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', "<testsuites>"]

        for i in range(100):
            xml_parts.append(f'  <testsuite name="suite_{i}">')
            for j in range(10):
                xml_parts.append(f'    <testcase name="test_{i}_{j}" classname="test.class.{i}">')
                xml_parts.append(f"      <system-out>Test output for {i}_{j}</system-out>")
                xml_parts.append("    </testcase>")
            xml_parts.append("  </testsuite>")

        xml_parts.append("</testsuites>")
        large_xml_content = "\n".join(xml_parts)

        # Measure parsing time
        start_time = time.time()
        parsed_xml = secure_xml_parse(large_xml_content)
        parsing_time = time.time() - start_time

        # Performance should be reasonable (less than 1 second for large XML)
        assert parsing_time < 1.0, f"XML parsing took {parsing_time:.2f}s, expected < 1.0s"

        # Verify parsing worked correctly
        assert parsed_xml.tag == "testsuites"
        testsuites = parsed_xml.findall("testsuite")
        assert len(testsuites) == 100

    def test_xml_pretty_printing_performance(self):
        """Test XML pretty printing performance"""
        from xml.etree.ElementTree import Element, SubElement

        # Create large XML structure
        root = Element("testsuites")

        for i in range(50):
            testsuite = SubElement(root, "testsuite")
            testsuite.set("name", f"suite_{i}")
            testsuite.set("tests", "10")

            for j in range(10):
                testcase = SubElement(testsuite, "testcase")
                testcase.set("name", f"test_{i}_{j}")
                testcase.set("classname", f"test.class.{i}")

                system_out = SubElement(testcase, "system-out")
                system_out.text = f"Test output for {i}_{j} with some detailed information"

        # Measure pretty printing time
        start_time = time.time()
        pretty_xml = secure_xml_pretty_print(root)
        pretty_print_time = time.time() - start_time

        # Performance should be reasonable (less than 2 seconds for large XML)
        assert pretty_print_time < 2.0, f"XML pretty printing took {pretty_print_time:.2f}s, expected < 2.0s"

        # Verify pretty printing worked correctly
        assert pretty_xml.startswith('<?xml version="1.0"')
        assert "<testsuites>" in pretty_xml
        assert "  <testsuite" in pretty_xml  # Proper indentation

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable during report generation"""
        import gc

        # Force garbage collection before test
        gc.collect()

        # Create multiple reports and verify memory doesn't grow excessively
        initial_objects = len(gc.get_objects())

        for i in range(10):
            report = self.create_large_validation_report(50)

            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate all report types
                json_path = os.path.join(temp_dir, f"report_{i}.json")
                html_path = os.path.join(temp_dir, f"report_{i}.html")
                junit_path = os.path.join(temp_dir, f"report_{i}.xml")

                report.save_report(json_path)
                report.generate_html_report(html_path)
                report.generate_junit_report(junit_path)

                # Verify files were created
                assert os.path.exists(json_path)
                assert os.path.exists(html_path)
                assert os.path.exists(junit_path)

            # Clear references
            del report
            gc.collect()

        # Check that object count hasn't grown excessively
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects

        # Allow some growth but not excessive (less than 1000 new objects)
        assert object_growth < 1000, f"Memory usage grew by {object_growth} objects, expected < 1000"


if __name__ == "__main__":
    pytest.main([__file__])
