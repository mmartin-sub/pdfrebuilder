#!/usr/bin/env python3
"""
Documentation monitoring script.
Runs automated checks on documentation health.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from security.subprocess_compatibility import run
except ImportError:
    # Fallback for development script when secure modules unavailable
    import subprocess  # nosec B404 # Fallback for development script when secure modules unavailable

    run = subprocess.run


def main():
    """Run documentation health checks."""
    print(f"🔍 Documentation Health Check - {datetime.now()}")
    print("=" * 50)

    issues = []

    # Check links
    print("📋 Checking links...")
    result = run(
        ["hatch", "run", "python", "scripts/validate_links.py"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        issues.append("Broken links detected")
        print("❌ Link validation failed")
    else:
        print("✅ All links valid")

    # Test examples
    print("📋 Testing examples...")
    result = run(
        ["hatch", "run", "python", "examples/comprehensive_example.py"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        issues.append("Example execution failed")
        print("❌ Example test failed")
    else:
        print("✅ Examples working")

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy" if not issues else "issues_detected",
        "issues": issues,
        "checks_performed": ["link_validation", "example_testing"],
    }

    report_file = Path(".kiro/monitoring/last_check.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Health check complete: {len(issues)} issues found")
    if issues:
        for issue in issues:
            print(f"  ❌ {issue}")
        sys.exit(1)
    else:
        print("  ✅ Documentation is healthy")
        sys.exit(0)


if __name__ == "__main__":
    main()
