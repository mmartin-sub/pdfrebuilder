#!/usr/bin/env python3
"""
Documentation Quality Assurance Script

This script provides comprehensive quality assurance for documentation,
including automated checks, quality metrics, and maintenance procedures.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docs.tools.coverage_reporter import DocumentationCoverageReporter
from docs.tools.validation import DocumentationValidator


class DocumentationQualityAssurance:
    """Comprehensive documentation quality assurance system."""

    def __init__(self):
        self.docs_dir = Path("docs")
        self.src_dir = Path("src")
        self.validator = DocumentationValidator()
        self.coverage_reporter = DocumentationCoverageReporter()

        # Quality thresholds
        self.quality_thresholds = {
            "api_coverage": 90.0,
            "example_pass_rate": 95.0,
            "config_coverage": 100.0,
            "link_pass_rate": 100.0,
            "overall_quality": 85.0,
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def run_comprehensive_quality_check(self) -> dict:
        """Run comprehensive documentation quality check."""
        self.logger.info("Starting comprehensive documentation quality check...")

        quality_report = {
            "timestamp": datetime.now().isoformat(),
            "quality_checks": {},
            "metrics": {},
            "issues": [],
            "recommendations": [],
            "overall_score": 0.0,
            "quality_grade": "F",
        }

        # Run individual quality checks
        quality_report["quality_checks"]["api_coverage"] = self._check_api_coverage()
        quality_report["quality_checks"]["example_validation"] = self._check_example_validation()
        quality_report["quality_checks"]["configuration_coverage"] = self._check_configuration_coverage()
        quality_report["quality_checks"]["link_validation"] = self._check_link_validation()
        quality_report["quality_checks"]["content_quality"] = self._check_content_quality()

        # Calculate metrics
        quality_report["metrics"] = self._calculate_quality_metrics(quality_report["quality_checks"])

        # Generate issues and recommendations
        quality_report["issues"] = self._identify_quality_issues(quality_report["quality_checks"])
        quality_report["recommendations"] = self._generate_quality_recommendations(quality_report["quality_checks"])

        # Calculate overall score and grade
        quality_report["overall_score"] = self._calculate_overall_score(quality_report["metrics"])
        quality_report["quality_grade"] = self._calculate_quality_grade(quality_report["overall_score"])

        self.logger.info(f"Quality check completed. Overall score: {quality_report['overall_score']:.1f}")
        return quality_report

    def _check_api_coverage(self) -> dict:
        """Check API documentation coverage."""
        self.logger.info("Checking API documentation coverage...")

        try:
            # Count Python files in src/
            py_files = list(self.src_dir.rglob("*.py"))
            total_files = len([f for f in py_files if not f.name.startswith("__")])

            # Count files with docstrings
            documented_files = 0
            undocumented_files = []

            for py_file in py_files:
                if py_file.name.startswith("__"):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")
                    if '"""' in content or "'''" in content:
                        documented_files += 1
                    else:
                        undocumented_files.append(str(py_file))
                except Exception as e:
                    self.logger.warning(f"Could not read {py_file}: {e}")
                    continue

            coverage_percentage = (documented_files / total_files * 100) if total_files > 0 else 0

            return {
                "status": ("pass" if coverage_percentage >= self.quality_thresholds["api_coverage"] else "fail"),
                "total_files": total_files,
                "documented_files": documented_files,
                "coverage_percentage": round(coverage_percentage, 1),
                "threshold": self.quality_thresholds["api_coverage"],
                "undocumented_files": undocumented_files[:10],  # Limit to first 10
            }

        except Exception as e:
            self.logger.error(f"Failed to check API coverage: {e}")
            return {"status": "error", "error": str(e)}

    def _check_example_validation(self) -> dict:
        """Check code example validation."""
        self.logger.info("Checking code example validation...")

        try:
            md_files = list(self.docs_dir.rglob("*.md"))
            total_examples = 0
            failed_examples = []

            for md_file in md_files:
                try:
                    results = self.validator.validate_code_examples(md_file)
                    total_examples += len(results)

                    for result in results:
                        if result.get("status") == "failed":
                            failed_examples.append(
                                {
                                    "file": str(md_file),
                                    "error": result.get("message", "Unknown error"),
                                }
                            )

                except Exception as e:
                    self.logger.warning(f"Could not validate examples in {md_file}: {e}")
                    continue

            passed_examples = total_examples - len(failed_examples)
            pass_rate = (passed_examples / total_examples * 100) if total_examples > 0 else 100

            return {
                "status": ("pass" if pass_rate >= self.quality_thresholds["example_pass_rate"] else "fail"),
                "total_examples": total_examples,
                "passed_examples": passed_examples,
                "failed_examples": len(failed_examples),
                "pass_rate": round(pass_rate, 1),
                "threshold": self.quality_thresholds["example_pass_rate"],
                "failures": failed_examples[:10],  # Limit to first 10
            }

        except Exception as e:
            self.logger.error(f"Failed to check example validation: {e}")
            return {"status": "error", "error": str(e)}

    def _check_configuration_coverage(self) -> dict:
        """Check configuration documentation coverage."""
        self.logger.info("Checking configuration documentation coverage...")

        try:
            # Import settings to get configuration options
            from pdfrebuilder.settings import CONFIG

            total_options = len(CONFIG)

            # Check if configuration reference exists
            config_file = self.docs_dir / "reference" / "configuration.md"

            if not config_file.exists():
                return {
                    "status": "fail",
                    "total_options": total_options,
                    "documented_options": 0,
                    "coverage_percentage": 0.0,
                    "threshold": self.quality_thresholds["config_coverage"],
                    "missing_file": True,
                }

            # Count documented options (simplified check)
            content = config_file.read_text(encoding="utf-8")
            documented_options = 0
            missing_options = []

            for key in CONFIG.keys():
                if f"### {key}" in content or f"#### `{key}`" in content:
                    documented_options += 1
                else:
                    missing_options.append(key)

            coverage_percentage = (documented_options / total_options * 100) if total_options > 0 else 0

            return {
                "status": ("pass" if coverage_percentage >= self.quality_thresholds["config_coverage"] else "fail"),
                "total_options": total_options,
                "documented_options": documented_options,
                "coverage_percentage": round(coverage_percentage, 1),
                "threshold": self.quality_thresholds["config_coverage"],
                "missing_options": missing_options,
            }

        except Exception as e:
            self.logger.error(f"Failed to check configuration coverage: {e}")
            return {"status": "error", "error": str(e)}

    def _check_link_validation(self) -> dict:
        """Check internal link validation."""
        self.logger.info("Checking internal link validation...")

        try:
            md_files = list(self.docs_dir.rglob("*.md"))
            total_links = 0
            broken_links = []

            import re

            for md_file in md_files:
                try:
                    content = md_file.read_text(encoding="utf-8")

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
                            total_links += 1

                            if link_url.startswith("/"):
                                link_path = Path(link_url[1:])
                            else:
                                link_path = md_file.parent / link_url

                            if not link_path.exists():
                                broken_links.append(
                                    {
                                        "file": str(md_file),
                                        "link": link_url,
                                        "target": str(link_path),
                                    }
                                )

                except Exception as e:
                    self.logger.warning(f"Could not check links in {md_file}: {e}")
                    continue

            working_links = total_links - len(broken_links)
            pass_rate = (working_links / total_links * 100) if total_links > 0 else 100

            return {
                "status": ("pass" if pass_rate >= self.quality_thresholds["link_pass_rate"] else "fail"),
                "total_links": total_links,
                "working_links": working_links,
                "broken_links": len(broken_links),
                "pass_rate": round(pass_rate, 1),
                "threshold": self.quality_thresholds["link_pass_rate"],
                "broken_link_details": broken_links[:10],  # Limit to first 10
            }

        except Exception as e:
            self.logger.error(f"Failed to check link validation: {e}")
            return {"status": "error", "error": str(e)}

    def _check_content_quality(self) -> dict:
        """Check general content quality."""
        self.logger.info("Checking content quality...")

        try:
            md_files = list(self.docs_dir.rglob("*.md"))
            total_files = len(md_files)

            quality_issues = []

            for md_file in md_files:
                try:
                    content = md_file.read_text(encoding="utf-8")

                    # Check for common quality issues
                    if len(content.strip()) < 100:
                        quality_issues.append(
                            {
                                "file": str(md_file),
                                "issue": "Very short content (less than 100 characters)",
                                "severity": "low",
                            }
                        )

                    if not content.startswith("#"):
                        quality_issues.append(
                            {
                                "file": str(md_file),
                                "issue": "Missing main heading",
                                "severity": "medium",
                            }
                        )

                    # Check for TODO or FIXME comments
                    if "TODO" in content or "FIXME" in content:
                        quality_issues.append(
                            {
                                "file": str(md_file),
                                "issue": "Contains TODO or FIXME comments",
                                "severity": "low",
                            }
                        )

                except Exception as e:
                    quality_issues.append(
                        {
                            "file": str(md_file),
                            "issue": f"Could not read file: {e}",
                            "severity": "high",
                        }
                    )

            # Calculate quality score based on issues
            high_issues = len([i for i in quality_issues if i["severity"] == "high"])
            medium_issues = len([i for i in quality_issues if i["severity"] == "medium"])
            low_issues = len([i for i in quality_issues if i["severity"] == "low"])

            # Simple scoring: high issues = -10, medium = -5, low = -1
            penalty = (high_issues * 10) + (medium_issues * 5) + (low_issues * 1)
            quality_score = max(0, 100 - penalty)

            return {
                "status": "pass" if quality_score >= 80 else "fail",
                "total_files": total_files,
                "quality_score": quality_score,
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "low_issues": low_issues,
                "issues": quality_issues[:20],  # Limit to first 20
            }

        except Exception as e:
            self.logger.error(f"Failed to check content quality: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_quality_metrics(self, quality_checks: dict) -> dict:
        """Calculate overall quality metrics."""
        metrics = {}

        # Extract key metrics from quality checks
        api_check = quality_checks.get("api_coverage", {})
        metrics["api_coverage"] = api_check.get("coverage_percentage", 0.0)

        example_check = quality_checks.get("example_validation", {})
        metrics["example_pass_rate"] = example_check.get("pass_rate", 0.0)

        config_check = quality_checks.get("configuration_coverage", {})
        metrics["config_coverage"] = config_check.get("coverage_percentage", 0.0)

        link_check = quality_checks.get("link_validation", {})
        metrics["link_pass_rate"] = link_check.get("pass_rate", 0.0)

        content_check = quality_checks.get("content_quality", {})
        metrics["content_quality"] = content_check.get("quality_score", 0.0)

        return metrics

    def _calculate_overall_score(self, metrics: dict) -> float:
        """Calculate overall quality score."""
        # Weighted average of all metrics
        weights = {
            "api_coverage": 0.25,
            "example_pass_rate": 0.25,
            "config_coverage": 0.20,
            "link_pass_rate": 0.15,
            "content_quality": 0.15,
        }

        total_score = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in metrics:
                total_score += metrics[metric] * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _calculate_quality_grade(self, score: float) -> str:
        """Calculate quality grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _identify_quality_issues(self, quality_checks: dict) -> list[dict]:
        """Identify quality issues from checks."""
        issues = []

        for check_name, check_result in quality_checks.items():
            if check_result.get("status") == "fail":
                issues.append(
                    {
                        "category": check_name,
                        "severity": ("high" if check_name in ["api_coverage", "example_validation"] else "medium"),
                        "description": f"{check_name} failed quality threshold",
                        "details": check_result,
                    }
                )
            elif check_result.get("status") == "error":
                issues.append(
                    {
                        "category": check_name,
                        "severity": "high",
                        "description": f"Error during {check_name} check",
                        "details": check_result,
                    }
                )

        return issues

    def _generate_quality_recommendations(self, quality_checks: dict) -> list[str]:
        """Generate quality improvement recommendations."""
        recommendations = []

        # API coverage recommendations
        api_check = quality_checks.get("api_coverage", {})
        if api_check.get("status") == "fail":
            coverage = api_check.get("coverage_percentage", 0)
            threshold = api_check.get("threshold", 90)
            recommendations.append(
                f"Improve API documentation coverage from {coverage:.1f}% to {threshold:.1f}%. "
                f"Add docstrings to {len(api_check.get('undocumented_files', []))} undocumented files."
            )

        # Example validation recommendations
        example_check = quality_checks.get("example_validation", {})
        if example_check.get("status") == "fail":
            pass_rate = example_check.get("pass_rate", 0)
            threshold = example_check.get("threshold", 95)
            failed = example_check.get("failed_examples", 0)
            recommendations.append(
                f"Improve code example pass rate from {pass_rate:.1f}% to {threshold:.1f}%. "
                f"Fix {failed} failing code examples."
            )

        # Configuration coverage recommendations
        config_check = quality_checks.get("configuration_coverage", {})
        if config_check.get("status") == "fail":
            missing = len(config_check.get("missing_options", []))
            if missing > 0:
                recommendations.append(
                    f"Document {missing} missing configuration options in the configuration reference."
                )

        # Link validation recommendations
        link_check = quality_checks.get("link_validation", {})
        if link_check.get("status") == "fail":
            broken = link_check.get("broken_links", 0)
            recommendations.append(f"Fix {broken} broken internal links in documentation.")

        # Content quality recommendations
        content_check = quality_checks.get("content_quality", {})
        if content_check.get("status") == "fail":
            high_issues = content_check.get("high_issues", 0)
            medium_issues = content_check.get("medium_issues", 0)
            if high_issues > 0:
                recommendations.append(f"Address {high_issues} high-severity content quality issues.")
            if medium_issues > 0:
                recommendations.append(f"Address {medium_issues} medium-severity content quality issues.")

        return recommendations

    def generate_quality_report(self, output_file: Path | None = None) -> dict:
        """Generate comprehensive quality report."""
        self.logger.info("Generating comprehensive quality report...")

        report = self.run_comprehensive_quality_check()

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Quality report saved to {output_file}")

        return report

    def print_quality_summary(self, report: dict):
        """Print formatted quality summary."""
        print("\n" + "=" * 60)
        print("DOCUMENTATION QUALITY ASSURANCE REPORT")
        print("=" * 60)

        # Overall score and grade
        score = report.get("overall_score", 0)
        grade = report.get("quality_grade", "F")

        grade_icons = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "💀"}

        print(f"\nOverall Quality: {grade_icons.get(grade, '❓')} {grade} ({score:.1f}/100)")

        # Metrics summary
        metrics = report.get("metrics", {})
        print("\nQuality Metrics:")
        print(f"  API Coverage: {metrics.get('api_coverage', 0):.1f}%")
        print(f"  Example Pass Rate: {metrics.get('example_pass_rate', 0):.1f}%")
        print(f"  Config Coverage: {metrics.get('config_coverage', 0):.1f}%")
        print(f"  Link Pass Rate: {metrics.get('link_pass_rate', 0):.1f}%")
        print(f"  Content Quality: {metrics.get('content_quality', 0):.1f}%")

        # Issues summary
        issues = report.get("issues", [])
        if issues:
            high_issues = len([i for i in issues if i.get("severity") == "high"])
            medium_issues = len([i for i in issues if i.get("severity") == "medium"])
            low_issues = len([i for i in issues if i.get("severity") == "low"])

            print(f"\nQuality Issues: {len(issues)} total")
            print(f"  High: {high_issues}, Medium: {medium_issues}, Low: {low_issues}")

        # Top recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


def main():
    """Main function for documentation quality assurance."""
    parser = argparse.ArgumentParser(
        description="Documentation Quality Assurance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run comprehensive quality check
  python scripts/documentation_quality_assurance.py --check

  # Generate detailed quality report
  python scripts/documentation_quality_assurance.py --report --output quality_report.json

  # Run with verbose output
  python scripts/documentation_quality_assurance.py --check --verbose
        """,
    )

    parser.add_argument("--check", action="store_true", help="Run quality checks")
    parser.add_argument("--report", action="store_true", help="Generate quality report")
    parser.add_argument("--output", type=Path, help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    qa = DocumentationQualityAssurance()

    try:
        if args.report:
            report = qa.generate_quality_report(args.output)
            qa.print_quality_summary(report)
        elif args.check:
            report = qa.run_comprehensive_quality_check()
            qa.print_quality_summary(report)
        else:
            # Default to quality check
            report = qa.run_comprehensive_quality_check()
            qa.print_quality_summary(report)

        # Exit with non-zero code if quality is poor
        grade = report.get("quality_grade", "F")
        if grade in ["D", "F"]:
            return 1
        else:
            return 0

    except Exception as e:
        print(f"Error during quality assurance: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
