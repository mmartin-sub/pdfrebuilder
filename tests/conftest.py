"""
Pytest configuration and fixtures for comprehensive test support.

This module provides:
- Font error handling and validation fixtures
- Standardized test directory fixtures
- Test configuration and setup utilities
- Comprehensive test reporting capabilities
"""

import logging
import os
import shutil
import sys
from typing import Any
from unittest.mock import patch

import pytest

from pdfrebuilder.font.utils import (
    FontFallbackError,
    FontRegistrationError,
    FontValidationError,
    get_fallback_font_manager,
    get_font_error_reporter,
    get_font_registration_tracker,
    initialize_font_fallback_system,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from config import cleanup_test_output, get_test_fonts_dir, get_test_reports_dir, get_test_temp_dir, test_config

# ============================================================================
# STANDARDIZED TEST DIRECTORY FIXTURES
# ============================================================================


@pytest.fixture
def test_temp_dir(request):
    """
    Provide a temporary directory for test files.

    This fixture creates a test-specific temporary directory that is automatically
    cleaned up after the test completes. The directory name includes the test name
    for easy identification.

    Returns:
        str: Path to the temporary directory
    """
    test_name = f"{request.cls.__name__ if request.cls else 'function'}_{request.function.__name__}"
    temp_dir = get_test_temp_dir(test_name)

    yield temp_dir

    # Cleanup after test
    cleanup_test_output(test_name)


@pytest.fixture
def test_fonts_dir(request):
    """
    Provide a fonts directory for test font files.

    This fixture creates a test-specific fonts directory for storing test font files.
    The directory is automatically cleaned up after the test completes.

    Returns:
        str: Path to the fonts directory
    """
    test_name = f"{request.cls.__name__ if request.cls else 'function'}_{request.function.__name__}"
    fonts_dir = get_test_fonts_dir(test_name)

    yield fonts_dir

    # Cleanup after test
    cleanup_test_output(test_name)


@pytest.fixture
def test_reports_dir(request):
    """
    Provide a reports directory for test output files.

    This fixture creates a test-specific reports directory for storing test reports,
    logs, and other output files. The directory is automatically cleaned up after
    the test completes.

    Returns:
        str: Path to the reports directory
    """
    test_name = f"{request.cls.__name__ if request.cls else 'function'}_{request.function.__name__}"
    reports_dir = get_test_reports_dir(test_name)

    yield reports_dir

    # Cleanup after test
    cleanup_test_output(test_name)


@pytest.fixture
def temp_font_dir(test_fonts_dir):
    """
    Legacy fixture name for backward compatibility.

    This fixture provides the same functionality as test_fonts_dir but with
    the legacy name that some tests may still be using.

    Returns:
        str: Path to the fonts directory
    """
    return test_fonts_dir


@pytest.fixture
def test_output_dir(request):
    """
    Provide a general output directory for test files.

    This fixture creates a test-specific output directory for any test files
    that don't fit into the specific categories (temp, fonts, reports).

    Returns:
        str: Path to the output directory
    """
    test_name = f"{request.cls.__name__ if request.cls else 'function'}_{request.function.__name__}"
    output_dir = os.path.join(test_config.output_dir, test_name)
    os.makedirs(output_dir, exist_ok=True)

    yield output_dir

    # Cleanup after test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)


@pytest.fixture
def sample_pdf_path():
    """
    Provide path to sample PDF files for testing.

    This fixture provides access to sample PDF files stored in the tests/sample
    directory. It ensures the sample directory exists and can be used by tests.

    Returns:
        callable: Function that takes a filename and returns the full path
    """
    sample_dir = os.path.join("tests", "sample")
    os.makedirs(sample_dir, exist_ok=True)

    def get_sample_path(filename: str) -> str:
        """Get the full path to a sample file."""
        return os.path.join(sample_dir, filename)

    return get_sample_path


@pytest.fixture
def create_test_font():
    """
    Utility fixture for creating test font files.

    This fixture provides a function to create mock font files for testing
    purposes. The created files have minimal font headers to avoid parsing errors.

    Returns:
        callable: Function that creates a test font file
    """

    def _create_font(font_path: str, font_name: str | None = None) -> str:
        """
        Create a test font file.

        Args:
            font_path: Path where the font file should be created
            font_name: Optional font name (defaults to filename without extension)

        Returns:
            str: Path to the created font file
        """
        os.makedirs(os.path.dirname(font_path), exist_ok=True)

        # Create minimal font file with basic header to avoid "Not a TrueType" errors
        with open(font_path, "wb") as f:
            f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)

        return font_path

    return _create_font


@pytest.fixture
def create_test_config():
    """
    Utility fixture for creating test configuration files.

    This fixture provides a function to create test configuration files
    in JSON format for testing document processing workflows.

    Returns:
        callable: Function that creates a test configuration file
    """

    def _create_config(config_path: str, config_data: dict) -> str:
        """
        Create a test configuration file.

        Args:
            config_path: Path where the config file should be created
            config_data: Configuration data to write

        Returns:
            str: Path to the created configuration file
        """
        import json

        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        return config_path

    return _create_config


# ============================================================================
# EXISTING FIXTURES (Font Error Handling)
# ============================================================================


@pytest.fixture
def log_file(tmp_path_factory):
    """Provide a temporary log file path for tests."""
    # Create a unique log file for this test session
    log_dir = tmp_path_factory.mktemp("pytest-logs")
    log_file_path = log_dir / "test.log"
    return str(log_file_path)


class FontErrorDetector:
    """Detects and tracks font errors during test execution"""

    def __init__(self):
        self.font_errors: list[Exception] = []
        self.critical_errors: list[Exception] = []
        self.error_reporter = get_font_error_reporter()
        self.registration_tracker = get_font_registration_tracker()
        self.fallback_manager = get_fallback_font_manager()

    def setup_error_detection(self):
        """Setup error detection for the test session"""
        # Clear any existing errors
        self.font_errors.clear()
        self.critical_errors.clear()
        self.error_reporter.clear_errors()
        self.registration_tracker.clear_tracking_data()

        # Initialize font fallback system
        try:
            initialize_font_fallback_system()
        except Exception as e:
            logging.warning(f"Failed to initialize font fallback system: {e}")

    def record_font_error(self, error: Exception):
        """Record a font error for later analysis"""
        self.font_errors.append(error)

        # Check if this is a critical error that should fail tests
        if isinstance(error, FontRegistrationError):
            if error.is_need_font_file_error():
                self.critical_errors.append(error)
        elif isinstance(error, FontFallbackError):
            # Fallback system failures are always critical
            self.critical_errors.append(error)

    def check_for_critical_errors(self):
        """Check for critical font errors and fail test if found"""
        if self.critical_errors:
            error_messages = []
            for error in self.critical_errors:
                error_messages.append(f"CRITICAL FONT ERROR: {error}")

            pytest.fail(
                f"Test failed due to {len(self.critical_errors)} critical font error(s):\n" + "\n".join(error_messages)
            )

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of font errors detected during test"""
        return {
            "total_font_errors": len(self.font_errors),
            "critical_errors": len(self.critical_errors),
            "error_reporter_summary": self.error_reporter.generate_error_summary(),
            "registration_stats": self.registration_tracker.get_registration_statistics(),
            "substitution_summary": self.fallback_manager.get_substitution_summary(),
        }


# Global font error detector instance
_font_error_detector = FontErrorDetector()


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--range",
        action="store",
        default=None,
        help="Range of elements to test (e.g., '1-10' or '5')",
    )
    parser.addoption(
        "--draw_type",
        action="store",
        default=None,
        help="Comma-separated list of element types to test (e.g., 'text,rectangle')",
    )


def pytest_configure(config):
    """Configure pytest for font error detection"""
    # Add custom markers
    config.addinivalue_line("markers", "font_error_test: mark test as font error handling test")
    config.addinivalue_line("markers", "expect_font_errors: mark test as expecting font errors")
    config.addinivalue_line("markers", "critical_font_test: mark test as critical font functionality test")

    # Setup font error detection
    _font_error_detector.setup_error_detection()


def pytest_runtest_setup(item):
    """Setup for each test item"""
    # Clear font error tracking for each test
    _font_error_detector.font_errors.clear()
    _font_error_detector.critical_errors.clear()


def pytest_runtest_teardown(item, nextitem):
    """Teardown after each test item"""
    # Check for critical font errors unless test expects them
    if not item.get_closest_marker("expect_font_errors"):
        _font_error_detector.check_for_critical_errors()

    # Log font error summary if there were any errors
    error_summary = _font_error_detector.get_error_summary()
    if error_summary["total_font_errors"] > 0:
        logging.info(f"Font error summary for {item.name}: {error_summary}")


@pytest.fixture(scope="session")
def font_error_detector():
    """Session-scoped fixture for font error detector"""
    return _font_error_detector


@pytest.fixture
def font_error_validation():
    """Fixture for font error validation in tests"""

    class FontErrorValidator:
        def __init__(self):
            self.detector = _font_error_detector

        def assert_no_font_errors(self):
            """Assert that no font errors occurred"""
            assert len(self.detector.font_errors) == 0, (
                f"Expected no font errors, but found {len(self.detector.font_errors)}"
            )

        def assert_no_critical_errors(self):
            """Assert that no critical font errors occurred"""
            assert len(self.detector.critical_errors) == 0, (
                f"Expected no critical font errors, but found {len(self.detector.critical_errors)}"
            )

        def assert_expected_font_errors(self, expected_count: int):
            """Assert expected number of font errors"""
            actual_count = len(self.detector.font_errors)
            assert actual_count == expected_count, f"Expected {expected_count} font errors, but found {actual_count}"

        def get_font_errors(self) -> list[Exception]:
            """Get list of font errors that occurred"""
            return self.detector.font_errors.copy()

        def get_critical_errors(self) -> list[Exception]:
            """Get list of critical font errors that occurred"""
            return self.detector.critical_errors.copy()

    return FontErrorValidator()


@pytest.fixture
def mock_font_registration_failure():
    """Fixture to mock font registration failures"""

    def _mock_failure(error_type: str = "need_font_file"):
        if error_type == "need_font_file":
            error = Exception("need font file or buffer")
        elif error_type == "file_not_found":
            error = FileNotFoundError("Font file not found")
        else:
            error = Exception("Font registration failed")

        return patch("fitz.Page.insert_font", side_effect=error)

    return _mock_failure


@pytest.fixture
def mock_page():
    """Fixture providing a mock page object for font testing."""
    from unittest.mock import Mock

    page = Mock()
    page.insert_font = Mock(return_value=None)
    return page


@pytest.fixture
def failing_mock_page():
    """Fixture providing a mock page object that fails font registration."""
    from unittest.mock import Mock

    page = Mock()
    page.insert_font = Mock(side_effect=Exception("need font file or buffer"))
    return page


@pytest.fixture
def font_system_health_check():
    """Fixture to check font system health"""

    def _health_check():
        """Perform comprehensive font system health check"""
        try:
            # Initialize font systems
            initialize_font_fallback_system()

            # Get system status
            error_reporter = get_font_error_reporter()
            registration_tracker = get_font_registration_tracker()
            fallback_manager = get_fallback_font_manager()

            health_report = {
                "font_fallback_system": "initialized",
                "error_reporter": "active",
                "registration_tracker": "active",
                "fallback_manager": "active",
                "system_status": "healthy",
            }

            return health_report

        except Exception as e:
            return {"system_status": "unhealthy", "error": str(e)}

    return _health_check


# Custom pytest assertions
def pytest_assertrepr_compare(op, left, right):
    """Custom assertion representations for font errors"""
    if isinstance(left, FontRegistrationError) and op == "==":
        return [
            "FontRegistrationError comparison failed:",
            f"  Left font: {left.font_name}",
            f"  Right font: {right.font_name if hasattr(right, 'font_name') else right}",
            f"  Left error: {left}",
            f"  Left context: {left.context}",
        ]


# Test decorators
def font_error_test(func):
    """Decorator to mark a test as a font error handling test"""
    return pytest.mark.font_error_test(func)


def expect_font_errors(func):
    """Decorator to mark a test as expecting font errors"""
    return pytest.mark.expect_font_errors(func)


def critical_font_test(func):
    """Decorator to mark a test as critical font functionality test"""
    return pytest.mark.critical_font_test(func)


# Pytest hooks for font error handling
def pytest_exception_interact(node, call, report):
    """Handle exceptions during test execution"""
    if call.excinfo and call.excinfo.type in (
        FontRegistrationError,
        FontValidationError,
        FontFallbackError,
    ):
        # Record font error
        _font_error_detector.record_font_error(call.excinfo.value)


# Custom pytest markers and fixtures for font testing
@pytest.fixture
def font_test_environment():
    """Setup comprehensive font testing environment"""

    class FontTestEnvironment:
        def __init__(self):
            self.error_detector = _font_error_detector
            self.error_reporter = get_font_error_reporter()
            self.registration_tracker = get_font_registration_tracker()
            self.fallback_manager = get_fallback_font_manager()

        def setup(self):
            """Setup font test environment"""
            self.error_detector.setup_error_detection()
            return self

        def teardown(self):
            """Teardown font test environment"""
            # Generate final report
            return self.error_detector.get_error_summary()

        def simulate_font_error(self, error_type: str, font_name: str = "TestFont"):
            """Simulate a font error for testing"""
            if error_type == "registration":
                error = FontRegistrationError(
                    message="Test font registration error",
                    font_name=font_name,
                    context={"test": True},
                )
            elif error_type == "validation":
                error = FontValidationError(
                    message="Test font validation error",
                    font_name=font_name,
                    context={"test": True},
                )
            elif error_type == "fallback":
                error = FontFallbackError(
                    message="Test font fallback error",
                    original_font=font_name,
                    context={"test": True},
                )
            else:
                error = Exception(f"Unknown font error type: {error_type}")

            self.error_detector.record_font_error(error)
            return error

    env = FontTestEnvironment()
    env.setup()
    yield env
    env.teardown()
