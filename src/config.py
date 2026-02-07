"""Configuration settings for the OCR parser.

This module centralizes configuration values and settings
for easy maintenance and extension.
"""

from pathlib import Path
from decimal import Decimal


class Config:
    """Application configuration."""

    # Application info
    APP_NAME = "OCR Weighbridge Parser"
    VERSION = "1.0.0"

    # Logging
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Validation settings
    WEIGHT_TOLERANCE_KG = Decimal('1.0')  # Tolerance for weight calculations
    MAX_REASONABLE_WEIGHT_KG = Decimal('100000')  # 100 tons
    MIN_REASONABLE_WEIGHT_KG = Decimal('1')  # 1 kg

    # Output settings
    OUTPUT_DIR = Path("output")
    JSON_INDENT = 2

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    TESTS_DIR = PROJECT_ROOT / "tests"
    FIXTURES_DIR = TESTS_DIR / "fixtures"

    @classmethod
    def get_output_dir(cls) -> Path:
        """Get output directory, creating if it doesn't exist."""
        output_dir = cls.PROJECT_ROOT / cls.OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
