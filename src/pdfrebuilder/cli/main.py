import argparse
import os
from typing import Any

from pdfrebuilder.settings import CONFIG

# Rich console output for better CLI experience
try:
    from rich.console import Console
    from rich.panel import Panel  # noqa: F401 # Used for future CLI enhancements

    rich_console: Console | None = Console()
    HAS_RICH = True
except ImportError:
    rich_console = None
    HAS_RICH = False


def console_print(message: str, style: str = "default", log_level: int | None = None) -> None:
    """
    Print message with rich formatting if available, otherwise plain text.

    Args:
        message: Message to print
        style: Style for the message (success, error, warning, info, config, default)
        log_level: Optional log level to check against current logging level
    """
    import logging

    # Check if message should be displayed based on log level
    if log_level is not None:
        root_logger = logging.getLogger()
        if not root_logger.isEnabledFor(log_level):
            return

    if HAS_RICH and rich_console:
        if style == "success":
            rich_console.print(f"✅ {message}", style="green")
        elif style == "error":
            rich_console.print(f"❌ {message}", style="red")
        elif style == "warning":
            rich_console.print(f"⚠️  {message}", style="yellow")
        elif style == "info":
            rich_console.print(f"ℹ️  {message}", style="blue")
        elif style == "config":
            rich_console.print(f"⚙️  {message}", style="cyan")
        elif style == "debug":
            rich_console.print(f"🔧 {message}", style="dim")
        else:
            rich_console.print(message)
    else:
        # Fallback to plain print
        if style == "success":
            print(f"✅ {message}")
        elif style == "error":
            print(f"❌ {message}")
        elif style == "warning":
            print(f"⚠️  {message}")
        elif style == "info":
            print(f"ℹ️  {message}")
        elif style == "config":
            print(f"⚙️  {message}")
        elif style == "debug":
            print(f"🔧 {message}")
        else:
            print(message)


# Ensure no argparse usage at the top level; all CLI logic is inside main()


def run_pipeline(args):
    import logging

    # Load configuration from all sources
    from pdfrebuilder.config.manager import ConfigManager

    config_manager = ConfigManager()

    # Prepare CLI overrides
    cli_overrides: dict[str, Any] = {}
    if args.output_dir:
        cli_overrides.setdefault("paths", {})["output_dir"] = args.output_dir
    if args.temp_dir:
        cli_overrides.setdefault("paths", {})["temp_dir"] = args.temp_dir
    if args.test_output_dir:
        cli_overrides.setdefault("paths", {})["test_output_dir"] = args.test_output_dir
    if args.reports_output_dir:
        cli_overrides.setdefault("paths", {})["reports_output_dir"] = args.reports_output_dir
    if (
        hasattr(args, "log_level") and args.log_level and args.log_level != "INFO"
    ):  # Only override if different from default
        cli_overrides.setdefault("logging", {})["level"] = args.log_level.upper()
    if hasattr(args, "log_file") and args.log_file:
        cli_overrides.setdefault("logging", {})["log_file"] = args.log_file

    # Load configuration
    try:
        # In extract mode, we don't require an existing config file
        if args.mode == "extract" and args.config_file and not os.path.exists(args.config_file):
            # Create a minimal config for extract mode
            config = config_manager.load_config(config_file=None, cli_overrides=cli_overrides)
        elif args.mode == "generate":
            # In generate mode, we don't load a PDFRebuilderConfig, just use defaults
            config = config_manager.load_config(config_file=None, cli_overrides=cli_overrides)
        else:
            config = config_manager.load_config(config_file=args.config_file, cli_overrides=cli_overrides)
    except Exception as e:
        console_print(f"Configuration error: {e}", "error")
        raise

    # Configure output directories first (backward compatibility)
    from pdfrebuilder.settings import configure_output_directories, get_config_value

    if config.paths.output_dir:
        configure_output_directories(base_dir=str(config.paths.output_dir))
    if hasattr(config.paths, "test_output_dir") and config.paths.test_output_dir:
        configure_output_directories(test_dir=str(config.paths.test_output_dir))
    if hasattr(config.paths, "reports_output_dir") and config.paths.reports_output_dir:
        configure_output_directories(reports_dir=str(config.paths.reports_output_dir))

    # Resolve default output paths if not provided
    if args.output is None:
        args.output = get_config_value("rebuilt_pdf")
    if args.debugoutput is None:
        args.debugoutput = get_config_value("debug_pdf")

    # Set up logging configuration using new config system
    from pdfrebuilder.settings import configure_logging

    # Use configuration values, with CLI args taking precedence
    log_level = getattr(logging, config.logging.level.value, logging.INFO)
    log_file_path = str(config.logging.log_file) if config.logging.log_file else None

    # Create log file directory if specified
    if log_file_path:
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        console_print(f"Logging to file: {log_file_path}", "config")

    configure_logging(
        log_file=log_file_path,
        log_level=log_level,
        log_format="%(levelname)s %(name)s: %(message)s",
    )

    from pdfrebuilder.core.compare_pdfs_visual import compare_pdfs_visual
    from pdfrebuilder.core.generate_debug_pdf_layers import generate_debug_pdf_layers
    from pdfrebuilder.core.pdf_engine import FitzPDFEngine
    from pdfrebuilder.engine.document_parser import parse_document
    from pdfrebuilder.tools import serialize_pdf_content_to_config

    # Use configuration values, with CLI args taking precedence
    extraction_flags = {
        "include_text": (args.extract_text if hasattr(args, "extract_text") else config.extraction.include_text),
        "include_images": (
            args.extract_images if hasattr(args, "extract_images") else config.extraction.include_images
        ),
        "include_drawings_non_background": (
            args.extract_drawings if hasattr(args, "extract_drawings") else config.extraction.include_drawings
        ),
        "include_raw_background_drawings": (
            args.extract_raw_backgrounds
            if hasattr(args, "extract_raw_backgrounds")
            else config.extraction.include_raw_backgrounds
        ),
    }

    # Create necessary directories using the configured paths
    image_dir = get_config_value("image_dir")
    auto_fonts_dir = get_config_value("downloaded_fonts_dir")
    manual_fonts_dir = get_config_value("manual_fonts_dir")

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(auto_fonts_dir, exist_ok=True)
    os.makedirs(manual_fonts_dir, exist_ok=True)
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    if args.debugoutput:
        os.makedirs(os.path.dirname(args.debugoutput) or ".", exist_ok=True)

    # Print output directory configuration for user feedback
    console_print(
        f"Output directory: {get_config_value('base_output_dir') if callable(get_config_value('base_output_dir')) else args.output_dir or './output'}",
        "config",
    )
    console_print(f"Images directory: {image_dir}", "config")
    console_print(f"Auto fonts directory: {auto_fonts_dir}", "config")
    console_print(f"Manual fonts directory: {manual_fonts_dir}", "config")
    if args.test_output_dir:
        console_print(f"Test output directory: {get_config_value('test_output_dir')}", "config")
    if args.reports_output_dir:
        console_print(f"Reports directory: {get_config_value('reports_output_dir')}", "config")

    is_extract_mode = args.mode in ["full", "extract"]
    if is_extract_mode and not os.path.exists(args.input):
        console_print(f"Input file not found for extraction: {args.input}", "error")
        return

    try:
        # file_format is no longer used
        if args.mode == "extract":
            console_print("Entering extract mode...", "info")
            console_print(f"Parsing document: {args.input}", "info")
            console_print(f"Using input engine: {args.input_engine}", "info")
            # Log engine version info at DEBUG level if using fitz
            if args.input_engine.lower() in ["fitz", "auto"]:
                console_print(
                    f"Input engine selected: {args.input_engine}",
                    "debug",
                    logging.DEBUG,
                )
            try:
                content = parse_document(args.input, extraction_flags, engine=args.input_engine)
                console_print("Document parsed. Serializing to config...", "info")
                serialize_pdf_content_to_config(content, args.config)
                console_print(f"Extraction complete for {args.input}", "success")
            except ValueError as e:
                console_print(str(e), "error")
                raise
            except NotImplementedError as e:
                console_print(str(e), "error")
                console_print(
                    "Check installation instructions for the required dependencies.",
                    "warning",
                )
                raise
            console_print("Exiting extract mode.", "info")
        if args.mode == "generate":
            console_print("Entering generate mode...", "info")
            # Prepare engine configuration args
            from pdfrebuilder.engine.config_loader import load_engine_config
            from pdfrebuilder.engine.pdf_engine_selector import get_pdf_engine

            # Prepare CLI args for config loading
            cli_args: dict[str, Any] = {"output_engine": args.output_engine}

            # Load complete engine configuration
            engine_config = load_engine_config(cli_args=cli_args)

            engine_name = args.output_engine
            if engine_name == "auto":
                engine_name = engine_config.get("default_engine", "reportlab")

            console_print(f"Using output engine: {engine_name}", "info")

            engine: Any | None = None
            try:
                engine = get_pdf_engine(engine_name, engine_config)
                if engine:
                    original_file = args.input if args.input and os.path.exists(args.input) else None
                    # Ensure config is a dictionary before passing to the engine
                    config_dict = config.dict(exclude_unset=True) if hasattr(config, "dict") else dict(config)
                    engine.generate(config_dict, args.output, original_file)
                    console_print("PDF generation complete.", "success")
            except Exception as e:
                console_print(f"Engine error: {e}", "error")
                # Fallback to old engine for compatibility
                console_print("Falling back to legacy engine...", "warning")
                engine = FitzPDFEngine()
                # Ensure config is a dictionary for the fallback engine too
                config_dict = config.dict(exclude_unset=True) if hasattr(config, "dict") else dict(config)
                engine.generate(config_dict, args.output, original_file)
                console_print("PDF generation complete (using fallback).", "success")

            console_print("Exiting generate mode.", "info")
        elif args.mode == "full":
            console_print("Entering full mode...", "info")
            try:
                console_print(f"Parsing document: {args.input}", "info")
                console_print(f"Using input engine: {args.input_engine}", "info")
                # Log engine version info at DEBUG level if using fitz
                if args.input_engine.lower() in ["fitz", "auto"]:
                    console_print(
                        f"Input engine selected: {args.input_engine}",
                        "debug",
                        logging.DEBUG,
                    )
                content = parse_document(args.input, extraction_flags, engine=args.input_engine)
                console_print("Document parsed. Serializing to config...", "info")
                serialize_pdf_content_to_config(content, args.config)
                console_print("Config serialized. Recreating PDF...", "info")

                # Load the config that was just serialized
                import json

                with open(args.config) as f:
                    config = json.load(f)

            except ValueError as e:
                console_print(str(e), "error")
                raise

            # Load engine configuration
            from pdfrebuilder.engine.config_loader import load_engine_config
            from pdfrebuilder.engine.pdf_engine_selector import get_pdf_engine

            # Prepare CLI args for config loading
            cli_args = {"output_engine": args.output_engine}

            # Load complete engine configuration
            engine_config = load_engine_config(cli_args=cli_args)

            engine_name = args.output_engine
            if engine_name == "auto":
                engine_name = engine_config.get("default_engine", "reportlab")

            console_print(f"Using output engine: {engine_name}", "info")

            engine: Any | None = None
            try:
                engine = get_pdf_engine(engine_name, engine_config)
                if engine:
                    engine.generate(config, args.output, args.input)
            except Exception as e:
                console_print(f"Engine error: {e}", "error")
                # Fallback to old engine for compatibility
                console_print("Falling back to legacy engine...", "warning")
                engine = FitzPDFEngine()
                engine.generate(config, args.output, args.input)
                console_print("PDF generation complete (using fallback).", "success")

            console_print("PDF recreated. Comparing PDFs visually...", "info")
            output_dir = os.path.dirname(args.output) or "."
            from pdfrebuilder.settings import get_config_value

            diff_basename = os.path.basename(get_config_value("diff_image") or "diff.png")
            diff_image_path = os.path.join(output_dir, diff_basename)
            compare_pdfs_visual(args.input, args.output, diff_image_path)
            console_print("Visual comparison complete.", "success")
            if args.debugoutput:
                console_print("Generating debug PDF layers...", "info")
                generate_debug_pdf_layers(args.config, args.debugoutput)
                console_print("Debug PDF layers generated.", "success")
            console_print("Exiting full mode.", "info")
        elif args.mode == "debug":
            console_print("Entering debug mode...", "info")
            if not os.path.exists(args.config):
                console_print(f"Config file not found to debug: {args.config}", "error")
                raise FileNotFoundError(f"Config file not found to debug: {args.config}")
            generate_debug_pdf_layers(args.config, args.debugoutput)
            console_print("Debug PDF layers generated.", "success")
            console_print("Exiting debug mode.", "info")
    except Exception as e:
        console_print(f"An unhandled error occurred during the pipeline: {e}", "error")
        import traceback

        traceback.print_exc()
        # Re-raise the exception so tests can catch it
        raise


def main():
    parser = argparse.ArgumentParser(description="Extract and rebuild PDF layouts.")

    # Configuration file support
    parser.add_argument(
        "--config-file",
        default=None,
        help="Path to configuration file (TOML or JSON format). Overrides default configuration.",
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate a sample configuration file and exit.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current effective configuration and exit.",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level. Use DEBUG to see engine version information (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Path to log file. If not specified, logs are written to console. Directory will be created if it doesn't exist.",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "extract", "generate", "debug"],
        default="full",
        help="Operation: 'extract' only, 'generate' only, 'debug' drawing layers, or 'full' pipeline.",
    )
    parser.add_argument("--input", default="input/sample.pdf", help="Input PDF file path.")
    parser.add_argument(
        "--config",
        default=CONFIG.get("config_path", "layout_config.json"),
        help="Layout config JSON file path.",
    )
    parser.add_argument(
        "--output",
        default=None,  # Will be resolved from CONFIG after output dir is set
        help="Output PDF file path.",
    )
    parser.add_argument(
        "--debugoutput",
        default=None,  # Will be resolved from CONFIG after output dir is set
        help="Debug output PDF file path.",
    )
    # Output directory configuration
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Base output directory for all generated files (default: ./output)",
    )
    parser.add_argument(
        "--test-output-dir",
        default=None,
        help="Output directory for test files and reports (default: <output-dir>/tests)",
    )
    parser.add_argument(
        "--reports-output-dir",
        default=None,
        help="Output directory for reports and logs (default: <output-dir>/reports)",
    )
    parser.add_argument(
        "--temp-dir",
        default=None,
        help="Temporary directory for processing files (default: system temp + pdfrebuilder)",
    )
    parser.add_argument(
        "--extract-text",
        action="store_true",
        default=True,
        help="Include text blocks in extraction (default: True).",
    )
    parser.add_argument(
        "--no-extract-text",
        dest="extract_text",
        action="store_false",
        help="Exclude text blocks from extraction.",
    )
    parser.add_argument(
        "--extract-images",
        action="store_true",
        default=True,
        help="Include image blocks in extraction (default: True).",
    )
    parser.add_argument(
        "--no-extract-images",
        dest="extract_images",
        action="store_false",
        help="Exclude image blocks from extraction.",
    )
    parser.add_argument(
        "--extract-drawings",
        action="store_true",
        default=True,
        help="Include non-background vector drawings in extraction (default: True).",
    )
    parser.add_argument(
        "--no-extract-drawings",
        dest="extract_drawings",
        action="store_false",
        help="Exclude non-background vector drawings from extraction.",
    )
    parser.add_argument(
        "--extract-raw-backgrounds",
        action="store_true",
        default=False,
        help="Include raw background drawings identified (for debugging) (default: False).",
    )
    parser.add_argument(
        "--no-extract-raw-backgrounds",
        dest="extract_raw_backgrounds",
        action="store_false",
        help="Exclude raw background drawings identified.",
    )
    # Engine selection arguments
    parser.add_argument(
        "--input-engine",
        choices=["auto", "fitz", "psd-tools", "wand"],
        default="auto",
        help="Input processing engine: 'auto' (auto-detect based on file format), 'fitz' (PyMuPDF for PDF files), 'psd-tools' (psd-tools library for PSD files), or 'wand' (Python-Wand/ImageMagick for PSD and various image formats).",
    )
    parser.add_argument(
        "--output-engine",
        choices=["auto", "reportlab", "pymupdf", "fitz"],
        default="auto",
        help="Output rendering engine: 'auto' (use default), 'reportlab' (ReportLab), 'pymupdf' (PyMuPDF), or 'fitz' (alias for PyMuPDF).",
    )
    args = parser.parse_args()

    # Handle configuration file operations first
    if args.generate_config or args.show_config:
        from pdfrebuilder.config.manager import ConfigManager

        config_manager = ConfigManager()

        if args.generate_config:
            sample_file = config_manager.generate_sample_config()
            console_print(f"Sample configuration file generated: {sample_file}", "success")
            console_print(
                "Edit this file to customize your settings, then use --config-file to load it.",
                "info",
            )
            return

        if args.show_config:
            try:
                # Prepare CLI overrides for show-config too
                cli_overrides: dict[str, Any] = {}
                if hasattr(args, "log_level") and args.log_level and args.log_level != "INFO":
                    cli_overrides.setdefault("logging", {})["level"] = args.log_level.upper()
                if hasattr(args, "log_file") and args.log_file:
                    cli_overrides.setdefault("logging", {})["log_file"] = args.log_file

                # Load configuration with any provided config file and CLI overrides
                config_manager.load_config(config_file=args.config_file, cli_overrides=cli_overrides)
                config_output = config_manager.show_config()
                print(config_output)
                return
            except Exception as e:
                console_print(f"Error loading configuration: {e}", "error")
                return

    run_pipeline(args)


if __name__ == "__main__":
    main()
