"""Tests for text preprocessing/cleaning module."""

import pytest
from src.preprocessing.cleaner import TextCleaner


class TestTextCleaner:
    """Test suite for TextCleaner class."""

    @pytest.fixture
    def cleaner(self):
        """Fixture to provide TextCleaner instance."""
        return TextCleaner()

    def test_normalize_whitespace(self, cleaner):
        """Test whitespace normalization."""
        text = "계량일자:  2026-02-02   \n\n차량번호:  8713  "
        result = cleaner._normalize_whitespace(text)

        assert "  " not in result  # No double spaces
        assert result.startswith("계량일자:")
        assert result.endswith("8713")

    def test_normalize_unicode(self, cleaner):
        """Test Unicode normalization."""
        text = "계량증명서"  # Korean text
        result = cleaner._normalize_unicode(text)

        assert result == "계량증명서"
        assert len(result) > 0

    def test_remove_noise(self, cleaner):
        """Test noise removal."""
        text = "계량일자: 2026-02-02\n·\n차량번호: 8713"
        result = cleaner._remove_noise(text)

        # Should preserve meaningful content
        assert "계량일자" in result
        assert "차량번호" in result

    def test_normalize_korean_labels(self, cleaner):
        """Test Korean label normalization."""
        test_cases = [
            ("차 량 번 호", "차량번호"),
            ("총 중 량", "총중량"),
            ("실 중 량", "실중량"),
            ("계 량 일 자", "계량일자"),
        ]

        for input_text, expected in test_cases:
            result = cleaner.normalize_korean_labels(input_text)
            assert expected in result

    def test_extract_text_from_ocr_json(self, cleaner):
        """Test extraction of text from OCR JSON structure."""
        ocr_data = {
            "pages": [{
                "text": "계량일자: 2026-02-02\n차량번호: 8713",
                "confidence": 0.95
            }]
        }

        result = cleaner._extract_text_from_ocr(ocr_data)

        assert "계량일자" in result
        assert "2026-02-02" in result
        assert "차량번호" in result

    def test_extract_text_from_string(self, cleaner):
        """Test extraction when input is already a string."""
        text = "계량일자: 2026-02-02"
        result = cleaner._extract_text_from_ocr(text)

        assert result == text

    def test_clean_full_pipeline(self, cleaner):
        """Test complete cleaning pipeline."""
        ocr_data = {
            "pages": [{
                "text": "계 량 일 자:  2026-02-02  \n\n\n  차량번호:  8713  ",
                "confidence": 0.95
            }]
        }

        result = cleaner.clean(ocr_data)

        assert isinstance(result, str)
        assert "계 량 일 자:" in result or "계량일자" in result
        assert "2026-02-02" in result
        assert "  " not in result  # No excessive whitespace
