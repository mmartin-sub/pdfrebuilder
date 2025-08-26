import unittest


class DebugCliImport(unittest.TestCase):
    def test_import(self):
        try:
            from scripts.download_essential_fonts import download_essential_fonts

            print("Successfully imported download_essential_fonts")
        except Exception as e:
            print(f"Failed to import: {e}")
            self.fail("Import failed")
