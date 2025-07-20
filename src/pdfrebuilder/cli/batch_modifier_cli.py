"""
CLI interface for batch modification operations.
"""

import argparse
import json
import logging
import sys

from pdfrebuilder.engine.batch_modifier import BatchModifier, VariableSubstitution
from pdfrebuilder.models.universal_idm import UniversalDocument
from pdfrebuilder.settings import configure_logging

logger = logging.getLogger(__name__)


def load_document(input_path: str) -> UniversalDocument:
    """Load a document from JSON file."""
    try:
        with open(input_path) as f:
            data = json.load(f)
        return UniversalDocument.from_dict(data)
    except Exception as e:
        logger.error(f"Failed to load document from {input_path}: {e}")
        raise


def save_document(document: UniversalDocument, output_path: str) -> None:
    """Save a document to JSON file."""
    try:
        with open(output_path, "w") as f:
            json.dump(document.to_dict(), f, indent=2)
        logger.info(f"Document saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save document to {output_path}: {e}")
        raise


def cmd_replace(args: argparse.Namespace) -> None:
    """Handle the replace command."""
    try:
        # Load document
        document = load_document(args.input)

        # Create batch modifier
        modifier = BatchModifier()

        # Parse replacements
        replacements = []
        if hasattr(args, "replacements") and args.replacements:
            for replacement in args.replacements:
                if ":" in replacement:
                    search, replace = replacement.split(":", 1)
                    replacements.append((search, replace))
        elif args.search and args.replace:
            replacements.append((args.search, args.replace))

        if not replacements:
            print("No replacements specified. Use --search/--replace or --replacements")
            sys.exit(1)

        # Perform all replacements in one call
        result = modifier.batch_text_replacement(document=document, replacements=replacements, validate_fonts=True)

        if not result.success:
            print("Replacement failed:")
            for error in result.validation_errors:
                print(f"  - {error}")
            sys.exit(1)

        # Save modified document
        output_path = args.output or args.input
        save_document(document, output_path)

        print("Replacement completed successfully:")
        print(f"  Modified elements: {result.modified_elements}")
        print(f"  Skipped elements: {result.skipped_elements}")

        if result.font_warnings:
            print("Font warnings:")
            for warning in result.font_warnings:
                print(f"  - {warning}")

    except Exception as e:
        logger.error(f"Replace command failed: {e}")
        sys.exit(1)


def cmd_substitute(args: argparse.Namespace) -> None:
    """Handle the substitute command."""
    try:
        # Load document
        document = load_document(args.input)

        # Create batch modifier
        modifier = BatchModifier()

        # Parse variables from command line or file
        variables = []
        if hasattr(args, "variables") and args.variables:
            for var_def in args.variables:
                parts = var_def.split("=", 1)
                if len(parts) == 2:
                    variables.append(VariableSubstitution(variable_name=parts[0], replacement_value=parts[1]))

        # Perform substitution
        result = modifier.variable_substitution(document, variables)

        if result.success:
            # Save modified document
            output_path = args.output or args.input
            save_document(document, output_path)

            print("Variable substitution completed successfully:")
            print(f"  Modified elements: {result.modified_elements}")
            print(f"  Skipped elements: {result.skipped_elements}")

        else:
            print("Variable substitution failed:")
            for error in result.validation_errors:
                print(f"  - {error}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Substitute command failed: {e}")
        sys.exit(1)


def cmd_validate(args: argparse.Namespace) -> None:
    """Handle the validate command."""
    try:
        # Load document
        document = load_document(args.input)

        # Create batch modifier
        modifier = BatchModifier()

        # Validate fonts
        result = modifier.validate_document_fonts(document)

        print("Font validation completed:")
        print(f"  Fonts used: {len(result['fonts_used'])}")
        print(f"  Fonts missing: {len(result['fonts_missing'])}")
        print(f"  Fonts unlicensed: {len(result['fonts_unlicensed'])}")

        if result.get("elements_with_issues"):
            print("Elements with issues:")
            for issue in result["elements_with_issues"]:
                element_id = issue.get("element_id", "?")
                page_number = issue.get("page_number", "?")
                font_name = issue.get("font_name", "?")
                issue_type = issue.get("issue", "unknown")
                print(f"  - [p{page_number}] {element_id}: {issue_type} ({font_name})")

        if result.get("overall_status") == "passed":
            print("All fonts validated successfully!")
        else:
            print("Font validation failed.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validate command failed: {e}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Batch modification tool for document content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s replace --input doc.json --search "old text" --replace "new text"
  %(prog)s substitute --input doc.json --variables "VAR1=value1" "VAR2=value2"
  %(prog)s validate --input doc.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Replace command
    replace_parser = subparsers.add_parser("replace", help="Replace text in document")
    replace_parser.add_argument("--input", "-i", required=True, help="Input JSON document file")
    replace_parser.add_argument("--search", "-s", help="Text to search for")
    replace_parser.add_argument("--replace", "-r", help="Replacement text")
    replace_parser.add_argument("--replacements", nargs="+", help="Replacements in format search:replace")
    replace_parser.add_argument("--output", "-o", help="Output file (defaults to input file)")
    replace_parser.add_argument("--case-sensitive", action="store_true", help="Case sensitive search")

    # Substitute command
    substitute_parser = subparsers.add_parser("substitute", help="Substitute variables in document")
    substitute_parser.add_argument("--input", "-i", required=True, help="Input JSON document file")
    substitute_parser.add_argument("--variables", "-v", nargs="+", help="Variables in format VAR=value")
    substitute_parser.add_argument("--output", "-o", help="Output file (defaults to input file)")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate fonts in document")
    validate_parser.add_argument("--input", "-i", required=True, help="Input JSON document file")

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    configure_logging(log_level=logging.INFO)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "replace":
            cmd_replace(args)
        elif args.command == "substitute":
            cmd_substitute(args)
        elif args.command == "validate":
            cmd_validate(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
