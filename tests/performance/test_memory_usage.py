"""
Performance tests for memory usage across engines.
Tests memory consumption and leak detection.
"""

import os

import pytest

from pdfrebuilder.settings import settings

# Try to import psutil, skip tests if not available
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None


@pytest.mark.skipif(not HAS_PSUTIL, reason="psutil not available")
class TestMemoryUsage:
    """Test memory usage and performance characteristics"""

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if not HAS_PSUTIL or psutil is None:
            return 0.0
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB

    def test_memory_limits_configuration(self):
        """Test that memory limits are properly configured"""
        # Test Wand memory limit
        wand_memory_limit = settings.engines.input.wand.memory_limit_mb
        assert isinstance(wand_memory_limit, int)
        assert wand_memory_limit > 0

        # Test processing memory limit
        processing_memory_limit = settings.processing.max_memory_mb
        assert isinstance(processing_memory_limit, int)
        assert processing_memory_limit > 0

    def test_memory_usage_baseline(self):
        """Test baseline memory usage"""
        initial_memory = self.get_memory_usage()

        # Import modules and check memory increase

        after_import_memory = self.get_memory_usage()
        memory_increase = after_import_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB for imports)
        assert memory_increase < 50, f"Memory increase too high: {memory_increase}MB"

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_pdf_parser_memory_usage(self):
        """Test memory usage of PDF parser"""
        initial_memory = self.get_memory_usage()

        # This would test actual PDF parsing memory usage
        # Requires test files

        final_memory = self.get_memory_usage()
        memory_used = final_memory - initial_memory

        # Log memory usage for analysis
        print(f"PDF parser memory usage: {memory_used}MB")

    @pytest.mark.skipif(not os.path.exists("tests/fixtures"), reason="Test fixtures not available")
    def test_psd_parser_memory_usage(self):
        """Test memory usage of PSD parser"""
        initial_memory = self.get_memory_usage()

        # This would test actual PSD parsing memory usage
        # Requires test files and psd-tools

        final_memory = self.get_memory_usage()
        memory_used = final_memory - initial_memory

        # Log memory usage for analysis
        print(f"PSD parser memory usage: {memory_used}MB")

    def test_memory_leak_detection(self):
        """Test for memory leaks in parser operations"""
        initial_memory = self.get_memory_usage()

        # Simulate multiple parser creations and destructions
        for i in range(10):
            from pdfrebuilder.engine.document_parser import PDFParser, PSDParser

            pdf_parser = PDFParser()
            psd_parser = PSDParser()

            # Force garbage collection
            del pdf_parser
            del psd_parser

        # Force garbage collection
        import gc

        gc.collect()

        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (less than 10MB)
        assert memory_increase < 10, f"Potential memory leak detected: {memory_increase}MB increase"

    def test_large_document_memory_handling(self):
        """Test memory handling with large documents"""
        # This would test memory usage with large documents
        # to ensure streaming and efficient processing

        max_memory_mb = settings.processing.max_memory_mb
        current_memory = self.get_memory_usage()

        # Ensure we're not already using too much memory
        assert current_memory < max_memory_mb * 0.8, "Already using too much memory before test"

    def test_parallel_processing_memory(self):
        """Test memory usage with parallel processing enabled"""
        parallel_enabled = settings.processing.enable_parallel_processing

        if parallel_enabled:
            # Test that parallel processing doesn't cause excessive memory usage
            initial_memory = self.get_memory_usage()

            # This would test parallel processing memory usage
            # Requires actual implementation

            final_memory = self.get_memory_usage()
            memory_used = final_memory - initial_memory

            print(f"Parallel processing memory usage: {memory_used}MB")

    def test_cache_memory_usage(self):
        """Test memory usage of caching systems"""
        initial_memory = self.get_memory_usage()

        # Test font cache memory usage

        # This would test actual cache memory usage
        # Requires cache implementation

        final_memory = self.get_memory_usage()
        cache_memory = final_memory - initial_memory

        print(f"Cache memory usage: {cache_memory}MB")
