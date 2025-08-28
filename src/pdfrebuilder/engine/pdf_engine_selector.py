from pdfrebuilder.engine.engine_selector import get_pdf_engine_selector
from pdfrebuilder.engine.pdf_rendering_engine import PDFRenderingEngine


def get_pdf_engine(engine_name: str, config: dict = None) -> PDFRenderingEngine:
    """Get a PDF engine instance."""
    selector = get_pdf_engine_selector()
    return selector.get_engine(engine_name, config)


def get_default_pdf_engine(config: dict = None) -> PDFRenderingEngine:
    """Get the default PDF engine."""
    selector = get_pdf_engine_selector()
    return selector.get_default_engine(config)
