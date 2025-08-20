"""
Test suite for XML security functions in validation_report.py

This test suite verifies that the secure XML parsing functions work correctly
and handle security issues appropriately.
"""

import logging
from xml.etree.ElementTree import Element, SubElement

import pytest

from pdfrebuilder.engine.validation_report import (
    XML_SECURITY_ENABLED,
    XMLParsingError,
    XMLSecurityError,
    log_xml_security_event,
    secure_xml_parse,
    secure_xml_pretty_print,
)


class TestXMLSecurityFunctions:
    """Test class for XML security functions"""

    def test_secure_xml_parse_valid_xml(self):
        """Test secure_xml_parse with valid XML content"""
        xml_content = "<root><child>test content</child></root>"
        element = secure_xml_parse(xml_content)

        assert element.tag == "root"
        assert element.find("child").text == "test content"

    def test_secure_xml_parse_malformed_xml(self):
        """Test secure_xml_parse with malformed XML content"""
        malformed_xml = "<root><unclosed_tag>"

        with pytest.raises(XMLParsingError) as exc_info:
            secure_xml_parse(malformed_xml)

        assert "Invalid XML content" in str(exc_info.value)

    def test_secure_xml_parse_empty_xml(self):
        """Test secure_xml_parse with empty XML content"""
        empty_xml = ""

        with pytest.raises(XMLParsingError) as exc_info:
            secure_xml_parse(empty_xml)

        assert "Invalid XML content" in str(exc_info.value)

    def test_secure_xml_pretty_print_basic(self):
        """Test secure_xml_pretty_print with basic XML element"""
        root = Element("testsuites")
        root.set("name", "Test Suite")
        root.set("tests", "1")

        suite = SubElement(root, "testsuite")
        suite.set("name", "Test")

        case = SubElement(suite, "testcase")
        case.set("name", "Test Case 1")
        case.set("classname", "TestClass")

        pretty_xml = secure_xml_pretty_print(root)

        # Verify the XML is properly formatted
        assert "<?xml version=" in pretty_xml
        assert '<testsuites name="Test Suite"' in pretty_xml
        assert '<testsuite name="Test"' in pretty_xml
        assert '<testcase name="Test Case 1"' in pretty_xml
        assert "  " in pretty_xml  # Check for indentation

    def test_secure_xml_pretty_print_complex_structure(self):
        """Test secure_xml_pretty_print with complex XML structure"""
        root = Element("testsuites")

        # Create multiple test suites
        for i in range(2):
            suite = SubElement(root, "testsuite")
            suite.set("name", f"Suite {i}")

            # Add properties
            properties = SubElement(suite, "properties")
            prop = SubElement(properties, "property")
            prop.set("name", "test_property")
            prop.set("value", "test_value")

            # Add test cases
            for j in range(2):
                case = SubElement(suite, "testcase")
                case.set("name", f"Test {j}")
                case.set("classname", f"TestClass{j}")

        pretty_xml = secure_xml_pretty_print(root)

        # Verify structure is preserved
        assert "Suite 0" in pretty_xml
        assert "Suite 1" in pretty_xml
        assert "test_property" in pretty_xml
        assert "TestClass0" in pretty_xml
        assert "TestClass1" in pretty_xml

    def test_xml_security_error_exception(self):
        """Test XMLSecurityError exception class"""
        error_message = "Test security error message"

        with pytest.raises(XMLSecurityError) as exc_info:
            raise XMLSecurityError(error_message)

        assert str(exc_info.value) == error_message
        assert isinstance(exc_info.value, Exception)

    def test_xml_parsing_error_exception(self):
        """Test XMLParsingError exception class"""
        error_message = "Test parsing error message"

        with pytest.raises(XMLParsingError) as exc_info:
            raise XMLParsingError(error_message)

        assert str(exc_info.value) == error_message
        assert isinstance(exc_info.value, Exception)

    def test_log_xml_security_event_basic(self, caplog):
        """Test log_xml_security_event with basic parameters"""
        with caplog.at_level(logging.INFO):
            log_xml_security_event(
                event_type="test_event",
                details={"test_key": "test_value"},
                severity="low",
            )

        # Check that the log message was created
        assert "XML Security Event: test_event" in caplog.text

    def test_log_xml_security_event_different_severities(self, caplog):
        """Test log_xml_security_event with different severity levels"""
        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            caplog.clear()
            with caplog.at_level(logging.INFO):
                log_xml_security_event(
                    event_type=f"test_event_{severity}",
                    details={"severity": severity},
                    severity=severity,
                )

            assert f"XML Security Event: test_event_{severity}" in caplog.text

    def test_log_xml_security_event_with_complex_details(self, caplog):
        """Test log_xml_security_event with complex details dictionary"""
        complex_details = {
            "error_type": "parsing_error",
            "file_path": "/path/to/file.xml",
            "line_number": 42,
            "nested_data": {"sub_key": "sub_value", "numbers": [1, 2, 3]},
        }

        with caplog.at_level(logging.WARNING):
            log_xml_security_event(
                event_type="complex_test_event",
                details=complex_details,
                severity="medium",
            )

        assert "XML Security Event: complex_test_event" in caplog.text

    def test_xml_security_enabled_flag(self):
        """Test that XML_SECURITY_ENABLED flag is properly set"""
        # This test verifies that the flag exists and is a boolean
        assert isinstance(XML_SECURITY_ENABLED, bool)

        # If defusedxml is available, it should be True
        # If not available, it should be False
        try:
            pass

            assert XML_SECURITY_ENABLED is True
        except ImportError:
            assert XML_SECURITY_ENABLED is False

    def test_secure_xml_parse_with_namespaces(self):
        """Test secure_xml_parse with XML namespaces"""
        xml_with_ns = """<?xml version="1.0"?>
        <root xmlns:test="http://example.com/test">
            <test:element>content</test:element>
        </root>"""

        element = secure_xml_parse(xml_with_ns)
        assert element.tag == "root"

    def test_secure_xml_parse_with_attributes(self):
        """Test secure_xml_parse with XML attributes"""
        xml_with_attrs = """<root attr1="value1" attr2="value2">
            <child id="123" class="test">content</child>
        </root>"""

        element = secure_xml_parse(xml_with_attrs)
        assert element.get("attr1") == "value1"
        assert element.get("attr2") == "value2"

        child = element.find("child")
        assert child.get("id") == "123"
        assert child.get("class") == "test"
        assert child.text == "content"

    def test_secure_xml_pretty_print_preserves_attributes(self):
        """Test that secure_xml_pretty_print preserves XML attributes"""
        root = Element("root")
        root.set("version", "1.0")
        root.set("encoding", "utf-8")

        child = SubElement(root, "child")
        child.set("id", "test-id")
        child.text = "test content"

        pretty_xml = secure_xml_pretty_print(root)

        assert 'version="1.0"' in pretty_xml
        assert 'encoding="utf-8"' in pretty_xml
        assert 'id="test-id"' in pretty_xml
        assert "test content" in pretty_xml

    def test_secure_xml_pretty_print_with_cdata(self):
        """Test secure_xml_pretty_print with text content"""
        root = Element("root")
        child = SubElement(root, "description")
        child.text = 'This is a test description with special chars: <>&"'

        pretty_xml = secure_xml_pretty_print(root)

        # XML should be properly escaped
        assert "<description>" in pretty_xml
        assert "This is a test description" in pretty_xml

    def test_error_handling_in_secure_functions(self):
        """Test error handling in secure XML functions"""
        # Test with None input
        with pytest.raises((XMLParsingError, TypeError)):
            secure_xml_parse(None)

        # Test with non-string input
        with pytest.raises((XMLParsingError, TypeError)):
            secure_xml_parse(123)


class TestXMLSecurityIntegration:
    """Integration tests for XML security functions"""

    def test_junit_xml_generation_workflow(self):
        """Test the complete workflow of generating JUnit XML with secure functions"""
        # Create a test suite structure similar to what's used in validation_report.py
        test_suites = Element("testsuites")
        test_suites.set("name", "Document Validation Test")
        test_suites.set("tests", "2")
        test_suites.set("failures", "1")
        test_suites.set("errors", "0")

        test_suite = SubElement(test_suites, "testsuite")
        test_suite.set("name", "ValidationTest")
        test_suite.set("tests", "2")
        test_suite.set("failures", "1")

        # Add properties
        properties = SubElement(test_suite, "properties")
        prop = SubElement(properties, "property")
        prop.set("name", "ssim_threshold")
        prop.set("value", "0.95")

        # Add passing test case
        test_case1 = SubElement(test_suite, "testcase")
        test_case1.set("name", "Validation 1")
        test_case1.set("classname", "document.validation.test")

        # Add failing test case
        test_case2 = SubElement(test_suite, "testcase")
        test_case2.set("name", "Validation 2")
        test_case2.set("classname", "document.validation.test")

        failure = SubElement(test_case2, "failure")
        failure.set("message", "SSIM score 0.85 below threshold 0.95")
        failure.set("type", "ValidationFailure")
        failure.text = "Visual validation failed due to low SSIM score"

        # Test that we can pretty print this structure
        pretty_xml = secure_xml_pretty_print(test_suites)

        # Verify the structure is correct
        assert "testsuites" in pretty_xml
        assert "testsuite" in pretty_xml
        assert "testcase" in pretty_xml
        assert "properties" in pretty_xml
        assert "failure" in pretty_xml
        assert "SSIM score 0.85 below threshold 0.95" in pretty_xml

    def test_security_logging_integration(self, caplog):
        """Test integration of security logging with XML processing"""
        # Simulate a security event during XML processing
        with caplog.at_level(logging.WARNING):
            log_xml_security_event(
                event_type="junit_xml_formatting_error",
                details={
                    "error": "Test formatting error",
                    "output_path": "/tmp/test_report.xml",
                },
                severity="medium",
            )

        assert "XML Security Event: junit_xml_formatting_error" in caplog.text

    def test_fallback_behavior_simulation(self):
        """Test fallback behavior when pretty printing fails"""
        # Create an element that should work with basic serialization
        root = Element("simple")
        root.text = "content"

        # This should work with both secure and fallback methods
        result = secure_xml_pretty_print(root)
        assert "simple" in result
        assert "content" in result
