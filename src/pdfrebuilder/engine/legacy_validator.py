import cv2
from skimage.metrics import structural_similarity as compare_ssim

from .validation_strategy import ValidationResult, Validator


class LegacyValidator(Validator):
    def validate(self, image_path1: str, image_path2: str, threshold: float) -> ValidationResult:
        try:
            # Load images
            img1 = cv2.imread(image_path1)
            img2 = cv2.imread(image_path2)

            # Check if images were loaded
            if img1 is None:
                raise ValueError(f"Failed to load image: {image_path1}")
            if img2 is None:
                raise ValueError(f"Failed to load image: {image_path2}")

            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Resize if dimensions don't match
            if gray1.shape != gray2.shape:
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))

            # Calculate SSIM using the legacy method
            score, _ = compare_ssim(gray1, gray2, full=True)

            return ValidationResult(passed=score >= threshold, score=score, engine_used="legacy")
        except Exception as e:
            return ValidationResult(passed=False, score=0.0, engine_used="legacy", error_message=str(e))
