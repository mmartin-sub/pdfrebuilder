
from pydantic import BaseModel, Field


class WandConfig(BaseModel):
    density: int = 300
    use_ocr: bool = False
    tesseract_lang: str = "eng"
    image_format: str = "png"
    color_management: bool = True
    memory_limit_mb: int = 1024
    enhance_images: bool = False
    auto_level: bool = False
    auto_gamma: bool = False
    sharpen: bool = False
    noise_reduction: bool = False
    normalize_colors: bool = False
    enhance_contrast: bool = False
    strip_metadata: bool = False
    jpeg_quality: int = 90
    png_compression: int = 95
    webp_quality: int = 85

class PsdToolsConfig(BaseModel):
    extract_text_layers: bool = True
    extract_image_layers: bool = True
    extract_shape_layers: bool = True
    preserve_layer_effects: bool = True

class FitzConfig(BaseModel):
    extract_text: bool = True
    extract_images: bool = True
    extract_drawings: bool = True
    extract_raw_backgrounds: bool = False

class InputEnginesConfig(BaseModel):
    default: str = "auto"
    wand: WandConfig = Field(default_factory=WandConfig)
    psd_tools: PsdToolsConfig = Field(default_factory=PsdToolsConfig)
    fitz: FitzConfig = Field(default_factory=FitzConfig)

class ReportLabConfig(BaseModel):
    compression: int = 1
    page_mode: str = "portrait"
    embed_fonts: bool = True
    color_space: str = "RGB"
    output_dpi: int = 300

class PyMuPDFConfig(BaseModel):
    overlay_mode: bool = False
    annotation_mode: str = "ignore"
    compression: str = "flate"
    embed_fonts: bool = True

class OutputEnginesConfig(BaseModel):
    default: str = "reportlab"
    reportlab: ReportLabConfig = Field(default_factory=ReportLabConfig)
    pymupdf: PyMuPDFConfig = Field(default_factory=PyMuPDFConfig)
    fitz: PyMuPDFConfig = Field(default_factory=PyMuPDFConfig) # fitz is an alias for pymupdf here

class EnginesConfig(BaseModel):
    input: InputEnginesConfig = Field(default_factory=InputEnginesConfig)
    output: OutputEnginesConfig = Field(default_factory=OutputEnginesConfig)

class FontManagementConfig(BaseModel):
    font_directory: str = "fonts"
    downloaded_fonts_dir: str = "fonts/auto"
    manual_fonts_dir: str = "fonts/manual"
    enable_google_fonts: bool = True
    fallback_font: str = "Noto Sans"
    cache_file: str = "fonts/font_cache.json"
    default_font: str = "Noto Sans"

class ValidationConfig(BaseModel):
    ssim_threshold: float = 0.98
    rendering_dpi: int = 300
    comparison_engine: str = "opencv"
    generate_diff_images: bool = True
    fail_on_font_substitution: bool = False
    visual_diff_threshold: int = 5
    ssim_score_display_digits: int = 3

class LoggingConfig(BaseModel):
    show_engine_versions: bool = False
    show_load_paths: bool = False
    show_python_executable: bool = False
    engine_selection_level: str = "INFO"
    engine_fallback_level: str = "WARNING"
    engine_error_level: str = "ERROR"
    debug_logs_dir: str = "tests/output/debug_logs"

class DebugConfig(BaseModel):
    font_name: str = "cour"
    fontsize: int = 8
    line_height: float = 1.2
    max_height_ratio: float = 0.8
    text_wrap_width: int = 100
    text_padding: int = 10
    font: str = "Lato-Regular"
    overlay_width_ratio: float = 0.33
    overlay_bg_color: list[float] = [0.1, 0.1, 0.1]
    overlay_text_color: list[float] = [0.95, 0.95, 0.95]
    text_background: bool = True
    number_display_digits: int = 3
    overlay_margin: int = 10
    overlay_width: int = 450
    overlay_height: int = 180

class ProcessingConfig(BaseModel):
    space_density_threshold: float = 0.3
    max_memory_mb: int = 2048
    enable_parallel_processing: bool = True
    temp_dir: str = "output/temp"

class TestFrameworkConfig(BaseModel):
    cleanup_after_tests: bool = True
    preserve_test_outputs: bool = False
    generate_test_reports: bool = True
    max_test_output_size_mb: int = 100
    test_timeout_seconds: int = 300
    font_test_timeout_seconds: int = 60
    enable_performance_tracking: bool = True
    enable_memory_monitoring: bool = True
    test_data_retention_days: int = 7
    test_output_dir: str = "tests/output"
    test_temp_dir: str = "tests/temp"
    test_fonts_dir: str = "tests/output/fonts"
    test_reports_dir: str = "tests/output/reports"

class TestFixturesConfig(BaseModel):
    auto_cleanup: bool = True
    preserve_on_failure: bool = True
    create_debug_outputs: bool = True
    mock_external_dependencies: bool = True
    use_temporary_directories: bool = True
    font_fixture_timeout: int = 30

class TestSamplesConfig(BaseModel):
    sample_pdfs_dir: str = "tests/sample/pdfs"
    sample_fonts_dir: str = "tests/sample/fonts"
    sample_configs_dir: str = "tests/sample/configs"
    sample_images_dir: str = "tests/sample/images"
    create_missing_samples: bool = True
    validate_sample_integrity: bool = True
