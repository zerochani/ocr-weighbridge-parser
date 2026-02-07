"""Field extraction from cleaned OCR text.

This module implements pattern-based extraction of structured fields
from preprocessed OCR text using regex patterns defined in patterns.py.
"""

import logging
from typing import Dict, Any, Optional, List
import re

from .patterns import COMPILED_PATTERNS

logger = logging.getLogger(__name__)


class FieldExtractor:
    """
    Extracts structured fields from cleaned OCR text.

    Uses pattern matching to identify and extract key fields such as
    weights, dates, vehicle numbers, etc. from weighbridge receipts.
    """

    def __init__(self):
        """Initialize the field extractor."""
        self.patterns = COMPILED_PATTERNS
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract all fields from cleaned text.

        Args:
            text: Cleaned OCR text

        Returns:
            Dictionary of extracted fields with raw values
        """
        self.logger.debug("Starting field extraction")

        extracted = {
            'date': self._extract_date(text),
            'time': self._extract_time(text),
            'vehicle_number': self._extract_vehicle_number(text),
            'gross_weight': self._extract_weight(text, 'gross'),
            'tare_weight': self._extract_weight(text, 'tare'),
            'net_weight': self._extract_weight(text, 'net'),
            'customer_name': self._extract_customer(text),
            'product_name': self._extract_product(text),
            'transaction_type': self._extract_transaction_type(text),
            'measurement_id': self._extract_measurement_id(text),
            'location': self._extract_location(text),
            'raw_text': text,
        }

        # Log extraction results
        non_null_fields = {k: v for k, v in extracted.items() if v is not None and k != 'raw_text'}
        self.logger.info(f"Extracted {len(non_null_fields)} fields: {list(non_null_fields.keys())}")

        return extracted

    def _extract_with_patterns(self, text: str, pattern_key: str) -> Optional[str]:
        """
        Generic pattern-based extraction.

        Args:
            text: Text to search
            pattern_key: Key in COMPILED_PATTERNS dict

        Returns:
            First match found, or None
        """
        if pattern_key not in self.patterns:
            self.logger.warning(f"Pattern key '{pattern_key}' not found")
            return None

        for pattern in self.patterns[pattern_key]:
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                self.logger.debug(f"Extracted {pattern_key}: {value}")
                return value

        self.logger.debug(f"No match found for {pattern_key}")
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract measurement date."""
        return self._extract_with_patterns(text, 'date')

    def _extract_time(self, text: str) -> Optional[str]:
        """Extract measurement time."""
        return self._extract_with_patterns(text, 'time')

    def _extract_vehicle_number(self, text: str) -> Optional[str]:
        """Extract vehicle number."""
        return self._extract_with_patterns(text, 'vehicle')

    def _extract_weight(self, text: str, weight_type: str) -> Optional[str]:
        """
        Extract weight value.

        Args:
            text: Text to search
            weight_type: Type of weight ('gross', 'tare', or 'net')

        Returns:
            Weight value as string (with commas/spaces preserved)
        """
        pattern_key = f'weight_{weight_type}'

        if pattern_key not in self.patterns:
            self.logger.warning(f"Pattern key '{pattern_key}' not found")
            return None

        for pattern in self.patterns[pattern_key]:
            match = pattern.search(text)
            if match:
                # Handle patterns with multiple capture groups
                if len(match.groups()) > 1:
                    # Combine all captured groups
                    value = ''.join(g for g in match.groups() if g)
                else:
                    value = match.group(1)

                value = value.strip()
                self.logger.debug(f"Extracted {pattern_key}: {value}")
                return value

        self.logger.debug(f"No match found for {pattern_key}")
        return None

    def _extract_customer(self, text: str) -> Optional[str]:
        """Extract customer/company name."""
        return self._extract_with_patterns(text, 'customer')

    def _extract_product(self, text: str) -> Optional[str]:
        """Extract product name."""
        return self._extract_with_patterns(text, 'product')

    def _extract_transaction_type(self, text: str) -> Optional[str]:
        """Extract transaction type (입고/출고)."""
        return self._extract_with_patterns(text, 'transaction_type')

    def _extract_measurement_id(self, text: str) -> Optional[str]:
        """Extract measurement ID or count."""
        return self._extract_with_patterns(text, 'measurement_id')

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract weighbridge location/company."""
        return self._extract_with_patterns(text, 'location')

    def extract_all_weights(self, text: str) -> List[str]:
        """
        Extract all weight values from text (for debugging/validation).

        Args:
            text: Text to search

        Returns:
            List of all weight strings found
        """
        weights = []
        # Pattern to find any number followed by kg
        weight_pattern = re.compile(r'(\d{1,3}[,\s]?\d{3}|\d{1,6})\s*kg', re.IGNORECASE)

        for match in weight_pattern.finditer(text):
            weights.append(match.group(1))

        return weights
