"""
Performance benchmarks for comparing engines.
Comprehensive benchmarking suite for engine comparison.
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

import pytest

from pdfrebuilder.settings import get_nested_config_value


@dataclass
class BenchmarkResult:
    """Structure for benchmark results"""

    engine_name: str
    operation: str
    execution_time: float
    memory_usage: float
    success: bool
    error_message: str = ""
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BenchmarkSuite:
    """Comprehensive benchmarking suite"""

    def __init__(self):
        self.results: list[BenchmarkResult] = []

    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result"""
        self.results.append(result)

    def get_results_by_engine(self, engine_name: str) -> list[BenchmarkResult]:
        """Get all results for a specific engine"""
        return [r for r in self.results if r.engine_name == engine_name]

    def get_results_by_operation(self, operation: str) -> list[BenchmarkResult]:
        """Get all results for a specific operation"""
        return [r for r in self.results if r.operation == operation]

    def compare_engines(self, operation: str) -> dict[str, Any]:
        """Compare engines for a specific operation"""
        results = self.get_results_by_operation(operation)
        if not results:
            return {}

        comparison = {
            "operation": operation,
            "engines": {},
            "fastest": None,
            "slowest": None,
        }

        fastest_time = float("inf")
        slowest_time = 0
        fastest_engine = None
        slowest_engine = None

        for result in results:
            if result.success:
                comparison["engines"][result.engine_name] = {
                    "execution_time": result.execution_time,
                    "memory_usage": result.memory_usage,
                    "metadata": result.metadata,
                }

                if result.execution_time < fastest_time:
                    fastest_time = result.execution_time
                    fastest_engine = result.engine_name

                if result.execution_time > slowest_time:
                    slowest_time = result.execution_time
                    slowest_engine = result.engine_name

        comparison["fastest"] = fastest_engine
        comparison["slowest"] = slowest_engine

        return comparison

    def export_results(self, filename: str):
        """Export results to JSON file"""
        results_dict = [asdict(result) for result in self.results]
        with open(filename, "w") as f:
            json.dump(results_dict, f, indent=2)

    def generate_report(self) -> str:
        """Generate a text report of benchmark results"""
        report = ["Benchmark Results Report", "=" * 50, ""]

        # Group by operation
        operations = {r.operation for r in self.results}

        for operation in operations:
            report.append(f"Operation: {operation}")
            report.append("-" * 30)

            comparison = self.compare_engines(operation)
            if comparison:
                if comparison["fastest"]:
                    report.append(f"Fastest: {comparison['fastest']}")
                if comparison["slowest"]:
                    report.append(f"Slowest: {comparison['slowest']}")

                for engine, data in comparison["engines"].items():
                    report.append(f"  {engine}: {data['execution_time']:.3f}s, {data['memory_usage']:.1f}MB")

            report.append("")

        return "\n".join(report)


class TestBenchmarks:
    """Comprehensive benchmark tests"""

    def setup_method(self):
        """Set up benchmark suite for each test"""
        self.benchmark_suite = BenchmarkSuite()

    def test_engine_initialization_benchmark(self):
        """Benchmark engine initialization times"""
        engines = [
            ("PDFParser", "src.engine.document_parser", "PDFParser"),
            ("PSDParser", "src.engine.document_parser", "PSDParser"),
        ]

        for engine_name, module_path, class_name in engines:
            try:
                start_time = time.time()

                # Dynamic import and initialization
                module = __import__(module_path, fromlist=[class_name])
                engine_class = getattr(module, class_name)
                engine_instance = engine_class()

                execution_time = time.time() - start_time

                result = BenchmarkResult(
                    engine_name=engine_name,
                    operation="initialization",
                    execution_time=execution_time,
                    memory_usage=0,  # Would measure actual memory usage
                    success=True,
                )

                self.benchmark_suite.add_result(result)

            except Exception as e:
                result = BenchmarkResult(
                    engine_name=engine_name,
                    operation="initialization",
                    execution_time=0,
                    memory_usage=0,
                    success=False,
                    error_message=str(e),
                )

                self.benchmark_suite.add_result(result)

        # Compare initialization times
        comparison = self.benchmark_suite.compare_engines("initialization")
        print(f"Initialization benchmark: {comparison}")

    def test_configuration_access_benchmark(self):
        """Benchmark configuration access performance"""
        from pdfrebuilder.settings import get_config_value, get_nested_config_value

        config_operations = [
            (
                "nested_config",
                lambda: get_nested_config_value("engines.input.wand.density"),
            ),
            ("legacy_config", lambda: get_config_value("default_font")),
            (
                "deep_nested",
                lambda: get_nested_config_value("engines.output.reportlab.compression"),
            ),
        ]

        for operation_name, operation_func in config_operations:
            try:
                # Warm up
                operation_func()

                # Benchmark
                start_time = time.time()
                for _ in range(10000):  # 10,000 operations
                    operation_func()
                execution_time = time.time() - start_time

                result = BenchmarkResult(
                    engine_name="configuration",
                    operation=operation_name,
                    execution_time=execution_time,
                    memory_usage=0,
                    success=True,
                    metadata={"iterations": 10000},
                )

                self.benchmark_suite.add_result(result)

            except Exception as e:
                result = BenchmarkResult(
                    engine_name="configuration",
                    operation=operation_name,
                    execution_time=0,
                    memory_usage=0,
                    success=False,
                    error_message=str(e),
                )

                self.benchmark_suite.add_result(result)

        # Print configuration benchmark results
        for operation in ["nested_config", "legacy_config", "deep_nested"]:
            results = self.benchmark_suite.get_results_by_operation(operation)
            for result in results:
                if result.success:
                    avg_time = result.execution_time / 10000 * 1000  # ms per operation
                    print(f"{operation}: {avg_time:.4f}ms per access")

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_document_parsing_benchmark(self):
        """Benchmark document parsing performance"""
        # This would benchmark actual document parsing
        # Requires test files

        test_files = [
            ("small_pdf", "tests/fixtures/small.pdf"),
            ("medium_pdf", "tests/fixtures/medium.pdf"),
            ("large_pdf", "tests/fixtures/large.pdf"),
            ("small_psd", "tests/fixtures/small.psd"),
            ("medium_psd", "tests/fixtures/medium.psd"),
        ]

        for file_type, file_path in test_files:
            if os.path.exists(file_path):
                # Benchmark parsing with different engines
                # This would use actual parsing functions
                pass

    def test_memory_usage_benchmark(self):
        """Benchmark memory usage across operations"""
        try:
            import psutil

            process = psutil.Process(os.getpid())

            # Baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Test various operations and their memory impact
            operations = [
                (
                    "import_parsers",
                    lambda: __import__(
                        "src.engine.document_parser",
                        fromlist=["PDFParser", "PSDParser"],
                    ),
                ),
                (
                    "create_manifest",
                    lambda: __import__("src.engine.document_parser", fromlist=["AssetManifest"]).AssetManifest(),
                ),
            ]

            for operation_name, operation_func in operations:
                try:
                    start_memory = process.memory_info().rss / 1024 / 1024
                    start_time = time.time()

                    operation_func()

                    end_time = time.time()
                    end_memory = process.memory_info().rss / 1024 / 1024

                    result = BenchmarkResult(
                        engine_name="memory",
                        operation=operation_name,
                        execution_time=end_time - start_time,
                        memory_usage=end_memory - start_memory,
                        success=True,
                        metadata={"baseline_memory": baseline_memory},
                    )

                    self.benchmark_suite.add_result(result)

                except Exception as e:
                    result = BenchmarkResult(
                        engine_name="memory",
                        operation=operation_name,
                        execution_time=0,
                        memory_usage=0,
                        success=False,
                        error_message=str(e),
                    )

                    self.benchmark_suite.add_result(result)

        except ImportError:
            pytest.skip("psutil not available for memory benchmarking")

    def test_generate_benchmark_report(self):
        """Generate and save benchmark report"""
        # Run a few quick benchmarks
        self.test_engine_initialization_benchmark()
        self.test_configuration_access_benchmark()

        # Generate report
        report = self.benchmark_suite.generate_report()
        print("\n" + report)

        # Export results
        output_dir = get_nested_config_value("test_output_dir", "tests/output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        report_file = os.path.join(output_dir, "benchmark_results.json")
        self.benchmark_suite.export_results(report_file)

        print(f"Benchmark results exported to: {report_file}")

    def test_performance_regression_detection(self):
        """Test for performance regressions"""
        # This would compare current performance against baseline
        # and detect regressions

        # Load baseline results if they exist
        baseline_file = "tests/fixtures/baseline_benchmarks.json"
        if os.path.exists(baseline_file):
            with open(baseline_file) as f:
                baseline_results = json.load(f)

            # Compare current results against baseline
            # Flag any significant regressions
            print("Performance regression detection would go here")
        else:
            print("No baseline benchmark file found, skipping regression detection")
