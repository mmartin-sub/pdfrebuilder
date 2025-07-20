"""
Schema migration utilities for Universal IDM

This module provides utilities for migrating between different versions of the Universal IDM schema.
"""

import json
import logging
from typing import Any

from .universal_idm import UNIVERSAL_IDM_VERSION

logger = logging.getLogger(__name__)


class SchemaMigrationError(Exception):
    """Raised when schema migration fails"""


def get_schema_version(data: dict[str, Any]) -> str:
    """Get the schema version from a document"""
    return data.get("version", "unknown")


def migrate_v0_to_v1(data: dict[str, Any]) -> dict[str, Any]:
    """
    Migrate from legacy schema (v0) to Universal IDM v1.0

    This handles the migration from the original PDF-only schema to the Universal IDM schema.
    """
    logger.info("Migrating from legacy schema to Universal IDM v1.0")

    # Create a new document with the v1.0 structure
    migrated = {
        "version": "1.0",
        "engine": data.get("engine", "fitz"),
        "engine_version": data.get("engine_version", "unknown"),
        "metadata": {},
        "document_structure": [],
    }

    # Migrate metadata
    if "metadata" in data:
        migrated["metadata"] = data["metadata"]

    # Handle different legacy formats
    if "pages" in data:
        # Legacy format with "pages" key
        for page in data["pages"]:
            migrated_page = {
                "type": "page",
                "page_number": page.get("page_number", 0),
                "size": page.get("size", [0, 0]),
                "background_color": page.get("page_background_color"),
                "layers": [],
            }

            # Create a base layer if not present
            if "layers" not in page or not page["layers"]:
                base_layer = {
                    "layer_id": f"page_{page.get('page_number', 0)}_base_layer",
                    "layer_name": "Page Content",
                    "layer_type": "base",
                    "bbox": [
                        0,
                        0,
                        page.get("size", [0, 0])[0],
                        page.get("size", [0, 0])[1],
                    ],
                    "visibility": True,
                    "opacity": 1.0,
                    "blend_mode": "Normal",
                    "children": [],
                    "content": page.get("content", []),
                }
                migrated_page["layers"].append(base_layer)
            else:
                # Copy existing layers
                migrated_page["layers"] = page["layers"]

            migrated["document_structure"].append(migrated_page)

    elif "document_structure" in data:
        # Already has document_structure, just ensure all fields are present
        migrated["document_structure"] = data["document_structure"]

    return migrated


def migrate_schema(data: dict[str, Any], target_version: str = UNIVERSAL_IDM_VERSION) -> dict[str, Any]:
    """
    Migrate a document schema to the target version

    Args:
        data: Document data to migrate
        target_version: Target schema version

    Returns:
        Migrated document data

    Raises:
        SchemaMigrationError: If migration fails
    """
    current_version = get_schema_version(data)

    if current_version == target_version:
        logger.info(f"Document already at target version {target_version}")
        return data

    logger.info(f"Migrating document from version {current_version} to {target_version}")

    try:
        # Migration path from legacy/unknown to v1.0
        if current_version in ["unknown", "0", "0.1"] and target_version == "1.0":
            return migrate_v0_to_v1(data)

        # Add more migration paths here as needed

        # If we don't have a specific migration path, try to adapt the document
        # by adding missing fields based on the target version
        if target_version == "1.0":
            return adapt_to_v1(data)

        raise SchemaMigrationError(f"No migration path from {current_version} to {target_version}")

    except Exception as e:
        raise SchemaMigrationError(f"Migration failed: {e!s}")


def adapt_to_v1(data: dict[str, Any]) -> dict[str, Any]:
    """
    Adapt a document to v1.0 schema by adding missing fields

    This is a best-effort approach when no specific migration path exists.
    """
    result = data.copy()
    result["version"] = "1.0"

    # Ensure required top-level fields
    if "engine" not in result:
        result["engine"] = "unknown"

    if "engine_version" not in result:
        result["engine_version"] = "unknown"

    if "metadata" not in result:
        result["metadata"] = {}

    if "document_structure" not in result:
        result["document_structure"] = []

    return result


def load_and_migrate(file_path: str, target_version: str = UNIVERSAL_IDM_VERSION) -> dict[str, Any]:
    """
    Load a document from file and migrate it to the target version

    Args:
        file_path: Path to the document file
        target_version: Target schema version

    Returns:
        Migrated document data

    Raises:
        SchemaMigrationError: If migration fails
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        return migrate_schema(data, target_version)

    except json.JSONDecodeError as e:
        raise SchemaMigrationError(f"Invalid JSON: {e!s}")
    except FileNotFoundError:
        raise SchemaMigrationError(f"File not found: {file_path}")
    except Exception as e:
        raise SchemaMigrationError(f"Migration failed: {e!s}")


def save_migrated(data: dict[str, Any], file_path: str) -> None:
    """
    Save migrated document data to file

    Args:
        data: Document data to save
        file_path: Path to save the document

    Raises:
        SchemaMigrationError: If saving fails
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        raise SchemaMigrationError(f"Failed to save migrated document: {e!s}")


def migrate_document_file(input_path: str, output_path: str, target_version: str = UNIVERSAL_IDM_VERSION) -> None:
    """
    Migrate a document file to the target version and save it

    Args:
        input_path: Path to the input document file
        output_path: Path to save the migrated document
        target_version: Target schema version

    Raises:
        SchemaMigrationError: If migration fails
    """
    data = load_and_migrate(input_path, target_version)
    save_migrated(data, output_path)
