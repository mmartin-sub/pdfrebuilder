#!/usr/bin/env python3
"""
Link validation script for documentation.
Validates internal links and cross-references in markdown files.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def find_markdown_files(docs_dir: Path) -> list[Path]:
    """Find all markdown files in the documentation directory."""
    markdown_files = []
    for root, _dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(Path(root) / file)
    return markdown_files


def extract_links(file_path: Path) -> list[tuple[str, int]]:
    """Extract all markdown links from a file."""
    links = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Find markdown links [text](url)
        link_pattern = r"\[([^\]]*)\]\(([^)]+)\)"
        for line_num, line in enumerate(content.split("\n"), 1):
            matches = re.finditer(link_pattern, line)
            for match in matches:
                link_url = match.group(2)
                links.append((link_url, line_num))

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return links


def is_internal_link(url: str) -> bool:
    """Check if a URL is an internal link."""
    parsed = urlparse(url)
    # Internal links have no scheme or are relative
    return not parsed.scheme or parsed.scheme in ["", "file"]


def resolve_link_path(base_file: Path, link_url: str, docs_root: Path) -> Path:
    """Resolve a relative link to an absolute path."""
    # Remove anchor fragments
    clean_url = link_url.split("#")[0]

    if not clean_url:  # Just an anchor
        return base_file

    # Handle relative paths
    if clean_url.startswith("./"):
        clean_url = clean_url[2:]
    elif clean_url.startswith("../"):
        # Resolve relative to base file directory
        base_dir = base_file.parent
        while clean_url.startswith("../"):
            clean_url = clean_url[3:]
            base_dir = base_dir.parent
        return base_dir / clean_url
    elif clean_url.startswith("/"):
        # Absolute path from docs root
        return docs_root / clean_url[1:]
    else:
        # Relative to current file directory
        return base_file.parent / clean_url


def validate_links(docs_dir: Path) -> dict[str, list[str]]:
    """Validate all internal links in documentation."""
    results = {"valid": [], "invalid": [], "warnings": []}

    markdown_files = find_markdown_files(docs_dir)
    print(f"Found {len(markdown_files)} markdown files to validate")

    for file_path in markdown_files:
        print(f"Validating links in: {file_path.relative_to(docs_dir)}")
        links = extract_links(file_path)

        for link_url, line_num in links:
            if not is_internal_link(link_url):
                # Skip external links
                continue

            try:
                resolved_path = resolve_link_path(file_path, link_url, docs_dir)

                if resolved_path.exists():
                    results["valid"].append(f"✅ {file_path.relative_to(docs_dir)}:{line_num} -> {link_url}")
                else:
                    results["invalid"].append(
                        f"❌ {file_path.relative_to(docs_dir)}:{line_num} -> {link_url} (target not found: {resolved_path})"
                    )

            except Exception as e:
                results["warnings"].append(
                    f"⚠️  {file_path.relative_to(docs_dir)}:{line_num} -> {link_url} (error: {e})"
                )

    return results


def main():
    """Main validation function."""
    docs_dir = Path(__file__).parent.parent / "docs"

    if not docs_dir.exists():
        print(f"Documentation directory not found: {docs_dir}")
        sys.exit(1)

    print("🔗 Validating documentation links...")
    print("=" * 50)

    results = validate_links(docs_dir)

    print("\n📊 LINK VALIDATION RESULTS")
    print("=" * 50)

    if results["valid"]:
        print(f"\n✅ Valid Links ({len(results['valid'])}):")
        for link in results["valid"][:10]:  # Show first 10
            print(f"  {link}")
        if len(results["valid"]) > 10:
            print(f"  ... and {len(results['valid']) - 10} more")

    if results["invalid"]:
        print(f"\n❌ Invalid Links ({len(results['invalid'])}):")
        for link in results["invalid"]:
            print(f"  {link}")

    if results["warnings"]:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"  {warning}")

    print("\n📋 Summary:")
    print(f"  ✅ Valid: {len(results['valid'])}")
    print(f"  ❌ Invalid: {len(results['invalid'])}")
    print(f"  ⚠️  Warnings: {len(results['warnings'])}")

    if results["invalid"]:
        print("\n❌ Link validation failed!")
        sys.exit(1)
    else:
        print("\n✅ All internal links are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
