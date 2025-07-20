"""
Configuration example for the Multi-Format Document Engine.
"""

import json
import sys


def main():
    """Configuration example."""
    print("Configuration Example")
    print("=" * 30)

    # Example configuration structure
    config = {
        "version": "1.0",
        "engine": "fitz",
        "metadata": {"title": "Example Document"},
        "document_structure": [],
    }

    print("Example configuration:")
    print(json.dumps(config, indent=2))

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
