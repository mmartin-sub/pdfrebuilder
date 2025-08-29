#!/usr/bin/env python3
"""
JSON Compliance Fixer for Documentation

This tool identifies and fixes JSON compliance issues in documentation files.
It can:
- Find invalid JSON in code blocks
- Suggest fixes for common JSON issues
- Auto-fix simple problems like missing quotes
- Report detailed issues for manual fixing
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


class JSONComplianceFixer:
    """Tool to fix JSON compliance issues in documentation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / "docs"

    def find_json_issues(self) -> list[dict[str, Any]]:
        """Find all JSON compliance issues in documentation."""
        issues = []

        if not self.docs_dir.exists():
            print(f"Documentation directory not found: {self.docs_dir}")
            return issues

        md_files = list(self.docs_dir.rglob("*.md"))

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                file_issues = self._check_file_json(md_file, content)
                issues.extend(file_issues)
            except Exception as e:
                print(f"Error processing {md_file}: {e}")

        return issues

    def _check_file_json(self, file_path: Path, content: str) -> list[dict[str, Any]]:
        """Check JSON compliance in a single file."""
        issues = []

        # Find JSON code blocks - only look for explicitly marked JSON blocks
        json_patterns = [
            r"```(?:json|json5)\n(.*?)\n```",
        ]

        for pattern in json_patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                json_content = match.group(1).strip()
                if not json_content:
                    continue

                line_number = content[: match.start()].count("\n") + 1

                # Try to parse as JSON
                try:
                    json.loads(json_content)
                    # Valid JSON, no issue
                    continue
                except json.JSONDecodeError as e:
                    # Invalid JSON, analyze the issue
                    issue = self._analyze_json_issue(json_content, str(e), file_path, line_number)
                    issues.append(issue)

        return issues

    def _analyze_json_issue(
        self, json_content: str, error_msg: str, file_path: Path, line_number: int
    ) -> dict[str, Any]:
        """Analyze a JSON issue and suggest fixes."""
        issue = {
            "file": str(file_path.relative_to(self.docs_dir)),
            "line": line_number,
            "error": error_msg,
            "content": json_content,
            "suggested_fix": None,
            "auto_fixable": False,
        }

        # Common JSON issues and their fixes
        if "Expecting property name enclosed in double quotes" in error_msg:
            # Unquoted property names
            fix = self._fix_unquoted_properties(json_content)
            if fix:
                issue["suggested_fix"] = fix
                issue["auto_fixable"] = True

        elif "Expecting value: line 1 column 1" in error_msg:
            # Empty or invalid content
            issue["suggested_fix"] = "Add valid JSON content"
            issue["auto_fixable"] = False

        elif "Expecting ',' delimiter" in error_msg:
            # Missing commas
            fix = self._fix_missing_commas(json_content)
            if fix:
                issue["suggested_fix"] = fix
                issue["auto_fixable"] = True

        elif "Expecting value" in error_msg:
            # Missing values
            issue["suggested_fix"] = "Add missing values to JSON object"
            issue["auto_fixable"] = False

        return issue

    def _fix_unquoted_properties(self, json_content: str) -> str | None:
        """Fix unquoted property names in JSON."""
        # Pattern to match unquoted property names
        pattern = r"(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):"

        def replace_property(match):
            indent = match.group(1)
            prop_name = match.group(2)
            spacing = match.group(3)
            return f'{indent}"{prop_name}"{spacing}:'

        fixed = re.sub(pattern, replace_property, json_content)

        # Test if the fix works
        try:
            json.loads(fixed)
            return fixed
        except json.JSONDecodeError:
            return None

    def _fix_missing_commas(self, json_content: str) -> str | None:
        """Fix missing commas in JSON."""
        # Pattern to match object properties without trailing commas
        pattern = r'(\s*"[^"]+"\s*:\s*[^,}\]]+)(\s*)([}\]])'

        def add_comma(match):
            prop = match.group(1)
            spacing = match.group(2)
            closing = match.group(3)
            return f"{prop},{spacing}{closing}"

        fixed = re.sub(pattern, add_comma, json_content)

        # Test if the fix works
        try:
            json.loads(fixed)
            return fixed
        except json.JSONDecodeError:
            return None

    def auto_fix_issues(self, issues: list[dict[str, Any]]) -> int:
        """Automatically fix JSON issues that can be fixed."""
        fixed_count = 0

        for issue in issues:
            if not issue["auto_fixable"] or not issue["suggested_fix"]:
                continue

            file_path = self.docs_dir / issue["file"]
            try:
                content = file_path.read_text(encoding="utf-8")

                # Find the problematic JSON block and replace it
                json_patterns = [
                    r"```(?:json|json5)\n(.*?)\n```",
                    r"```\n(.*?)\n```",
                ]

                for pattern in json_patterns:
                    matches = list(re.finditer(pattern, content, re.DOTALL))
                    for match in matches:
                        json_content = match.group(1).strip()
                        if json_content == issue["content"]:
                            # Replace with fixed content
                            new_block = f"```json\n{issue['suggested_fix']}\n```"
                            content = content[: match.start()] + new_block + content[match.end() :]

                            # Write back to file
                            file_path.write_text(content, encoding="utf-8")
                            fixed_count += 1
                            print(f"Fixed JSON in {issue['file']}:{issue['line']}")
                            break

            except Exception as e:
                print(f"Error fixing {issue['file']}: {e}")

        return fixed_count

    def report_issues(self, issues: list[dict[str, Any]]):
        """Generate a detailed report of JSON issues."""
        if not issues:
            print("✅ No JSON compliance issues found!")
            return

        print(f"\n❌ Found {len(issues)} JSON compliance issues:")
        print("=" * 60)

        auto_fixable = [i for i in issues if i["auto_fixable"]]
        manual_fixable = [i for i in issues if not i["auto_fixable"]]

        if auto_fixable:
            print(f"\n🔧 Auto-fixable issues ({len(auto_fixable)}):")
            for issue in auto_fixable[:5]:  # Show first 5
                print(f"  {issue['file']}:{issue['line']} - {issue['error']}")
                if issue["suggested_fix"]:
                    print(f"    Suggested fix: {issue['suggested_fix'][:100]}...")

        if manual_fixable:
            print(f"\n📝 Manual fixes needed ({len(manual_fixable)}):")
            for issue in manual_fixable[:5]:  # Show first 5
                print(f"  {issue['file']}:{issue['line']} - {issue['error']}")
                print(f"    Content: {issue['content'][:100]}...")

        if len(issues) > 10:
            print(f"\n... and {len(issues) - 10} more issues")


def main():
    """Main function to run the JSON compliance fixer."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/fix_json_examples.py <project_root>")
        sys.exit(1)

    project_root = Path(sys.argv[1])
    if not project_root.exists():
        print(f"Project root not found: {project_root}")
        sys.exit(1)

    fixer = JSONComplianceFixer(project_root)

    print("🔍 Scanning for JSON compliance issues...")
    issues = fixer.find_json_issues()

    fixer.report_issues(issues)

    if issues:
        auto_fixable = [i for i in issues if i["auto_fixable"]]
        if auto_fixable:
            print(f"\n🔧 Attempting to auto-fix {len(auto_fixable)} issues...")
            fixed_count = fixer.auto_fix_issues(issues)
            print(f"✅ Auto-fixed {fixed_count} issues")

            # Re-check after fixes
            print("\n🔍 Re-checking after fixes...")
            remaining_issues = fixer.find_json_issues()
            if remaining_issues:
                print(f"⚠️  {len(remaining_issues)} issues remain (manual fixes needed)")
            else:
                print("✅ All JSON issues resolved!")

    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
