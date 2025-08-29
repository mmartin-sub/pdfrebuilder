# src/pdf_engine.py

import logging
from typing import Any, ClassVar

import pymupdf as fitz

from pdfrebuilder.models.universal_idm import UniversalDocument

from .render import _render_element


class PDFEngineBase:
    """
    Abstract base class for PDF engines (e.g., fitz, reportlab).
    Provides metadata, extraction, and generation interfaces.
    """

    engine_name: str = "base"
    engine_version: str = "unknown"
    supported_features: ClassVar[dict[str, bool]] = {}
    logger: logging.Logger = logging.getLogger(__name__)
    output_schema_version: str = "1.0"

    def extract(self, input_pdf_path: str) -> UniversalDocument:
        """
        Extracts layout/content from a PDF and returns universal JSON.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("extract() must be implemented by subclasses.")

    def generate(self, config: dict[str, Any], output_pdf_path: str) -> None:
        """
        Generates a PDF from universal JSON config.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("generate() must be implemented by subclasses.")

    def get_supported_features(self) -> dict[str, bool]:
        """
        Returns a dict of supported features (e.g., rotation, images, transparency).
        """
        return self.supported_features.copy()

    def warn_unsupported(self, feature: str, context: str = ""):
        """
        Logs a warning if a feature is not supported, and attempts best-effort fallback.
        """
        msg = f"[PDFEngineBase] WARNING: Feature '{feature}' is not fully supported by {self.engine_name}. Context: {context}"
        self.logger.warning(msg)

    @property
    def engine_info(self):
        return {
            "version": self.output_schema_version,
            "engine": self.engine_name,
            "engine_version": self.engine_version,
        }


class FitzPDFEngine(PDFEngineBase):
    engine_name = "fitz"
    engine_version = getattr(fitz, "__doc__", "unknown").splitlines()[0] if hasattr(fitz, "__doc__") else "unknown"
    supported_features: ClassVar[dict[str, bool]] = {
        "rotation": False,
        "images": True,
        "drawings": True,
        "text": True,
    }

    def extract(self, input_pdf_path: str) -> UniversalDocument:
        """
        Extracts layout/content from a PDF and returns universal JSON.
        """
        from pdfrebuilder.engine.extract_pdf_content_fitz import extract_pdf_content

        return extract_pdf_content(input_pdf_path)

    def generate(self, config: dict, output_pdf_path: str, original_pdf_for_template=None) -> None:
        """
        Generates a PDF from universal JSON config.
        """
        doc: fitz.Document = fitz.open()
        try:
            tpl_doc = fitz.open(original_pdf_for_template) if original_pdf_for_template else None
            for doc_unit_idx, doc_unit_data in enumerate(config.get("document_structure", [])):
                if doc_unit_data.get("type") != "page":
                    continue
                page_data = doc_unit_data
                page_idx = page_data.get("page_number", doc_unit_idx)
                page = doc.new_page(width=page_data["size"][0], height=page_data["size"][1])  # type: ignore[attr-defined]
                page_bg_color = page_data.get("page_background_color")
                if page_bg_color is not None:
                    page.draw_rect(page.rect, fill=page_bg_color)
                if tpl_doc and page_idx < tpl_doc.page_count:
                    # The 'show_pdf_page' method is valid in PyMuPDF, but the library's type
                    # stubs are incomplete, causing mypy/pyright to raise a false positive.
                    page.show_pdf_page(page.rect, tpl_doc, page_idx)  # type: ignore[attr-defined]
                for layer_data in page_data.get("layers", []):
                    for element in layer_data.get("content", []):
                        _render_element(page, element, page_idx, {}, config)
            doc.save(output_pdf_path)
            if tpl_doc:
                tpl_doc.close()
        except Exception as e:
            self.warn_unsupported("PDF generation", str(e))
            raise
