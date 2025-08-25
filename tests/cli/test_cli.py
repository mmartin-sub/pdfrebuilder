import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from pdfrebuilder.cli.main import app


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_version_callback(self):
        """Test the --version callback."""
        with patch("pdfrebuilder.cli.main.typer.echo") as mock_echo:
            result = self.runner.invoke(app, ["--version"], catch_exceptions=False)
            self.assertEqual(result.exit_code, 0)
            mock_echo.assert_called_once()
            # Check that the output starts with "pdfrebuilder version:"
            args, kwargs = mock_echo.call_args
            self.assertTrue(args[0].startswith("pdfrebuilder version:"))

    @patch("scripts.download_essential_fonts.download_essential_fonts")
    def test_download_fonts_command(self, mock_download):
        """Test the download-fonts command."""
        result = self.runner.invoke(app, ["download-fonts", "--priority", "high", "--force", "-v"])
        self.assertEqual(result.exit_code, 0)
        mock_download.assert_called_once_with(priority_filter="high", force_redownload=True, verbose=True)
