#!/usr/bin/env python3
"""
Enhanced documentation validation script.

This script provides comprehensive validation of documentation files,
including code examples, API references, configuration examples, and coverage reporting.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docs.tools.coverage_reporter import DocumentationCoverageReporter
from docs.tools.validation import DocumentationValidator, ValidationStatus


def print_results(results: list, title: str):
    """Print validation results with formatting."""
    if not results:
        print(f"\n{title}: No issues found ✅")
        return

    print(f"\n{title}:")
    print("-" * len(title))

    for result in results:
        status_icon = {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.SKIPPED: "⏭️",
        }.get(result.status, "❓")

        print(f"{status_icon} {result.message}")
        if result.file_path:
            print(f"   File: {result.file_path}")
        if result.line_number:
            print(f"   Line: {result.line_number}")
        if result.details and args.verbose:
            print(f"   Details: {result.details}")
        print()


def validate_documentation(validator: DocumentationValidator, verbose: bool = False) -> tuple[list, int]:
    """Validate all documentation files."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ Documentation directory not found")
        return [], 1

    all_results = []

    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    print(f"Found {len(md_files)} documentation files")

    for md_file in md_files:
        if verbose:
            print(f"\nValidating {md_file.relative_to(docs_dir)}...")

        # Validate code examples
        code_results = validator.validate_code_examples(md_file)
        all_results.extend(code_results)

        # Validate API references
        api_results = validator.validate_api_references(md_file)
        all_results.extend(api_results)

        # Validate configuration examples
        config_results = validator.validate_configuration_examples(md_file)
        all_results.extend(config_results)

    return all_results, 0


def generate_coverage_report(reporter: DocumentationCoverageReporter, export_path: Path | None = None) -> dict:
    """Generate and optionally export coverage report."""
    print("\n📊 Generating documentation coverage report...")

    report = reporter.generate_coverage_report()

    if export_path:
        reporter.export_coverage_report(export_path, report)

    reporter.print_coverage_summary(report)

    return report


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Enhanced documentation validation and coverage reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python scripts/validate_docs.py

  # Validate with coverage report
  python scripts/validate_docs.py --coverage

  # Export results to JSON
  python scripts/validate_docs.py --export results.json

  # Validate specific types only
  python scripts/validate_docs.py --examples --api-refs

  # Verbose output
  python scripts/validate_docs.py --verbose --coverage
        """,
    )

    parser.add_argument("--examples", action="store_true", help="Validate code examples only")
    parser.add_argument("--api-refs", action="store_true", help="Validate API references only")
    parser.add_argument("--config", action="store_true", help="Validate configuration examples only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--all", action="store_true", help="Run all validations (default)")
    parser.add_argument("--export", type=Path, help="Export results to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    global args
    args = parser.parse_args()

    # Initialize components
    validator = DocumentationValidator()
    coverage_reporter = DocumentationCoverageReporter()

    # Determine what to run
    run_examples = args.examples or args.all or not (args.examples or args.api_refs or args.config or args.coverage)
    run_api_refs = args.api_refs or args.all or not (args.examples or args.api_refs or args.config or args.coverage)
    run_config = args.config or args.all or not (args.examples or args.api_refs or args.config or args.coverage)
    run_coverage = args.coverage or args.all

    results = {}
    exit_code = 0

    # Run validation if requested
    if run_examples or run_api_refs or run_config:
        print("🔍 Running documentation validation...")

        docs_dir = Path("docs")
        if not docs_dir.exists():
            print("❌ Documentation directory not found")
            return 1

        all_results = []
        md_files = list(docs_dir.rglob("*.md"))
        print(f"Found {len(md_files)} documentation files")

        for md_file in md_files:
            if args.verbose:
                print(f"\nValidating {md_file.relative_to(docs_dir)}...")

            file_results = []

            if run_examples:
                code_results = validator.validate_code_examples(md_file)
                file_results.extend(code_results)

            if run_api_refs:
                api_results = validator.validate_api_references(md_file)
                file_results.extend(api_results)

            if run_config:
                config_results = validator.validate_configuration_examples(md_file)
                file_results.extend(config_results)

            all_results.extend(file_results)

        # Print validation results
        if run_examples:
            example_results = [r for r in all_results if "code example" in r.message.lower()]
            print_results(example_results, "Code Example Validation")

        if run_api_refs:
            api_results = [
                r for r in all_results if "api reference" in r.message.lower() or "module" in r.message.lower()
            ]
            print_results(api_results, "API Reference Validation")

        if run_config:
            config_results = [r for r in all_results if "configuration" in r.message.lower()]
            print_results(config_results, "Configuration Validation")

        # Count results
        passed = sum(1 for r in all_results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in all_results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in all_results if r.status == ValidationStatus.WARNING)

        print("\n📋 Validation Summary:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        print(f"  📊 Total: {len(all_results)}")

        if failed > 0:
            exit_code = 1

        results["validation"] = {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": len(all_results),
            "results": [
                {
                    "status": r.status.value,
                    "message": r.message,
                    "file_path": r.file_path,
                    "line_number": r.line_number,
                    "details": r.details,
                }
                for r in all_results
            ],
        }

    # Run coverage report if requested
    if run_coverage:
        coverage_report = generate_coverage_report(
            coverage_reporter,
            args.export.with_suffix(".coverage.json") if args.export else None,
        )
        results["coverage"] = coverage_report

        # Set exit code based on coverage threshold
        coverage_percentage = coverage_report["overall_metrics"]["coverage_percentage"]
        if coverage_percentage < 50.0:  # Minimum threshold
            print(
                f"\n⚠️  Warning: Documentation coverage ({coverage_percentage:.1f}%) is below recommended threshold (50%)"
            )
            if exit_code == 0:  # Don't override validation failures
                exit_code = 2  # Different exit code for coverage issues

    # Export results if requested
    if args.export and results:
        try:
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Results exported to: {args.export}")
        except Exception as e:
            print(f"\n❌ Failed to export results: {e}")
            exit_code = 1

    # Final summary
    if exit_code == 0:
        print("\n🎉 All documentation validation checks passed!")
    elif exit_code == 1:
        print("\n❌ Documentation validation failed. See details above.")
    elif exit_code == 2:
        print("\n⚠️  Documentation validation passed but coverage is below threshold.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
