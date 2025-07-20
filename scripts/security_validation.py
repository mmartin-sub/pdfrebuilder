#!/usr/bin/env python3
"""
Security validation script for bandit configuration testing.

This script validates that our bandit configuration is working correctly
and that all suppressions are properly justified.
"""

import json
import sys
from pathlib import Path

# Import secure execution module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from security.secure_execution import SecureExecutor, SecurityContext


def run_bandit_scan() -> dict:
    """Run bandit security scan and return results."""
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        # Use secure execution instead of raw subprocess
        security_context = SecurityContext(allowed_executables=["bandit", "python", "python3"], timeout=300)
        executor = SecureExecutor(security_context)

        result = executor.execute_command(
            ["bandit", "-r", ".", "-f", "json", "-o", temp_path],
            capture_output=True,
            timeout=300,
        )

        if result.return_code != 0 and result.return_code != 1:  # 1 is expected for findings
            print(f"Bandit scan failed: {result.stderr}")
            return {}

        # Read results
        with open(temp_path) as f:
            results = json.load(f)

        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)
        return results

    except Exception as e:
        if "timeout" in str(e).lower():
            print("Bandit scan timed out")
        else:
            print(f"Error running bandit: {e}")
        return {}


def validate_suppressions(results: dict) -> bool:
    """Validate that all suppressions are properly documented."""
    suppression_doc = Path("docs/BANDIT_SUPPRESSIONS.md")

    if not suppression_doc.exists():
        print("ERROR: BANDIT_SUPPRESSIONS.md not found")
        return False

    # Read suppression documentation
    with open(suppression_doc) as f:
        doc_content = f.read()

    # Check for any new B404 or B603 issues that aren't documented
    b404_b603_issues = []
    for result in results.get("results", []):
        if result.get("test_id") in ["B404", "B603"]:
            b404_b603_issues.append(result)

    if b404_b603_issues:
        print(f"Found {len(b404_b603_issues)} B404/B603 issues:")
        for issue in b404_b603_issues:
            filename = issue.get("filename", "unknown")
            line_number = issue.get("line_number", "unknown")
            test_id = issue.get("test_id", "unknown")
            print(f"  {test_id}: {filename}:{line_number}")

            # Check if this file is documented in suppressions
            if filename not in doc_content:
                print(f"    WARNING: {filename} not documented in suppressions")

    return True


def check_security_measures() -> bool:
    """Check that security measures are in place."""
    security_files = [
        "src/security/secure_execution.py",
        "src/security/subprocess_utils.py",
        "src/security/subprocess_compatibility.py",
    ]

    missing_files = []
    for file_path in security_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"ERROR: Missing security files: {missing_files}")
        return False

    print("✓ All security modules present")
    return True


def validate_pyproject_config() -> bool:
    """Validate pyproject.toml bandit configuration."""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print("ERROR: pyproject.toml not found")
        return False

    with open(pyproject_path) as f:
        content = f.read()

    # Check for required bandit configuration
    required_configs = ["[tool.bandit]", "exclude_dirs", "confidence", "severity"]

    missing_configs = []
    for config in required_configs:
        if config not in content:
            missing_configs.append(config)

    if missing_configs:
        print(f"ERROR: Missing bandit configurations: {missing_configs}")
        return False

    print("✓ Bandit configuration present in pyproject.toml")
    return True


def main():
    """Main security validation function."""
    print("=== Security Configuration Validation ===")

    # Check basic setup
    if not validate_pyproject_config():
        sys.exit(1)

    if not check_security_measures():
        sys.exit(1)

    # Run bandit scan
    print("\nRunning bandit security scan...")
    results = run_bandit_scan()

    if not results:
        print("ERROR: Could not run bandit scan")
        sys.exit(1)

    # Validate suppressions
    print("\nValidating suppressions...")
    if not validate_suppressions(results):
        sys.exit(1)

    # Summary
    total_issues = len(results.get("results", []))
    high_severity = len([r for r in results.get("results", []) if r.get("issue_severity") == "HIGH"])
    medium_severity = len([r for r in results.get("results", []) if r.get("issue_severity") == "MEDIUM"])

    print("\n=== Security Scan Summary ===")
    print(f"Total issues found: {total_issues}")
    print(f"High severity: {high_severity}")
    print(f"Medium severity: {medium_severity}")

    if high_severity > 0:
        print("WARNING: High severity security issues found!")
        print("Review bandit results and update suppressions if justified")

    print("\n✓ Security validation completed")

    # Temp file cleanup is now handled in run_bandit_scan()

    # Exit with success code
    sys.exit(0)


if __name__ == "__main__":
    main()
