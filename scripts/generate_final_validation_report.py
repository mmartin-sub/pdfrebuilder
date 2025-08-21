#!/usr/bin/env python3
"""
Generate final validation report for the complete documentation system.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for security utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from pdfrebuilder.security.path_utils import PathSecurityError, SecurePathManager
from pdfrebuilder.security.subprocess_utils import SecureSubprocessRunner, SecurityError


def count_documentation_files() -> dict:
    """Count and categorize documentation files."""
    docs_dir = Path("docs")
    stats = {"total_files": 0, "total_size": 0, "by_category": {}, "by_directory": {}}

    categories = {
        "guides": ["guides/"],
        "api": ["api/"],
        "reference": ["reference/"],
        "examples": ["examples/"],
        "core": [
            "README.md",
            "INSTALLATION.md",
            "ARCHITECTURE.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "MIGRATION.md",
        ],
    }

    for root, _dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(docs_dir)

                stats["total_files"] += 1
                file_size = file_path.stat().st_size
                stats["total_size"] += file_size

                # Categorize by directory
                dir_name = str(rel_path.parent) if str(rel_path.parent) != "." else "root"
                if dir_name not in stats["by_directory"]:
                    stats["by_directory"][dir_name] = {"count": 0, "size": 0}
                stats["by_directory"][dir_name]["count"] += 1
                stats["by_directory"][dir_name]["size"] += file_size

                # Categorize by type
                categorized = False
                for category, patterns in categories.items():
                    for pattern in patterns:
                        if str(rel_path).startswith(pattern) or file == pattern:
                            if category not in stats["by_category"]:
                                stats["by_category"][category] = {"count": 0, "size": 0}
                            stats["by_category"][category]["count"] += 1
                            stats["by_category"][category]["size"] += file_size
                            categorized = True
                            break
                    if categorized:
                        break

                if not categorized:
                    if "other" not in stats["by_category"]:
                        stats["by_category"]["other"] = {"count": 0, "size": 0}
                    stats["by_category"]["other"]["count"] += 1
                    stats["by_category"]["other"]["size"] += file_size

    return stats


def validate_examples() -> dict:
    """Validate all examples and return results."""
    examples_dir = Path("examples")
    results = {
        "total_examples": 0,
        "working_examples": 0,
        "failed_examples": 0,
        "example_details": [],
    }

    if not examples_dir.exists():
        return results

    for example_file in examples_dir.glob("*.py"):
        if example_file.name.startswith("__"):
            continue

        results["total_examples"] += 1

        # Test the example
        try:
            # Validate file path using secure path manager
            try:
                validated_path = SecurePathManager.validate_path(example_file, base_path=Path.cwd(), must_exist=True)
            except PathSecurityError as e:
                raise ValueError(f"Path security validation failed: {e}")

            cmd = ["hatch", "run", "python", str(validated_path)]

            runner = SecureSubprocessRunner(base_path=Path.cwd(), timeout=300)
            result = runner.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                results["working_examples"] += 1
                status = "working"
            else:
                results["failed_examples"] += 1
                status = "failed"

            results["example_details"].append(
                {
                    "file": example_file.name,
                    "status": status,
                    "exit_code": result.returncode,
                }
            )

        except SecurityError as e:
            results["failed_examples"] += 1
            results["example_details"].append({"file": example_file.name, "status": "security_error", "error": str(e)})
        except Exception as e:
            results["failed_examples"] += 1
            if "timeout" in str(e).lower():
                results["example_details"].append({"file": example_file.name, "status": "timeout", "exit_code": -1})
            else:
                results["example_details"].append({"file": example_file.name, "status": "error", "error": str(e)})

    return results


def check_api_coverage() -> dict:
    """Check API documentation coverage."""
    src_dir = Path("src")
    api_docs_dir = Path("docs/api")

    coverage = {
        "total_modules": 0,
        "documented_modules": 0,
        "coverage_percentage": 0,
        "missing_docs": [],
        "documented_modules_list": [],
    }

    if not src_dir.exists():
        return coverage

    # Find all Python modules
    python_files = []
    for root, _dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = Path(root) / file
                python_files.append(rel_path)

    coverage["total_modules"] = len(python_files)

    # Check which modules have documentation
    for py_file in python_files:
        rel_path = py_file.relative_to(src_dir)
        module_name = str(rel_path).replace("/", ".").replace(".py", "")

        # Look for corresponding documentation
        possible_doc_paths = [
            api_docs_dir / f"{rel_path.stem}.md",
            api_docs_dir / rel_path.parent / f"{rel_path.stem}.md",
        ]

        documented = False
        for doc_path in possible_doc_paths:
            if doc_path.exists():
                documented = True
                coverage["documented_modules_list"].append(module_name)
                break

        if not documented:
            coverage["missing_docs"].append(module_name)

    coverage["documented_modules"] = len(coverage["documented_modules_list"])
    if coverage["total_modules"] > 0:
        coverage["coverage_percentage"] = (coverage["documented_modules"] / coverage["total_modules"]) * 100

    return coverage


def generate_report() -> dict:
    """Generate comprehensive validation report."""
    print("📊 Generating final validation report...")

    report = {
        "generated_at": datetime.now().isoformat(),
        "validation_summary": {
            "overall_status": "success",
            "issues_found": 0,
            "warnings": 0,
        },
        "documentation_stats": count_documentation_files(),
        "examples_validation": validate_examples(),
        "api_coverage": check_api_coverage(),
        "quality_metrics": {},
        "recommendations": [],
    }

    # Calculate quality metrics
    doc_stats = report["documentation_stats"]
    examples = report["examples_validation"]
    api_cov = report["api_coverage"]

    report["quality_metrics"] = {
        "documentation_completeness": min(100, (doc_stats["total_files"] / 50) * 100),  # Target: 50+ files
        "example_success_rate": (examples["working_examples"] / max(1, examples["total_examples"])) * 100,
        "api_documentation_coverage": api_cov["coverage_percentage"],
        "overall_quality_score": 0,
    }

    # Calculate overall quality score
    metrics = report["quality_metrics"]
    overall_score = (
        metrics["documentation_completeness"] * 0.3
        + metrics["example_success_rate"] * 0.4
        + metrics["api_documentation_coverage"] * 0.3
    )
    report["quality_metrics"]["overall_quality_score"] = min(100, overall_score)

    # Generate recommendations
    recommendations = []

    if examples["failed_examples"] > 0:
        recommendations.append(f"Fix {examples['failed_examples']} failing examples")
        report["validation_summary"]["issues_found"] += examples["failed_examples"]

    if api_cov["coverage_percentage"] < 80:
        recommendations.append(f"Improve API documentation coverage (currently {api_cov['coverage_percentage']:.1f}%)")
        report["validation_summary"]["warnings"] += 1

    if doc_stats["total_files"] < 50:
        recommendations.append("Consider adding more comprehensive documentation")
        report["validation_summary"]["warnings"] += 1

    if not recommendations:
        recommendations.append("Documentation system is in excellent condition!")

    report["recommendations"] = recommendations

    # Set overall status
    if report["validation_summary"]["issues_found"] > 0:
        report["validation_summary"]["overall_status"] = "issues_found"
    elif report["validation_summary"]["warnings"] > 0:
        report["validation_summary"]["overall_status"] = "warnings"

    return report


def print_report(report: dict):
    """Print formatted validation report."""
    print("\n" + "=" * 70)
    print("📋 FINAL DOCUMENTATION VALIDATION REPORT")
    print("=" * 70)

    # Overall status
    status = report["validation_summary"]["overall_status"]
    status_icon = "✅" if status == "success" else "⚠️" if status == "warnings" else "❌"
    print(f"\n{status_icon} Overall Status: {status.upper()}")

    # Documentation statistics
    stats = report["documentation_stats"]
    print("\n📚 Documentation Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size']:,} bytes")
    print("  Categories:")
    for category, data in stats["by_category"].items():
        print(f"    {category}: {data['count']} files ({data['size']:,} bytes)")

    # Examples validation
    examples = report["examples_validation"]
    print("\n🧪 Examples Validation:")
    print(f"  Total examples: {examples['total_examples']}")
    print(f"  Working: {examples['working_examples']}")
    print(f"  Failed: {examples['failed_examples']}")
    if examples["total_examples"] > 0:
        success_rate = (examples["working_examples"] / examples["total_examples"]) * 100
        print(f"  Success rate: {success_rate:.1f}%")

    # API coverage
    api_cov = report["api_coverage"]
    print("\n📖 API Documentation Coverage:")
    print(f"  Total modules: {api_cov['total_modules']}")
    print(f"  Documented: {api_cov['documented_modules']}")
    print(f"  Coverage: {api_cov['coverage_percentage']:.1f}%")

    # Quality metrics
    metrics = report["quality_metrics"]
    print("\n📊 Quality Metrics:")
    print(f"  Documentation completeness: {metrics['documentation_completeness']:.1f}%")
    print(f"  Example success rate: {metrics['example_success_rate']:.1f}%")
    print(f"  API coverage: {metrics['api_documentation_coverage']:.1f}%")
    print(f"  Overall quality score: {metrics['overall_quality_score']:.1f}/100")

    # Issues and recommendations
    validation = report["validation_summary"]
    if validation["issues_found"] > 0 or validation["warnings"] > 0:
        print("\n⚠️  Issues Summary:")
        print(f"  Issues: {validation['issues_found']}")
        print(f"  Warnings: {validation['warnings']}")

    print("\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")

    print("\n" + "=" * 70)


def main():
    """Main function."""
    try:
        report = generate_report()

        # Save report to file
        report_file = Path("docs/final_validation_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print formatted report
        print_report(report)

        print(f"\n📄 Full report saved to: {report_file}")

        # Exit with appropriate code
        if report["validation_summary"]["overall_status"] == "issues_found":
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"❌ Error generating validation report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
