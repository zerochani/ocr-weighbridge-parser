"""Tests for data validation module."""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from src.validation.validator import DataValidator


class TestDataValidator:
    """Test suite for DataValidator class."""

    @pytest.fixture
    def validator(self):
        """Fixture to provide DataValidator instance."""
        return DataValidator(tolerance_kg=Decimal('1.0'))

    def test_validate_complete_valid_data(self, validator):
        """Test validation with complete and valid data."""
        data = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
            'vehicle_number': '8713',
            'measurement_date': datetime(2026, 2, 2),
        }

        result = validator.validate(data)

        assert result.is_valid is True
        assert result.weight_consistency is True
        assert len(result.errors) == 0
        assert result.computed_net_weight == Decimal('5010')

    def test_validate_weight_consistency_violation(self, validator):
        """Test validation when weight math doesn't match."""
        data = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('4000'),  # Wrong!
            'vehicle_number': '8713',
        }

        result = validator.validate(data)

        assert result.weight_consistency is False
        assert len(result.warnings) > 0
        assert any('discrepancy' in w.lower() for w in result.warnings)

    def test_validate_gross_less_than_tare(self, validator):
        """Test validation when gross < tare (impossible)."""
        data = {
            'gross_weight_kg': Decimal('7470'),
            'tare_weight_kg': Decimal('12480'),  # Tare > Gross (wrong!)
            'net_weight_kg': Decimal('-5010'),
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any('must be greater than' in e.lower() for e in result.errors)

    def test_validate_missing_critical_fields(self, validator):
        """Test validation with missing critical fields."""
        data = {
            'gross_weight_kg': Decimal('12480'),
            # Missing tare and net weights
            'vehicle_number': '8713',
        }

        result = validator.validate(data)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any('missing critical fields' in e.lower() for e in result.errors)

    def test_validate_missing_important_fields(self, validator):
        """Test validation with missing important but non-critical fields."""
        data = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
            # Missing vehicle_number and date
        }

        result = validator.validate(data)

        assert result.is_valid is True  # Still valid
        assert len(result.warnings) > 0
        assert any('missing important fields' in w.lower() for w in result.warnings)

    def test_validate_future_date(self, validator):
        """Test validation when date is in the future."""
        future_date = datetime.now() + timedelta(days=30)

        data = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
            'measurement_date': future_date,
        }

        result = validator.validate(data)

        assert len(result.warnings) > 0
        assert any('future' in w.lower() for w in result.warnings)

    def test_validate_unreasonable_weight(self, validator):
        """Test validation with unreasonably high/low weights."""
        data = {
            'gross_weight_kg': Decimal('150000'),  # Too high
            'tare_weight_kg': Decimal('140000'),
            'net_weight_kg': Decimal('10000'),
        }

        result = validator.validate(data)

        assert len(result.warnings) > 0
        assert any('reasonable maximum' in w.lower() for w in result.warnings)

    def test_validate_completeness_score(self, validator):
        """Test completeness score calculation."""
        # All fields present
        complete_data = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
            'vehicle_number': '8713',
            'measurement_date': datetime(2026, 2, 2),
            'customer_name': 'Test Company',
            'product_name': 'Test Product',
            'transaction_type': '입고',
            'measurement_id': '0001',
            'location': 'Test Location',
        }

        score = validator.validate_completeness(complete_data)
        assert score == 1.0  # 100% complete

        # Partial data
        partial_data = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
        }

        score = validator.validate_completeness(partial_data)
        assert 0.0 < score < 1.0  # Partially complete

    def test_validate_vehicle_number_length(self, validator):
        """Test validation of vehicle number length."""
        # Too short
        data_short = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
            'vehicle_number': '1',  # Too short
        }

        result = validator.validate(data_short)
        assert any('unusually short' in w.lower() for w in result.warnings)

        # Too long
        data_long = {
            'gross_weight_kg': Decimal('12480'),
            'tare_weight_kg': Decimal('7470'),
            'net_weight_kg': Decimal('5010'),
            'vehicle_number': '1' * 25,  # Too long
        }

        result = validator.validate(data_long)
        assert any('unusually long' in w.lower() for w in result.warnings)
