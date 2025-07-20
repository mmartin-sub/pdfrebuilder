from .legacy_validator import LegacyValidator
from .scikit_image_validator import ScikitImageValidator
from .validation_strategy import ValidationResult


class ValidationManager:
    def __init__(self, primary_engine="scikit-image"):
        self.engines = {
            "scikit-image": ScikitImageValidator(),
            "legacy": LegacyValidator(),
        }
        self.primary_engine_name = primary_engine
        self.fallback_engine_name = "legacy" if primary_engine == "scikit-image" else "scikit-image"

    def validate_with_failover(self, image1, image2, threshold) -> ValidationResult:
        try:
            # Attempt to use the primary engine
            primary_engine = self.engines[self.primary_engine_name]
            result = primary_engine.validate(image1, image2, threshold)
            if result.error_message:
                raise Exception(result.error_message)
            return result
        except Exception as e:
            # If it fails, log the error and use the fallback
            print(
                f"Primary engine '{self.primary_engine_name}' failed: {e}. Falling back to '{self.fallback_engine_name}'."
            )
            fallback_engine = self.engines[self.fallback_engine_name]
            return fallback_engine.validate(image1, image2, threshold)
