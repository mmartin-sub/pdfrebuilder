import logging
import os
from types import SimpleNamespace
from typing import Annotated, Any

import typer

from pdfrebuilder.cli.app import app
from pdfrebuilder.settings import settings

# Rich console output for better CLI experience
try:
    from rich.console import Console

    rich_console: Console | None = Console()
    HAS_RICH = True
except ImportError:
    rich_console = None
    HAS_RICH = False


def console_print(message: str, style: str = "default", log_level: int | None = None) -> None:
    """
    Print message with rich formatting if available, otherwise plain text.
    """
    if log_level is not None:
        root_logger = logging.getLogger()
        if not root_logger.isEnabledFor(log_level):
            return

    if HAS_RICH and rich_console:
        style_map = {
            "success": ("✅", "green"),
            "error": ("❌", "red"),
            "warning": ("⚠️ ", "yellow"),
            "info": ("ℹ️ ", "blue"),
            "config": ("⚙️ ", "cyan"),
            "debug": ("🔧", "dim"),
        }
        icon, color = style_map.get(style, ("", "default"))
        rich_console.print(f"{icon}{message}", style=color)
    else:
        print(message)


def _version_callback(value: bool):
    if value:
        try:
            from pdfrebuilder import __version__

            version = __version__
        except ImportError:
            try:
                import toml

                with open("pyproject.toml") as f:
                    version = toml.load(f)["project"]["version"]
            except (ImportError, FileNotFoundError):
                version = "unknown"
        typer.echo(f"pdfrebuilder version: {version}")
        raise typer.Exit()


def _setup_environment(args: SimpleNamespace) -> Any:
    """Shared setup logic for commands."""
    from pdfrebuilder.config.manager import ConfigManager

    config_manager = ConfigManager()

    cli_overrides: dict[str, Any] = {
        "paths": {
            "output_dir": args.output_dir,
            "temp_dir": args.temp_dir,
            "test_output_dir": args.test_output_dir,
            "reports_output_dir": args.reports_output_dir,
        },
        "logging": {
            "level": args.log_level.upper(),
            "log_file": args.log_file,
        },
    }
    # Filter out None values
    cli_overrides["paths"] = {k: v for k, v in cli_overrides["paths"].items() if v is not None}
    cli_overrides["logging"] = {k: v for k, v in cli_overrides["logging"].items() if v is not None}

    config = config_manager.load_config(config_file=args.config_file, cli_overrides=cli_overrides)

    from pdfrebuilder.settings import configure_logging

    if config.paths.output_dir:
        # This is now handled by the settings object, but we can keep it for backward compatibility
        # with the old config system.
        pass

    log_level_val = getattr(logging, config.logging.level.value, logging.INFO)
    log_file_path = str(config.logging.log_file) if config.logging.log_file else None
    if log_file_path:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    configure_logging(log_file=log_file_path, log_level=log_level_val, log_format="%(levelname)s %(name)s: %(message)s")

    image_dir = settings.image_dir
    auto_fonts_dir = settings.font_management.downloaded_fonts_dir
    manual_fonts_dir = settings.font_management.manual_fonts_dir

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(auto_fonts_dir, exist_ok=True)
    os.makedirs(manual_fonts_dir, exist_ok=True)

    console_print(f"Output directory: {settings.rebuilt_pdf.parent}", "config")

    return config


def _run_extract(args: SimpleNamespace, config: Any):
    from pdfrebuilder.engine.document_parser import parse_document
    from pdfrebuilder.tools import serialize_pdf_content_to_config

    if not os.path.exists(args.input):
        console_print(f"Input file not found: {args.input}", "error")
        raise typer.Exit(1)

    console_print("Entering extract mode...", "info")
    extraction_flags = {
        "include_text": args.extract_text,
        "include_images": args.extract_images,
        "include_drawings_non_background": args.extract_drawings,
        "include_raw_background_drawings": args.extract_raw_backgrounds,
    }
    content = parse_document(args.input, extraction_flags, engine=args.input_engine)
    serialize_pdf_content_to_config(content, args.config)
    console_print(f"Extraction complete for {args.input}", "success")


def _run_generate(args: SimpleNamespace, config: Any):
    from pdfrebuilder.engine.config_loader import load_engine_config
    from pdfrebuilder.engine.pdf_engine_selector import get_pdf_engine

    console_print("Entering generate mode...", "info")
    cli_args = {"output_engine": args.output_engine}
    engine_config = load_engine_config(cli_args=cli_args)
    engine_name = args.output_engine or engine_config.get("default_engine", "reportlab")

    console_print(f"Using output engine: {engine_name}", "info")
    engine = get_pdf_engine(engine_name, engine_config)

    if not os.path.exists(args.config):
        console_print(f"Config file not found: {args.config}", "error")
        raise typer.Exit(1)

    with open(args.config) as f:
        config_data = f.read()

    engine.generate(config_data, args.output, args.input)
    console_print("PDF generation complete.", "success")


def _run_debug(args: SimpleNamespace, config: Any):
    from pdfrebuilder.core.generate_debug_pdf_layers import generate_debug_pdf_layers

    if not os.path.exists(args.config):
        console_print(f"Config file not found: {args.config}", "error")
        raise typer.Exit(1)

    console_print("Generating debug PDF layers...", "info")
    generate_debug_pdf_layers(args.config, args.debugoutput)
    console_print("Debug PDF layers generated.", "success")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool, typer.Option("--version", callback=_version_callback, is_eager=True, help="Show the version and exit.")
    ] = False,
    config_file: Annotated[
        str | None, typer.Option("--config-file", help="Path to configuration file (TOML or JSON format).")
    ] = None,
    output_dir: Annotated[str | None, typer.Option(help="Base output directory for all generated files.")] = None,
    temp_dir: Annotated[str | None, typer.Option(help="Temporary directory for processing files.")] = None,
    log_level: Annotated[str, typer.Option(help="Set the logging level.")] = "INFO",
    log_file: Annotated[str | None, typer.Option(help="Path to log file.")] = None,
):
    """PDFRebuilder CLI"""
    ctx.meta["args"] = SimpleNamespace(
        config_file=config_file,
        output_dir=output_dir,
        temp_dir=temp_dir,
        log_level=log_level,
        log_file=log_file,
        test_output_dir=None,
        reports_output_dir=None,  # These are not global
    )
    if ctx.invoked_subcommand is None:
        typer.echo("No command specified. Use --help for available commands.")


@app.command()
def full(
    ctx: typer.Context,
    input_file: Annotated[str, typer.Option("--input", help="Input PDF file path.")] = "input/sample.pdf",
    output_file: Annotated[str | None, typer.Option("--output", help="Output PDF file path.")] = None,
    config_file: Annotated[str | None, typer.Option("--config", help="Layout config JSON file path.")] = None,
    debug_output_file: Annotated[str | None, typer.Option("--debugoutput", help="Debug output PDF file path.")] = None,
    input_engine: Annotated[str, typer.Option(help="Input processing engine.")] = "auto",
    output_engine: Annotated[str, typer.Option(help="Output rendering engine.")] = "auto",
    extract_text: Annotated[bool, typer.Option(help="Include text blocks in extraction.")] = True,
    extract_images: Annotated[bool, typer.Option(help="Include image blocks in extraction.")] = True,
    extract_drawings: Annotated[bool, typer.Option(help="Include non-background vector drawings.")] = True,
    extract_raw_backgrounds: Annotated[bool, typer.Option(help="Include raw background drawings.")] = False,
):
    """Runs the full pipeline: extract, generate, and optionally compare."""
    args = ctx.meta["args"]
    args.input = input_file
    args.output = output_file or os.path.join(args.output_dir or "output", os.path.basename(input_file))
    args.config = config_file or settings.config_path
    args.debugoutput = debug_output_file
    args.input_engine = input_engine
    args.output_engine = output_engine
    args.extract_text = extract_text
    args.extract_images = extract_images
    args.extract_drawings = extract_drawings
    args.extract_raw_backgrounds = extract_raw_backgrounds

    config = _setup_environment(args)
    _run_extract(args, config)
    _run_generate(args, config)
    if args.debugoutput:
        _run_debug(args, config)

    from pdfrebuilder.core.compare_pdfs_visual import compare_pdfs_visual

    console_print("Comparing PDFs visually...", "info")
    diff_image_path = os.path.join(os.path.dirname(args.output), "diff.png")
    compare_pdfs_visual(args.input, args.output, diff_image_path)
    console_print("Visual comparison complete.", "success")


@app.command()
def extract(
    ctx: typer.Context,
    input_file: Annotated[str, typer.Option("--input", help="Input PDF file path.")] = "input/sample.pdf",
    config_output_file: Annotated[str, typer.Option("--config", help="Layout config JSON file path.")] = settings.config_path,
    input_engine: Annotated[str, typer.Option(help="Input processing engine.")] = "auto",
    extract_text: Annotated[bool, typer.Option(help="Include text blocks in extraction.")] = True,
    extract_images: Annotated[bool, typer.Option(help="Include image blocks in extraction.")] = True,
    extract_drawings: Annotated[bool, typer.Option(help="Include non-background vector drawings.")] = True,
    extract_raw_backgrounds: Annotated[bool, typer.Option(help="Include raw background drawings.")] = False,
):
    """Extracts content and layout from a document into a JSON config file."""
    args = ctx.meta["args"]
    args.input = input_file
    args.config = config_output_file
    args.input_engine = input_engine
    args.extract_text = extract_text
    args.extract_images = extract_images
    args.extract_drawings = extract_drawings
    args.extract_raw_backgrounds = extract_raw_backgrounds

    config = _setup_environment(args)
    _run_extract(args, config)


@app.command()
def generate(
    ctx: typer.Context,
    config_input_file: Annotated[str, typer.Option("--config", help="Layout config JSON file path.")] = settings.config_path,
    output_file: Annotated[str | None, typer.Option("--output", help="Output PDF file path.")] = None,
    input_file: Annotated[str | None, typer.Option("--input", help="Original input PDF file path (optional).")] = None,
    output_engine: Annotated[str, typer.Option(help="Output rendering engine.")] = "auto",
):
    """Generates a PDF from a JSON config file."""
    args = ctx.meta["args"]
    args.input = input_file
    args.config = config_input_file
    args.output = output_file or os.path.join(args.output_dir or "output", "rebuilt.pdf")
    args.output_engine = output_engine

    config = _setup_environment(args)
    _run_generate(args, config)


@app.command()
def debug(
    ctx: typer.Context,
    config_input_file: Annotated[str, typer.Option("--config", help="Layout config JSON file path.")] = settings.config_path,
    debug_output_file: Annotated[str | None, typer.Option("--debugoutput", help="Debug output PDF file path.")] = None,
):
    """Generates a debug PDF with drawing layers from a JSON config file."""
    args = ctx.meta["args"]
    args.config = config_input_file
    args.debugoutput = debug_output_file or os.path.join(args.output_dir or "output", "debug.pdf")

    config = _setup_environment(args)
    _run_debug(args, config)


@app.command(name="download-fonts")
def download_fonts(
    priority: Annotated[
        str | None, typer.Option(help="Download only fonts of specified priority level ('high', 'medium', 'low').")
    ] = None,
    force: Annotated[bool, typer.Option(help="Force redownload of existing fonts.")] = False,
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Enable verbose output.")] = False,
):
    """Downloads essential fonts for pdfrebuilder."""
    from scripts.download_essential_fonts import download_essential_fonts

    console_print("Downloading essential fonts...", "info")
    download_essential_fonts(priority_filter=priority, force_redownload=force, verbose=verbose)


if __name__ == "__main__":
    app()
