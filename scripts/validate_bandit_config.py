#!/usr/bin/env python3
"""
Validate bandit configuration and security testing setup.

This script validates that the bandit configuration is working correctly
and that security testing is properly integrated.
"""

import json
import sys
from pathlib import Path

# Import secure execution module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from security.secure_execution import SecureExecutor, SecurityContext


def run_bandit_scan():
    """Run bandit scan and return results."""
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        # Use secure execution instead of raw subprocess
        security_context = SecurityContext(allowed_executables=["bandit", "python", "python3"], timeout=60)
        executor = SecureExecutor(security_context)

        result = executor.execute_command(
            [
                "bandit",
                "-r",
                "src/",
                "scripts/",
                "--severity-level",
                "medium",
                "--confidence-level",
                "medium",
                "-f",
                "json",
                "-o",
                temp_path,
            ],
            capture_output=True,
            timeout=60,
        )

        # Read results from temp file
        try:
            with open(temp_path) as f:
                scan_results = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            scan_results = {}
        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

        if result.return_code == 0:
            print("✅ Bandit scan completed successfully with no issues")
            return scan_results
        elif result.return_code == 1:
            # Exit code 1 means issues found
            print("⚠️  Bandit scan found security issues")
            return scan_results
        else:
            print(f"❌ Bandit scan failed with exit code {result.return_code}")
            print(f"Error: {result.stderr}")
            return None

    except Exception as e:
        if "timeout" in str(e).lower():
            print("❌ Bandit scan timed out")
        else:
            print(f"❌ Error running bandit: {e}")
        return None


def validate_configuration():
    """Validate bandit configuration in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False

    content = pyproject_path.read_text()

    # Check for bandit configuration section
    if "[tool.bandit]" not in content:
        print("❌ [tool.bandit] section not found in pyproject.toml")
        return False

    print("✅ Bandit configuration section found")

    # Check for key configuration elements
    required_configs = ["exclude_dirs", "skips", "confidence", "severity"]

    missing_configs = []
    for config in required_configs:
        if config not in content:
            missing_configs.append(config)

    if missing_configs:
        print(f"❌ Missing configuration elements: {missing_configs}")
        return False

    print("✅ All required configuration elements present")
    return True


def validate_security_commands():
    """Validate that security testing commands are available."""
    commands = [
        "security-scan",
        "security-scan-json",
        "security-test",
        "security-validate",
    ]

    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    missing_commands = []
    for command in commands:
        if command not in content:
            missing_commands.append(command)

    if missing_commands:
        print(f"❌ Missing security commands: {missing_commands}")
        return False

    print("✅ All security testing commands configured")
    return True


def validate_documentation():
    """Validate that security documentation exists."""
    docs_path = Path("docs/BANDIT_SUPPRESSIONS.md")

    if not docs_path.exists():
        print("❌ Security documentation not found")
        return False

    content = docs_path.read_text()

    # Check for key documentation sections
    required_sections = [
        "Security Review Process",
        "Bandit Configuration",
        "Security Testing Configuration",
        "Regular Review Schedule",
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        print(f"❌ Missing documentation sections: {missing_sections}")
        return False

    print("✅ Security documentation complete")
    return True


def main():
    """Main validation function."""
    print("🔒 Validating Bandit Security Configuration")
    print("=" * 50)

    all_passed = True

    # Validate configuration
    print("\n📋 Validating Configuration...")
    if not validate_configuration():
        all_passed = False

    # Validate security commands
    print("\n⚙️  Validating Security Commands...")
    if not validate_security_commands():
        all_passed = False

    # Validate documentation
    print("\n📚 Validating Documentation...")
    if not validate_documentation():
        all_passed = False

    # Run bandit scan
    print("\n🔍 Running Bandit Scan...")
    scan_results = run_bandit_scan()

    if scan_results is not None:
        metrics = scan_results.get("metrics", {}).get("_totals", {})
        medium_issues = metrics.get("SEVERITY.MEDIUM", 0)
        high_issues = metrics.get("SEVERITY.HIGH", 0)

        print("📊 Scan Results:")
        print(f"   - Medium severity issues: {medium_issues}")
        print(f"   - High severity issues: {high_issues}")

        if high_issues > 0:
            print("❌ High severity security issues found")
            all_passed = False
        elif medium_issues > 5:  # Allow some medium issues in development scripts
            print("⚠️  Many medium severity issues found")
        else:
            print("✅ Security scan results acceptable")
    else:
        all_passed = False

    # Final result
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All security configuration validations passed!")
        return 0
    else:
        print("❌ Some security configuration validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
