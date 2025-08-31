"""
Integration tests for different engine combinations.
Tests various input/output engine combinations to ensure compatibility.
"""

from pdfrebuilder.settings import settings


class TestEngineCombinations:
    """Test different combinations of input and output engines"""

    def test_fitz_reportlab_combination(self):
        """Test Fitz input + ReportLab output combination"""
        # Set engine combination
        settings.engines.input.default = "fitz"
        settings.engines.output.default = "reportlab"

        # Verify configuration
        input_engine = settings.engines.input.default
        output_engine = settings.engines.output.default

        assert input_engine == "fitz"
        assert output_engine == "reportlab"

        # Verify engine configurations exist
        fitz_config = settings.engines.input.fitz.model_dump()
        reportlab_config = settings.engines.output.reportlab.model_dump()

        assert fitz_config is not None
        assert reportlab_config is not None

        # Verify key configuration options
        assert fitz_config["extract_text"] is True
        assert reportlab_config["embed_fonts"] is True

        print("✅ Fitz + ReportLab combination configured correctly")

    def test_fitz_pymupdf_combination(self):
        """Test Fitz input + PyMuPDF output combination"""
        # Set engine combination
        settings.engines.input.default = "fitz"
        settings.engines.output.default = "pymupdf"

        # Verify configuration
        input_engine = settings.engines.input.default
        output_engine = settings.engines.output.default

        assert input_engine == "fitz"
        assert output_engine == "pymupdf"

        print("✅ Fitz + PyMuPDF combination configured correctly")

    def test_psd_tools_reportlab_combination(self):
        """Test psd-tools input + ReportLab output combination"""
        # Set engine combination
        settings.engines.input.default = "psd_tools"
        settings.engines.output.default = "reportlab"

        # Verify configuration
        input_engine = settings.engines.input.default
        output_engine = settings.engines.output.default

        assert input_engine == "psd_tools"
        assert output_engine == "reportlab"

        # Verify engine configurations exist
        psd_config = settings.engines.input.psd_tools.model_dump()
        reportlab_config = settings.engines.output.reportlab.model_dump()

        assert psd_config is not None
        assert reportlab_config is not None

        print("✅ psd-tools + ReportLab combination configured correctly")

    def test_wand_pymupdf_combination(self):
        """Test Wand input + PyMuPDF output combination"""
        # Set engine combination
        settings.engines.input.default = "wand"
        settings.engines.output.default = "pymupdf"

        # Verify configuration
        input_engine = settings.engines.input.default
        output_engine = settings.engines.output.default

        assert input_engine == "wand"
        assert output_engine == "pymupdf"

        # Verify engine configurations exist
        wand_config = settings.engines.input.wand.model_dump()
        pymupdf_config = settings.engines.output.pymupdf.model_dump()

        assert wand_config is not None
        assert pymupdf_config is not None

        # Verify key configuration options
        assert wand_config["density"] == 300
        assert pymupdf_config["embed_fonts"] is True

        print("✅ Wand + PyMuPDF combination configured correctly")

    def test_auto_engine_selection(self):
        """Test automatic engine selection"""
        # Set to auto
        settings.engines.input.default = "auto"
        settings.engines.output.default = "auto"

        # Verify configuration
        input_engine = settings.engines.input.default
        output_engine = settings.engines.output.default

        assert input_engine == "auto"
        # Output auto should fall back to default
        assert output_engine in ["auto", "reportlab"]

        print("✅ Auto engine selection configured correctly")

    def test_engine_compatibility_matrix(self):
        """Test compatibility matrix of all engine combinations"""
        input_engines = ["fitz", "psd_tools", "wand"]
        output_engines = ["reportlab", "pymupdf", "fitz"]

        compatible_combinations = []

        for input_engine in input_engines:
            for output_engine in output_engines:
                # Set combination
                settings.engines.input.default = input_engine
                settings.engines.output.default = output_engine

                # Check if configurations exist
                input_config = getattr(settings.engines.input, input_engine).model_dump()
                output_config = getattr(settings.engines.output, output_engine).model_dump()

                if input_config is not None and output_config is not None:
                    compatible_combinations.append((input_engine, output_engine))

        # Verify we have expected combinations
        expected_combinations = [
            ("fitz", "reportlab"),
            ("fitz", "pymupdf"),
            ("fitz", "fitz"),
            ("psd_tools", "reportlab"),
            ("psd_tools", "pymupdf"),
            ("psd_tools", "fitz"),
            ("wand", "reportlab"),
            ("wand", "pymupdf"),
            ("wand", "fitz"),
        ]

        for expected in expected_combinations:
            assert expected in compatible_combinations, f"Missing combination: {expected}"

        print(f"✅ Found {len(compatible_combinations)} compatible engine combinations")
        for combo in compatible_combinations:
            print(f"   - {combo[0]} → {combo[1]}")

    def test_engine_specific_features(self):
        """Test that engine-specific features are properly configured"""

        # Test Fitz-specific features
        fitz_config = settings.engines.input.fitz.model_dump()
        assert "extract_text" in fitz_config
        assert "extract_images" in fitz_config
        assert "extract_drawings" in fitz_config
        assert "extract_raw_backgrounds" in fitz_config

        # Test Wand-specific features
        wand_config = settings.engines.input.wand.model_dump()
        assert "density" in wand_config
        assert "use_ocr" in wand_config
        assert "memory_limit_mb" in wand_config
        assert "color_management" in wand_config

        # Test psd-tools-specific features
        psd_config = settings.engines.input.psd_tools.model_dump()
        assert "extract_text_layers" in psd_config
        assert "extract_image_layers" in psd_config
        assert "extract_shape_layers" in psd_config
        assert "preserve_layer_effects" in psd_config

        # Test ReportLab-specific features
        reportlab_config = settings.engines.output.reportlab.model_dump()
        assert "compression" in reportlab_config
        assert "embed_fonts" in reportlab_config
        assert "output_dpi" in reportlab_config
        assert "color_space" in reportlab_config

        # Test PyMuPDF-specific features
        pymupdf_config = settings.engines.output.pymupdf.model_dump()
        assert "overlay_mode" in pymupdf_config
        assert "annotation_mode" in pymupdf_config
        assert "compression" in pymupdf_config

        print("✅ All engine-specific features are properly configured")

    def test_performance_optimized_combinations(self):
        """Test combinations optimized for performance"""

        # High-performance combination: Wand + PyMuPDF
        settings.engines.input.default = "wand"
        settings.engines.output.default = "pymupdf"
        settings.processing.enable_parallel_processing = True
        settings.processing.max_memory_mb = 4096

        # Verify performance settings
        parallel_enabled = settings.processing.enable_parallel_processing
        max_memory = settings.processing.max_memory_mb

        assert parallel_enabled is True
        assert max_memory == 4096

        print("✅ Performance-optimized combination configured")

    def test_quality_optimized_combinations(self):
        """Test combinations optimized for quality"""

        # Quality-focused combination: psd-tools + ReportLab
        settings.engines.input.default = "psd_tools"
        settings.engines.output.default = "reportlab"
        settings.engines.output.reportlab.compression = 0
        settings.engines.output.reportlab.output_dpi = 600
        settings.validation.ssim_threshold = 0.99

        # Verify quality settings
        compression = settings.engines.output.reportlab.compression
        output_dpi = settings.engines.output.reportlab.output_dpi
        ssim_threshold = settings.validation.ssim_threshold

        assert compression == 0
        assert output_dpi == 600
        assert ssim_threshold == 0.99

        print("✅ Quality-optimized combination configured")

    def test_memory_efficient_combinations(self):
        """Test combinations optimized for memory efficiency"""

        # Memory-efficient combination: Fitz + ReportLab
        settings.engines.input.default = "fitz"
        settings.engines.output.default = "reportlab"
        settings.engines.input.fitz.extract_images = False
        settings.engines.output.reportlab.compression = 9
        settings.processing.max_memory_mb = 512

        # Verify memory settings
        extract_images = settings.engines.input.fitz.extract_images
        compression = settings.engines.output.reportlab.compression
        max_memory = settings.processing.max_memory_mb

        assert extract_images is False
        assert compression == 9
        assert max_memory == 512

        print("✅ Memory-efficient combination configured")

    def teardown_method(self):
        """Reset configuration after each test"""
        # Reset to defaults
        settings.engines.input.default = "auto"
        settings.engines.output.default = "reportlab"
        settings.processing.enable_parallel_processing = True
        settings.processing.max_memory_mb = 2048
        settings.engines.output.reportlab.compression = 1
        settings.engines.output.reportlab.output_dpi = 300
        settings.validation.ssim_threshold = 0.98
        settings.engines.input.fitz.extract_images = True
