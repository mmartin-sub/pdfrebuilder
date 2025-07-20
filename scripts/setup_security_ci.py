#!/usr/bin/env python3
"""
Setup script for automated security testing in CI/CD pipeline.

This script configures automated security testing integration for continuous
integration and deployment pipelines.
"""

import sys
from pathlib import Path

import yaml


def create_github_security_workflow():
    """Create GitHub Actions workflow for security testing."""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)

    security_workflow = {
        "name": "Security Testing",
        "on": {
            "push": {"branches": ["main", "develop"]},
            "pull_request": {"branches": ["main", "develop"]},
            "schedule": [{"cron": "0 2 * * 1"}],  # Weekly on Monday at 2 AM
        },
        "jobs": {
            "security-scan": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"name": "Checkout code", "uses": "actions/checkout@v4"},
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.12"},
                    },
                    {"name": "Install dependencies", "run": "pip install hatch bandit"},
                    {
                        "name": "Run bandit security scan",
                        "run": "hatch run security-scan",
                    },
                    {
                        "name": "Run security validation tests",
                        "run": "hatch run security-test",
                    },
                    {
                        "name": "Validate bandit configuration",
                        "run": "hatch run security-config-validate",
                    },
                    {
                        "name": "Generate security report",
                        "run": "hatch run security-scan-json",
                    },
                    {
                        "name": "Upload security report",
                        "uses": "actions/upload-artifact@v3",
                        "if": "always()",
                        "with": {
                            "name": "security-report",
                            "path": "reports/bandit_results.json",
                        },
                    },
                ],
            }
        },
    }

    workflow_file = workflow_dir / "security.yml"
    with open(workflow_file, "w") as f:
        yaml.dump(security_workflow, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created GitHub Actions security workflow: {workflow_file}")
    return workflow_file


def create_pre_commit_security_hook():
    """Create pre-commit hook for security testing."""
    pre_commit_config = Path(".pre-commit-config.yaml")

    if pre_commit_config.exists():
        print("⚠️  Pre-commit config already exists, adding security hooks...")
        with open(pre_commit_config) as f:
            config = yaml.safe_load(f)
    else:
        config = {"repos": []}

    # Add bandit security hook
    bandit_hook = {
        "repo": "https://github.com/PyCQA/bandit",
        "rev": "1.7.5",
        "hooks": [
            {
                "id": "bandit",
                "args": ["-r", "src/", "scripts/", "--severity-level", "medium"],
                "exclude": "tests/",
            }
        ],
    }

    # Check if bandit hook already exists
    bandit_exists = any(repo.get("repo") == "https://github.com/PyCQA/bandit" for repo in config["repos"])

    if not bandit_exists:
        config["repos"].append(bandit_hook)

        with open(pre_commit_config, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print("✅ Added bandit security hook to pre-commit config")
    else:
        print("ℹ️  Bandit hook already exists in pre-commit config")

    return pre_commit_config


def create_security_makefile_targets():
    """Add security testing targets to Makefile."""
    makefile = Path("Makefile")

    security_targets = """
# Security testing targets
.PHONY: security-scan security-test security-validate security-all

security-scan:
	@echo "Running bandit security scan..."
	hatch run security-scan

security-test:
	@echo "Running security validation tests..."
	hatch run security-test

security-validate:
	@echo "Validating security configuration..."
	hatch run security-config-validate

security-all: security-scan security-test security-validate
	@echo "All security checks completed"

security-report:
	@echo "Generating security report..."
	mkdir -p reports
	hatch run security-scan-json
	@echo "Security report generated: reports/bandit_results.json"
"""

    if makefile.exists():
        content = makefile.read_text()
        if "security-scan:" not in content:
            with open(makefile, "a") as f:
                f.write(security_targets)
            print("✅ Added security targets to Makefile")
        else:
            print("ℹ️  Security targets already exist in Makefile")
    else:
        with open(makefile, "w") as f:
            f.write("# Makefile for PDF/PSD processing tool\n")
            f.write(security_targets)
        print("✅ Created Makefile with security targets")

    return makefile


def create_security_documentation():
    """Create or update security testing documentation."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    security_ci_doc = docs_dir / "SECURITY_CI.md"

    documentation = """# Security Testing in CI/CD

This document describes the automated security testing setup for the PDF/PSD processing tool.

## Overview

Security testing is integrated into the CI/CD pipeline to ensure that:
- No new security vulnerabilities are introduced
- Bandit configuration remains effective
- Security suppressions are properly justified
- Security documentation stays up-to-date

## Automated Security Checks

### GitHub Actions Workflow

The security workflow (`.github/workflows/security.yml`) runs:
- On every push to main/develop branches
- On every pull request
- Weekly on schedule (Mondays at 2 AM)

### Security Tests Include

1. **Bandit Security Scan**
   - Scans source code for security issues
   - Uses medium severity and confidence levels
   - Excludes test directories

2. **Security Validation Tests**
   - Tests bandit configuration effectiveness
   - Validates suppression accuracy
   - Checks security rule coverage

3. **Configuration Validation**
   - Ensures bandit configuration is complete
   - Validates security command availability
   - Checks documentation completeness

## Local Security Testing

### Commands Available

```bash
# Run bandit security scan
make security-scan
# or
hatch run security-scan

# Run security validation tests
make security-test
# or
hatch run security-test

# Validate bandit configuration
make security-validate
# or
hatch run security-config-validate

# Run all security checks
make security-all

# Generate security report
make security-report
```

### Pre-commit Hooks

Security checks are integrated with pre-commit hooks:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Security Reports

Security reports are generated in JSON format and stored in `reports/bandit_results.json`.

In CI/CD, reports are uploaded as artifacts for review.

## Suppression Management

All security suppressions must be:
1. Documented in `docs/BANDIT_SUPPRESSIONS.md`
2. Justified with security rationale
3. Reviewed regularly (every 6 months)

## Troubleshooting

### Common Issues

1. **Bandit scan fails**: Check that bandit is installed and configuration is valid
2. **Too many false positives**: Review and update suppressions in `pyproject.toml`
3. **Missing documentation**: Update `docs/BANDIT_SUPPRESSIONS.md`

### Getting Help

- Review bandit documentation: https://bandit.readthedocs.io/
- Check security validation scripts in `scripts/`
- Review existing security implementations in `src/security/`

## Security Review Schedule

- **Weekly**: Automated scans via CI/CD
- **Monthly**: Review security reports and trends
- **Quarterly**: Update security dependencies
- **Semi-annually**: Full security suppression review
"""

    with open(security_ci_doc, "w") as f:
        f.write(documentation)

    print(f"✅ Created security CI documentation: {security_ci_doc}")
    return security_ci_doc


def validate_setup():
    """Validate that security CI setup is complete."""
    print("\n🔍 Validating security CI setup...")

    required_files = [
        ".github/workflows/security.yml",
        ".pre-commit-config.yaml",
        "Makefile",
        "docs/SECURITY_CI.md",
        "pyproject.toml",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    # Check that pyproject.toml has security commands
    pyproject_content = Path("pyproject.toml").read_text()
    security_commands = ["security-scan", "security-test", "security-validate"]

    missing_commands = []
    for command in security_commands:
        if command not in pyproject_content:
            missing_commands.append(command)

    if missing_commands:
        print(f"❌ Missing security commands in pyproject.toml: {missing_commands}")
        return False

    print("✅ Security CI setup validation passed")
    return True


def main():
    """Main setup function."""
    print("🔒 Setting up automated security testing for CI/CD")
    print("=" * 60)

    try:
        # Create GitHub Actions workflow
        create_github_security_workflow()

        # Create pre-commit hooks
        create_pre_commit_security_hook()

        # Add Makefile targets
        create_security_makefile_targets()

        # Create documentation
        create_security_documentation()

        # Validate setup
        if validate_setup():
            print("\n✅ Security CI/CD setup completed successfully!")
            print("\nNext steps:")
            print("1. Commit the new files to your repository")
            print("2. Install pre-commit hooks: pre-commit install")
            print("3. Test security commands: make security-all")
            print("4. Review and customize the GitHub Actions workflow")
            return 0
        else:
            print("\n❌ Security CI/CD setup validation failed")
            return 1

    except Exception as e:
        print(f"\n❌ Error setting up security CI/CD: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
