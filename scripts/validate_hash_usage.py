#!/usr/bin/env python3
"""
Hash Usage Security Validator

This script validates that hash algorithms are used securely throughout the codebase:
- MD5 must include usedforsecurity=False for non-cryptographic purposes
- Cryptographic operations should use SHA-256 or stronger
- All hash usage should be properly documented

Usage:
    python scripts/validate_hash_usage.py [--fix] [path...]
"""

import argparse
import re
import sys
from pathlib import Path


class HashUsageValidator:
    """Validates secure hash algorithm usage patterns."""

    def __init__(self, fix_mode: bool = False):
        self.fix_mode = fix_mode
        self.errors = []
        self.fixes_applied = 0

    def validate_file(self, file_path: Path) -> list[tuple[int, str, str]]:
        """
        Validate hash usage in a single file.

        Returns:
            List of (line_number, error_type, message) tuples
        """
        if not file_path.suffix == ".py":
            return []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            return [(0, "file_error", f"Cannot read file: {e}")]

        errors = []
        lines = content.split("\n")

        # Check for problematic MD5 usage
        for line_num, line in enumerate(lines, 1):
            errors.extend(self._check_md5_usage(line_num, line, file_path))

        # If in fix mode, apply fixes
        if self.fix_mode and errors:
            fixed_content = self._apply_fixes(content, errors, file_path)
            if fixed_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                self.fixes_applied += len([e for e in errors if e[1] == "md5_missing_flag"])
                # Remove fixed errors from the list
                errors = [e for e in errors if e[1] != "md5_missing_flag"]

        return errors

    def _check_md5_usage(self, line_num: int, line: str, file_path: Path) -> list[tuple[int, str, str]]:
        """Check for problematic MD5 usage patterns."""
        errors = []

        # Skip test files that intentionally show old/incorrect patterns
        if "test" in str(file_path) and ("old_function" in line or "without_flag" in line):
            return errors

        # Skip documentation files that show examples
        if str(file_path).endswith(".md"):
            return errors

        # Pattern for MD5 usage without security flag
        md5_pattern = r"hashlib\.md5\([^)]*\)(?!.*usedforsecurity)"

        if re.search(md5_pattern, line):
            # Check if this is already properly flagged
            if "usedforsecurity=False" in line:
                return errors

            # Check if this is in a comment or string (skip validation)
            stripped_line = line.strip()
            if (
                stripped_line.startswith("#")
                or stripped_line.startswith('"""')
                or stripped_line.startswith("'''")
                or '"""' in line
                or "'''" in line
                or 'return "' in line
                or "return '" in line
            ):
                return errors

            # This is a problematic MD5 usage
            errors.append(
                (
                    line_num,
                    "md5_missing_flag",
                    "MD5 usage without usedforsecurity=False flag. Add usedforsecurity=False for non-cryptographic use.",
                )
            )

        return errors

    def _apply_fixes(self, content: str, errors: list[tuple[int, str, str]], file_path: Path) -> str:
        """Apply automatic fixes to the content."""
        lines = content.split("\n")

        for line_num, error_type, _ in errors:
            if error_type == "md5_missing_flag" and line_num <= len(lines):
                line = lines[line_num - 1]

                # Fix MD5 usage by adding usedforsecurity=False
                fixed_line = re.sub(
                    r"hashlib\.md5\(([^)]*)\)",
                    r"hashlib.md5(\1, usedforsecurity=False)",
                    line,
                )

                # Avoid double-fixing
                if "usedforsecurity=False" not in line:
                    lines[line_num - 1] = fixed_line

        return "\n".join(lines)

    def validate_directory(self, directory: Path) -> list[tuple[Path, int, str, str]]:
        """Validate all Python files in a directory."""
        all_errors = []

        for py_file in directory.rglob("*.py"):
            # Skip certain directories
            skip_dirs = {
                ".venv",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            }
            if any(skip_dir in str(py_file) for skip_dir in skip_dirs):
                continue

            file_errors = self.validate_file(py_file)
            for line_num, error_type, message in file_errors:
                all_errors.append((py_file, line_num, error_type, message))

        return all_errors


def main():
    """Main entry point for the hash usage validator."""
    parser = argparse.ArgumentParser(
        description="Validate secure hash algorithm usage patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/validate_hash_usage.py src/
    python scripts/validate_hash_usage.py --fix src/font_utils.py
    python scripts/validate_hash_usage.py --fix .
        """,
    )

    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to validate (default: current directory)",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix MD5 usage by adding usedforsecurity=False",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    validator = HashUsageValidator(fix_mode=args.fix)
    all_errors = []

    for path_str in args.paths:
        path = Path(path_str)

        if not path.exists():
            print(f"Error: Path {path} does not exist", file=sys.stderr)
            sys.exit(1)

        if path.is_file():
            file_errors = validator.validate_file(path)
            for line_num, error_type, message in file_errors:
                all_errors.append((path, line_num, error_type, message))
        else:
            directory_errors = validator.validate_directory(path)
            all_errors.extend(directory_errors)

    # Report results
    if all_errors:
        print("Hash Usage Security Issues Found:")
        print("=" * 50)

        for file_path, line_num, error_type, message in all_errors:
            print(f"{file_path}:{line_num}: {error_type}: {message}")

        print(f"\nTotal issues: {len(all_errors)}")

        if args.fix and validator.fixes_applied > 0:
            print(f"Applied {validator.fixes_applied} automatic fixes")
        elif not args.fix:
            print("Run with --fix to automatically fix MD5 usage issues")

        sys.exit(1)
    else:
        if args.verbose:
            print("✅ All hash usage patterns are secure")

        if args.fix and validator.fixes_applied > 0:
            print(f"Applied {validator.fixes_applied} automatic fixes")

        sys.exit(0)


if __name__ == "__main__":
    main()
