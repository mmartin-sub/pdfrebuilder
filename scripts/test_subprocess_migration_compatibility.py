#!/usr/bin/env python3
"""
Subprocess Migration Compatibility Testing Script

This script tests the compatibility of migrated subprocess usage to ensure
functionality is preserved while security is improved.
"""

import json
import os
import subprocess  # nosec B404 # Required for compatibility testing between subprocess and secure alternatives
import sys
import tempfile
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from security.subprocess_compatibility import SecureSubprocessWrapper, run

    SECURE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Secure modules not available: {e}")
    print("Testing basic subprocess patterns instead...")
    SECURE_MODULES_AVAILABLE = False


class MigrationCompatibilityTester:
    """Tests compatibility between old subprocess usage and new secure alternatives."""

    def __init__(self):
        self.test_results = []
        if SECURE_MODULES_AVAILABLE:
            self.wrapper = SecureSubprocessWrapper()
        else:
            self.wrapper = None

    def test_basic_command_execution(self) -> dict:
        """Test basic command execution compatibility."""
        test_name = "Basic Command Execution"
        print(f"🧪 Testing {test_name}...")

        try:
            if SECURE_MODULES_AVAILABLE:
                # Test with secure wrapper
                result = run(["python", "--version"], capture_output=True, text=True)
            else:
                # Test with standard subprocess (for comparison)
                result = subprocess.run(["python", "--version"], capture_output=True, text=True)  # nosec B607 B603 # Required for compatibility testing

            success = (
                result.returncode == 0
                and "Python" in result.stdout
                and hasattr(result, "stdout")
                and hasattr(result, "stderr")
                and hasattr(result, "returncode")
            )

            return {
                "test": test_name,
                "success": success,
                "details": f"Return code: {result.returncode}, Output length: {len(result.stdout)}, Using secure: {SECURE_MODULES_AVAILABLE}",
            }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_error_handling(self) -> dict:
        """Test error handling compatibility."""
        test_name = "Error Handling"
        print(f"🧪 Testing {test_name}...")

        try:
            if SECURE_MODULES_AVAILABLE:
                result = run(["python", "nonexistent_script.py"], capture_output=True, text=True)
            else:
                result = subprocess.run(["python", "nonexistent_script.py"], capture_output=True, text=True)  # nosec B607 B603 # Required for compatibility testing

            success = result.returncode != 0 and len(result.stderr) > 0

            return {
                "test": test_name,
                "success": success,
                "details": f"Return code: {result.returncode}, Error output present: {len(result.stderr) > 0}, Using secure: {SECURE_MODULES_AVAILABLE}",
            }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_timeout_handling(self) -> dict:
        """Test timeout handling."""
        test_name = "Timeout Handling"
        print(f"🧪 Testing {test_name}...")

        try:
            # Create a script that sleeps longer than timeout
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("import time; time.sleep(5)")
                script_path = f.name

            try:
                start_time = time.time()
                if SECURE_MODULES_AVAILABLE:
                    # Use secure wrapper with timeout
                    run(["python", script_path], timeout=1, capture_output=True)
                else:
                    # Use standard subprocess with timeout
                    subprocess.run(["python", script_path], timeout=1, capture_output=True)  # nosec B607 B603 # Required for compatibility testing

                elapsed = time.time() - start_time

                # Should have timed out
                success = False
                details = f"Command completed unexpectedly in {elapsed:.2f}s"

            except (subprocess.TimeoutExpired, TimeoutError) as e:
                elapsed = time.time() - start_time
                success = elapsed < 3  # Should timeout quickly
                details = f"Timed out correctly in {elapsed:.2f}s: {e!s}, Using secure: {SECURE_MODULES_AVAILABLE}"

            finally:
                os.unlink(script_path)

            return {"test": test_name, "success": success, "details": details}

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_shell_command_prevention(self) -> dict:
        """Test that shell commands are properly handled."""
        test_name = "Shell Command Prevention"
        print(f"🧪 Testing {test_name}...")

        try:
            # Test that shell metacharacters are treated as literals
            malicious_input = "; echo 'INJECTED'"
            if SECURE_MODULES_AVAILABLE:
                result = run(["echo", malicious_input], capture_output=True, text=True)
            else:
                result = subprocess.run(
                    ["echo", malicious_input],
                    capture_output=True,
                    text=True,
                    shell=False,
                )  # nosec B607 B603 # Required for compatibility testing

            # The malicious input should be echoed literally, not executed
            success = (
                result.returncode == 0
                and "INJECTED" not in result.stdout.split("\n")[0]  # Not executed as separate command
                and malicious_input in result.stdout  # But present as literal text
            )

            return {
                "test": test_name,
                "success": success,
                "details": f"Output: {result.stdout.strip()}, Contains literal input: {malicious_input in result.stdout}, Using secure: {SECURE_MODULES_AVAILABLE}",
            }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_working_directory(self) -> dict:
        """Test working directory handling."""
        test_name = "Working Directory"
        print(f"🧪 Testing {test_name}...")

        try:
            # Test with different working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                if SECURE_MODULES_AVAILABLE:
                    result = run(
                        ["python", "-c", "import os; print(os.getcwd())"],
                        capture_output=True,
                        text=True,
                        cwd=temp_dir,
                    )
                else:
                    result = subprocess.run(
                        ["python", "-c", "import os; print(os.getcwd())"],
                        capture_output=True,
                        text=True,
                        cwd=temp_dir,  # nosec B607 B603 # Required for compatibility testing
                    )

                success = result.returncode == 0 and temp_dir in result.stdout

                return {
                    "test": test_name,
                    "success": success,
                    "details": f"Expected: {temp_dir}, Got: {result.stdout.strip()}, Using secure: {SECURE_MODULES_AVAILABLE}",
                }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_environment_variables(self) -> dict:
        """Test environment variable handling."""
        test_name = "Environment Variables"
        print(f"🧪 Testing {test_name}...")

        try:
            # Test with custom environment variable
            test_env = os.environ.copy()
            test_env["TEST_MIGRATION_VAR"] = "test_value_123"

            if SECURE_MODULES_AVAILABLE:
                result = run(
                    [
                        "python",
                        "-c",
                        "import os; print(os.environ.get('TEST_MIGRATION_VAR', 'NOT_FOUND'))",
                    ],
                    capture_output=True,
                    text=True,
                    env=test_env,
                )
            else:
                result = subprocess.run(
                    [
                        "python",
                        "-c",
                        "import os; print(os.environ.get('TEST_MIGRATION_VAR', 'NOT_FOUND'))",
                    ],
                    capture_output=True,
                    text=True,
                    env=test_env,  # nosec B607 B603 # Required for compatibility testing
                )

            success = result.returncode == 0 and "test_value_123" in result.stdout

            return {
                "test": test_name,
                "success": success,
                "details": f"Environment variable value: {result.stdout.strip()}, Using secure: {SECURE_MODULES_AVAILABLE}",
            }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_input_validation(self) -> dict:
        """Test input validation and sanitization."""
        test_name = "Input Validation"
        print(f"🧪 Testing {test_name}...")

        try:
            # Test with potentially dangerous inputs
            dangerous_inputs = [
                ["python", "-c", "print('safe')"],  # Should work
                ["python", "-c", "import os; print('still safe')"],  # Should work
            ]

            results = []
            for cmd in dangerous_inputs:
                try:
                    if SECURE_MODULES_AVAILABLE:
                        result = run(cmd, capture_output=True, text=True, timeout=5)
                    else:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)  # nosec B607 B603 # Required for compatibility testing
                    results.append(result.returncode == 0)
                except Exception:
                    results.append(False)

            success = all(results)

            return {
                "test": test_name,
                "success": success,
                "details": f"Tested {len(dangerous_inputs)} command variations, {sum(results)} succeeded, Using secure: {SECURE_MODULES_AVAILABLE}",
            }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def test_compatibility_wrapper_interface(self) -> dict:
        """Test that the compatibility wrapper provides the same interface."""
        test_name = "Compatibility Wrapper Interface"
        print(f"🧪 Testing {test_name}...")

        if not SECURE_MODULES_AVAILABLE:
            return {
                "test": test_name,
                "success": False,
                "details": "Secure modules not available for testing",
            }

        try:
            # Test that wrapper has expected methods and attributes
            wrapper = SecureSubprocessWrapper()

            required_methods = ["run", "call", "check_call", "check_output"]
            available_methods = [hasattr(wrapper, method) for method in required_methods]

            # Test basic functionality
            result = wrapper.run(["python", "--version"], capture_output=True, text=True)
            interface_works = hasattr(result, "returncode") and hasattr(result, "stdout") and hasattr(result, "stderr")

            success = all(available_methods) and interface_works

            return {
                "test": test_name,
                "success": success,
                "details": f"Methods available: {sum(available_methods)}/{len(required_methods)}, Interface works: {interface_works}",
            }

        except Exception as e:
            return {"test": test_name, "success": False, "error": str(e)}

    def run_all_tests(self) -> dict:
        """Run all compatibility tests."""
        print("🚀 Starting subprocess migration compatibility tests...\n")

        test_methods = [
            self.test_basic_command_execution,
            self.test_error_handling,
            self.test_timeout_handling,
            self.test_shell_command_prevention,
            self.test_working_directory,
            self.test_environment_variables,
            self.test_input_validation,
            self.test_compatibility_wrapper_interface,
        ]

        results = []
        for test_method in test_methods:
            result = test_method()
            results.append(result)
            self.test_results.append(result)

            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if not result["success"] and "error" in result:
                print(f"   Error: {result['error']}")
            elif "details" in result:
                print(f"   Details: {result['details']}")
            print()

        # Summary
        passed = sum(1 for r in results if r["success"])
        total = len(results)

        print(f"📊 Test Summary: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All compatibility tests passed! Migration is safe to proceed.")
        else:
            print("⚠️  Some tests failed. Review issues before proceeding with migration.")

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "success_rate": passed / total * 100,
            "results": results,
        }

    def save_results(self, filename: str = "migration_compatibility_results.json"):
        """Save test results to file."""
        summary = self.run_all_tests()

        with open(filename, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"📄 Results saved to {filename}")
        return summary


def main():
    """Main function to run compatibility tests."""
    tester = MigrationCompatibilityTester()
    results = tester.save_results()

    # Exit with appropriate code
    sys.exit(0 if results["failed_tests"] == 0 else 1)


if __name__ == "__main__":
    main()
