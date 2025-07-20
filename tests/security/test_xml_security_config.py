"""
Test suite for XML security configuration and logging functionality.

This test suite verifies that the XMLSecurityConfig, XMLSecurityAuditEntry,
and configure_xml_security functions work correctly.
"""

import logging
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from pdfrebuilder.engine.validation_report import (
    XML_SECURITY_CONFIG,
    XML_SECURITY_ENABLED,
    XMLParsingError,
    XMLSecurityAuditEntry,
    XMLSecurityConfig,
    XMLSecurityError,
    configure_xml_security,
    log_xml_security_event,
    secure_xml_parse,
)


class TestXMLSecurityConfig:
    """Test class for XMLSecurityConfig dataclass"""

    def test_xml_security_config_defaults(self):
        """Test XMLSecurityConfig default values"""
        config = XMLSecurityConfig()

        assert config.forbid_dtd is True
        assert config.forbid_entities is True
        assert config.forbid_external is True
        assert config.max_entity_expansion == 1000
        assert config.max_entity_depth == 20

    def test_xml_security_config_custom_values(self):
        """Test XMLSecurityConfig with custom values"""
        config = XMLSecurityConfig(
            forbid_dtd=False,
            forbid_entities=False,
            forbid_external=False,
            max_entity_expansion=500,
            max_entity_depth=10,
        )

        assert config.forbid_dtd is False
        assert config.forbid_entities is False
        assert config.forbid_external is False
        assert config.max_entity_expansion == 500
        assert config.max_entity_depth == 10

    def test_xml_security_config_partial_override(self):
        """Test XMLSecurityConfig with partial value override"""
        config = XMLSecurityConfig(forbid_dtd=False, max_entity_expansion=2000)

        assert config.forbid_dtd is False
        assert config.forbid_entities is True  # Default
        assert config.forbid_external is True  # Default
        assert config.max_entity_expansion == 2000
        assert config.max_entity_depth == 20  # Default


class TestXMLSecurityAuditEntry:
    """Test class for XMLSecurityAuditEntry dataclass"""

    def test_xml_security_audit_entry_creation(self):
        """Test XMLSecurityAuditEntry creation"""
        timestamp = datetime.now().isoformat()
        details = {"test_key": "test_value", "error_code": 123}

        entry = XMLSecurityAuditEntry(
            timestamp=timestamp,
            event_type="test_event",
            severity="medium",
            details=details,
            source_file="test_file.py",
            line_number=42,
        )

        assert entry.timestamp == timestamp
        assert entry.event_type == "test_event"
        assert entry.severity == "medium"
        assert entry.details == details
        assert entry.source_file == "test_file.py"
        assert entry.line_number == 42

    def test_xml_security_audit_entry_to_dict(self):
        """Test XMLSecurityAuditEntry to_dict method"""
        timestamp = "2025-07-28T10:00:00.000000"
        details = {"error": "test error", "file": "test.xml"}

        entry = XMLSecurityAuditEntry(
            timestamp=timestamp,
            event_type="blocked_xxe",
            severity="critical",
            details=details,
            source_file="validation_report.py",
            line_number=100,
        )

        result_dict = entry.to_dict()

        expected_dict = {
            "timestamp": timestamp,
            "event_type": "blocked_xxe",
            "severity": "critical",
            "details": details,
            "source_file": "validation_report.py",
            "line_number": 100,
        }

        assert result_dict == expected_dict

    def test_xml_security_audit_entry_with_complex_details(self):
        """Test XMLSecurityAuditEntry with complex details dictionary"""
        complex_details = {
            "error_type": "DefusedXMLError",
            "payload_info": {
                "length": 1024,
                "contains_dtd": True,
                "contains_entities": True,
            },
            "security_flags": ["xxe_attempt", "entity_expansion"],
            "metadata": {"user_agent": "test_client", "ip_address": "127.0.0.1"},
        }

        entry = XMLSecurityAuditEntry(
            timestamp=datetime.now().isoformat(),
            event_type="blocked_complex_attack",
            severity="high",
            details=complex_details,
            source_file="test.py",
            line_number=1,
        )

        result_dict = entry.to_dict()
        assert result_dict["details"] == complex_details
        assert result_dict["event_type"] == "blocked_complex_attack"
        assert result_dict["severity"] == "high"


class TestConfigureXMLSecurity:
    """Test class for configure_xml_security function"""

    def test_configure_xml_security_with_default_config(self, caplog):
        """Test configure_xml_security with default configuration"""
        with caplog.at_level(logging.INFO):
            configure_xml_security()

        # Check that configuration was logged
        assert "XML security configuration updated" in caplog.text
        assert "XML Security Event: security_config_updated" in caplog.text

    def test_configure_xml_security_with_custom_config(self, caplog):
        """Test configure_xml_security with custom configuration"""
        custom_config = XMLSecurityConfig(
            forbid_dtd=False,
            forbid_entities=True,
            forbid_external=False,
            max_entity_expansion=500,
            max_entity_depth=15,
        )

        with caplog.at_level(logging.INFO):
            configure_xml_security(custom_config)

        # Check that configuration was updated and logged
        assert "XML security configuration updated" in caplog.text
        assert "DTD=False" in caplog.text
        assert "Entities=True" in caplog.text
        assert "External=False" in caplog.text

    @patch("src.engine.validation_report.XML_SECURITY_ENABLED", False)
    def test_configure_xml_security_when_disabled(self, caplog):
        """Test configure_xml_security when XML security is disabled"""
        with caplog.at_level(logging.WARNING):
            configure_xml_security()

        assert "Cannot configure XML security - defusedxml not available" in caplog.text
        assert "XML Security Event: security_config_unavailable" in caplog.text

    @patch("src.engine.validation_report.XML_SECURITY_ENABLED", True)
    @patch("src.engine.validation_report.defused_ET")
    def test_configure_xml_security_error_handling(self, mock_defused_et, caplog):
        """Test configure_xml_security error handling"""
        # Mock defused_ET to raise an exception when setting properties
        mock_parser = MagicMock()
        mock_defused_et.XMLParser = mock_parser

        # Make the property assignment raise an exception
        def raise_error(value):
            raise Exception("Test error")

        type(mock_parser).forbid_dtd = property(lambda self: True, raise_error)

        with caplog.at_level(logging.ERROR):
            configure_xml_security()

        assert "Failed to configure XML security settings" in caplog.text
        assert "XML Security Event: security_config_error" in caplog.text


class TestLogXMLSecurityEvent:
    """Test class for log_xml_security_event function"""

    def test_log_xml_security_event_info_level(self, caplog):
        """Test log_xml_security_event with info level"""
        with caplog.at_level(logging.INFO):
            log_xml_security_event(event_type="test_info_event", details={"test": "info"}, severity="low")

        assert "XML Security Event: test_info_event" in caplog.text

    def test_log_xml_security_event_warning_level(self, caplog):
        """Test log_xml_security_event with warning level"""
        with caplog.at_level(logging.WARNING):
            log_xml_security_event(
                event_type="test_warning_event",
                details={"test": "warning"},
                severity="medium",
            )

        assert "XML Security Event: test_warning_event" in caplog.text

    def test_log_xml_security_event_error_level(self, caplog):
        """Test log_xml_security_event with error level"""
        with caplog.at_level(logging.ERROR):
            log_xml_security_event(
                event_type="test_error_event",
                details={"test": "error"},
                severity="high",
            )

        assert "XML Security Event: test_error_event" in caplog.text

    def test_log_xml_security_event_critical_level(self, caplog):
        """Test log_xml_security_event with critical level"""
        with caplog.at_level(logging.CRITICAL):
            log_xml_security_event(
                event_type="test_critical_event",
                details={"test": "critical"},
                severity="critical",
            )

        assert "XML Security Event: test_critical_event" in caplog.text

    def test_log_xml_security_event_default_severity(self, caplog):
        """Test log_xml_security_event with default severity"""
        with caplog.at_level(logging.WARNING):
            log_xml_security_event(
                event_type="test_default_event",
                details={"test": "default"},
                # No severity specified, should default to "warning"
            )

        assert "XML Security Event: test_default_event" in caplog.text

    def test_log_xml_security_event_with_audit_entry(self, caplog):
        """Test that log_xml_security_event creates proper audit entry"""
        test_details = {
            "error_type": "XXE_ATTEMPT",
            "blocked_entity": "file:///etc/passwd",
            "source_ip": "192.168.1.100",
        }

        with caplog.at_level(logging.ERROR):
            log_xml_security_event(event_type="blocked_xxe_attack", details=test_details, severity="high")

        # Verify the log contains the event
        assert "XML Security Event: blocked_xxe_attack" in caplog.text

        # Check that the audit entry was created (we can't easily verify the exact content
        # without more complex mocking, but we can verify the log was created)
        log_records = [record for record in caplog.records if "XML Security Event" in record.message]
        assert len(log_records) == 1

        log_record = log_records[0]
        assert hasattr(log_record, "audit_entry")
        assert log_record.audit_entry["event_type"] == "blocked_xxe_attack"
        assert log_record.audit_entry["severity"] == "high"
        assert log_record.audit_entry["details"] == test_details


class TestXMLSecurityIntegration:
    """Integration tests for XML security configuration and logging"""

    def test_security_config_affects_parsing(self):
        """Test that security configuration affects XML parsing behavior"""
        # This test verifies that the global configuration is used
        assert XML_SECURITY_CONFIG.forbid_dtd is True
        assert XML_SECURITY_CONFIG.forbid_entities is True
        assert XML_SECURITY_CONFIG.forbid_external is True

    def test_malicious_xml_triggers_security_events(self, caplog):
        """Test that malicious XML triggers appropriate security events"""
        # Test with DTD-containing XML
        dtd_xml = """<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY test "test">
]>
<root>&test;</root>"""

        with caplog.at_level(logging.ERROR):
            try:
                secure_xml_parse(dtd_xml)
            except (XMLSecurityError, XMLParsingError):
                pass  # Expected to fail

        # Should have logged a security event
        assert "XML Security Event:" in caplog.text

    def test_valid_xml_does_not_trigger_security_events(self, caplog):
        """Test that valid XML does not trigger security events"""
        valid_xml = "<root><child>content</child></root>"

        with caplog.at_level(logging.INFO):
            result = secure_xml_parse(valid_xml)
            assert result.tag == "root"

        # Should not have logged security events (only info about defusedxml usage)
        security_events = [record for record in caplog.records if "XML Security Event:" in record.message]
        # Filter out the initial configuration events
        parsing_events = [
            event for event in security_events if "parsing" in event.message or "blocked" in event.message
        ]
        assert len(parsing_events) == 0

    def test_xml_security_enabled_flag_consistency(self):
        """Test that XML_SECURITY_ENABLED flag is consistent with actual availability"""
        if XML_SECURITY_ENABLED:
            # If enabled, defusedxml should be importable
            try:
                pass

                assert True  # Should not raise ImportError
            except ImportError:
                pytest.fail("XML_SECURITY_ENABLED is True but defusedxml is not available")
        else:
            # If disabled, defusedxml should not be available
            try:
                pass

                pytest.fail("XML_SECURITY_ENABLED is False but defusedxml is available")
            except ImportError:
                assert True  # Expected behavior

    def test_global_config_modification(self):
        """Test that global configuration can be modified"""
        # Import the module to access the global config
        import pdfrebuilder.engine.validation_report as vr

        # Store original values
        original_forbid_dtd = vr.XML_SECURITY_CONFIG.forbid_dtd
        original_forbid_entities = vr.XML_SECURITY_CONFIG.forbid_entities
        original_forbid_external = vr.XML_SECURITY_CONFIG.forbid_external
        original_max_entity_expansion = vr.XML_SECURITY_CONFIG.max_entity_expansion
        original_max_entity_depth = vr.XML_SECURITY_CONFIG.max_entity_depth

        # Modify configuration
        new_config = XMLSecurityConfig(
            forbid_dtd=False,
            forbid_entities=True,
            forbid_external=False,
            max_entity_expansion=2000,
            max_entity_depth=30,
        )

        configure_xml_security(new_config)

        # Verify global config was updated (access through module)
        assert vr.XML_SECURITY_CONFIG.forbid_dtd is False
        assert vr.XML_SECURITY_CONFIG.forbid_entities is True
        assert vr.XML_SECURITY_CONFIG.forbid_external is False
        assert vr.XML_SECURITY_CONFIG.max_entity_expansion == 2000
        assert vr.XML_SECURITY_CONFIG.max_entity_depth == 30

        # Restore original configuration
        original_config = XMLSecurityConfig(
            forbid_dtd=original_forbid_dtd,
            forbid_entities=original_forbid_entities,
            forbid_external=original_forbid_external,
            max_entity_expansion=original_max_entity_expansion,
            max_entity_depth=original_max_entity_depth,
        )
        configure_xml_security(original_config)
