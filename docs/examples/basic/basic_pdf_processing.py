"""
Basic PDF processing example for the Multi-Format Document Engine.
"""

import json
import sys


def main():
    """Basic PDF processing example."""
    print("Basic PDF Processing Example")
    print("=" * 35)

    # Example PDF processing configuration
    config = {
        "version": "1.0",
        "engine": "fitz",
        "metadata": {
            "title": "Sample PDF Document",
            "creator": "Multi-Format Document Engine",
        },
        "document_structure": [{"type": "page", "page_number": 1, "size": [612.0, 792.0], "layers": []}],
    }

    print("Example PDF processing configuration:")
    print(json.dumps(config, indent=2))

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
