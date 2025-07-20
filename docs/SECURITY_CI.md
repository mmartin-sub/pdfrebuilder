# Security Testing in CI/CD

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

- Review bandit documentation: <https://bandit.readthedocs.io/>
- Check security validation scripts in `scripts/`
- Review existing security implementations in `src/security/`

## Security Review Schedule

- **Weekly**: Automated scans via CI/CD
- **Monthly**: Review security reports and trends
- **Quarterly**: Update security dependencies
- **Semi-annually**: Full security suppression review
