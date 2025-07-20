from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ValidationConfig:
    ssim_threshold: float = 0.99
    rendering_dpi: int = 300
    generate_diff_images: bool = True
    pixel_threshold: int = 5


@dataclass
class ValidationResult:
    passed: bool
    score: float
    engine_used: str
    error_message: str | None = None


class Validator(ABC):
    @abstractmethod
    def validate(self, image_path1: str, image_path2: str, threshold: float) -> ValidationResult:
        """Compares two images and returns a standardized result."""
