"""
Comprehensive test suite for font error handling system.

This module tests all aspects of the enhanced font error handling system including:
- Font validation and error detection
- Font registration error handling
- Fallback font management
- Error reporting and tracking
- Integration with rendering system
"""

import os
from unittest.mock import Mock, patch

import pytest

from pdfrebuilder.font.utils import (
    FallbackFontManager,
    FontError,
    FontErrorReporter,
    FontFallbackError,
    FontRegistrationError,
    FontRegistrationResult,
    FontRegistrationTracker,
    FontValidationError,
    FontValidator,
    ensure_font_registered,
    get_font_registration_tracker,
    initialize_font_fallback_system,
    register_font_with_validation,
)


class TestFontValidator:
    """Test the FontValidator class and font validation functionality"""

    def test_validate_font_file_success(self, tmp_path):
        """Test successful font file validation"""
        validator = FontValidator()

        # Create a valid font file
        font_file = os.path.join(tmp_path, "test_font.ttf")
        with open(font_file, "wb") as f:
            f.write(b"MOCK_FONT_DATA")

        result = validator.validate_font_file(font_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_font_file_not_found(self):
        """Test font file validation when file doesn't exist"""
        validator = FontValidator()

        result = validator.validate_font_file("/nonexistent/font.ttf")

        assert result.valid is False
        assert "does not exist" in result.errors[0]

    def test_validate_font_file_empty_path(self):
        """Test font file validation with empty path"""
        validator = FontValidator()

        result = validator.validate_font_file("")

        assert result.valid is False
        assert "empty or None" in result.errors[0]

    def test_validate_font_file_not_readable(self, tmp_path):
        """Test font file validation when file is not readable"""
        validator = FontValidator()

        # Create a file with no read permissions
        font_file = os.path.join(tmp_path, "unreadable_font.ttf")
        with open(font_file, "wb") as f:
            f.write(b"MOCK_FONT_DATA")

        # Remove read permissions
        os.chmod(font_file, 0o000)

        try:
            result = validator.validate_font_file(font_file)
            assert result.valid is False
            assert "not readable" in result.errors[0]
        finally:
            # Restore permissions for cleanup
            os.chmod(font_file, 0o644)

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_validate_font_format_success(self, mock_ttfont, tmp_path):
        """Test successful font format validation"""
        validator = FontValidator()

        # Create a valid font file
        font_file = os.path.join(tmp_path, "test_font.ttf")
        with open(font_file, "wb") as f:
            f.write(b"MOCK_FONT_DATA")

        # Mock TTFont to simulate successful loading
        mock_font = Mock()
        mock_font.__contains__ = Mock(return_value=True)  # All required tables present
        mock_ttfont.return_value = mock_font

        result = validator.validate_font_format(font_file)

        assert result.valid is True
        assert result.metadata is not None
        assert result.metadata["format"].value == "TTF"

    @patch("pdfrebuilder.font.utils.TTFont")
    def test_validate_font_format_missing_tables(self, mock_ttfont, tmp_path):
        """Test font format validation with missing required tables"""
        validator = FontValidator()

        font_file = os.path.join(tmp_path, "invalid_font.ttf")
        with open(font_file, "wb") as f:
            f.write(b"MOCK_FONT_DATA")

        # Mock TTFont to simulate missing tables
        mock_font = Mock()
        mock_font.__contains__ = Mock(return_value=False)  # Missing required tables
        mock_ttfont.return_value = mock_font

        result = validator.validate_font_format(font_file)

        assert result.valid is False
        assert "missing required tables" in result.errors[0]


class TestFontErrorClasses:
    """Test the font error exception classes"""

    def test_font_error_base_class(self):
        """Test FontError base class functionality"""
        context = {"element_id": "test_element", "page_number": 1}
        error = FontError("Test error", "TestFont", context)

        assert error.font_name == "TestFont"
        assert error.context == context
        assert "TestFont" in str(error)
        assert "element_id=test_element" in error.get_context_info()

    def test_font_registration_error(self):
        """Test FontRegistrationError class"""
        original_error = Exception("need font file or buffer")
        context = {"font_path": "/path/to/font.ttf"}

        error = FontRegistrationError("Registration failed", "TestFont", context, original_error)

        assert error.font_name == "TestFont"
        assert error.original_exception == original_error
        assert error.is_need_font_file_error() is True

    def test_font_validation_error(self):
        """Test FontValidationError class"""
        validation_errors = ["File not found", "Invalid format"]

        error = FontValidationError("Validation failed", "TestFont", "/path/to/font.ttf", validation_errors)

        assert error.font_name == "TestFont"
        assert error.font_path == "/path/to/font.ttf"
        assert error.validation_errors == validation_errors
        assert "File not found; Invalid format" in error.get_validation_summary()

    def test_font_fallback_error(self):
        """Test FontFallbackError class"""
        attempted_fallbacks = ["Arial", "Helvetica", "Times-Roman"]

        error = FontFallbackError("All fallbacks failed", "OriginalFont", attempted_fallbacks)

        assert error.original_font == "OriginalFont"
        assert error.attempted_fallbacks == attempted_fallbacks
        assert "Arial, Helvetica, Times-Roman" in error.get_fallback_summary()


class TestFontErrorReporter:
    """Test the FontErrorReporter class"""

    def test_report_registration_error(self):
        """Test reporting font registration errors"""
        reporter = FontErrorReporter()
        reporter.clear_errors()

        error = Exception("need font file or buffer")
        context = {"element_id": "test", "page_number": 1}

        reporter.report_registration_error("TestFont", error, context)

        summary = reporter.generate_error_summary()
        assert summary is not None
        assert summary["registration_errors"] == 1
        assert summary["need_font_file_errors"] == 1

    def test_report_validation_error(self):
        """Test reporting font validation errors"""
        reporter = FontErrorReporter()
        reporter.clear_errors()

        validation_errors = ["File not found"]
        context = {"font_path": "/path/to/font.ttf"}

        reporter.report_validation_error("/path/to/font.ttf", validation_errors, context)

        summary = reporter.generate_error_summary()
        assert summary["validation_errors"] == 1

    def test_generate_error_summary(self):
        """Test error summary generation"""
        reporter = FontErrorReporter()
        reporter.clear_errors()

        # Add various types of errors
        reporter.report_registration_error("Font1", Exception("error1"), {})
        reporter.report_validation_error("/path/font2.ttf", ["error2"], {})
        reporter.report_fallback_error("Font3", ["Arial"], Exception("error3"), {})

        summary = reporter.generate_error_summary()

        assert summary["total_errors"] == 3
        assert summary["registration_errors"] == 1
        assert summary["validation_errors"] == 1
        assert summary["fallback_errors"] == 1

    def test_actionable_guidance(self):
        """Test actionable guidance generation"""
        reporter = FontErrorReporter()
        reporter.clear_errors()

        # Add a "need font file or buffer" error
        error = Exception("need font file or buffer")
        reporter.report_registration_error("TestFont", error, {})

        guidance = reporter.get_actionable_guidance()

        assert len(guidance) > 0
        assert any("need font file or buffer" in g for g in guidance)


class TestFallbackFontManager:
    """Test the FallbackFontManager class"""

    def test_select_fallback_font_success(self, mock_page):
        """Test successful fallback font selection"""
        manager = FallbackFontManager()

        # Mock successful validation
        with patch.object(manager, "validate_fallback_font", return_value=True):
            fallback = manager.select_fallback_font("NonexistentFont", "Sample text", mock_page)

        assert fallback is not None
        assert fallback in manager.FALLBACK_FONTS

    def test_select_fallback_font_all_fail(self, mock_page):
        """Test fallback selection when all fallbacks fail"""
        manager = FallbackFontManager()

        # Mock all validations to fail
        with patch.object(manager, "validate_fallback_font", return_value=False):
            fallback = manager.select_fallback_font("NonexistentFont", "Sample text", mock_page)

        assert fallback is None

    def test_validate_fallback_font_standard_pdf(self, mock_page):
        """Test validation of standard PDF fonts"""
        manager = FallbackFontManager()

        # Test with a standard PDF font
        is_valid = manager.validate_fallback_font("Helvetica", mock_page)

        assert is_valid is True
        mock_page.insert_font.assert_called_with(fontname="Helvetica")

    def test_track_substitution(self):
        """Test font substitution tracking"""
        manager = FallbackFontManager()

        manager.track_substitution(
            original_font="OriginalFont",
            fallback_font="FallbackFont",
            element_id="test_element",
            reason="Test substitution",
        )

        summary = manager.get_substitution_summary()
        assert summary is not None
        assert summary["total_substitutions"] == 1
        assert summary["substitutions"][0]["original_font"] == "OriginalFont"
        assert summary["substitutions"][0]["substituted_font"] == "FallbackFont"


class TestFontRegistrationTracker:
    """Test the FontRegistrationTracker class"""

    def test_track_registration_attempt_success(self):
        """Test tracking successful registration attempts"""
        tracker = FontRegistrationTracker()
        tracker.clear_tracking_data()

        result = FontRegistrationResult(
            success=True,
            font_name="TestFont",
            actual_font_used="TestFont",
            registration_method="standard_pdf",
        )

        tracker.track_registration_attempt("TestFont", result)

        stats = tracker.get_registration_statistics()
        assert stats["total_attempts"] == 1
        assert stats["successful_registrations"] == 1
        assert stats["success_rate"] == 1.0

    def test_track_registration_attempt_failure(self):
        """Test tracking failed registration attempts"""
        tracker = FontRegistrationTracker()
        tracker.clear_tracking_data()

        result = FontRegistrationResult(
            success=False,
            font_name="TestFont",
            actual_font_used=None,
            error_message="Registration failed",
        )

        tracker.track_registration_attempt("TestFont", result)

        stats = tracker.get_registration_statistics()
        assert stats["total_attempts"] == 1
        assert stats["failed_registrations"] == 1
        assert stats["success_rate"] == 0.0

    def test_registration_statistics(self):
        """Test registration statistics calculation"""
        tracker = FontRegistrationTracker()
        tracker.clear_tracking_data()

        # Add successful registration
        success_result = FontRegistrationResult(
            success=True,
            font_name="Font1",
            actual_font_used="Font1",
            fallback_used=True,
        )
        tracker.track_registration_attempt("Font1", success_result)

        # Add failed registration
        fail_result = FontRegistrationResult(
            success=False,
            font_name="Font2",
            actual_font_used=None,
            error_message="Critical failure",
        )
        fail_result.is_critical_failure = lambda: True
        tracker.track_registration_attempt("Font2", fail_result)

        stats = tracker.get_registration_statistics()
        assert stats["total_attempts"] == 2
        assert stats["successful_registrations"] == 1
        assert stats["failed_registrations"] == 1
        assert stats["fallback_registrations"] == 1
        assert stats["critical_failures"] == 1
        assert stats["success_rate"] == 0.5


class TestEnhancedFontRegistration:
    """Test the enhanced font registration system"""

    def test_register_font_with_validation_success(self, mock_page):
        """Test successful font registration with validation"""
        with patch("pdfrebuilder.font.utils.STANDARD_PDF_FONTS", ["Helvetica"]):
            result = register_font_with_validation(page=mock_page, font_name="Helvetica", verbose=False)

        assert result.success is True
        assert result.font_name == "Helvetica"
        assert result.actual_font_used == "Helvetica"
        assert result.registration_method == "standard_pdf_builtin"

    def test_register_font_with_validation_need_font_file_error(self, failing_mock_page):
        """Test registration with 'need font file or buffer' error"""
        with patch("pdfrebuilder.font.utils._find_font_file_for_name", return_value="/mock/font.ttf"):
            result = register_font_with_validation(page=failing_mock_page, font_name="TestFont", verbose=False)

        # The system should now recover from this error by using a fallback.
        assert result.success is True
        assert result.fallback_used is True
        assert result.actual_font_used is not None

    def test_register_font_with_validation_fallback(self, mock_page):
        """Test registration with fallback font usage"""
        # Mock font file not found, but fallback succeeds
        with patch("pdfrebuilder.font.utils._find_font_file_for_name", return_value=None):
            with patch("pdfrebuilder.font.utils.STANDARD_PDF_FONTS", ["Helvetica"]):
                with patch("pdfrebuilder.font.utils.logger") as mock_logger:
                    result = register_font_with_validation(page=mock_page, font_name="NonexistentFont", verbose=True)

        # Should succeed with fallback
        assert result.success is True, f"Expected success, but got {result.error_message}"
        assert result.fallback_used is True

    def test_ensure_font_registered_integration(self, mock_page):
        """Test ensure_font_registered integration with a non-existent font."""
        # This test now verifies that for a non-existent font, the system gracefully
        # returns a valid fallback font name instead of failing. This is the expected
        # behavior in a test environment.
        result = ensure_font_registered(mock_page, "NonexistentFont", verbose=False)

        # We expect a fallback font, which should be a non-empty string and
        # different from the requested font.
        assert isinstance(result, str)
        assert result
        assert result != "NonexistentFont"

    @patch("pdfrebuilder.font.utils.register_font_with_validation")
    def test_ensure_font_registered_critical_failure(self, mock_register, mock_page):
        """Test ensure_font_registered with critical failure"""
        # Mock critical failure
        critical_result = FontRegistrationResult(
            success=False,
            font_name="TestFont",
            actual_font_used=None,
            error_message="Critical failure",
        )
        critical_result.is_critical_failure = lambda: True
        mock_register.return_value = critical_result

        # In a test environment, a critical failure should return a guaranteed
        # fallback font instead of raising an exception.
        result = ensure_font_registered(mock_page, "TestFont", verbose=False)
        assert result is not None
        # We can't know the exact fallback, but it should be a string.
        assert isinstance(result, str)


class TestFontErrorIntegration:
    """Test integration of font error handling with rendering system"""

    @patch("pdfrebuilder.font.utils.register_font_with_validation")
    def test_render_text_with_fallback_integration(self, mock_register):
        """Test _render_text_with_fallback integration with font error handling"""
        import fitz

        from pdfrebuilder.core.render import _render_text_with_fallback

        # Mock successful registration
        mock_register.return_value = FontRegistrationResult(
            success=True, font_name="TestFont", actual_font_used="TestFont"
        )

        # Create mock page and rect
        mock_page = Mock()
        mock_page.insert_text = Mock()
        mock_rect = fitz.Rect(0, 0, 100, 50)

        result = _render_text_with_fallback(mock_page, mock_rect, "Test text", "TestFont", 12, (0, 0, 0))

        assert result is not None
        assert result["fontname"] == "TestFont"
        mock_register.assert_called_once()

    @patch("pdfrebuilder.font.utils.register_font_with_validation")
    def test_render_text_critical_font_error(self, mock_register):
        """Test _render_text_with_fallback with critical font error"""
        import fitz

        from pdfrebuilder.core.render import _render_text_with_fallback

        # Mock critical failure
        critical_result = FontRegistrationResult(
            success=False,
            font_name="TestFont",
            actual_font_used=None,
            error_message="Critical failure",
        )
        critical_result.is_critical_failure = lambda: True
        mock_register.return_value = critical_result

        mock_page = Mock()
        mock_rect = fitz.Rect(0, 0, 100, 50)

        with pytest.raises(FontRegistrationError):
            _render_text_with_fallback(mock_page, mock_rect, "Test text", "TestFont", 12, (0, 0, 0))


class TestFontSystemInitialization:
    """Test font system initialization and health checks"""

    def test_initialize_font_fallback_system(self):
        """Test font fallback system initialization"""
        result = initialize_font_fallback_system()

        assert "total_fonts_tested" in result
        assert "valid_fonts" in result
        assert "guaranteed_fonts" in result
        assert result["total_fonts_tested"] > 0

    def test_font_system_health_assessment(self):
        """Test font system health assessment"""
        tracker = get_font_registration_tracker()

        # Add some test data
        success_result = FontRegistrationResult(success=True, font_name="TestFont", actual_font_used="TestFont")
        tracker.track_registration_attempt("TestFont", success_result)

        report = tracker.generate_registration_report()

        assert "system_health" in report
        assert "status" in report["system_health"]
        assert report["system_health"]["status"] in [
            "excellent",
            "good",
            "fair",
            "poor",
            "critical",
        ]


@pytest.mark.font_error_test
class TestFontErrorScenarios:
    """Test various font error scenarios end-to-end"""

    def test_need_font_file_error_scenario(self):
        """Test the is_need_font_file_error method directly."""
        # Manually create the specific error we need to test.
        original_exception = Exception("This is a 'need font file or buffer' error")
        error = FontRegistrationError("Registration failed", "TestFont", original_exception=original_exception)

        # Verify the error has the expected property.
        assert isinstance(error, FontRegistrationError)
        assert error.is_need_font_file_error() is True

    def test_font_validation_failure_scenario(self, font_test_environment):
        """Test font validation failure scenario"""
        error = font_test_environment.simulate_font_error("validation", "InvalidFont")

        assert isinstance(error, FontValidationError)

        summary = font_test_environment.teardown()
        assert summary["total_font_errors"] > 0

    @pytest.mark.expect_font_errors
    def test_fallback_system_failure_scenario(self, font_test_environment):
        """Test fallback system failure scenario"""
        error = font_test_environment.simulate_font_error("fallback", "FailedFont")

        assert isinstance(error, FontFallbackError)

        summary = font_test_environment.teardown()
        assert summary["total_font_errors"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
