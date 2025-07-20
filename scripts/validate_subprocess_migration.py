#!/usr/bin/env python3
"""
Subprocess Migration Validation Script

This script validates that the subprocess migration has been completed successfully
by checking for remaining insecure patterns and verifying secure alternatives are used.
"""

import json
import logging
import re
from pathlib import Path


class MigrationValidator:
    """Validates subprocess migration completion."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.validation_results = {
            "migrated_files": [],
            "remaining_issues": [],
            "nosec_suppressions": [],
            "validation_summary": {},
        }

    def validate_file(self, file_path: Path) -> dict:
        """Validate a single file for migration completion."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            issues = []

            # Check for direct subprocess imports
            if re.search(r"^import subprocess$", content, re.MULTILINE):
                # Check if it's followed by secure import fallback
                if not re.search(r"from src\.security\.subprocess_compatibility import", content):
                    issues.append("Direct subprocess import without secure fallback")

            # Check for shell=True usage
            if re.search(r"shell\s*=\s*True", content):
                issues.append("shell=True usage found")

            # Check for subprocess.run calls without secure wrapper
            subprocess_calls = re.findall(r"subprocess\.(run|call|check_output|check_call|Popen)", content)
            if subprocess_calls and not re.search(r"from src\.security\.subprocess_compatibility import", content):
                issues.append(f"Direct subprocess calls found: {len(subprocess_calls)}")

            # Check for nosec suppressions
            nosec_patterns = re.findall(r"# nosec B(404|603|602|605|607)", content)
            if nosec_patterns:
                issues.append(f"Nosec suppressions found: {nosec_patterns}")

            # Check for secure imports (positive validation)
            has_secure_import = bool(re.search(r"from src\.security\.subprocess_compatibility import", content))

            return {
                "file": str(file_path),
                "issues": issues,
                "has_secure_import": has_secure_import,
                "nosec_suppressions": nosec_patterns,
            }

        except Exception as e:
            return {"file": str(file_path), "error": str(e)}

    def validate_migration(self) -> dict:
        """Validate the entire migration."""
        print("🔍 Validating subprocess migration...")

        # Files that were identified for migration
        migration_targets = [
            "tests/run_human_review.py",
            "scripts/autofix.py",
            "scripts/update_dependencies.py",
            "scripts/validate_batch_modification.py",
            "tests/test_bandit_configuration_validation.py",
            "tests/test_e2e_pdf_pipeline.py",
            ".kiro/monitoring/check_documentation.py",
            "scripts/deploy_documentation.py",
            "scripts/security_validation.py",
            "scripts/validate_bandit_config.py",
            "src/docs/validation.py",
        ]

        migrated_count = 0
        remaining_issues = []

        for file_path in migration_targets:
            full_path = self.root_dir / file_path
            if full_path.exists():
                result = self.validate_file(full_path)

                if result.get("issues"):
                    remaining_issues.append(result)
                    print(f"❌ {file_path}: {len(result['issues'])} issues")
                    for issue in result["issues"]:
                        print(f"   - {issue}")
                else:
                    migrated_count += 1
                    print(f"✅ {file_path}: Migration complete")

                self.validation_results["migrated_files"].append(result)
            else:
                print(f"⚠️  {file_path}: File not found")

        # Summary
        total_files = len(migration_targets)
        success_rate = (migrated_count / total_files) * 100 if total_files > 0 else 0

        self.validation_results["validation_summary"] = {
            "total_files": total_files,
            "migrated_files": migrated_count,
            "files_with_issues": len(remaining_issues),
            "success_rate": success_rate,
        }

        self.validation_results["remaining_issues"] = remaining_issues

        print("\n📊 Migration Validation Summary:")
        print(f"   Total files: {total_files}")
        print(f"   Successfully migrated: {migrated_count}")
        print(f"   Files with remaining issues: {len(remaining_issues)}")
        print(f"   Success rate: {success_rate:.1f}%")

        return self.validation_results

    def check_nosec_suppressions(self) -> list[dict]:
        """Check for remaining nosec suppressions."""
        print("\n🔍 Checking for remaining nosec suppressions...")

        python_files = list(self.root_dir.rglob("*.py"))
        excluded_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
        }
        python_files = [f for f in python_files if not any(part in excluded_dirs for part in f.parts)]

        suppressions = []

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if re.search(r"# nosec B(404|603|602|605|607)", line):
                        suppressions.append({"file": str(file_path), "line": i, "content": line.strip()})
            except Exception as e:
                logging.debug(f"Error processing file {file_path}: {e}")
                continue

        print(f"Found {len(suppressions)} nosec suppressions")
        for suppression in suppressions[:10]:  # Show first 10
            print(f"   {suppression['file']}:{suppression['line']} - {suppression['content']}")

        if len(suppressions) > 10:
            print(f"   ... and {len(suppressions) - 10} more")

        self.validation_results["nosec_suppressions"] = suppressions
        return suppressions

    def generate_report(self, filename: str = "migration_validation_report.json"):
        """Generate a comprehensive validation report."""
        results = self.validate_migration()
        self.check_nosec_suppressions()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Validation report saved to {filename}")

        # Return success status
        return results["validation_summary"]["files_with_issues"] == 0


def main():
    """Main function to run validation."""
    validator = MigrationValidator()
    success = validator.generate_report()

    if success:
        print("\n🎉 Migration validation passed! All files successfully migrated.")
        return 0
    else:
        print("\n⚠️  Migration validation failed. Some files still have issues.")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
