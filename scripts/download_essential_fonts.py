#!/usr/bin/env python3
"""
Essential Font Downloader

This script downloads essential free fonts for the PDF rebuilder system.
It ensures that users have access to high-quality, free fonts that work
well across different languages and use cases.

Usage:
    python scripts/download_essential_fonts.py [--fonts-dir DIRECTORY]
"""

import argparse
import logging
import os
import shutil
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pdfrebuilder.font.googlefonts import download_google_font
from pdfrebuilder.settings import get_config_value

# Essential fonts list - prioritized by importance and coverage
ESSENTIAL_FONTS = [
    # Primary fonts (highest priority)
    {
        "name": "Noto Sans",
        "description": "Google's comprehensive Unicode font family (free Helvetica alternative)",
        "priority": "high",
        "use_cases": [
            "multilingual text",
            "Unicode characters",
            "international documents",
        ],
    },
    {
        "name": "Open Sans",
        "description": "Popular open-source font optimized for readability (free Arial alternative)",
        "priority": "high",
        "use_cases": ["body text", "forms", "technical documents", "web content"],
    },
    {
        "name": "Roboto",
        "description": "Google's modern sans-serif font with excellent readability",
        "priority": "high",
        "use_cases": ["body text", "headings", "UI elements", "modern documents"],
    },
    # Secondary fonts (medium priority)
    {
        "name": "Source Sans Pro",
        "description": "Adobe's open-source sans-serif font with excellent readability",
        "priority": "medium",
        "use_cases": ["technical text", "presentations", "modern documents"],
    },
    {
        "name": "Noto Serif",
        "description": "Google's serif font with Unicode support (free Times alternative)",
        "priority": "medium",
        "use_cases": ["formal documents", "academic papers", "books"],
    },
    {
        "name": "Roboto Mono",
        "description": "Google's monospace font for code and technical content",
        "priority": "medium",
        "use_cases": ["code", "technical documentation", "data tables"],
    },
    # Specialized fonts (lower priority)
    {
        "name": "Noto Sans Mono",
        "description": "Google's monospace font with Unicode support",
        "priority": "low",
        "use_cases": ["code", "terminal output", "fixed-width layouts"],
    },
    {
        "name": "Lato",
        "description": "Humanist sans-serif font with warm character",
        "priority": "low",
        "use_cases": ["friendly documents", "presentations", "marketing materials"],
    },
    {
        "name": "Montserrat",
        "description": "Geometric sans-serif inspired by urban typography",
        "priority": "low",
        "use_cases": ["headings", "titles", "modern designs"],
    },
    {
        "name": "Inter",
        "description": "Font designed specifically for computer screens",
        "priority": "low",
        "use_cases": ["UI elements", "digital interfaces", "screen reading"],
    },
]


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(__name__)


def download_font_with_retry(font_name: str, fonts_dir: str, max_retries: int = 3) -> bool:
    """
    Download a font with retry logic

    Args:
        font_name: Name of the font to download
        fonts_dir: Directory to download fonts to
        max_retries: Maximum number of retry attempts

    Returns:
        True if download succeeded, False otherwise
    """
    logger = logging.getLogger(__name__)

    for attempt in range(max_retries):
        try:
            logger.info(f"Downloading '{font_name}' (attempt {attempt + 1}/{max_retries})")
            result = download_google_font(font_name, fonts_dir)

            if result:
                # Create deterministic family filename so engines can find it via "<font_name>.ttf/.otf"
                try:
                    created = _ensure_family_alias_file(font_name, fonts_dir, result)
                    if created:
                        logger.info(f"✓ Successfully downloaded '{font_name}' → {created}")
                    else:
                        logger.info(f"✓ Successfully downloaded '{font_name}'")
                except Exception as alias_err:
                    logger.warning(f"Created downloads for '{font_name}' but failed to create alias file: {alias_err}")
                return True
            else:
                logger.warning(f"✗ Download failed for '{font_name}' (attempt {attempt + 1})")

        except Exception as e:
            logger.warning(f"✗ Error downloading '{font_name}' (attempt {attempt + 1}): {e}")

        if attempt < max_retries - 1:
            logger.info(f"Retrying '{font_name}' in 2 seconds...")
            import time

            time.sleep(2)

    logger.error(f"✗ Failed to download '{font_name}' after {max_retries} attempts")
    return False


def check_existing_fonts(fonts_dir: str) -> set[str]:
    """
    Check which fonts are already available in the fonts directory

    Args:
        fonts_dir: Directory to check for existing fonts

    Returns:
        Set of font names that already exist
    """
    logger = logging.getLogger(__name__)
    existing_fonts = set()

    if not os.path.exists(fonts_dir):
        return existing_fonts

    for font_info in ESSENTIAL_FONTS:
        font_name = font_info["name"]
        # Check for common font file patterns (both ttf and otf)
        base_variants = [
            f"{font_name}",
            f"{font_name.replace(' ', '')}",
            f"{font_name.replace(' ', '-')}",
            f"{font_name.replace(' ', '_')}",
        ]
        font_patterns = [f"{b}.ttf" for b in base_variants] + [f"{b}.otf" for b in base_variants]

        for pattern in font_patterns:
            font_path = os.path.join(fonts_dir, pattern)
            if os.path.exists(font_path):
                existing_fonts.add(font_name)
                logger.debug(f"Found existing font: {font_name} at {font_path}")
                break

    return existing_fonts


def _ensure_family_alias_file(font_name: str, fonts_dir: str, downloaded_files: list[str]) -> str | None:
    """
    Ensure a deterministic alias file exists for the font family, e.g. "Roboto.ttf".

    Heuristic:
    - Prefer a .ttf file if available; otherwise use .otf.
    - Among candidates, pick the first one returned by Google Fonts API.
    - Create or overwrite the alias file only if missing; do not overwrite an existing family file.

    Returns the created alias path or None if skipped.
    """
    # Choose candidate file
    ttf_candidates = [p for p in downloaded_files if p.lower().endswith(".ttf")]
    otf_candidates = [p for p in downloaded_files if p.lower().endswith(".otf")]
    chosen_src = ttf_candidates[0] if ttf_candidates else (otf_candidates[0] if otf_candidates else None)
    if not chosen_src:
        return None

    ext = os.path.splitext(chosen_src)[1].lower()
    # Prepare a small set of alias variants to maximize pickup by engines
    variants = [
        f"{font_name}{ext}",
        f"{font_name.replace(' ', '')}{ext}",
        f"{font_name.replace(' ', '-')}{ext}",
        f"{font_name.replace(' ', '_')}{ext}",
    ]

    created_any = None
    for fname in variants:
        alias_path = os.path.join(fonts_dir, fname)
        if os.path.exists(alias_path):
            continue
        shutil.copyfile(chosen_src, alias_path)
        if created_any is None:
            created_any = alias_path

    return created_any


def download_essential_fonts(
    fonts_dir: str | None = None,
    priority_filter: str | None = None,
    force_redownload: bool = False,
    verbose: bool = False,
) -> dict[str, bool]:
    """
    Download essential fonts for the PDF rebuilder system

    Args:
        fonts_dir: Directory to download fonts to (uses config default if None)
        priority_filter: Filter by priority level ('high', 'medium', 'low', or None for all)
        force_redownload: Whether to redownload existing fonts
        verbose: Whether to enable verbose logging

    Returns:
        Dictionary mapping font names to download success status
    """
    logger = setup_logging(verbose)

    # Use configured fonts directory if not specified
    if fonts_dir is None:
        fonts_dir = get_config_value("downloaded_fonts_dir")

    # Ensure fonts directory exists
    os.makedirs(fonts_dir, exist_ok=True)

    logger.info(f"Downloading essential fonts to: {fonts_dir}")

    # Check existing fonts unless force redownload
    existing_fonts = set() if force_redownload else check_existing_fonts(fonts_dir)

    if existing_fonts and not force_redownload:
        logger.info(f"Found {len(existing_fonts)} existing fonts: {', '.join(sorted(existing_fonts))}")

    # Filter fonts by priority if specified
    fonts_to_download = ESSENTIAL_FONTS
    if priority_filter:
        fonts_to_download = [f for f in ESSENTIAL_FONTS if f["priority"] == priority_filter]
        logger.info(f"Filtering to {priority_filter} priority fonts ({len(fonts_to_download)} fonts)")

    # Download fonts
    results = {}
    successful_downloads = 0
    skipped_fonts = 0

    for font_info in fonts_to_download:
        font_name = font_info["name"]

        if font_name in existing_fonts and not force_redownload:
            logger.info(f"⏭ Skipping '{font_name}' (already exists)")
            results[font_name] = True
            skipped_fonts += 1
            continue

        logger.info(f"📥 {font_info['description']}")
        success = download_font_with_retry(font_name, fonts_dir)
        results[font_name] = success

        if success:
            successful_downloads += 1

    # Summary
    total_fonts = len(fonts_to_download)
    failed_downloads = total_fonts - successful_downloads - skipped_fonts

    logger.info("\n" + "=" * 60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total fonts processed: {total_fonts}")
    logger.info(f"Successfully downloaded: {successful_downloads}")
    logger.info(f"Already existed (skipped): {skipped_fonts}")
    logger.info(f"Failed downloads: {failed_downloads}")

    if failed_downloads > 0:
        failed_fonts = [name for name, success in results.items() if not success]
        logger.warning(f"Failed to download: {', '.join(failed_fonts)}")

    logger.info(f"Fonts directory: {fonts_dir}")

    return results


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Download essential fonts for PDF rebuilder system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all essential fonts
  python scripts/download_essential_fonts.py

  # Download only high priority fonts
  python scripts/download_essential_fonts.py --priority high

  # Download to custom directory
  python scripts/download_essential_fonts.py --fonts-dir ./my-fonts

  # Force redownload all fonts
  python scripts/download_essential_fonts.py --force

  # Verbose output
  python scripts/download_essential_fonts.py --verbose

Priority Levels:
  high   - Essential fonts for basic functionality (Nimbus Sans, Liberation Sans, Noto Sans)
  medium - Important fonts for common use cases (DejaVu Sans, Liberation Serif/Mono)
  low    - Specialized fonts for specific needs (Source Sans Pro, Open Sans, etc.)
        """,
    )

    parser.add_argument(
        "--fonts-dir",
        help="Directory to download fonts to (default: from configuration)",
    )

    parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        help="Download only fonts of specified priority level",
    )

    parser.add_argument("--force", action="store_true", help="Force redownload of existing fonts")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--list", action="store_true", help="List available fonts and exit")

    args = parser.parse_args()

    if args.list:
        print("Available Essential Fonts:")
        print("=" * 50)
        for priority in ["high", "medium", "low"]:
            fonts = [f for f in ESSENTIAL_FONTS if f["priority"] == priority]
            print(f"\n{priority.upper()} PRIORITY ({len(fonts)} fonts):")
            for font in fonts:
                print(f"  • {font['name']}")
                print(f"    {font['description']}")
                print(f"    Use cases: {', '.join(font['use_cases'])}")
        return

    try:
        results = download_essential_fonts(
            fonts_dir=args.fonts_dir,
            priority_filter=args.priority,
            force_redownload=args.force,
            verbose=args.verbose,
        )

        # Exit with error code if any downloads failed
        failed_count = sum(1 for success in results.values() if not success)
        if failed_count > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
