"""
Schema tools for the Multi-Format Document Engine.

This module provides utilities for working with the Universal IDM schema,
including validation, migration, and conversion.
"""

import logging
from typing import Any

# Replace with:

logger = logging.getLogger(__name__)


def get_document_statistics(document) -> dict[str, Any]:
    """
    Get statistics about a document

    Args:
        document: Document to analyze (dict or object with to_dict method)

    Returns:
        Dictionary of statistics
    """
    """
    Get statistics about a document

    Args:
        document: Document to analyze

    Returns:
        Dictionary of statistics
    """
    stats = {
        "unit_count": 0,
        "page_count": 0,
        "canvas_count": 0,
        "layer_count": 0,
        "text_count": 0,
        "image_count": 0,
        "drawing_count": 0,
        "total_element_count": 0,
    }

    # Convert to dictionary if needed
    if hasattr(document, "to_dict"):
        doc_dict = document.to_dict()
    else:
        doc_dict = document

    # Get document structure
    doc_structure = doc_dict.get("document_structure", [])
    stats["unit_count"] = len(doc_structure)

    # Count pages and canvases
    for unit in doc_structure:
        if unit.get("type") == "page":
            stats["page_count"] += 1
        elif unit.get("type") == "canvas":
            stats["canvas_count"] += 1

        # Count layers and elements
        layers = unit.get("layers", [])
        stats["layer_count"] += len(layers)

        def count_elements(layer_list):
            for layer in layer_list:
                # Count elements in this layer
                for element in layer.get("content", []):
                    stats["total_element_count"] += 1
                    if element.get("type") == "text":
                        stats["text_count"] += 1
                    elif element.get("type") == "image":
                        stats["image_count"] += 1
                    elif element.get("type") == "drawing":
                        stats["drawing_count"] += 1

                # Count child layers
                children = layer.get("children", [])
                stats["layer_count"] += len(children)
                count_elements(children)

        count_elements(layers)

    return stats
