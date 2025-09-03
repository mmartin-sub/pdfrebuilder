import sys
import os
import shutil
import pytest

print("--- Debugging Pytest Execution ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")
print(f"Pytest Location: {pytest.__file__}")
print("\n--- sys.path ---")
for path in sys.path:
    print(path)
print("------------------\n")

print("Attempting to run pytest...")
try:
    exit_code = pytest.main(['-v', 'tests/slow'])
    print(f"Pytest exited with code: {exit_code}")
except Exception as e:
    print(f"An error occurred while running pytest: {e}")
