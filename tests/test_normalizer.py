"""Tests for data normalization module."""

import pytest
from decimal import Decimal
from datetime import datetime
from src.normalization.normalizer import DataNormalizer


class TestDataNormalizer:
    """Test suite for DataNormalizer class."""

    @pytest.fixture
    def normalizer(self):
        """Fixture to provide DataNormalizer instance."""
        return DataNormalizer()

    def test_normalize_weight_with_comma(self, normalizer):
        """Test weight normalization with comma separator."""
        test_cases = [
            ("12,480", Decimal("12480")),
            ("7,470", Decimal("7470")),
            ("5,010", Decimal("5010")),
            ("1,320", Decimal("1320")),
        ]

        for input_str, expected in test_cases:
            result = normalizer.normalize_weight(input_str)
            assert result == expected

    def test_normalize_weight_with_spaces(self, normalizer):
        """Test weight normalization with space separators."""
        test_cases = [
            ("13 460", Decimal("13460")),
            ("7 560", Decimal("7560")),
            ("5 900", Decimal("5900")),
        ]

        for input_str, expected in test_cases:
            result = normalizer.normalize_weight(input_str)
            assert result == expected

    def test_normalize_weight_plain_number(self, normalizer):
        """Test weight normalization with plain numbers."""
        test_cases = [
            ("12480", Decimal("12480")),
            ("130", Decimal("130")),
        ]

        for input_str, expected in test_cases:
            result = normalizer.normalize_weight(input_str)
            assert result == expected

    def test_normalize_weight_invalid(self, normalizer):
        """Test weight normalization with invalid input."""
        invalid_inputs = [None, "", "abc", "12,abc"]

        for invalid_input in invalid_inputs:
            result = normalizer.normalize_weight(invalid_input)
            assert result is None

    def test_normalize_date_standard_format(self, normalizer):
        """Test date normalization with standard formats."""
        test_cases = [
            "2026-02-02",
            "2025-12-01",
            "2026/02/01",
        ]

        for date_str in test_cases:
            result = normalizer.normalize_date(date_str)
            assert result is not None
            assert isinstance(result, datetime)

    def test_normalize_date_with_suffix(self, normalizer):
        """Test date normalization with trailing suffixes."""
        date_str = "2026-02-02-00004"
        result = normalizer.normalize_date(date_str)

        assert result is not None
        assert result.year == 2026
        assert result.month == 2
        assert result.day == 2

    def test_normalize_time_formats(self, normalizer):
        """Test time normalization with various formats."""
        test_cases = [
            ("05:26:18", "05:26:18"),
            ("02:07", "02:07"),
            ("11시 33분", "11:33"),
        ]

        for input_str, expected in test_cases:
            result = normalizer.normalize_time(input_str)
            assert result is not None
            assert expected in result

    def test_normalize_vehicle_number(self, normalizer):
        """Test vehicle number normalization."""
        test_cases = [
            ("80구8713", "80구8713"),
            ("  8713  ", "8713"),
            ("5405", "5405"),
        ]

        for input_str, expected in test_cases:
            result = normalizer.normalize_vehicle_number(input_str)
            assert result == expected

    def test_calculate_net_weight(self, normalizer):
        """Test net weight calculation."""
        gross = Decimal("12480")
        tare = Decimal("7470")
        expected_net = Decimal("5010")

        result = normalizer.calculate_net_weight(gross, tare)

        assert result == expected_net

    def test_calculate_net_weight_missing_values(self, normalizer):
        """Test net weight calculation with missing values."""
        assert normalizer.calculate_net_weight(None, Decimal("100")) is None
        assert normalizer.calculate_net_weight(Decimal("100"), None) is None

    def test_normalize_full_data(self, normalizer):
        """Test normalization of complete extracted data."""
        extracted = {
            'gross_weight': '12,480',
            'tare_weight': '7,470',
            'net_weight': '5,010',
            'vehicle_number': '  8713  ',
            'date': '2026-02-02',
            'time': '05:26:18',
            'customer_name': '동우바이오',
            'raw_text': 'test'
        }

        result = normalizer.normalize(extracted)

        assert result['gross_weight_kg'] == Decimal("12480")
        assert result['tare_weight_kg'] == Decimal("7470")
        assert result['net_weight_kg'] == Decimal("5010")
        assert result['vehicle_number'] == "8713"
        assert isinstance(result['measurement_date'], datetime)
        assert result['measurement_time'] == "05:26:18"
        assert result['customer_name'] == "동우바이오"
