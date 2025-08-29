"""
Performance tests for processing speed across engines.
Tests processing time and throughput benchmarks.
"""

import os
import time
from typing import Any

import pytest

from pdfrebuilder.settings import settings


class TestProcessingSpeed:
    """Test processing speed and performance benchmarks"""

    def measure_execution_time(self, func, *args, **kwargs) -> tuple[float, Any]:
        """Measure execution time of a function in seconds"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time, result

    def test_parser_initialization_speed(self):
        """Test speed of parser initialization"""
        # Test PDF parser initialization
        start_time = time.time()
        from pdfrebuilder.engine.document_parser import PDFParser

        pdf_parser = PDFParser()
        pdf_init_time = time.time() - start_time

        # Test PSD parser initialization
        start_time = time.time()
        from pdfrebuilder.engine.document_parser import PSDParser

        psd_parser = PSDParser()
        psd_init_time = time.time() - start_time

        # Initialization should be fast (less than 1 second)
        assert pdf_init_time < 1.0, f"PDF parser initialization too slow: {pdf_init_time}s"
        assert psd_init_time < 1.0, f"PSD parser initialization too slow: {psd_init_time}s"

        print(f"PDF parser init time: {pdf_init_time:.3f}s")
        print(f"PSD parser init time: {psd_init_time:.3f}s")

    def test_configuration_access_speed(self):
        """Test speed of configuration access"""
        # Test multiple configuration accesses
        access_functions = [
            lambda: settings.engines.input.wand.density,
            lambda: settings.engines.output.reportlab.compression,
            lambda: settings.font_management.font_directory,
            lambda: settings.validation.ssim_threshold,
            lambda: settings.debug.font_name,
        ]

        start_time = time.time()
        for _ in range(1000):  # Test 1000 accesses
            for func in access_functions:
                func()
        total_time = time.time() - start_time

        # Should be very fast (less than 0.1 seconds for 5000 accesses)
        assert total_time < 0.1, f"Configuration access too slow: {total_time}s for 5000 accesses"

        avg_time_per_access = total_time / 5000
        print(f"Average config access time: {avg_time_per_access * 1000:.3f}ms")

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_pdf_parsing_speed(self):
        """Test PDF parsing speed"""
        # This would test actual PDF parsing speed
        # Requires test files

        # Example structure:
        # execution_time, result = self.measure_execution_time(
        #     parse_document, "tests/fixtures/sample.pdf"
        # )
        #
        # # PDF parsing should complete within reasonable time
        # assert execution_time < 30.0, f"PDF parsing too slow: {execution_time}s"
        # print(f"PDF parsing time: {execution_time:.3f}s")

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_psd_parsing_speed(self):
        """Test PSD parsing speed"""
        # This would test actual PSD parsing speed
        # Requires test files and psd-tools

    def test_asset_manifest_performance(self):
        """Test performance of asset manifest operations"""
        from pdfrebuilder.engine.document_parser import AssetManifest

        # Test creating and populating manifest
        start_time = time.time()
        manifest = AssetManifest()

        # Add many assets to test performance
        for i in range(1000):
            manifest.add_image(f"image_{i}.png", f"original_{i}.png", {"id": i})
            manifest.add_font(f"font_{i}.ttf", f"Font{i}", {"weight": "normal"})
            manifest.add_asset(f"asset_{i}.svg", "vector", {"type": "icon"})

        # Convert to dict
        manifest_dict = manifest.to_dict()

        total_time = time.time() - start_time

        # Should be reasonably fast (less than 1 second for 3000 assets)
        assert total_time < 1.0, f"Asset manifest operations too slow: {total_time}s"

        # Verify all assets were added
        assert len(manifest_dict["images"]) == 1000
        assert len(manifest_dict["fonts"]) == 1000
        assert len(manifest_dict["other_assets"]) == 1000

        print(f"Asset manifest time for 3000 assets: {total_time:.3f}s")

    def test_parallel_processing_speedup(self):
        """Test that parallel processing provides speedup"""
        parallel_enabled = settings.processing.enable_parallel_processing

        if not parallel_enabled:
            pytest.skip("Parallel processing not enabled")

        # This would test actual parallel processing speedup
        # Requires implementation of parallel processing

        print("Parallel processing speedup test would go here")

    def test_cache_performance_impact(self):
        """Test performance impact of caching"""
        # This would test the performance difference with and without caching
        # Requires cache implementation

        print("Cache performance impact test would go here")

    def test_memory_vs_speed_tradeoffs(self):
        """Test memory vs speed configuration tradeoffs"""
        # Test different memory limit configurations and their impact on speed
        memory_limits = [512, 1024, 2048]  # MB

        for limit in memory_limits:
            # This would test processing speed with different memory limits
            # Requires actual document processing
            print(f"Testing with memory limit: {limit}MB")

    def test_engine_selection_overhead(self):
        """Test overhead of engine selection process"""
        from pdfrebuilder.engine.document_parser import get_parser_for_file

        test_files = [
            "test.pdf",
            "test.psd",
            "test.docx",  # unsupported
            "test.jpg",  # unsupported
        ]

        start_time = time.time()
        for _ in range(1000):  # Test 1000 selections
            for file_path in test_files:
                get_parser_for_file(file_path)
        total_time = time.time() - start_time

        # Engine selection should be very fast
        assert total_time < 0.5, f"Engine selection too slow: {total_time}s for 4000 selections"

        avg_time = total_time / 4000
        print(f"Average engine selection time: {avg_time * 1000:.3f}ms")
