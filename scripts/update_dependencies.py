#!/usr/bin/env python3
"""
Dependency Update Script

This script helps check for and update dependencies to their latest versions
while respecting version constraints defined in pyproject.toml.

Usage:
    python scripts/update_dependencies.py [--check-only] [--update]
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for secure execution imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import CalledProcessError from subprocess for exception handling
from subprocess import CalledProcessError  # nosec B404 # Required for exception handling only

# Import secure subprocess alternatives
from pdfrebuilder.security.subprocess_compatibility import run


def get_outdated_packages():
    """Get list of outdated packages"""
    try:
        result = run(
            ["hatch", "run", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,  # Add timeout for security
        )
        return json.loads(result.stdout)
    except CalledProcessError as e:
        print(f"Error getting outdated packages: {e}")
        return []


def get_current_packages():
    """Get list of currently installed packages"""
    try:
        result = run(
            ["hatch", "run", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,  # Add timeout for security
        )
        return {pkg["name"].lower(): pkg["version"] for pkg in json.loads(result.stdout)}
    except CalledProcessError as e:
        print(f"Error getting current packages: {e}")
        return {}


def check_security_updates():
    """Check for security updates using pip-audit if available"""
    try:
        result = run(
            ["hatch", "run", "pip-audit", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,  # Add timeout for security
        )
        return json.loads(result.stdout)
    except (CalledProcessError, FileNotFoundError):
        print("pip-audit not available. Install with: hatch run pip install pip-audit")
        return []


def main():
    parser = argparse.ArgumentParser(description="Check and update dependencies")
    parser.add_argument("--check-only", action="store_true", help="Only check for updates")
    parser.add_argument("--update", action="store_true", help="Update packages")
    parser.add_argument("--security", action="store_true", help="Check for security updates")

    args = parser.parse_args()

    print("🔍 Checking for outdated dependencies...")
    outdated = get_outdated_packages()
    get_current_packages()

    if not outdated:
        print("✅ All dependencies are up to date!")
        return 0

    print(f"\n📦 Found {len(outdated)} outdated packages:")
    print("-" * 80)
    print(f"{'Package':<25} {'Current':<15} {'Latest':<15} {'Type':<10}")
    print("-" * 80)

    for pkg in outdated:
        name = pkg["name"]
        current_ver = pkg["version"]
        latest_ver = pkg["latest_version"]
        pkg_type = pkg.get("latest_filetype", "wheel")

        print(f"{name:<25} {current_ver:<15} {latest_ver:<15} {pkg_type:<10}")

    # Check for security updates
    if args.security:
        print("\n🔒 Checking for security updates...")
        security_issues = check_security_updates()
        if security_issues:
            print(f"⚠️  Found {len(security_issues)} security issues!")
            for issue in security_issues:
                print(f"  - {issue.get('package', 'Unknown')}: {issue.get('description', 'No description')}")
        else:
            print("✅ No known security issues found")

    if args.check_only:
        return 0

    if args.update:
        print("\n🚀 Updating packages...")
        for pkg in outdated:
            name = pkg["name"]
            print(f"Updating {name}...")
            try:
                run(
                    ["hatch", "run", "pip", "install", "--upgrade", name],
                    check=True,
                    timeout=300,  # Add timeout for security
                )
                print(f"✅ Updated {name}")
            except CalledProcessError as e:
                print(f"❌ Failed to update {name}: {e}")

    else:
        print("\n💡 To update packages, run:")
        print("  python scripts/update_dependencies.py --update")
        print("\n💡 To update specific packages:")
        for pkg in outdated[:5]:  # Show first 5
            print(f"  hatch run pip install --upgrade {pkg['name']}")
        if len(outdated) > 5:
            print(f"  ... and {len(outdated) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
