from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .config_models import (
    DebugConfig,
    EnginesConfig,
    FontManagementConfig,
    LoggingConfig,
    ProcessingConfig,
    TestFixturesConfig,
    TestFrameworkConfig,
    TestSamplesConfig,
    ValidationConfig,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env_id: str = "Dev"
    engines: EnginesConfig = Field(default_factory=EnginesConfig)
    font_management: FontManagementConfig = Field(default_factory=FontManagementConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    debug: DebugConfig = Field(default_factory=DebugConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    test_framework: TestFrameworkConfig = Field(default_factory=TestFrameworkConfig)
    test_fixtures: TestFixturesConfig = Field(default_factory=TestFixturesConfig)
    test_samples: TestSamplesConfig = Field(default_factory=TestSamplesConfig)

    # Core paths and files
    image_dir: str = "output/images"
    config_path: str = "./layout_config.json"
    override_config_path: str = "./override_config.json5"
    rebuilt_pdf: str = "output/rebuilt.pdf"
    diff_image: str = "output/visual_diff.png"
    debug_pdf: str = "output/debug_layers.pdf"

    # Legacy compatibility
    fonts_dir: str = "fonts"
    downloaded_fonts_dir: str = "fonts/auto"
    manual_fonts_dir: str = "fonts/manual"
    default_font: str = "Noto Sans"
    visual_diff_threshold: int = 5


settings = Settings()

# The 14 standard PDF fonts are guaranteed to be available with any PDF viewer/engine.
# They do not need to be embedded in the PDF file.
STANDARD_PDF_FONTS = [
    "helv",
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-Oblique",
    "Helvetica-BoldOblique",
    "cour",
    "Courier",
    "Courier-Bold",
    "Courier-Oblique",
    "Courier-BoldOblique",
    "tiro",
    "Times-Roman",
    "Times-Bold",
    "Times-Italic",
    "Times-BoldItalic",
    "Symbol",
    "ZapfDingbats",
]
