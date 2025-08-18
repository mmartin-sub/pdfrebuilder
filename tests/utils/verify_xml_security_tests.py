#!/usr/bin/env python3
"""
Verification script for XML security test module.

This script verifies that the XML security test module can be imported
and that the test classes are properly structured.
"""

import sys
from pathlib import Path

# Import pytest for test framework compatibility
try:
    import pytest
except ImportError:
    pytest = None

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_test_module():
    """Verify that the XML security test module is properly structured"""
    print("Verifying XML security test module...")

    try:
        # Import the test module
        from ..security.test_xml_security import (
            TestEdgeCasesAndCornerCases,
            TestEntityExpansionLimits,
            TestExternalEntityBlocking,
            TestFallbackBehavior,
            TestMalformedXMLHandling,
            TestSecurityConfigurationIntegration,
            TestSecurityEventLogging,
            TestXMLBombProtection,
            TestXXEAttackPrevention,
        )

        print("✓ All test classes imported successfully")

        # Verify test classes have test methods
        test_classes = [
            TestXXEAttackPrevention,
            TestXMLBombProtection,
            TestEntityExpansionLimits,
            TestExternalEntityBlocking,
            TestMalformedXMLHandling,
            TestSecurityConfigurationIntegration,
            TestSecurityEventLogging,
            TestFallbackBehavior,
            TestEdgeCasesAndCornerCases,
        ]

        total_test_methods = 0
        for test_class in test_classes:
            test_methods = [method for method in dir(test_class) if method.startswith("test_")]
            total_test_methods += len(test_methods)
            print(f"✓ {test_class.__name__}: {len(test_methods)} test methods")

        print(f"✓ Total test methods: {total_test_methods}")

        # Verify imports work
        from pdfrebuilder.engine.validation_report import XML_SECURITY_ENABLED, secure_xml_parse

        print("✓ All required imports from validation_report work")

        print(f"✓ XML Security Enabled: {XML_SECURITY_ENABLED}")

        # Test basic functionality
        result = secure_xml_parse("<root>test</root>")
        assert result.tag == "root"
        print("✓ Basic XML parsing works")

        print("\n🎉 XML security test module verification completed successfully!")
        return True

    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    success = verify_test_module()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
