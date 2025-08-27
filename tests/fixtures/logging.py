import logging

import pytest


@pytest.fixture
def suppress_logging(caplog):
    """A pytest fixture to suppress logging output."""

    class SuppressLogging:
        def __init__(self, logger_name, level=logging.CRITICAL):
            self.logger = logging.getLogger(logger_name)
            self.level = level
            self.original_level = self.logger.level

        def __enter__(self):
            self.logger.setLevel(self.level)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.logger.setLevel(self.original_level)

    return SuppressLogging
