def test_document_error_recovery_workflow(self, document_font_integration_test):
        """Test error recovery in document processing workflow"""
        test_name, temp_dir, test_fonts_dir, font_validator, document_config = document_font_integration_test

        error_config = {
            "version": "1.0",
            "document_structure": [{
                "type": "page", "page_number": 0,
                "layers": [{"content": [
                    {"type": "text", "text": "Good text", "font_details": {"name": "helv"}},
                    {"type": "text", "text": "Problematic text", "font_details": {"name": "ProblematicFont"}},
                    {"type": "text", "text": "Unnamed T3 text", "font_details": {"name": "Unnamed-T3"}},
                ]}]
            }]
        }
        os.makedirs(test_fonts_dir, exist_ok=True)
        problematic_path = os.path.join(test_fonts_dir, "ProblematicFont.ttf")
        with open(problematic_path, "wb") as f:
            f.write(b"OTTO\x00\x01\x00\x00" + b"\x00" * 100)

        mock_page = Mock()
        def insert_font_side_effect(fontfile=None, fontname=None):
            if fontname == "ProblematicFont":
                raise Exception("Font loading error")
        mock_page.insert_font.side_effect = insert_font_side_effect

        def selective_exists(path):
            if str(path) == str(test_fonts_dir):
                return True
            if str(path) == str(problematic_path):
                return True
            return False

        with patch("pdfrebuilder.font.utils.TTFont") as mock_ttfont:
            def create_mock_font(font_path):
                mock_font = MagicMock()
                font_name = os.path.basename(font_path).replace(".ttf", "").replace(".otf", "")
                mock_name_table = Mock()
                mock_name_table.names = [Mock(nameID=1, platformID=3, string=font_name.encode())]
                mock_cmap_table = Mock()
                char_map = {ord(c): i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ")}
                mock_cmap_table.cmap = char_map
                mock_cmap_subtable = Mock()
                mock_cmap_subtable.tables = [mock_cmap_table]
                def getitem_side_effect(key):
                    if key == "name": return mock_name_table
                    elif key == "cmap": return mock_cmap_subtable
                    else: return Mock()
                mock_font.__getitem__.side_effect = getitem_side_effect
                return mock_font
            mock_ttfont.side_effect = create_mock_font

            with (
                patch("pdfrebuilder.settings.settings.font_management.downloaded_fonts_dir", "/nonexistent"),
                patch("pdfrebuilder.settings.settings.font_management.default_font", "helv"),
                patch("pdfrebuilder.font.utils.os.path.exists", side_effect=selective_exists),
                patch("pdfrebuilder.font.utils.download_google_font", return_value=None)
            ):
                for doc_unit in error_config["document_structure"]:
                    for layer in doc_unit["layers"]:
                        for element in layer["content"]:
                            if element["type"] == "text":
                                font_name = element["font_details"]["name"]
                                text_content = element["text"]
                                result = ensure_font_registered(mock_page, font_name, verbose=False, text=text_content)
                                if font_name == "helv":
                                    assert result == "helv"
                                elif font_name in ["ProblematicFont", "Unnamed-T3"]:
                                    assert result in ["helv", "Helvetica"]

        substitutions = font_validator.substitution_tracker
        problematic_substitutions = [s for s in substitutions if any(keyword in s.reason.lower() for keyword in ["not supported", "no font covers", "font not found", "loading error", "font registration failed"])]
        assert len(problematic_substitutions) > 0
        t3_substitutions = [s for s in substitutions if s.original_font == "Unnamed-T3"]
        assert len(t3_substitutions) == 1

        reporter = get_font_error_reporter()
        assert reporter._error_counts.get("registration", 0) > 0
