#!/usr/bin/env python3
"""
Installation verification script for PDFRebuilder.

This script helps verify that PDFRebuilder is properly installed and configured.
"""

import importlib.util
import sys
from pathlib import Path

# Add src to path for secure execution imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdfrebuilder.security.secure_execution import SecureExecutionError, execute_secure_command


def check_python_version():
    """Check if Python version meets requirements."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 12):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (meets requirement: >=3.12)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires: >=3.12)")
        return False


def check_uv_installation():
    """Check if uv is installed."""
    print("\n🔍 Checking uv installation...")
    try:
        result = execute_secure_command(["uv", "--version"], capture_output=True)
        if result.returncode == 0:
            print(f"✅ uv {result.stdout.strip()}")
            return True
        else:
            print("❌ uv not found or not working")
            return False
    except SecureExecutionError:
        print("❌ uv not found in PATH")
        print("💡 Install with: pip install uv")
        return False


def check_pdfrebuilder_cli():
    """Check if pdfrebuilder CLI is available."""
    print("\n🔍 Checking PDFRebuilder CLI...")
    try:
        result = execute_secure_command(["pdfrebuilder", "--help"], capture_output=True)
        if result.returncode == 0:
            print("✅ PDFRebuilder CLI is working")
            return True
        else:
            print("❌ PDFRebuilder CLI not working")
            return False
    except SecureExecutionError:
        print("❌ PDFRebuilder CLI not found in PATH")
        print("💡 Install with: uv tool install pdfrebuilder")
        return False


def check_pdfrebuilder_library():
    """Check if pdfrebuilder can be imported as a library."""
    print("\n🔍 Checking PDFRebuilder library import...")
    try:
        # Try importing key modules
        from pdfrebuilder.config import ConfigManager

        print("✅ PDFRebuilder library modules can be imported")

        # Test configuration system
        ConfigManager()
        print("✅ Configuration system is working")

        return True
    except ImportError as e:
        print(f"❌ Cannot import PDFRebuilder library: {e}")
        print("💡 This is normal if you only installed the CLI tool")
        return False


def check_dependencies():
    """Check key dependencies."""
    print("\n🔍 Checking key dependencies...")

    dependencies = [
        ("PyMuPDF", "fitz"),
        ("Pillow", "PIL"),
        ("Rich", "rich"),
        ("Pydantic", "pydantic"),
        ("Platform Dirs", "platformdirs"),
    ]

    all_good = True
    for name, module in dependencies:
        try:
            spec = importlib.util.find_spec(module)
            if spec is not None:
                print(f"✅ {name} is available")
            else:
                print(f"❌ {name} not found")
                all_good = False
        except ImportError:
            print(f"❌ {name} not found")
            all_good = False

    return all_good


def test_configuration_system():
    """Test the configuration system."""
    print("\n🔍 Testing configuration system...")
    try:
        result = execute_secure_command(["pdfrebuilder", "--show-config"], capture_output=True)
        if result.returncode == 0:
            print("✅ Configuration system is working")
            return True
        else:
            print(f"❌ Configuration system error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("🚀 PDFRebuilder Installation Verification")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("uv Installation", check_uv_installation),
        ("PDFRebuilder CLI", check_pdfrebuilder_cli),
        ("PDFRebuilder Library", check_pdfrebuilder_library),
        ("Dependencies", check_dependencies),
        ("Configuration System", test_configuration_system),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📋 Verification Summary")
    print("=" * 50)

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! PDFRebuilder is ready to use.")
        print("\n📚 Next steps:")
        print("   • Run 'pdfrebuilder --help' to see available commands")
        print("   • Run 'pdfrebuilder --generate-config' to create a configuration file")
        print("   • Check the documentation at docs/guides/getting-started.md")
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please address the issues above.")
        print("\n💡 Common solutions:")
        print("   • Install uv: pip install uv")
        print("   • Install PDFRebuilder: uv tool install pdfrebuilder")
        print('   • Update PATH: export PATH="$HOME/.local/bin:$PATH"')

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
