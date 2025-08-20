"""
Test utilities and helper functions.

This module provides utility functions and classes to support testing
across the entire test suite. It complements the fixtures in conftest.py
with reusable test utilities.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from pdfrebuilder.settings import get_config_value


class TestFileManager:
    """Manages test files and directories with automatic cleanup."""

    def __init__(self, test_name: str):
        """
        Initialize the test file manager.

        Args:
            test_name: Name of the test (used for directory naming)
        """
        self.test_name = test_name
        self.created_files: list[str] = []
        self.created_dirs: list[str] = []
        self.temp_dirs: list[str] = []

    def create_temp_dir(self, suffix: str = "") -> str:
        """
        Create a temporary directory.

        Args:
            suffix: Optional suffix for the directory name

        Returns:
            str: Path to the created directory
        """
        if suffix:
            dir_name = f"{self.test_name}_{suffix}"
        else:
            dir_name = self.test_name

        temp_dir = tempfile.mkdtemp(prefix=f"test_{dir_name}_")
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def create_test_file(self, file_path: str, content: str | bytes | dict[str, Any]) -> str:
        """
        Create a test file with the specified content.

        Args:
            file_path: Path where the file should be created
            content: Content to write (string, bytes, or dict for JSON)

        Returns:
            str: Path to the created file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if isinstance(content, dict):
            # Write as JSON
            with open(file_path, "w") as f:
                json.dump(content, f, indent=2)
        elif isinstance(content, bytes):
            # Write as binary
            with open(file_path, "wb") as f:
                f.write(content)
        else:
            # Write as text
            with open(file_path, "w") as f:
                f.write(str(content))

        self.created_files.append(file_path)
        return file_path

    def create_font_file(self, font_path: str, font_name: str | None = None) -> str:
        """
        Create a mock font file for testing.

        Args:
            font_path: Path where the font file should be created
            font_name: Optional font name (defaults to filename without extension)

        Returns:
            str: Path to the created font file
        """
        # Create minimal font file with basic header to avoid "Not a TrueType" errors
        font_content = b"OTTO\x00\x01\x00\x00" + b"\x00" * 100
        return self.create_test_file(font_path, font_content)

    def create_pdf_config(self, config_path: str, pages: int = 1, elements_per_page: int = 5) -> str:
        """
        Create a test PDF configuration file.

        Args:
            config_path: Path where the config file should be created
            pages: Number of pages to include
            elements_per_page: Number of elements per page

        Returns:
            str: Path to the created configuration file
        """
        config = {
            "version": "1.0",
            "engine": "fitz",
            "metadata": {
                "title": f"Test Document - {self.test_name}",
                "author": "Test Suite",
                "subject": "Test Document",
            },
            "document_structure": [],
        }

        for page_num in range(pages):
            page = {
                "type": "page",
                "page_number": page_num,
                "size": [612, 792],
                "page_background_color": [1.0, 1.0, 1.0],
                "layers": [
                    {
                        "layer_id": f"page_{page_num}_base_layer",
                        "layer_name": "Page Content",
                        "layer_type": "base",
                        "bbox": [0, 0, 612, 792],
                        "visibility": True,
                        "opacity": 1.0,
                        "blend_mode": "Normal",
                        "children": [],
                        "content": [],
                    }
                ],
            }

            # Add test elements
            for elem_num in range(elements_per_page):
                element = {
                    "type": "text",
                    "id": f"text_{page_num}_{elem_num}",
                    "bbox": [50, 700 - (elem_num * 50), 562, 720 - (elem_num * 50)],
                    "text": f"Test text element {elem_num} on page {page_num}",
                    "font_details": {"name": "Arial", "size": 12, "color": 0},
                }
                page["layers"][0]["content"].append(element)

            config["document_structure"].append(page)

        return self.create_test_file(config_path, config)

    def cleanup(self):
        """Clean up all created files and directories."""
        # Remove created files
        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors

        # Remove created directories
        for dir_path in self.created_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass  # Ignore cleanup errors

        # Remove temporary directories
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass  # Ignore cleanup errors

        # Clear tracking lists
        self.created_files.clear()
        self.created_dirs.clear()
        self.temp_dirs.clear()


class TestDataGenerator:
    """Generates test data for various testing scenarios."""

    @staticmethod
    def create_font_test_data(num_fonts: int = 5) -> list[dict[str, Any]]:
        """
        Create test data for font testing.

        Args:
            num_fonts: Number of fonts to generate data for

        Returns:
            List of font test data dictionaries
        """
        fonts = []
        font_names = ["Arial", "Times", "Helvetica", "Courier", "Symbol"]

        for i in range(num_fonts):
            font_name = font_names[i % len(font_names)]
            fonts.append(
                {
                    "name": f"{font_name}-{i}" if i >= len(font_names) else font_name,
                    "size": 12 + (i * 2),
                    "color": i * 1000000,  # Different colors
                    "is_bold": i % 2 == 0,
                    "is_italic": i % 3 == 0,
                }
            )

        return fonts

    @staticmethod
    def create_document_test_data(pages: int = 2, elements_per_page: int = 3) -> dict[str, Any]:
        """
        Create test document data.

        Args:
            pages: Number of pages
            elements_per_page: Number of elements per page

        Returns:
            Document configuration dictionary
        """
        fonts = TestDataGenerator.create_font_test_data(elements_per_page)

        config = {
            "version": "1.0",
            "engine": "fitz",
            "metadata": {"title": "Test Document", "author": "Test Suite"},
            "document_structure": [],
        }

        for page_num in range(pages):
            page = {
                "type": "page",
                "page_number": page_num,
                "size": [612, 792],
                "layers": [{"layer_id": f"page_{page_num}_layer", "content": []}],
            }

            for elem_num in range(elements_per_page):
                font = fonts[elem_num]
                element = {
                    "type": "text",
                    "id": f"text_{page_num}_{elem_num}",
                    "text": f"Test text {elem_num}",
                    "font_details": font,
                }
                page["layers"][0]["content"].append(element)

            config["document_structure"].append(page)

        return config

    @staticmethod
    def create_drawing_test_data(num_shapes: int = 5) -> list[dict[str, Any]]:
        """
        Create test data for drawing/shape testing.

        Args:
            num_shapes: Number of shapes to generate

        Returns:
            List of drawing element dictionaries
        """
        shapes = []
        shape_types = ["rect", "ellipse", "line", "curve"]
        colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1]]

        for i in range(num_shapes):
            shape_type = shape_types[i % len(shape_types)]
            color = colors[i % len(colors)]

            if shape_type == "rect":
                commands = [
                    {
                        "cmd": "rect",
                        "bbox": [i * 50, i * 50, (i + 1) * 50, (i + 1) * 50],
                    }
                ]
            elif shape_type == "ellipse":
                commands = [
                    {
                        "cmd": "ellipse",
                        "bbox": [i * 50, i * 50, (i + 1) * 50, (i + 1) * 50],
                    }
                ]
            else:
                commands = [
                    {"cmd": "M", "pts": [i * 50, i * 50]},
                    {"cmd": "L", "pts": [(i + 1) * 50, (i + 1) * 50]},
                    {"cmd": "H"},
                ]

            shape = {
                "type": "drawing",
                "id": f"shape_{i}",
                "color": color,
                "fill": [c * 0.5 for c in color],  # Lighter fill
                "width": 1.0 + i * 0.5,
                "drawing_commands": commands,
            }
            shapes.append(shape)

        return shapes


class TestAssertions:
    """Custom assertions for testing."""

    @staticmethod
    def assert_file_exists(file_path: str, message: str | None = None):
        """Assert that a file exists."""
        if not os.path.exists(file_path):
            msg = message or f"Expected file to exist: {file_path}"
            raise AssertionError(msg)

    @staticmethod
    def assert_directory_exists(dir_path: str, message: str | None = None):
        """Assert that a directory exists."""
        if not os.path.isdir(dir_path):
            msg = message or f"Expected directory to exist: {dir_path}"
            raise AssertionError(msg)

    @staticmethod
    def assert_file_not_empty(file_path: str, message: str | None = None):
        """Assert that a file exists and is not empty."""
        TestAssertions.assert_file_exists(file_path)
        if os.path.getsize(file_path) == 0:
            msg = message or f"Expected file to not be empty: {file_path}"
            raise AssertionError(msg)

    @staticmethod
    def assert_json_file_valid(file_path: str, message: str | None = None):
        """Assert that a JSON file exists and contains valid JSON."""
        TestAssertions.assert_file_exists(file_path)
        try:
            with open(file_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            msg = message or f"Expected valid JSON file: {file_path}, error: {e}"
            raise AssertionError(msg)

    @staticmethod
    def assert_config_has_required_fields(
        config: dict[str, Any], required_fields: list[str], message: str | None = None
    ):
        """Assert that a configuration dictionary has all required fields."""
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            msg = message or f"Configuration missing required fields: {missing_fields}"
            raise AssertionError(msg)

    @staticmethod
    def assert_font_data_valid(font_data: dict[str, Any], message: str | None = None):
        """Assert that font data dictionary has valid structure."""
        required_fields = ["name", "size"]
        TestAssertions.assert_config_has_required_fields(font_data, required_fields, message)

        if not isinstance(font_data["size"], int | float) or font_data["size"] <= 0:
            msg = message or f"Font size must be a positive number: {font_data['size']}"
            raise AssertionError(msg)


def get_test_resource_path(resource_name: str) -> str:
    """
    Get the path to a test resource file.

    Args:
        resource_name: Name of the resource file

    Returns:
        str: Full path to the resource file
    """
    test_resources_dir = get_config_value("test_sample_dir")
    return os.path.join(test_resources_dir, resource_name)


def create_minimal_test_config() -> dict[str, Any]:
    """
    Create a minimal test configuration for basic testing.

    Returns:
        Dict containing minimal test configuration
    """
    return {
        "version": "1.0",
        "engine": "fitz",
        "metadata": {"title": "Minimal Test"},
        "document_structure": [
            {
                "type": "page",
                "page_number": 0,
                "layers": [
                    {
                        "content": [
                            {
                                "type": "text",
                                "id": "test_text",
                                "text": "Test",
                                "font_details": {"name": "Arial", "size": 12},
                            }
                        ]
                    }
                ],
            }
        ],
    }


def normalize_path_separators(path: str) -> str:
    """
    Normalize path separators for cross-platform compatibility.

    Args:
        path: Path string to normalize

    Returns:
        str: Normalized path string
    """
    return str(Path(path))


def ensure_test_directory_structure():
    """Ensure that the standard test directory structure exists."""
    test_dirs = [
        get_config_value("test_output_dir"),
        get_config_value("test_temp_dir"),
        get_config_value("test_fonts_dir"),
        get_config_value("test_reports_dir"),
        get_config_value("test_sample_dir"),
        get_config_value("test_fixtures_dir"),
        get_config_value("test_debug_dir"),
    ]

    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
