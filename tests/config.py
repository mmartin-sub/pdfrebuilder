"""
Test Configuration Module

This module provides centralized configuration for test output directories
and other test-related settings. It integrates with the main settings.py
to provide consistent output directory management.
"""

import os

# Import the main settings configuration
from pdfrebuilder.settings import settings


class TestConfig:
    """Configuration class for test settings and output directories"""

    def __init__(self):
        self._output_dir: str | None = None
        self._temp_dir: str | None = None
        self._fonts_dir: str | None = None
        self._reports_dir: str | None = None

    @property
    def output_dir(self) -> str:
        """Get the base output directory for all test outputs"""
        if self._output_dir is None:
            # Use the main settings test output directory or a default
            self._output_dir = settings.test_framework.test_output_dir or "tests/output"

        # The 'or' above ensures _output_dir is a string, but we assert for type checker
        assert self._output_dir is not None
        # Ensure directory exists
        os.makedirs(self._output_dir, exist_ok=True)
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value: str):
        """Set the base output directory"""
        self._output_dir = value
        # Also update the main settings
        settings.test_framework.test_output_dir = value
        os.makedirs(self._output_dir, exist_ok=True)

    @property
    def temp_dir(self) -> str:
        """Get the temporary directory for test files"""
        if self._temp_dir is None:
            self._temp_dir = settings.test_framework.test_temp_dir or os.path.join(self.output_dir, "temp")
        assert self._temp_dir is not None
        os.makedirs(self._temp_dir, exist_ok=True)
        return self._temp_dir

    @property
    def fonts_dir(self) -> str:
        """Get the directory for test font files"""
        if self._fonts_dir is None:
            self._fonts_dir = settings.test_framework.test_fonts_dir or os.path.join(self.output_dir, "fonts")
        assert self._fonts_dir is not None
        os.makedirs(self._fonts_dir, exist_ok=True)
        return self._fonts_dir

    @property
    def reports_dir(self) -> str:
        """Get the directory for test reports and logs"""
        if self._reports_dir is None:
            self._reports_dir = settings.test_framework.test_reports_dir or os.path.join(self.output_dir, "reports")
        assert self._reports_dir is not None
        os.makedirs(self._reports_dir, exist_ok=True)
        return self._reports_dir

    def get_test_temp_dir(self, test_name: str) -> str:
        """Get a temporary directory specific to a test"""
        test_temp_dir = os.path.join(self.temp_dir, test_name)
        os.makedirs(test_temp_dir, exist_ok=True)
        return test_temp_dir

    def get_test_fonts_dir(self, test_name: str) -> str:
        """Get a fonts directory specific to a test"""
        test_fonts_dir = os.path.join(self.fonts_dir, test_name)
        os.makedirs(test_fonts_dir, exist_ok=True)
        return test_fonts_dir

    def get_test_reports_dir(self, test_name: str) -> str:
        """Get a reports directory specific to a test"""
        test_reports_dir = os.path.join(self.reports_dir, test_name)
        os.makedirs(test_reports_dir, exist_ok=True)
        return test_reports_dir

    def cleanup_test_dir(self, test_name: str):
        """Clean up test-specific directories"""
        import shutil

        test_temp_dir = os.path.join(self.temp_dir, test_name)
        if os.path.exists(test_temp_dir):
            shutil.rmtree(test_temp_dir, ignore_errors=True)

        test_fonts_dir = os.path.join(self.fonts_dir, test_name)
        if os.path.exists(test_fonts_dir):
            shutil.rmtree(test_fonts_dir, ignore_errors=True)

        test_reports_dir = os.path.join(self.reports_dir, test_name)
        if os.path.exists(test_reports_dir):
            shutil.rmtree(test_reports_dir, ignore_errors=True)

    def cleanup_all(self):
        """Clean up all test output directories"""
        import shutil

        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir, ignore_errors=True)

    def generate_test_report(self, test_name: str, report_data: dict, format: str = "json"):
        """Generate a test report in the specified format"""
        report_dir = self.get_test_reports_dir(test_name)

        if format.lower() == "json":
            import json

            report_file = os.path.join(report_dir, f"{test_name}_report.json")
            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2)
        elif format.lower() == "html":
            report_file = os.path.join(report_dir, f"{test_name}_report.html")
            self._generate_html_report(report_file, report_data)
        elif format.lower() == "txt":
            report_file = os.path.join(report_dir, f"{test_name}_report.txt")
            with open(report_file, "w") as f:
                f.write(str(report_data))

        return report_file

    def _generate_html_report(self, report_file: str, report_data: dict):
        """Generate an HTML test report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Font Management Test Report</h1>
                <p>Generated: {report_data.get("timestamp", "Unknown")}</p>
            </div>
            <div class="section">
                <h2>Test Summary</h2>
                <p>Total Tests: {report_data.get("total_tests", 0)}</p>
                <p class="success">Passed: {report_data.get("passed", 0)}</p>
                <p class="failure">Failed: {report_data.get("failed", 0)}</p>
                <p class="warning">Skipped: {report_data.get("skipped", 0)}</p>
            </div>
        </body>
        </html>
        """

        with open(report_file, "w") as f:
            f.write(html_content)


# Global test configuration instance
test_config = TestConfig()


def configure_test_output(output_dir: str):
    """Configure the test output directory"""
    test_config.output_dir = output_dir


def get_test_output_dir() -> str:
    """Get the current test output directory"""
    return test_config.output_dir


def get_test_temp_dir(test_name: str) -> str:
    """Get a temporary directory for a specific test"""
    return test_config.get_test_temp_dir(test_name)


def get_test_fonts_dir(test_name: str) -> str:
    """Get a fonts directory for a specific test"""
    return test_config.get_test_fonts_dir(test_name)


def get_test_reports_dir(test_name: str) -> str:
    """Get a reports directory for a specific test"""
    return test_config.get_test_reports_dir(test_name)


def cleanup_test_output(test_name: str):
    """Clean up output for a specific test"""
    test_config.cleanup_test_dir(test_name)


def cleanup_all_test_output():
    """Clean up all test output"""
    test_config.cleanup_all()


def generate_test_report(test_name: str, report_data: dict, format: str = "json") -> str:
    """Generate a test report in the specified format"""
    return test_config.generate_test_report(test_name, report_data, format)


def get_test_output_path(base_name: str, unique_id: str | None = None, ext: str = ".pdf") -> str:
    """
    Generate a test output file path with optional unique ID and extension.

    Args:
        base_name: Base name for the file
        unique_id: Optional unique identifier to append
        ext: File extension (default: .pdf)

    Returns:
        Full path to the test output file
    """
    if unique_id:
        filename = f"{base_name}_{unique_id}{ext}"
    else:
        filename = f"{base_name}{ext}"

    return os.path.join(test_config.output_dir, filename)


def get_unique_id() -> str:
    """
    Generate a unique identifier for test files.

    Returns:
        Unique string identifier
    """
    import random
    import string
    import time

    timestamp = str(int(time.time()))
    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{timestamp}_{random_suffix}"


def get_fixture_path(filename: str) -> str:
    """
    Get path to a test fixture file.

    Args:
        filename: Name of the fixture file

    Returns:
        Full path to the test fixture file
    """
    # Look for fixture files in the tests/fixtures directory
    return os.path.join("tests", "fixtures", filename)


def get_sample_input_path(filename: str) -> str:
    """
    Get path to a sample input file.

    Args:
        filename: Name of the sample file

    Returns:
        Full path to the sample input file
    """
    # Look for sample files in the tests/sample directory
    return os.path.join("tests", "sample", filename)


def get_debug_output_path(base_name: str, ext: str = ".log") -> str:
    """
    Get path for debug output files.

    Args:
        base_name: Base name for the debug file
        ext: File extension (default: .log)

    Returns:
        Full path to the debug output file
    """
    # Use the main settings for debug logs directory
    debug_logs_dir = settings.logging.debug_logs_dir or os.path.join(test_config.output_dir, "debug_logs")
    assert debug_logs_dir is not None
    os.makedirs(debug_logs_dir, exist_ok=True)
    return os.path.join(debug_logs_dir, f"{base_name}{ext}")
