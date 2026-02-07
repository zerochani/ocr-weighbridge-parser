"""Tests for field extraction module."""

import pytest
from src.extraction.extractor import FieldExtractor


class TestFieldExtractor:
    """Test suite for FieldExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Fixture to provide FieldExtractor instance."""
        return FieldExtractor()

    def test_extract_date(self, extractor):
        """Test date extraction."""
        test_cases = [
            ("계량일자: 2026-02-02", "2026-02-02"),
            ("날짜: 2025-12-01", "2025-12-01"),
            ("일시 2026-02-01", "2026-02-01"),
        ]

        for text, expected in test_cases:
            result = extractor._extract_date(text)
            assert result is not None
            assert expected in result

    def test_extract_vehicle_number(self, extractor):
        """Test vehicle number extraction."""
        test_cases = [
            ("차량번호: 8713", "8713"),
            ("차번호: 80구8713", "80구8713"),
            ("차량번호: 5405", "5405"),
        ]

        for text, expected in test_cases:
            result = extractor._extract_vehicle_number(text)
            assert result is not None
            assert expected in result

    def test_extract_weights(self, extractor):
        """Test weight extraction."""
        text = """
        총중량: 12,480 kg
        차중량: 7,470 kg
        실중량: 5,010 kg
        """

        gross = extractor._extract_weight(text, 'gross')
        tare = extractor._extract_weight(text, 'tare')
        net = extractor._extract_weight(text, 'net')

        assert gross is not None
        assert "12" in gross and "480" in gross
        assert tare is not None
        assert "7" in tare and "470" in tare
        assert net is not None
        assert "5" in net and "010" in net

    def test_extract_customer(self, extractor):
        """Test customer name extraction."""
        test_cases = [
            ("거래처: 고요환경", "고요환경"),
            ("상호: 동우바이오", "동우바이오"),
        ]

        for text, expected in test_cases:
            result = extractor._extract_customer(text)
            assert result is not None
            assert expected in result

    def test_extract_product(self, extractor):
        """Test product name extraction."""
        test_cases = [
            ("품명: 식물", "식물"),
            ("제품명: 국판", "국판"),
        ]

        for text, expected in test_cases:
            result = extractor._extract_product(text)
            assert result is not None
            assert expected in result

    def test_extract_transaction_type(self, extractor):
        """Test transaction type extraction."""
        test_cases = [
            ("구분: 입고", "입고"),
            ("입고", "입고"),
            ("출고", "출고"),
        ]

        for text, expected in test_cases:
            result = extractor._extract_transaction_type(text)
            assert result is not None
            assert expected in result

    def test_extract_all_fields(self, extractor):
        """Test extraction of all fields from complete text."""
        text = """
        계량증명서
        계량일자: 2026-02-02
        차량번호: 8713
        거래처: 동우바이오
        품명: 폐기물
        총중량: 12,480 kg
        차중량: 7,470 kg
        실중량: 5,010 kg
        """

        result = extractor.extract(text)

        assert result['date'] is not None
        assert result['vehicle_number'] is not None
        assert result['gross_weight'] is not None
        assert result['tare_weight'] is not None
        assert result['net_weight'] is not None
        assert result['raw_text'] == text

    def test_extract_with_spaces_in_numbers(self, extractor):
        """Test extraction when numbers have spaces instead of commas."""
        text = "총중량: 13 460 kg"

        result = extractor._extract_weight(text, 'gross')

        assert result is not None
        assert "13" in result
        assert "460" in result
