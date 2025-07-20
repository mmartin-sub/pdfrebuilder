# pdf_engine

## Classes

### PDFEngineBase

Abstract base class for PDF engines (e.g., fitz, reportlab).
Provides metadata, extraction, and generation interfaces.

#### Methods

##### extract(input_pdf_path)

Extracts layout/content from a PDF and returns universal JSON.
Must be implemented by subclasses.

##### generate(config, output_pdf_path)

Generates a PDF from universal JSON config.
Must be implemented by subclasses.

##### get_supported_features()

Returns a dict of supported features (e.g., rotation, images, transparency).

##### warn_unsupported(feature, context)

Logs a warning if a feature is not supported, and attempts best-effort fallback.

##### engine_info()

### FitzPDFEngine

#### Methods

##### extract(input_pdf_path)

Extracts layout/content from a PDF and returns universal JSON.

##### generate(config, output_pdf_path, original_pdf_for_template)

Generates a PDF from universal JSON config.
