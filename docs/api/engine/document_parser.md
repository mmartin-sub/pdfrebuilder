# document_parser

Universal document parser interface for the Multi-Format Document Engine.
This module provides a unified interface for parsing different document formats.

## Classes

### AssetManifest

Tracks extracted assets from a document

#### Methods

##### __init__()

##### add_image(path, original_name, metadata)

Add an image to the manifest

##### add_font(path, font_name, metadata)

Add a font to the manifest

##### add_asset(path, asset_type, metadata)

Add another type of asset to the manifest

##### to_dict()

Convert manifest to dictionary

### DocumentParser

Abstract base class for document parsers

#### Methods

##### can_parse(file_path)

Check if this parser can handle the given file

##### parse(file_path, extraction_flags)

Parse document into Universal IDM

##### extract_assets(file_path, output_dir)

Extract and save images, fonts, and other assets

### PDFParser

PDF document parser using PyMuPDF (fitz)

#### Methods

##### can_parse(file_path)

Check if this parser can handle the given file

##### parse(file_path, extraction_flags)

Parse PDF document into Universal IDM

##### extract_assets(file_path, output_dir)

Extract and save images, fonts, and other assets from PDF

### PSDParser

PSD document parser using psd-tools

#### Methods

##### can_parse(file_path)

Check if this parser can handle the given file

##### parse(file_path, extraction_flags)

Parse PSD document into Universal IDM

##### extract_assets(file_path, output_dir)

Extract and save images, fonts, and other assets from PSD

## Functions

### get_parser_for_file(file_path)

Get the appropriate parser for the given file

### parse_document(file_path, extraction_flags)

Parse a document using the appropriate parser based on file format

Args:
    file_path: Path to the document file
    extraction_flags: Optional flags to control extraction behavior

Returns:
    UniversalDocument: Parsed document structure

Raises:
    ValueError: If no parser is available for the file format
