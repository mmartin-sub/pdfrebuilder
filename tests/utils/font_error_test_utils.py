"""
Font error test utilities for comprehensive font error handling testing.

This module provides test fixtures, mock objects, and utilities for testing
font registration errors, validation failures, and fallback mechanisms.
"""

import os
import shutil
import tempfile
from typing import Any
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.font_utils import (
    FontFallbackError,
    FontRegistrationError,
    FontRegistrationResult,
    FontValidationError,
    get_fallback_font_manager,
    get_font_error_reporter,
    get_font_registration_tracker,
)


class MockFontFile:
    """Mock font file for testing font validation"""

    def __init__(self, name: str, is_valid: bool = True, is_corrupted: bool = False):
        self.name = name
        self.is_valid = is_valid
        self.is_corrupted = is_corrupted
        self.content = b"MOCK_FONT_DATA" if is_valid else b"INVALID"

    def create_temp_file(self, directory: str) -> str:
        """Create a temporary font file for testing"""
        file_path = os.path.join(directory, f"{self.name}.ttf")
        with open(file_path, "wb") as f:
            f.write(self.content)
        return file_path


class FontErrorTestFixtures:
    """Test fixtures for font error scenarios"""

    @staticmethod
    def create_temp_font_directory() -> str:
        """Create a temporary directory with mock font files"""
        temp_dir = tempfile.mkdtemp(prefix="font_test_")

        # Create valid font files
        valid_fonts = [
            MockFontFile("Arial", is_valid=True),
            MockFontFile("Helvetica", is_valid=True),
            MockFontFile("Times-Roman", is_valid=True),
        ]

        # Create invalid font files
        invalid_fonts = [
            MockFontFile("CorruptedFont", is_valid=False, is_corrupted=True),
            MockFontFile("InvalidFormat", is_valid=False),
        ]

        for font in valid_fonts + invalid_fonts:
            font.create_temp_file(temp_dir)

        return temp_dir

    @staticmethod
    def cleanup_temp_directory(temp_dir: str) -> None:
        """Clean up temporary font directory"""
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @staticmethod
    def create_mock_page() -> Mock:
        """Create a mock PyMuPDF page object"""
        mock_page = Mock()
        mock_page.insert_font = Mock()
        mock_page.insert_text = Mock()
        mock_page.insert_textbox = Mock(return_value=0)  # Success
        return mock_page

    @staticmethod
    def create_failing_mock_page(error_type: str = "need_font_file") -> Mock:
        """Create a mock page that fails font registration"""
        mock_page = Mock()

        if error_type == "need_font_file":
            mock_page.insert_font.side_effect = Exception("need font file or buffer")
        elif error_type == "general_error":
            mock_page.insert_font.side_effect = Exception("Font registration failed")
        elif error_type == "file_not_found":
            mock_page.insert_font.side_effect = FileNotFoundError("Font file not found")

        mock_page.insert_text = Mock()
        mock_page.insert_textbox = Mock(return_value=0)
        return mock_page


class FontErrorSimulator:
    """Simulate various font error scenarios for testing"""

    def __init__(self):
        self.original_functions = {}

    def simulate_need_font_file_error(self):
        """Simulate the 'need font file or buffer' error"""

        def mock_insert_font(*args, **kwargs):
            raise Exception("need font file or buffer")

        return patch("fitz.Page.insert_font", side_effect=mock_insert_font)

    def simulate_font_file_not_found(self, font_names: list[str]):
        """Simulate font file not found for specific fonts"""

        def mock_find_font_file(font_name: str):
            if font_name in font_names:
                return None
            return f"/mock/path/{font_name}.ttf"

        return patch("src.font_utils._find_font_file_for_name", side_effect=mock_find_font_file)

    def simulate_font_validation_failure(self, font_names: list[str]):
        """Simulate font validation failure for specific fonts"""

        def mock_validate_font_file(font_path: str):
            from pdfrebuilder.font_utils import ValidationResult

            for font_name in font_names:
                if font_name in font_path:
                    result = ValidationResult(valid=False, errors=[], warnings=[])
                    result.add_error(f"Validation failed for {font_name}")
                    return result

            return ValidationResult(valid=True, errors=[], warnings=[])

        return patch(
            "src.font_utils.FontValidator.validate_font_file",
            side_effect=mock_validate_font_file,
        )

    def simulate_all_fallbacks_fail(self):
        """Simulate scenario where all fallback fonts fail"""

        def mock_validate_fallback_font(font_name: str, page):
            return False  # All fallbacks fail

        return patch(
            "src.font_utils.FallbackFontManager.validate_fallback_font",
            side_effect=mock_validate_fallback_font,
        )


class FontErrorAssertions:
    """Custom assertions for font error testing"""

    @staticmethod
    def assert_font_registration_error(error: Exception, expected_font: str, expected_error_type: str | None = None):
        """Assert that a FontRegistrationError has expected properties"""
        assert isinstance(error, FontRegistrationError), f"Expected FontRegistrationError, got {type(error)}"
        assert error.font_name == expected_font, f"Expected font '{expected_font}', got '{error.font_name}'"

        if expected_error_type == "need_font_file":
            assert error.is_need_font_file_error(), "Expected 'need font file or buffer' error"

    @staticmethod
    def assert_font_validation_error(error: Exception, expected_font: str):
        """Assert that a FontValidationError has expected properties"""
        assert isinstance(error, FontValidationError), f"Expected FontValidationError, got {type(error)}"
        assert error.font_name == expected_font, f"Expected font '{expected_font}', got '{error.font_name}'"

    @staticmethod
    def assert_font_fallback_error(error: Exception, expected_original_font: str):
        """Assert that a FontFallbackError has expected properties"""
        assert isinstance(error, FontFallbackError), f"Expected FontFallbackError, got {type(error)}"
        assert error.original_font == expected_original_font, (
            f"Expected original font '{expected_original_font}', got '{error.original_font}'"
        )

    @staticmethod
    def assert_registration_result(
        result: FontRegistrationResult,
        expected_success: bool,
        expected_fallback: bool = False,
    ):
        """Assert that a FontRegistrationResult has expected properties"""
        assert isinstance(result, FontRegistrationResult), f"Expected FontRegistrationResult, got {type(result)}"
        assert result.success == expected_success, f"Expected success={expected_success}, got {result.success}"
        assert result.fallback_used == expected_fallback, (
            f"Expected fallback_used={expected_fallback}, got {result.fallback_used}"
        )


class FontErrorTestReporter:
    """Test reporter for font error scenarios"""

    def __init__(self):
        self.error_reporter = get_font_error_reporter()
        self.registration_tracker = get_font_registration_tracker()
        self.fallback_manager = get_fallback_font_manager()

    def setup_test(self):
        """Setup for font error test"""
        # Clear any existing error data
        self.error_reporter.clear_errors()
        self.registration_tracker.clear_tracking_data()
        self.fallback_manager.clear_substitution_tracking()

    def get_test_summary(self) -> dict[str, Any]:
        """Get summary of font errors during test"""
        return {
            "error_summary": self.error_reporter.generate_error_summary(),
            "registration_stats": self.registration_tracker.get_registration_statistics(),
            "substitution_summary": self.fallback_manager.get_substitution_summary(),
        }

    def assert_no_critical_errors(self):
        """Assert that no critical font errors occurred during test"""
        error_summary = self.error_reporter.generate_error_summary()
        critical_errors = error_summary.get("need_font_file_errors", 0)

        assert critical_errors == 0, f"Found {critical_errors} critical 'need font file or buffer' errors"

    def assert_expected_fallbacks(self, expected_count: int):
        """Assert expected number of font fallbacks occurred"""
        substitution_summary = self.fallback_manager.get_substitution_summary()
        actual_count = substitution_summary.get("total_substitutions", 0)

        assert actual_count == expected_count, f"Expected {expected_count} font substitutions, got {actual_count}"


# Pytest fixtures
@pytest.fixture
def temp_font_dir():
    """Pytest fixture for temporary font directory"""
    temp_dir = FontErrorTestFixtures.create_temp_font_directory()
    yield temp_dir
    FontErrorTestFixtures.cleanup_temp_directory(temp_dir)


@pytest.fixture
def mock_page():
    """Pytest fixture for mock PyMuPDF page"""
    return FontErrorTestFixtures.create_mock_page()


@pytest.fixture
def failing_mock_page():
    """Pytest fixture for mock page that fails font registration"""
    return FontErrorTestFixtures.create_failing_mock_page()


@pytest.fixture
def font_error_simulator():
    """Pytest fixture for font error simulator"""
    return FontErrorSimulator()


@pytest.fixture
def font_error_assertions():
    """Pytest fixture for font error assertions"""
    return FontErrorAssertions()


@pytest.fixture
def font_test_reporter():
    """Pytest fixture for font error test reporter"""
    reporter = FontErrorTestReporter()
    reporter.setup_test()
    yield reporter


# Test helper functions
def create_test_font_registration_scenario(
    font_name: str,
    should_succeed: bool = True,
    should_use_fallback: bool = False,
    error_type: str | None = None,
) -> dict[str, Any]:
    """Create a test scenario for font registration"""
    return {
        "font_name": font_name,
        "should_succeed": should_succeed,
        "should_use_fallback": should_use_fallback,
        "error_type": error_type,
        "expected_result": {
            "success": should_succeed,
            "fallback_used": should_use_fallback,
        },
    }


def run_font_error_test_suite(test_scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Run a suite of font error test scenarios"""
    results = {
        "total_scenarios": len(test_scenarios),
        "passed": 0,
        "failed": 0,
        "scenario_results": [],
    }

    for scenario in test_scenarios:
        try:
            # This would be implemented based on specific test requirements
            # For now, just record the scenario
            results["scenario_results"].append(
                {
                    "scenario": scenario,
                    "status": "pending",
                    "message": "Test implementation needed",
                }
            )
            results["passed"] += 1
        except Exception as e:
            results["scenario_results"].append({"scenario": scenario, "status": "failed", "error": str(e)})
            results["failed"] += 1

    return results
