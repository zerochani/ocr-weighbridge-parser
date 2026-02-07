"""Data normalization utilities.

This module handles normalization of extracted raw data into standardized
formats suitable for the data model.
"""

import re
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalizes extracted raw data into standardized formats.

    Handles:
    - Numeric normalization (removing commas, spaces, converting to Decimal)
    - Date/time normalization
    - String cleaning and standardization
    """

    def __init__(self):
        """Initialize the data normalizer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def normalize(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all extracted fields.

        Args:
            extracted_data: Dictionary of raw extracted fields

        Returns:
            Dictionary of normalized fields
        """
        self.logger.debug("Starting data normalization")

        normalized = {
            'gross_weight_kg': self.normalize_weight(extracted_data.get('gross_weight')),
            'tare_weight_kg': self.normalize_weight(extracted_data.get('tare_weight')),
            'net_weight_kg': self.normalize_weight(extracted_data.get('net_weight')),
            'vehicle_number': self.normalize_vehicle_number(extracted_data.get('vehicle_number')),
            'measurement_date': self.normalize_date(extracted_data.get('date')),
            'measurement_time': self.normalize_time(extracted_data.get('time')),
            'customer_name': self.normalize_string(extracted_data.get('customer_name')),
            'product_name': self.normalize_string(extracted_data.get('product_name')),
            'transaction_type': self.normalize_string(extracted_data.get('transaction_type')),
            'measurement_id': self.normalize_string(extracted_data.get('measurement_id')),
            'location': self.normalize_string(extracted_data.get('location')),
            'raw_text': extracted_data.get('raw_text', ''),
        }

        # Log normalization results
        non_null_count = sum(1 for v in normalized.values() if v is not None)
        self.logger.info(f"Normalized {non_null_count} non-null fields")

        return normalized

    def normalize_weight(self, weight_str: Optional[str]) -> Optional[Decimal]:
        """
        Normalize weight string to Decimal.

        Handles:
        - Comma removal (12,480 -> 12480)
        - Space removal (13 460 -> 13460)
        - Conversion to Decimal for precision

        Args:
            weight_str: Raw weight string

        Returns:
            Normalized weight as Decimal, or None if invalid
        """
        if not weight_str:
            return None

        try:
            # Remove commas and spaces
            cleaned = re.sub(r'[,\s]', '', weight_str)

            # Convert to Decimal for precision
            weight = Decimal(cleaned)

            if weight < 0:
                self.logger.warning(f"Negative weight detected: {weight}")
                return None

            self.logger.debug(f"Normalized weight: {weight_str} -> {weight}")
            return weight

        except (InvalidOperation, ValueError) as e:
            self.logger.error(f"Failed to normalize weight '{weight_str}': {e}")
            return None

    def normalize_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Normalize date string to datetime object.

        Handles multiple date formats:
        - YYYY-MM-DD
        - YYYY/MM/DD
        - YYYY.MM.DD
        - YYYY년 MM월 DD일

        Args:
            date_str: Raw date string

        Returns:
            Normalized datetime object, or None if invalid
        """
        if not date_str:
            return None

        # List of date format patterns to try
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y.%m.%d',
            '%Y-%m-%d-%H%M%S',  # With timestamp suffix
        ]

        # Handle Korean format (YYYY년 MM월 DD일)
        korean_date_pattern = r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'
        korean_match = re.search(korean_date_pattern, date_str)
        if korean_match:
            year, month, day = korean_match.groups()
            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Clean the string - extract just the date part
        date_str = re.sub(r'-\d{5,6}$', '', date_str)  # Remove trailing timestamp like -00004

        # Try each format
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                self.logger.debug(f"Normalized date: {date_str} -> {dt}")
                return dt
            except ValueError:
                continue

        self.logger.warning(f"Could not parse date: {date_str}")
        return None

    def normalize_time(self, time_str: Optional[str]) -> Optional[str]:
        """
        Normalize time string to standard format.

        Handles:
        - HH:MM:SS
        - HH:MM
        - HH시 MM분

        Args:
            time_str: Raw time string

        Returns:
            Normalized time string in HH:MM:SS or HH:MM format
        """
        if not time_str:
            return None

        # Handle Korean format (HH시 MM분)
        korean_time_pattern = r'(\d{1,2})시\s*(\d{1,2})분'
        korean_match = re.search(korean_time_pattern, time_str)
        if korean_match:
            hour, minute = korean_match.groups()
            return f"{hour.zfill(2)}:{minute.zfill(2)}"

        # Handle standard formats
        time_pattern = r'(\d{1,2}):(\d{2})(?::(\d{2}))?'
        match = re.search(time_pattern, time_str)
        if match:
            hour, minute, second = match.groups()
            if second:
                return f"{hour.zfill(2)}:{minute}:{second}"
            else:
                return f"{hour.zfill(2)}:{minute}"

        self.logger.warning(f"Could not parse time: {time_str}")
        return None

    def normalize_vehicle_number(self, vehicle_str: Optional[str]) -> Optional[str]:
        """
        Normalize vehicle number.

        Removes extra spaces and standardizes format.

        Args:
            vehicle_str: Raw vehicle number

        Returns:
            Normalized vehicle number
        """
        if not vehicle_str:
            return None

        # Remove extra whitespace
        normalized = re.sub(r'\s+', '', vehicle_str.strip())

        self.logger.debug(f"Normalized vehicle number: {vehicle_str} -> {normalized}")
        return normalized

    def normalize_string(self, value: Optional[str]) -> Optional[str]:
        """
        Normalize generic string field.

        Removes extra whitespace and standardizes.

        Args:
            value: Raw string value

        Returns:
            Normalized string
        """
        if not value:
            return None

        # Remove extra whitespace but preserve single spaces
        normalized = re.sub(r'\s+', ' ', value.strip())

        return normalized if normalized else None

    def calculate_net_weight(
        self,
        gross_weight: Optional[Decimal],
        tare_weight: Optional[Decimal]
    ) -> Optional[Decimal]:
        """
        Calculate net weight from gross and tare weights.

        Args:
            gross_weight: Gross weight
            tare_weight: Tare weight

        Returns:
            Calculated net weight (gross - tare)
        """
        if gross_weight is None or tare_weight is None:
            return None

        try:
            net = gross_weight - tare_weight
            self.logger.debug(f"Calculated net weight: {gross_weight} - {tare_weight} = {net}")
            return net
        except Exception as e:
            self.logger.error(f"Failed to calculate net weight: {e}")
            return None
