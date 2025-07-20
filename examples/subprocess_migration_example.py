#!/usr/bin/env python3
"""
Example demonstrating subprocess migration to secure execution.

This example shows how to migrate from direct subprocess usage to secure
execution using the compatibility wrapper.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from security.secure_execution import SecureExecutor, SecurityContext
from security.subprocess_compatibility import MigrationHelper, SecureSubprocessWrapper


def demonstrate_old_subprocess_pattern():
    """Demonstrate old subprocess usage patterns (INSECURE - for comparison only)."""
    print("=== OLD SUBPROCESS PATTERNS (INSECURE) ===")
    print("# These patterns are shown for comparison only - DO NOT USE")

    print("\n1. Direct subprocess import and usage:")
    print("import subprocess")
    print("result = subprocess.run(['python', '--version'], capture_output=True, text=True)")
    print("print(result.stdout)")

    print("\n2. Shell command execution (DANGEROUS):")
    print("result = subprocess.run('python --version', shell=True, capture_output=True, text=True)")
    print("print(result.stdout)")

    print("\n3. No validation or security checks")
    print("user_input = input('Enter command: ')")
    print("subprocess.run(user_input, shell=True)  # COMMAND INJECTION RISK!")


def demonstrate_compatibility_wrapper():
    """Demonstrate secure subprocess using compatibility wrapper."""
    print("\n=== SECURE SUBPROCESS WITH COMPATIBILITY WRAPPER ===")

    # Create wrapper with warnings disabled for demo
    wrapper = SecureSubprocessWrapper(enable_warnings=False)

    print("1. Drop-in replacement for subprocess.run():")
    try:
        result = wrapper.run(["python", "--version"], capture_output=True)
        print(f"   Command: {result.args}")
        print(f"   Return code: {result.returncode}")
        print(f"   Output: {result.stdout.strip()}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Automatic shell command parsing (secure):")
    try:
        result = wrapper.run("python --version", shell=True, capture_output=True)
        print(f"   Command parsed to: {result.args}")
        print(f"   Output: {result.stdout.strip()}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n3. Built-in security validation:")
    try:
        # This will fail due to security validation
        result = wrapper.run(["rm", "-rf", "/"], capture_output=True)
    except Exception as e:
        print(f"   Security validation prevented dangerous command: {e}")

    print("\n4. Compatibility with subprocess interface:")
    try:
        # Test check_output method
        output = wrapper.check_output(["python", "--version"])
        print(f"   check_output result: {output.strip()}")

        # Test call method
        returncode = wrapper.call(["python", "--version"])
        print(f"   call return code: {returncode}")
    except Exception as e:
        print(f"   Error: {e}")


def demonstrate_direct_secure_execution():
    """Demonstrate direct secure execution (recommended approach)."""
    print("\n=== DIRECT SECURE EXECUTION (RECOMMENDED) ===")

    # Create security context
    context = SecurityContext(allowed_executables=["python", "python3", "echo", "ls"], timeout=30)

    # Create secure executor
    executor = SecureExecutor(context)

    print("1. Secure command execution with validation:")
    try:
        result = executor.execute_command(["python", "--version"])
        print(f"   Command: {result.command}")
        print(f"   Success: {result.success}")
        print(f"   Output: {result.stdout.strip()}")
        print(f"   Execution time: {result.execution_time:.3f}s")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Command validation before execution:")
    validation = executor.validate_command(["python", "--version"])
    print(f"   Command valid: {validation.is_valid}")
    if validation.warnings:
        print(f"   Warnings: {validation.warnings}")

    print("\n3. Security context configuration:")
    print(f"   Allowed executables: {context.allowed_executables[:5]}...")
    print(f"   Timeout: {context.timeout}s")
    print(f"   Base path: {context.base_path}")


def demonstrate_migration_analysis():
    """Demonstrate migration analysis tools."""
    print("\n=== MIGRATION ANALYSIS TOOLS ===")

    # Create a sample file with subprocess usage
    sample_code = """
import subprocess
from subprocess import run, call

def process_files():
    result = subprocess.run(['python', 'process.py'], capture_output=True)
    subprocess.call(['echo', 'Processing complete'])
    return result.returncode
"""

    # Write sample file
    sample_file = Path("temp_sample.py")
    with open(sample_file, "w") as f:
        f.write(sample_code)

    try:
        print("1. Analyzing subprocess usage:")
        analysis = MigrationHelper.analyze_subprocess_usage(sample_file)
        print(f"   Total subprocess calls: {analysis['total_calls']}")
        print(f"   Migration complexity: {analysis['migration_complexity']}")
        print(f"   Subprocess imports: {len(analysis['subprocess_imports'])}")

        print("\n2. Migration suggestions:")
        suggestions = MigrationHelper.generate_migration_suggestions(analysis)
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion}")

        print("\n3. Creating migration script:")
        migration_script = MigrationHelper.create_migration_script(sample_file)
        print(f"   Migration script created: {migration_script}")

        # Show first few lines of migration script
        with open(migration_script) as f:
            lines = f.readlines()[:10]
        print("   Migration script preview:")
        for line in lines:
            print(f"   {line.rstrip()}")

        # Cleanup
        migration_script.unlink()

    finally:
        if sample_file.exists():
            sample_file.unlink()


def demonstrate_gradual_migration():
    """Demonstrate gradual migration strategy."""
    print("\n=== GRADUAL MIGRATION STRATEGY ===")

    print("1. Phase 1: Replace imports")
    print("   OLD: import subprocess")
    print("   NEW: from pdfrebuilder.security.subprocess_compatibility import run, call, check_output")

    print("\n2. Phase 2: Update function calls")
    print("   OLD: subprocess.run(['python', '--version'])")
    print("   NEW: run(['python', '--version'])")

    print("\n3. Phase 3: Add security context (optional)")
    print("   from pdfrebuilder.security.subprocess_compatibility import SecureSubprocessWrapper")
    print("   from pdfrebuilder.security.secure_execution import SecurityContext")
    print("   context = SecurityContext(allowed_executables=['python', 'git'])")
    print("   wrapper = SecureSubprocessWrapper(security_context=context)")

    print("\n4. Phase 4: Migrate to direct secure execution")
    print("   from pdfrebuilder.security.secure_execution import SecureExecutor")
    print("   executor = SecureExecutor(context)")
    print("   result = executor.execute_command(['python', '--version'])")


def main():
    """Run all demonstrations."""
    print("SUBPROCESS SECURITY MIGRATION DEMONSTRATION")
    print("=" * 50)

    demonstrate_old_subprocess_pattern()
    demonstrate_compatibility_wrapper()
    demonstrate_direct_secure_execution()
    demonstrate_migration_analysis()
    demonstrate_gradual_migration()

    print("\n" + "=" * 50)
    print("MIGRATION COMPLETE!")
    print("\nKey Benefits:")
    print("- Command injection prevention")
    print("- Input validation and sanitization")
    print("- Executable whitelisting")
    print("- Timeout enforcement")
    print("- Security audit logging")
    print("- Backward compatibility")


if __name__ == "__main__":
    main()
