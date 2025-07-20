import re

content = """
# API Documentation

Use `nonexistent.module.function()` for something.
"""

patterns = [
    r"`([a-zA-Z_][a-zA-Z0-9_.]*\.[a-zA-Z_][a-zA-Z0-9_]*(?:\([^)]*\))?)`",  # module.function or module.function()
    r"`([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))`",  # function()
]

for i, pattern in enumerate(patterns):
    print(f"Pattern {i}: {pattern}")
    matches = re.finditer(pattern, content)
    for match in matches:
        print(f"  Match: {match.group(1)}")
