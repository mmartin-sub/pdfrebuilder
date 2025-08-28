# Security

This document outlines the security considerations for the `pdfrebuilder` project.

## Secure Coding Practices

The `pdfrebuilder` project follows secure coding practices to prevent common vulnerabilities. This includes:

- **Input Validation**: All input is validated to prevent injection attacks.
- **Dependency Management**: Dependencies are regularly scanned for vulnerabilities.
- **Secure XML Parsing**: The `defusedxml` library is used to prevent XML-related attacks.
- **Path Traversal**: The `is_safe_path` utility is used to prevent path traversal attacks.
- **Subprocess Execution**: The `SecureExecutor` class is used to safely execute external commands.

## Vulnerability Reporting

If you discover a security vulnerability, please report it to us privately. Do not disclose the vulnerability publicly until we have had a chance to address it.

## Dependency Security

The project uses `safety` and `bandit` to scan for known security vulnerabilities in the dependencies. These checks are run as part of the CI/CD pipeline.
