"""
Schema validation and migration utilities for Universal IDM
"""

import json
import logging
from typing import Any

from .schema_migration import SchemaMigrationError, migrate_schema
from .universal_idm import UNIVERSAL_IDM_VERSION, UniversalDocument, validate_schema_version

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when schema validation fails"""


# SchemaMigrationError is already imported from schema_migration.py


class SchemaValidator:
    """Validates and migrates Universal IDM schemas"""

    def __init__(self):
        self.supported_versions = ["1.0"]
        self.current_version = UNIVERSAL_IDM_VERSION

    def validate_document(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate a document against the Universal IDM schema

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: list[str] = []

        # Check required top-level fields
        required_fields = [
            "version",
            "engine",
            "engine_version",
            "metadata",
            "document_structure",
        ]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate version
        if "version" in data:
            if not validate_schema_version(data):
                errors.append(f"Unsupported schema version: {data['version']}")

        # Validate document structure
        if "document_structure" in data:
            structure_errors = self._validate_document_structure(data["document_structure"])
            errors.extend(structure_errors)

        # Validate metadata
        if "metadata" in data:
            metadata_errors = self._validate_metadata(data["metadata"])
            errors.extend(metadata_errors)

        return len(errors) == 0, errors

    def _validate_document_structure(self, structure: list[dict[str, Any]]) -> list[str]:
        """Validate document structure array"""
        errors: list[str] = []

        if not isinstance(structure, list):
            errors.append("document_structure must be a list")
            return errors

        for i, unit in enumerate(structure):
            if not isinstance(unit, dict):
                errors.append(f"Document unit {i} must be a dictionary")
                continue

            # Check required unit fields
            required_unit_fields = ["type", "size", "layers"]
            for field in required_unit_fields:
                if field not in unit:
                    errors.append(f"Document unit {i} missing required field: {field}")

            # Validate unit type
            if "type" in unit:
                valid_types = ["page", "canvas"]
                if unit["type"] not in valid_types:
                    errors.append(f"Document unit {i} has invalid type: {unit['type']}")

            # Validate layers
            if "layers" in unit:
                layer_errors = self._validate_layers(unit["layers"], f"unit_{i}")
                errors.extend(layer_errors)

        return errors

    def _validate_layers(self, layers: list[dict[str, Any]], context: str) -> list[str]:
        """Validate layers array"""
        errors = []

        if not isinstance(layers, list):
            errors.append(f"{context} layers must be a list")
            return errors

        for i, layer in enumerate(layers):
            if not isinstance(layer, dict):
                errors.append(f"{context} layer {i} must be a dictionary")
                continue

            # Check required layer fields
            required_layer_fields = [
                "layer_id",
                "layer_name",
                "layer_type",
                "bbox",
                "content",
            ]
            for field in required_layer_fields:
                if field not in layer:
                    errors.append(f"{context} layer {i} missing required field: {field}")

            # Validate layer type
            if "layer_type" in layer:
                valid_layer_types = [
                    "base",
                    "pixel",
                    "text",
                    "shape",
                    "group",
                    "adjustment",
                    "smart_object",
                ]
                if layer["layer_type"] not in valid_layer_types:
                    errors.append(f"{context} layer {i} has invalid layer_type: {layer['layer_type']}")

            # Validate bbox format
            if "bbox" in layer:
                bbox_errors = self._validate_bbox(layer["bbox"], f"{context}_layer_{i}")
                errors.extend(bbox_errors)

            # Validate content elements
            if "content" in layer:
                content_errors = self._validate_elements(layer["content"], f"{context}_layer_{i}")
                errors.extend(content_errors)

            # Validate children (for group layers)
            if layer.get("children"):
                children_errors = self._validate_layers(layer["children"], f"{context}_layer_{i}_children")
                errors.extend(children_errors)

        return errors

    def _validate_elements(self, elements: list[dict[str, Any]], context: str) -> list[str]:
        """Validate elements array"""
        errors = []

        if not isinstance(elements, list):
            errors.append(f"{context} content must be a list")
            return errors

        for i, element in enumerate(elements):
            if not isinstance(element, dict):
                errors.append(f"{context} element {i} must be a dictionary")
                continue

            # Check required element fields
            required_element_fields = ["type", "id", "bbox"]
            for field in required_element_fields:
                if field not in element:
                    errors.append(f"{context} element {i} missing required field: {field}")

            # Validate element type
            if "type" in element:
                valid_element_types = ["text", "image", "drawing", "shape"]
                if element["type"] not in valid_element_types:
                    errors.append(f"{context} element {i} has invalid type: {element['type']}")

                # Type-specific validation
                if element["type"] == "text":
                    text_errors = self._validate_text_element(element, f"{context}_element_{i}")
                    errors.extend(text_errors)
                elif element["type"] == "image":
                    image_errors = self._validate_image_element(element, f"{context}_element_{i}")
                    errors.extend(image_errors)
                elif element["type"] == "drawing":
                    drawing_errors = self._validate_drawing_element(element, f"{context}_element_{i}")
                    errors.extend(drawing_errors)

            # Validate bbox
            if "bbox" in element:
                bbox_errors = self._validate_bbox(element["bbox"], f"{context}_element_{i}")
                errors.extend(bbox_errors)

        return errors

    def _validate_text_element(self, element: dict[str, Any], context: str) -> list[str]:
        """Validate text element specific fields"""
        errors = []

        required_text_fields = ["text", "font_details"]
        for field in required_text_fields:
            if field not in element:
                errors.append(f"{context} missing required text field: {field}")

        # Validate font details
        if "font_details" in element:
            font_details = element["font_details"]
            if not isinstance(font_details, dict):
                errors.append(f"{context} font_details must be a dictionary")
            else:
                required_font_fields = ["name", "size", "color"]
                for field in required_font_fields:
                    if field not in font_details:
                        errors.append(f"{context} font_details missing required field: {field}")

        return errors

    def _validate_image_element(self, element: dict[str, Any], context: str) -> list[str]:
        """Validate image element specific fields"""
        errors = []

        required_image_fields = ["image_file"]
        for field in required_image_fields:
            if field not in element:
                errors.append(f"{context} missing required image field: {field}")

        return errors

    def _validate_drawing_element(self, element: dict[str, Any], context: str) -> list[str]:
        """Validate drawing element specific fields"""
        errors = []

        # Drawing commands validation
        if "drawing_commands" in element:
            commands = element["drawing_commands"]
            if not isinstance(commands, list):
                errors.append(f"{context} drawing_commands must be a list")
            else:
                for i, cmd in enumerate(commands):
                    if not isinstance(cmd, dict):
                        errors.append(f"{context} drawing_command {i} must be a dictionary")
                        continue

                    if "cmd" not in cmd:
                        errors.append(f"{context} drawing_command {i} missing 'cmd' field")
                    else:
                        valid_commands = ["M", "L", "C", "H", "rect", "ellipse"]
                        if cmd["cmd"] not in valid_commands:
                            errors.append(f"{context} drawing_command {i} has invalid cmd: {cmd['cmd']}")

        return errors

    def _validate_bbox(self, bbox: Any, context: str) -> list[str]:
        """Validate bounding box format"""
        errors = []

        if not isinstance(bbox, list):
            errors.append(f"{context} bbox must be a list")
            return errors

        if len(bbox) != 4:
            errors.append(f"{context} bbox must have exactly 4 elements")
            return errors

        for i, coord in enumerate(bbox):
            if not isinstance(coord, int | float):
                errors.append(f"{context} bbox coordinate {i} must be a number")

        return errors

    def _validate_metadata(self, metadata: dict[str, Any]) -> list[str]:
        """Validate metadata structure"""
        errors: list[str] = []

        if not isinstance(metadata, dict):
            errors.append("metadata must be a dictionary")
            return errors

        # Metadata validation is more lenient as it's format-specific
        # Just check that it's a valid dictionary structure

        return errors

    def migrate_document(self, data: dict[str, Any], target_version: str | None = None) -> dict[str, Any]:
        """
        Migrate document to target version

        Args:
            data: Document data to migrate
            target_version: Target schema version (defaults to current)

        Returns:
            Migrated document data

        Raises:
            SchemaMigrationError: If migration fails
        """
        if target_version is None:
            target_version = self.current_version

        try:
            current_version = data.get("version", "1.0")

            if current_version == target_version:
                logger.info(f"Document already at target version {target_version}")
                return data

            logger.info(f"Migrating document from version {current_version} to {target_version}")

            # Perform migration
            migrated_data = migrate_schema(data, target_version)

            # Validate migrated data
            is_valid, errors = self.validate_document(migrated_data)
            if not is_valid:
                raise SchemaMigrationError(f"Migration validation failed: {errors}")

            logger.info(f"Successfully migrated document to version {target_version}")
            return migrated_data

        except Exception as e:
            raise SchemaMigrationError(f"Migration failed: {e!s}")

    def load_and_validate_document(self, file_path: str) -> UniversalDocument:
        """
        Load and validate a document from file

        Args:
            file_path: Path to JSON document file

        Returns:
            Validated UniversalDocument instance

        Raises:
            SchemaValidationError: If validation fails
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Validate schema
            is_valid, errors = self.validate_document(data)
            if not is_valid:
                raise SchemaValidationError(f"Schema validation failed: {errors}")

            # Migrate if necessary
            if not validate_schema_version(data):
                data = self.migrate_document(data)

            # Create UniversalDocument instance
            return UniversalDocument.from_dict(data)

        except json.JSONDecodeError as e:
            raise SchemaValidationError(f"Invalid JSON: {e!s}")
        except FileNotFoundError:
            raise SchemaValidationError(f"File not found: {file_path}")
        except Exception as e:
            raise SchemaValidationError(f"Validation failed: {e!s}")


# Convenience functions


def validate_document_file(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate a document file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = SchemaValidator()
    try:
        validator.load_and_validate_document(file_path)
        return True, []
    except SchemaValidationError as e:
        return False, [str(e)]


def migrate_document_file(input_path: str, output_path: str, target_version: str | None = None) -> bool:
    """
    Migrate a document file to target version

    Returns:
        True if successful, False otherwise
    """
    validator = SchemaValidator()
    try:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)

        migrated_data = validator.migrate_document(data, target_version)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(migrated_data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        logger.error(f"Migration failed: {e!s}")
        return False
