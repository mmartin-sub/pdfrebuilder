import pytest
from unittest.mock import Mock, patch
from pdfrebuilder.font.utils import ensure_font_registered, get_font_error_reporter

def test_debug_font_error_reporter():
    reporter = get_font_error_reporter()
    reporter.clear_errors()

    mock_page = Mock()
    with patch("pdfrebuilder.font.utils.download_google_font", return_value=None):
        ensure_font_registered(mock_page, "NonExistentFont", verbose=False)

    print(reporter._error_counts)
    assert reporter._error_counts.get("discovery", 0) > 0
