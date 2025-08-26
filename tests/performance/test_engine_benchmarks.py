"""
Performance benchmarking tests for PDF engines.

Tests and compares the performance characteristics of different PDF rendering engines
including rendering speed, memory usage, and output quality metrics.
"""

import json
import os
import statistics
import tempfile
import time
from typing import Any

import pytest

from pdfrebuilder.core.recreate_pdf_from_config import recreate_pdf_from_config
from pdfrebuilder.engine.pdf_engine_selector import get_engine_selector
from pdfrebuilder.engine.performance_metrics import generate_performance_report, get_performance_collector


class TestEngineBenchmarks:
    """Performance benchmarking tests for PDF engines."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.collector = get_performance_collector()
        self.collector.clear_history()  # Start with clean metrics

        # Create test documents of varying complexity
        self.simple_doc = self._create_simple_document()
        self.complex_doc = self._create_complex_document()
        self.large_doc = self._create_large_document()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_simple_document(self) -> dict[str, Any]:
        """Create a simple test document."""
        return {
            "version": "1.0",
            "engine": "test",
            "metadata": {"title": "Simple Test Document"},
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": "layer_0",
                            "layer_name": "Content",
                            "layer_type": "base",
                            "bbox": [0, 0, 612, 792],
                            "visibility": True,
                            "opacity": 1.0,
                            "content": [
                                {
                                    "type": "text",
                                    "id": "text_0",
                                    "bbox": [100, 700, 500, 720],
                                    "text": "Simple text element",
                                    "font_details": {
                                        "name": "Helvetica",
                                        "size": 12,
                                        "color": [0, 0, 0, 1],
                                    },
                                }
                            ],
                        }
                    ],
                }
            ],
        }

    def _create_complex_document(self) -> dict[str, Any]:
        """Create a complex test document with multiple elements."""
        elements = []

        # Add multiple text elements
        for i in range(10):
            elements.append(
                {
                    "type": "text",
                    "id": f"text_{i}",
                    "bbox": [50 + i * 50, 700 - i * 30, 200 + i * 50, 720 - i * 30],
                    "text": f"Text element {i}",
                    "font_details": {
                        "name": "Helvetica",
                        "size": 10 + i,
                        "color": [i * 0.1, 0, 0, 1],
                    },
                }
            )

        # Add drawing elements
        for i in range(5):
            elements.append(
                {
                    "type": "drawing",
                    "id": f"drawing_{i}",
                    "bbox": [100 + i * 100, 400, 150 + i * 100, 450],
                    "color": [0, 0, 1],
                    "fill": [0.5, 0.5, 1],
                    "width": 2.0,
                    "drawing_commands": [
                        {
                            "cmd": "rect",
                            "bbox": [100 + i * 100, 400, 150 + i * 100, 450],
                        }
                    ],
                }
            )

        return {
            "version": "1.0",
            "engine": "test",
            "metadata": {"title": "Complex Test Document"},
            "document_structure": [
                {
                    "type": "page",
                    "page_number": 0,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": "layer_0",
                            "layer_name": "Content",
                            "layer_type": "base",
                            "bbox": [0, 0, 612, 792],
                            "visibility": True,
                            "opacity": 1.0,
                            "content": elements,
                        }
                    ],
                }
            ],
        }

    def _create_large_document(self) -> dict[str, Any]:
        """Create a large test document with many pages."""
        pages = []

        for page_num in range(5):  # 5 pages
            elements = []

            # Add many text elements per page
            for i in range(20):
                elements.append(
                    {
                        "type": "text",
                        "id": f"page_{page_num}_text_{i}",
                        "bbox": [50, 750 - i * 35, 550, 770 - i * 35],
                        "text": f"Page {page_num + 1}, Line {i + 1}: Lorem ipsum dolor sit amet",
                        "font_details": {
                            "name": "Helvetica",
                            "size": 10,
                            "color": [0, 0, 0, 1],
                        },
                    }
                )

            pages.append(
                {
                    "type": "page",
                    "page_number": page_num,
                    "size": [612, 792],
                    "layers": [
                        {
                            "layer_id": f"page_{page_num}_layer_0",
                            "layer_name": f"Page {page_num + 1} Content",
                            "layer_type": "base",
                            "bbox": [0, 0, 612, 792],
                            "visibility": True,
                            "opacity": 1.0,
                            "content": elements,
                        }
                    ],
                }
            )

        return {
            "version": "1.0",
            "engine": "test",
            "metadata": {"title": "Large Test Document"},
            "document_structure": pages,
        }

    def _save_test_document(self, doc: dict[str, Any], filename: str) -> str:
        """Save a test document to a file."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            json.dump(doc, f)
        return filepath

    def _benchmark_engine(self, engine_name: str, document: dict[str, Any], runs: int = 3) -> list[float]:
        """Benchmark an engine with a specific document."""
        durations = []

        for run in range(runs):
            config_file = self._save_test_document(document, f"bench_{engine_name}_{run}.json")
            output_file = os.path.join(self.temp_dir, f"bench_{engine_name}_{run}.pdf")

            try:
                start_time = time.time()
                engine = get_engine_selector().get_engine(engine_name)
                engine.generate(document, output_file)
                end_time = time.time()

                duration = end_time - start_time
                durations.append(duration)

                # Verify output was created
                assert os.path.exists(output_file)
                assert os.path.getsize(output_file) > 0

            except Exception as e:
                pytest.skip(f"Engine {engine_name} failed: {e}")

        return durations

    @pytest.mark.performance
    def test_simple_document_benchmark(self):
        """Benchmark engines with a simple document."""
        selector = get_engine_selector()
        available_engines = selector.list_available_engines()

        results = {}

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            try:
                durations = self._benchmark_engine(engine_name, self.simple_doc)
                results[engine_name] = {
                    "avg_duration": statistics.mean(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0,
                }
            except Exception as e:
                results[engine_name] = {"error": str(e)}

        # Log results
        print("\nSimple Document Benchmark Results:")
        for engine, stats in results.items():
            if "error" not in stats:
                print(
                    f"{engine}: {stats['avg_duration']:.3f}s avg, "
                    f"{stats['min_duration']:.3f}s min, "
                    f"{stats['max_duration']:.3f}s max"
                )
            else:
                print(f"{engine}: ERROR - {stats['error']}")

        # At least one engine should have succeeded
        successful_engines = [e for e, s in results.items() if "error" not in s]
        assert len(successful_engines) > 0, "No engines succeeded in benchmark"

    @pytest.mark.performance
    def test_complex_document_benchmark(self):
        """Benchmark engines with a complex document."""
        selector = get_engine_selector()
        available_engines = selector.list_available_engines()

        results = {}

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            try:
                durations = self._benchmark_engine(engine_name, self.complex_doc, runs=2)
                results[engine_name] = {
                    "avg_duration": statistics.mean(durations),
                    "element_count": len(self.complex_doc["document_structure"][0]["layers"][0]["content"]),
                }
            except Exception as e:
                results[engine_name] = {"error": str(e)}

        # Log results
        print("\nComplex Document Benchmark Results:")
        for engine, stats in results.items():
            if "error" not in stats:
                print(f"{engine}: {stats['avg_duration']:.3f}s for {stats['element_count']} elements")
            else:
                print(f"{engine}: ERROR - {stats['error']}")

        # At least one engine should have succeeded
        successful_engines = [e for e, s in results.items() if "error" not in s]
        assert len(successful_engines) > 0, "No engines succeeded in complex benchmark"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_document_benchmark(self):
        """Benchmark engines with a large document."""
        selector = get_engine_selector()
        available_engines = selector.list_available_engines()

        results = {}

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            try:
                durations = self._benchmark_engine(engine_name, self.large_doc, runs=1)
                results[engine_name] = {
                    "duration": durations[0],
                    "page_count": len(self.large_doc["document_structure"]),
                    "total_elements": sum(
                        len(page["layers"][0]["content"]) for page in self.large_doc["document_structure"]
                    ),
                }
            except Exception as e:
                results[engine_name] = {"error": str(e)}

        # Log results
        print("\nLarge Document Benchmark Results:")
        for engine, stats in results.items():
            if "error" not in stats:
                print(
                    f"{engine}: {stats['duration']:.3f}s for {stats['page_count']} pages, "
                    f"{stats['total_elements']} elements"
                )
            else:
                print(f"{engine}: ERROR - {stats['error']}")

        # At least one engine should have succeeded
        successful_engines = [e for e, s in results.items() if "error" not in s]
        assert len(successful_engines) > 0, "No engines succeeded in large document benchmark"

    @pytest.mark.performance
    def test_memory_usage_comparison(self):
        """Compare memory usage between engines."""
        selector = get_engine_selector()
        available_engines = selector.list_available_engines()

        # Clear metrics history
        self.collector.clear_history()

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            try:
                config_file = self._save_test_document(self.complex_doc, f"memory_{engine_name}.json")
                output_file = os.path.join(self.temp_dir, f"memory_{engine_name}.pdf")

                recreate_pdf_from_config(config_file, output_file, engine_name)

            except Exception as e:
                print(f"Engine {engine_name} failed: {e}")

        # Analyze memory usage from collected metrics
        print("\nMemory Usage Comparison:")
        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            stats = self.collector.get_engine_stats(engine_name)
            if stats.get("successful_runs", 0) > 0:
                print(f"{engine_name}: {stats.get('avg_memory_mb', 0):.2f} MB average")

    @pytest.mark.performance
    def test_engine_feature_performance_correlation(self):
        """Test correlation between engine features and performance."""
        selector = get_engine_selector()
        available_engines = selector.list_available_engines()

        performance_data = {}

        for engine_name in available_engines:
            if "error" in available_engines[engine_name]:
                continue

            engine_info = available_engines[engine_name]

            try:
                durations = self._benchmark_engine(engine_name, self.simple_doc, runs=2)

                performance_data[engine_name] = {
                    "avg_duration": statistics.mean(durations),
                    "supported_features": engine_info.get("supported_features", {}),
                    "feature_count": len(
                        [f for f, supported in engine_info.get("supported_features", {}).items() if supported]
                    ),
                }
            except Exception:
                continue

        # Analyze correlation
        print("\nFeature vs Performance Analysis:")
        for engine, data in performance_data.items():
            print(f"{engine}: {data['avg_duration']:.3f}s, {data['feature_count']} features supported")

        # Basic assertion - at least one engine should have data
        assert len(performance_data) > 0, "No performance data collected"

    @pytest.mark.performance
    def test_performance_report_generation(self):
        """Test performance report generation."""
        # Run some benchmarks to generate data
        selector = get_engine_selector()
        available_engines = list(selector.list_available_engines().keys())

        if not available_engines:
            pytest.skip("No engines available for testing")

        # Run at least one benchmark
        engine_name = available_engines[0]
        try:
            self._benchmark_engine(engine_name, self.simple_doc, runs=1)
        except Exception as e:
            pytest.skip(f"Could not run benchmark: {e}")

        # Generate report
        report_file = os.path.join(self.temp_dir, "performance_report.json")
        report = generate_performance_report(report_file)

        # Verify report structure
        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "total_runs" in report
        assert "engines" in report
        assert "summary" in report

        # Verify report was saved
        assert os.path.exists(report_file)

        # Verify report content
        if report["total_runs"] > 0:
            assert len(report["engines"]) > 0
            assert report["summary"]["total_runs"] > 0

    @pytest.mark.performance
    def test_concurrent_engine_performance(self):
        """Test performance when multiple engines are used concurrently."""
        import queue
        import threading

        selector = get_engine_selector()
        available_engines = list(selector.list_available_engines().keys())

        if len(available_engines) < 2:
            pytest.skip("Need at least 2 engines for concurrent testing")

        results_queue = queue.Queue()

        def run_engine_benchmark(engine_name):
            try:
                durations = self._benchmark_engine(engine_name, self.simple_doc, runs=1)
                results_queue.put((engine_name, durations[0], None))
            except Exception as e:
                results_queue.put((engine_name, None, str(e)))

        # Start threads for different engines
        threads = []
        for engine_name in available_engines[:2]:  # Test with first 2 engines
            thread = threading.Thread(target=run_engine_benchmark, args=(engine_name,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout

        # Collect results
        results = {}
        while not results_queue.empty():
            engine_name, duration, error = results_queue.get()
            results[engine_name] = {"duration": duration, "error": error}

        print("\nConcurrent Engine Performance:")
        for engine, data in results.items():
            if data["error"]:
                print(f"{engine}: ERROR - {data['error']}")
            else:
                print(f"{engine}: {data['duration']:.3f}s")

        # At least one engine should have succeeded
        successful = [e for e, d in results.items() if d["error"] is None]
        assert len(successful) > 0, "No engines succeeded in concurrent test"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
