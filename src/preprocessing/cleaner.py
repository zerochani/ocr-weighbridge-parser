"""Text preprocessing and cleaning utilities.

This module handles the preprocessing of noisy OCR text, including:
- Normalization of whitespace
- Removal of special characters
- Unicode normalization
- Line consolidation
"""

import re
import unicodedata
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Handles preprocessing and cleaning of OCR text.

    This class provides methods to clean and normalize text extracted
    from OCR systems, preparing it for pattern-based field extraction.
    """

    def __init__(self):
        """Initialize the text cleaner."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def clean(self, ocr_data: Dict[str, Any]) -> str:
        """
        Clean and preprocess OCR data.

        Args:
            ocr_data: Raw OCR data (JSON structure from OCR API)

        Returns:
            Cleaned text string ready for extraction

        Raises:
            ValueError: If OCR data structure is invalid
        """
        try:
            # Extract text from OCR JSON structure
            raw_text = self._extract_text_from_ocr(ocr_data)

            # Apply cleaning pipeline
            cleaned_text = self._normalize_unicode(raw_text)
            cleaned_text = self._normalize_whitespace(cleaned_text)
            cleaned_text = self._remove_noise(cleaned_text)

            self.logger.debug(f"Cleaned text length: {len(cleaned_text)}")
            return cleaned_text

        except Exception as e:
            self.logger.error(f"Error during text cleaning: {e}")
            raise ValueError(f"Failed to clean OCR data: {e}")

    def _extract_text_from_ocr(self, ocr_data: Dict[str, Any]) -> str:
        """
        Extract text content from OCR JSON structure.

        Args:
            ocr_data: OCR API response JSON

        Returns:
            Extracted text string
        """
        # Handle different OCR response structures
        if isinstance(ocr_data, dict):
            # Try to extract from common OCR API formats
            if 'pages' in ocr_data and isinstance(ocr_data['pages'], list):
                if ocr_data['pages'] and 'text' in ocr_data['pages'][0]:
                    return ocr_data['pages'][0]['text']

            if 'text' in ocr_data:
                return ocr_data['text']

            # If we have the full structure, try to reconstruct from words/lines
            if 'pages' in ocr_data and isinstance(ocr_data['pages'], list):
                page = ocr_data['pages'][0]
                if 'lines' in page:
                    return '\n'.join(line.get('text', '') for line in page['lines'])
                elif 'words' in page:
                    return ' '.join(word.get('text', '') for word in page['words'])

        elif isinstance(ocr_data, str):
            return ocr_data

        raise ValueError("Invalid OCR data structure")

    def _normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters.

        Args:
            text: Input text

        Returns:
            Unicode-normalized text
        """
        # Use NFKC normalization to standardize Korean characters and symbols
        return unicodedata.normalize('NFKC', text)

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace characters.

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)

        # Preserve line breaks but remove excessive ones
        text = re.sub(r'\n\s*\n+', '\n', text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()

    def _remove_noise(self, text: str) -> str:
        """
        Remove common OCR noise and artifacts.

        Args:
            text: Input text

        Returns:
            Text with noise removed
        """
        # Remove common OCR artifacts
        # Keep Korean characters, numbers, basic punctuation, and spaces
        # This pattern preserves most useful characters while removing noise

        # Remove standalone special symbols that are likely OCR errors
        text = re.sub(r'(?<!\S)[·\*\-~]{1}(?!\S)', '', text)

        # Remove very short isolated fragments (likely OCR errors)
        # but preserve Korean single characters as they might be valid
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Keep lines that have substantial content
            if len(line.strip()) > 0:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def normalize_korean_labels(self, text: str) -> str:
        """
        Normalize Korean label variations.

        Handles common variations in Korean field labels to standardize them.

        Args:
            text: Input text

        Returns:
            Text with normalized Korean labels
        """
        # Normalize spacing in common labels
        label_variations = {
            r'차\s*량\s*번\s*호': '차량번호',
            r'차\s*번\s*호': '차량번호',
            r'총\s*중\s*량': '총중량',
            r'차\s*중\s*량': '차중량',
            r'공\s*차\s*중\s*량': '공차중량',
            r'실\s*중\s*량': '실중량',
            r'계\s*량\s*일\s*자': '계량일자',
            r'거\s*래\s*처': '거래처',
            r'상\s*호': '상호',
            r'품\s*명': '품명',
            r'제\s*품\s*명': '제품명',
        }

        for pattern, replacement in label_variations.items():
            text = re.sub(pattern, replacement, text)

        return text
