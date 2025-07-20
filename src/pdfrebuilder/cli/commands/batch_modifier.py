"""
CLI interface for batch modification operations.

Provides command-line access to batch text replacement, variable substitution,
and font validation capabilities.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from pdfrebuilder.engine.batch_modifier import BatchModifier, VariableSubstitution
from pdfrebuilder.settings import configure_logging

logger = logging.getLogger(__name__)


def create_batch_modifier_parser() -> argparse.ArgumentParser:
    """Create the argument parser for batch modification commands."""
    parser = argparse.ArgumentParser(
        description="Batch modification tools for document content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Batch text replacement
  python -m src.cli.batch_modifier_cli replace \\
    --input document.json \\
    --replacements "old text:new text" "another:replacement" \\
    --output modified_document.json

  # Variable substitution
  python -m src.cli.batch_modifier_cli substitute \\
    --input template.json \\
    --variables "NAME:John Doe" "DATE:2024-01-15" \\
    --output personalized_document.json

  # Font validation
  python -m src.cli.batch_modifier_cli validate \\
    --input document.json \\
    --output validation_report.json
        """,
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Replace command
    replace_parser = subparsers.add_parser("replace", help="Batch text replacement")
    replace_parser.add_argument("--input", "-i", required=True, help="Input document JSON file")
    replace_parser.add_argument("--output", "-o", required=True, help="Output file path")
    replace_parser.add_argument(
        "--replacements",
        nargs="+",
        required=True,
        help="Text replacements in format 'old:new'",
    )
    replace_parser.add_argument("--element-ids", nargs="+", help="Specific element IDs to target")
    replace_parser.add_argument("--page-numbers", type=int, nargs="+", help="Specific page numbers to target")
    replace_parser.add_argument("--no-font-validation", action="store_true", help="Skip font validation")

    # Substitute command
    substitute_parser = subparsers.add_parser("substitute", help="Variable substitution")
    substitute_parser.add_argument("--input", "-i", required=True, help="Input document JSON file")
    substitute_parser.add_argument("--output", "-o", required=True, help="Output file path")
    substitute_parser.add_argument(
        "--variables",
        nargs="+",
        required=True,
        help="Variable substitutions in format 'VAR_NAME:value'",
    )
    substitute_parser.add_argument(
        "--template-mode",
        action="store_true",
        default=True,
        help="Operate in template mode (default: True)",
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Font validation")
    validate_parser.add_argument("--input", "-i", required=True, help="Input document JSON file")
    validate_parser.add_argument("--output", "-o", required=True, help="Output file path")
    validate_parser.add_argument(
        "--check-licensing",
        action="store_true",
        default=True,
        help="Check font licensing compliance (default: True)",
    )
    validate_parser.add_argument(
        "--detailed-report",
        action="store_true",
        help="Generate detailed validation report",
    )

    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="Document statistics")
    stats_parser.add_argument("--input", "-i", required=True, help="Input document JSON file")
    stats_parser.add_argument("--output", "-o", required=True, help="Output file path")
    stats_parser.add_argument(
        "--substitution-stats",
        action="store_true",
        help="Show variable substitution statistics",
    )

    return parser


def parse_replacements(replacements: list[str]) -> list[tuple[str, str]]:
    """Parse replacement strings into tuples."""
    result = []
    for replacement in replacements:
        if ":" not in replacement:
            logger.error(f"Invalid replacement format: {replacement}. Use 'old:new' format.")
            continue
        old_text, new_text = replacement.split(":", 1)
        result.append((old_text.strip(), new_text.strip()))
    return result


def parse_variables(variables: list[str]) -> list[VariableSubstitution]:
    """Parse variable strings into VariableSubstitution objects."""
    result = []
    for variable in variables:
        if ":" not in variable:
            logger.error(f"Invalid variable format: {variable}. Use 'VAR_NAME:value' format.")
            continue
        var_name, value = variable.split(":", 1)
        result.append(VariableSubstitution(variable_name=var_name.strip(), replacement_value=value.strip()))
    return result


def load_document(input_path: str) -> Any:
    """Load document from JSON file."""
    try:
        with open(input_path, encoding="utf-8") as f:
            document_data = json.load(f)

        # Import here to avoid circular imports
        from pdfrebuilder.models.universal_idm import UniversalDocument

        return UniversalDocument.from_dict(document_data)
    except Exception as e:
        logger.error(f"Failed to load document from {input_path}: {e}")
        sys.exit(1)


def save_document(document: Any, output_path: str) -> None:
    """Save document to JSON file."""
    try:
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Document saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save document to {output_path}: {e}")
        sys.exit(1)


def handle_replace_command(args: argparse.Namespace) -> None:
    """Handle the replace command."""
    # Load document
    document = load_document(args.input)

    # Parse replacements
    replacements = parse_replacements(args.replacements)
    if not replacements:
        logger.error("No valid replacements provided")
        sys.exit(1)

    # Create batch modifier
    modifier = BatchModifier()

    # Perform batch replacement
    result = modifier.batch_text_replacement(
        document=document,
        replacements=replacements,
        element_ids=args.element_ids,
        page_numbers=args.page_numbers,
        validate_fonts=not args.no_font_validation,
    )

    # Save modified document
    save_document(document, args.output)

    # Print results
    print("\nBatch replacement completed:")
    print(f"  Modified elements: {result.modified_elements}")
    print(f"  Skipped elements: {result.skipped_elements}")
    print(f"  Font warnings: {len(result.font_warnings)}")

    if result.font_warnings:
        print("\nFont warnings:")
        for warning in result.font_warnings:
            print(f"  - {warning}")


def handle_substitute_command(args: argparse.Namespace) -> None:
    """Handle the substitute command."""
    # Load document
    document = load_document(args.input)

    # Parse variables
    variables = parse_variables(args.variables)
    if not variables:
        logger.error("No valid variables provided")
        sys.exit(1)

    # Create batch modifier
    modifier = BatchModifier()

    # Perform variable substitution
    result = modifier.variable_substitution(
        document=document,
        variables=variables,
        template_mode=args.template_mode,
    )

    # Save modified document
    save_document(document, args.output)

    # Print results
    print("\nVariable substitution completed:")
    print(f"  Modified elements: {result.modified_elements}")
    print(f"  Skipped elements: {result.skipped_elements}")
    print(f"  Font warnings: {len(result.font_warnings)}")

    if result.font_warnings:
        print("\nFont warnings:")
        for warning in result.font_warnings:
            print(f"  - {warning}")


def handle_validate_command(args: argparse.Namespace) -> None:
    """Handle the validate command."""
    # Load document
    document = load_document(args.input)

    # Create batch modifier
    modifier = BatchModifier()

    # Perform font validation
    validation_result = modifier.validate_document_fonts(
        document=document,
        check_licensing=args.check_licensing,
    )

    # Save validation report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(validation_result, f, indent=2, ensure_ascii=False)

    # Print results
    print("\nFont validation completed:")
    print(f"  Overall status: {validation_result['overall_status']}")
    print(f"  Fonts used: {len(validation_result['fonts_used'])}")
    print(f"  Fonts missing: {len(validation_result['fonts_missing'])}")
    print(f"  Fonts unlicensed: {len(validation_result['fonts_unlicensed'])}")
    print(f"  Elements with issues: {len(validation_result['elements_with_issues'])}")

    if validation_result["fonts_missing"]:
        print(f"\nMissing fonts: {', '.join(validation_result['fonts_missing'])}")

    if validation_result["fonts_unlicensed"]:
        print(f"\nUnlicensed fonts: {', '.join(validation_result['fonts_unlicensed'])}")

    if args.detailed_report and validation_result["elements_with_issues"]:
        print("\nDetailed issues:")
        for issue in validation_result["elements_with_issues"]:
            print(
                f"  - Element {issue['element_id']} (page {issue['page_number']}): {issue['issue']} - {issue['font_name']}"
            )


def handle_stats_command(args: argparse.Namespace) -> None:
    """Handle the stats command."""
    # Load document
    document = load_document(args.input)

    # Create batch modifier
    modifier = BatchModifier()

    if args.substitution_stats:
        # Get substitution statistics
        stats = modifier.get_substitution_statistics(document)

        print("\nVariable substitution statistics:")
        print(f"  Total text elements: {stats['total_text_elements']}")
        print(f"  Elements with variables: {stats['elements_with_variables']}")
        print(f"  Variable patterns found: {', '.join(stats['variable_patterns_found'])}")

        if stats["substitution_opportunities"]:
            print("\nSubstitution opportunities:")
            for opp in stats["substitution_opportunities"]:
                print(f"  - Element {opp['element_id']} (page {opp['page_number']}): {opp['variables']}")
                print(f"    Text: {opp['text_sample']}")

    # Save statistics to output file
    stats = modifier.get_substitution_statistics(document)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point for the batch modifier CLI."""
    parser = create_batch_modifier_parser()
    args = parser.parse_args()

    # Configure logging
    configure_logging(log_level=getattr(logging, args.log_level.upper()))

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle commands
    if args.command == "replace":
        handle_replace_command(args)
    elif args.command == "substitute":
        handle_substitute_command(args)
    elif args.command == "validate":
        handle_validate_command(args)
    elif args.command == "stats":
        handle_stats_command(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
