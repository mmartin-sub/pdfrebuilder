from .scikit_image_validator import ScikitImageValidator
from .validation_strategy import ValidationResult


class ValidationManager:
    def __init__(self, primary_engine="scikit-image"):
        self.engines = {
            "scikit-image": ScikitImageValidator(),
        }
        self.primary_engine_name = primary_engine

    def validate(self, image1, image2, threshold) -> ValidationResult:
        try:
            # Attempt to use the primary engine
            primary_engine = self.engines[self.primary_engine_name]
            result = primary_engine.validate(image1, image2, threshold)
            if result.error_message:
                raise Exception(result.error_message)
            return result
        except Exception as e:
            # If it fails, log the error and use the fallback
            print(f"Engine '{self.primary_engine_name}' failed: {e}.")
            raise e
