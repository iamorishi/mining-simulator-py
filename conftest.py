import logging
import pytest


@pytest.fixture(autouse=True, scope="session")
def setup_logging():
    """Setup logging for the test session"""
    # Implement logging to file here if needed. For now, just log to console
    logging.info("Logging initialized for test session.")
