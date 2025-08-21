#!/usr/bin/env python3
"""
Documentation maintenance and quality monitoring script.

This script provides comprehensive documentation maintenance procedures,
including quality metrics monitoring, automated updates, and maintenance reporting.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docs.tools.coverage_reporter import DocumentationCoverageReporter
from docs.tools.validation import DocumentationValidator, ValidationStatus


class DocumentationMaintenanceManager:
    """Manages documentation maintenance procedures and quality metrics."""

    def __init__(self):
        self.validator = DocumentationValidator()
        self.coverage_reporter = DocumentationCoverageReporter()
        self.docs_dir = Path("docs")
        self.src_dir = Path("src")
        self.scripts_dir = Path("scripts")

        # Quality thresholds
        self.quality_thresholds = {
            "api_coverage": 90.0,
            "example_pass_rate": 95.0,
            "config_pass_rate": 100.0,
            "link_pass_rate": 100.0,
            "overall_coverage": 80.0,
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def run_quality_audit(self) -> dict:
        """Run comprehensive documentation quality audit."""
        self.logger.info("Starting documentation quality audit...")

        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "coverage_report": {},
            "quality_metrics": {},
            "recommendations": [],
            "action_items": [],
        }

        # Run validation
        validation_results = self._run_comprehensive_validation()
        audit_results["validation_results"] = validation_results

        # Generate coverage report
        coverage_report = self.coverage_reporter.generate_coverage_report()
        audit_results["coverage_report"] = coverage_report

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(validation_results, coverage_report)
        audit_results["quality_metrics"] = quality_metrics

        # Generate recommendations
        recommendations = self._generate_recommendations(quality_metrics, validation_results)
        audit_results["recommendations"] = recommendations

        # Generate action items
        action_items = self._generate_action_items(quality_metrics, validation_results)
        audit_results["action_items"] = action_items

        self.logger.info("Documentation quality audit completed")
        return audit_results

    def _run_comprehensive_validation(self) -> dict:
        """Run comprehensive documentation validation."""
        self.logger.info("Running comprehensive documentation validation...")

        results = {
            "code_examples": [],
            "api_references": [],
            "configuration_examples": [],
            "link_validation": [],
            "summary": {},
        }

        # Find all markdown files
        md_files = list(self.docs_dir.rglob("*.md"))

        for md_file in md_files:
            # Validate code examples
            code_results = self.validator.validate_code_examples(md_file)
            results["code_examples"].extend(code_results)

            # Validate API references
            api_results = self.validator.validate_api_references(md_file)
            results["api_references"].extend(api_results)

            # Validate configuration examples
            config_results = self.validator.validate_configuration_examples(md_file)
            results["configuration_examples"].extend(config_results)

            # Validate links (basic implementation)
            link_results = self._validate_links(md_file)
            results["link_validation"].extend(link_results)

        # Calculate summary statistics
        results["summary"] = self._calculate_validation_summary(results)

        return results

    def _validate_links(self, md_file: Path) -> list:
        """Validate links in markdown file."""
        results = []

        try:
            content = md_file.read_text(encoding="utf-8")

            # Simple regex-based link validation
            import re

            # Find markdown links
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            links = re.findall(link_pattern, content)

            for _link_text, link_url in links:
                if link_url.startswith("http"):
                    # External link - skip for now
                    continue
                elif link_url.startswith("#"):
                    # Internal anchor - skip for now
                    continue
                else:
                    # Internal file link
                    if link_url.startswith("/"):
                        link_path = Path(link_url[1:])
                    else:
                        link_path = md_file.parent / link_url

                    if not link_path.exists():
                        results.append(
                            {
                                "status": ValidationStatus.FAILED,
                                "message": f"Broken internal link: {link_url}",
                                "file_path": str(md_file),
                                "line_number": None,
                                "details": f"Link target does not exist: {link_path}",
                            }
                        )
                    else:
                        results.append(
                            {
                                "status": ValidationStatus.PASSED,
                                "message": f"Valid internal link: {link_url}",
                                "file_path": str(md_file),
                                "line_number": None,
                                "details": None,
                            }
                        )

        except Exception as e:
            results.append(
                {
                    "status": ValidationStatus.FAILED,
                    "message": f"Error validating links in {md_file}",
                    "file_path": str(md_file),
                    "line_number": None,
                    "details": str(e),
                }
            )

        return results

    def _calculate_validation_summary(self, results: dict) -> dict:
        """Calculate summary statistics for validation results."""
        summary = {}

        for category, category_results in results.items():
            if category == "summary":
                continue

            if not category_results:
                summary[category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0,
                    "pass_rate": 100.0,
                }
                continue

            total = len(category_results)
            passed = sum(1 for r in category_results if r.get("status") == ValidationStatus.PASSED)
            failed = sum(1 for r in category_results if r.get("status") == ValidationStatus.FAILED)
            warnings = sum(1 for r in category_results if r.get("status") == ValidationStatus.WARNING)

            pass_rate = (passed / total * 100) if total > 0 else 100.0

            summary[category] = {
                "total": total,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "pass_rate": pass_rate,
            }

        return summary

    def _calculate_quality_metrics(self, validation_results: dict, coverage_report: dict) -> dict:
        """Calculate overall quality metrics."""
        metrics = {}

        # Extract validation pass rates
        summary = validation_results.get("summary", {})
        metrics["example_pass_rate"] = summary.get("code_examples", {}).get("pass_rate", 0.0)
        metrics["api_reference_pass_rate"] = summary.get("api_references", {}).get("pass_rate", 0.0)
        metrics["config_pass_rate"] = summary.get("configuration_examples", {}).get("pass_rate", 0.0)
        metrics["link_pass_rate"] = summary.get("link_validation", {}).get("pass_rate", 0.0)

        # Extract coverage metrics
        overall_metrics = coverage_report.get("overall_metrics", {})
        metrics["api_coverage"] = overall_metrics.get("coverage_percentage", 0.0)
        metrics["overall_coverage"] = overall_metrics.get("coverage_percentage", 0.0)

        # Calculate composite quality score
        weights = {
            "api_coverage": 0.25,
            "example_pass_rate": 0.25,
            "config_pass_rate": 0.20,
            "link_pass_rate": 0.15,
            "api_reference_pass_rate": 0.15,
        }

        quality_score = sum(metrics.get(metric, 0.0) * weight for metric, weight in weights.items())

        metrics["composite_quality_score"] = quality_score

        # Quality grade
        if quality_score >= 90:
            metrics["quality_grade"] = "A"
        elif quality_score >= 80:
            metrics["quality_grade"] = "B"
        elif quality_score >= 70:
            metrics["quality_grade"] = "C"
        elif quality_score >= 60:
            metrics["quality_grade"] = "D"
        else:
            metrics["quality_grade"] = "F"

        return metrics

    def _generate_recommendations(self, quality_metrics: dict, validation_results: dict) -> list[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []

        # Check against thresholds
        if quality_metrics.get("api_coverage", 0) < self.quality_thresholds["api_coverage"]:
            recommendations.append(
                f"API documentation coverage ({quality_metrics.get('api_coverage', 0):.1f}%) "
                f"is below target ({self.quality_thresholds['api_coverage']:.1f}%). "
                "Add docstrings to undocumented public APIs."
            )

        if quality_metrics.get("example_pass_rate", 0) < self.quality_thresholds["example_pass_rate"]:
            recommendations.append(
                f"Code example pass rate ({quality_metrics.get('example_pass_rate', 0):.1f}%) "
                f"is below target ({self.quality_thresholds['example_pass_rate']:.1f}%). "
                "Fix failing code examples in documentation."
            )

        if quality_metrics.get("config_pass_rate", 0) < self.quality_thresholds["config_pass_rate"]:
            recommendations.append(
                f"Configuration example pass rate ({quality_metrics.get('config_pass_rate', 0):.1f}%) "
                f"is below target ({self.quality_thresholds['config_pass_rate']:.1f}%). "
                "Fix invalid configuration examples."
            )

        if quality_metrics.get("link_pass_rate", 0) < self.quality_thresholds["link_pass_rate"]:
            recommendations.append(
                f"Link validation pass rate ({quality_metrics.get('link_pass_rate', 0):.1f}%) "
                f"is below target ({self.quality_thresholds['link_pass_rate']:.1f}%). "
                "Fix broken internal links in documentation."
            )

        # Quality grade recommendations
        quality_grade = quality_metrics.get("quality_grade", "F")
        if quality_grade in ["D", "F"]:
            recommendations.append(
                f"Overall documentation quality grade is {quality_grade}. "
                "Consider a comprehensive documentation review and improvement effort."
            )
        elif quality_grade == "C":
            recommendations.append(
                "Documentation quality is acceptable but has room for improvement. Focus on the lowest-scoring metrics."
            )

        return recommendations

    def _generate_action_items(self, quality_metrics: dict, validation_results: dict) -> list[dict]:
        """Generate specific action items based on validation results."""
        action_items = []

        # Failed validations become action items
        for category, results in validation_results.items():
            if category == "summary":
                continue

            failed_results = [r for r in results if r.get("status") == ValidationStatus.FAILED]

            for failed_result in failed_results[:5]:  # Limit to top 5 per category
                action_items.append(
                    {
                        "category": category,
                        "priority": self._determine_priority(category, failed_result),
                        "description": failed_result.get("message", ""),
                        "file_path": failed_result.get("file_path", ""),
                        "line_number": failed_result.get("line_number"),
                        "details": failed_result.get("details", ""),
                    }
                )

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        action_items.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return action_items

    def _determine_priority(self, category: str, failed_result: dict) -> str:
        """Determine priority level for action item."""
        if category == "code_examples":
            return "high"  # Broken examples are high priority
        elif category == "configuration_examples":
            return "high"  # Invalid config examples are high priority
        elif category == "api_references":
            return "medium"  # API reference issues are medium priority
        elif category == "link_validation":
            return "low"  # Broken links are lower priority
        else:
            return "medium"

    def generate_maintenance_report(self, output_path: Path | None = None) -> dict:
        """Generate comprehensive maintenance report."""
        self.logger.info("Generating documentation maintenance report...")

        # Run quality audit
        audit_results = self.run_quality_audit()

        # Add maintenance-specific information
        maintenance_report = {
            **audit_results,
            "maintenance_info": {
                "last_audit": datetime.now().isoformat(),
                "next_scheduled_audit": (datetime.now() + timedelta(days=7)).isoformat(),
                "maintenance_status": self._determine_maintenance_status(audit_results),
                "urgent_actions": len(
                    [item for item in audit_results.get("action_items", []) if item.get("priority") == "high"]
                ),
            },
        }

        # Export report if path provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(maintenance_report, f, indent=2, default=str)
            self.logger.info(f"Maintenance report exported to: {output_path}")

        return maintenance_report

    def _determine_maintenance_status(self, audit_results: dict) -> str:
        """Determine overall maintenance status."""
        quality_metrics = audit_results.get("quality_metrics", {})
        quality_score = quality_metrics.get("composite_quality_score", 0)

        high_priority_actions = len(
            [item for item in audit_results.get("action_items", []) if item.get("priority") == "high"]
        )

        if quality_score >= 90 and high_priority_actions == 0:
            return "excellent"
        elif quality_score >= 80 and high_priority_actions <= 2:
            return "good"
        elif quality_score >= 70 and high_priority_actions <= 5:
            return "needs_attention"
        else:
            return "critical"

    def print_maintenance_summary(self, report: dict):
        """Print a formatted maintenance summary."""
        print("\n" + "=" * 60)
        print("DOCUMENTATION MAINTENANCE REPORT")
        print("=" * 60)

        # Overall status
        maintenance_info = report.get("maintenance_info", {})
        status = maintenance_info.get("maintenance_status", "unknown")

        status_icons = {
            "excellent": "🟢",
            "good": "🟡",
            "needs_attention": "🟠",
            "critical": "🔴",
        }

        print(f"\nOverall Status: {status_icons.get(status, '❓')} {status.upper()}")

        # Quality metrics
        quality_metrics = report.get("quality_metrics", {})
        print(f"\nQuality Score: {quality_metrics.get('composite_quality_score', 0):.1f}/100")
        print(f"Quality Grade: {quality_metrics.get('quality_grade', 'N/A')}")

        # Key metrics
        print("\nKey Metrics:")
        print(f"  API Coverage: {quality_metrics.get('api_coverage', 0):.1f}%")
        print(f"  Example Pass Rate: {quality_metrics.get('example_pass_rate', 0):.1f}%")
        print(f"  Config Pass Rate: {quality_metrics.get('config_pass_rate', 0):.1f}%")
        print(f"  Link Pass Rate: {quality_metrics.get('link_pass_rate', 0):.1f}%")

        # Action items
        action_items = report.get("action_items", [])
        urgent_actions = maintenance_info.get("urgent_actions", 0)

        print(f"\nAction Items: {len(action_items)} total, {urgent_actions} urgent")

        # Top recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


def main():
    """Main function for documentation maintenance."""
    parser = argparse.ArgumentParser(
        description="Documentation maintenance and quality monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run quality audit
  python scripts/documentation_maintenance.py --audit

  # Generate maintenance report
  python scripts/documentation_maintenance.py --report

  # Export detailed report
  python scripts/documentation_maintenance.py --report --export maintenance_report.json

  # Run with verbose output
  python scripts/documentation_maintenance.py --audit --verbose
        """,
    )

    parser.add_argument("--audit", action="store_true", help="Run quality audit")
    parser.add_argument("--report", action="store_true", help="Generate maintenance report")
    parser.add_argument("--export", type=Path, help="Export report to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize maintenance manager
    manager = DocumentationMaintenanceManager()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.audit:
            # Run quality audit
            audit_results = manager.run_quality_audit()

            if args.export:
                with open(args.export, "w", encoding="utf-8") as f:
                    json.dump(audit_results, f, indent=2, default=str)
                print(f"Audit results exported to: {args.export}")

            # Print summary
            manager.print_maintenance_summary(audit_results)

        elif args.report:
            # Generate maintenance report
            report = manager.generate_maintenance_report(args.export)
            manager.print_maintenance_summary(report)

        else:
            # Default: run audit
            audit_results = manager.run_quality_audit()
            manager.print_maintenance_summary(audit_results)

    except Exception as e:
        print(f"Error during documentation maintenance: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
