"""Regex patterns for field extraction.

This module contains all regex patterns used for extracting fields
from weighbridge receipts. Patterns are designed to handle variations
and noise in OCR output.
"""

import re
from typing import Dict, List

# Date patterns - handle various date formats
DATE_PATTERNS = [
    # YYYY-MM-DD format
    r'(?:계량\s*일자|날\s*짜|일\s*시|일\s*자)[\s:：]*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',
    # Alternative date patterns
    r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*\d{2}:\d{2}',
    # Year-Month-Day with variations
    r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
]

# Time patterns - handle HH:MM or HH:MM:SS formats
TIME_PATTERNS = [
    r'(\d{1,2}:\d{2}:\d{2})',  # HH:MM:SS
    r'(\d{1,2}:\d{2})',  # HH:MM
    r'(\d{1,2}시\s*\d{1,2}분)',  # Korean format
]

# Vehicle number patterns
VEHICLE_NUMBER_PATTERNS = [
    # Handle various vehicle number formats
    r'(?:차량\s*번호|차\s*번호|차량No\.|차량\s*No)[\s:：]*([0-9가-힣]{2,20})',
    # Standalone numbers that look like vehicle IDs
    r'(?:번호|No\.?)[\s:：]*([0-9]{4,10})',
]

# Weight patterns - handle weights with units and various formats
WEIGHT_PATTERNS = {
    'gross': [
        # Pattern with time followed by weight
        r'(?:총\s*중\s*량|총중량)[\s:：]*(?:\d{1,2}시\s*\d{1,2}분|\d{1,2}:\d{2})\s*(\d{1,2})\s+(\d{3})\s*kg',
        r'(?:총\s*중\s*량|총중량)[\s:：]*(?:(?:\d{1,2}시\s*\d{1,2}분|\d{1,2}:\d{2})\s*)?(\d{1,3}[,\s]?\d{3}|\d{1,6})\s*kg',
        # Fallback pattern
        r'(?:총\s*중\s*량|총중량)[\s:：]*(?:[^\d]*)(\d{1,3}[,\s]?\d{3}|\d{1,6})\s*kg',
        # For sample_01: timestamp followed by weight (no label)
        r'\d{2}:\d{2}:\d{2}\s+(\d{1,3}[,\s]?\d{3})\s*kg',
    ],
    'tare': [
        # Pattern with time and spaces in number (e.g., "02 : 13 7 560 kg")
        r'(?:차\s*중\s*량|차중량|공\s*차\s*중\s*량|공차중량)[\s:：]*(?:\d{1,2}\s*:\s*\d{2})\s*(\d{1,2})\s+(\d{3})\s*kg',
        r'(?:차\s*중\s*량|차중량|공\s*차\s*중\s*량|공차중량)[\s:：]*(?:(?:\d{1,2}시\s*\d{1,2}분|\d{1,2}:\d{2})\s*)?(\d{1,3}[,\s]?\d{3}|\d{1,6})\s*kg',
        r'(?:차\s*중\s*량|차중량|공\s*차\s*중\s*량|공차중량)[\s:：]*(?:[^\d]*)(\d{1,3}[,\s]?\d{3}|\d{1,6})\s*kg',
        # Bare "중량:" pattern for sample_01
        r'중\s*량[\s:：]*\d{2}:\d{2}:\d{2}\s+(\d{1,3}[,\s]?\d{3})\s*kg',
    ],
    'net': [
        r'(?:실\s*중\s*량|실중량)[\s:：]*(\d{1,3}[,\s]?\d{3}|\d{1,6})\s*kg',
        # Handle spaces in numbers like "5 900"
        r'(?:실\s*중\s*량|실중량)[\s:：]*(\d{1,2})\s+(\d{3})\s*kg',
    ],
}

# Customer/Company name patterns
CUSTOMER_PATTERNS = [
    r'(?:거\s*래\s*처|거래처|상\s*호|상호|회\s*사\s*명|회사명)[\s:：]*([가-힣()]{2,30})',
]

# Product name patterns
PRODUCT_PATTERNS = [
    r'(?:품\s*명|품명|제\s*품\s*명|제품명)[\s:：]*([가-힣]{1,20})',
]

# Transaction type patterns
TRANSACTION_TYPE_PATTERNS = [
    r'(?:구\s*분)[\s:：]*(입고|출고)',
    r'(입고|출고)',
]

# Measurement ID/Count patterns
MEASUREMENT_ID_PATTERNS = [
    r'(?:계량\s*횟수|ID-NO)[\s:：]*(\d{4,10})',
    r'(?:NO|번호)[\s:：]*(\d{4,10})',
]

# Location/Company patterns (from header)
LOCATION_PATTERNS = [
    r'\(주\)\s*([가-힣\s]{2,20})',
    r'([가-힣]{2,10}(?:환경|바이오|리사이클링|C&S)(?:\(주\))?)',
]


def compile_patterns() -> Dict[str, List[re.Pattern]]:
    """
    Compile all regex patterns for efficient reuse.

    Returns:
        Dictionary mapping field names to compiled regex patterns
    """
    compiled = {}

    # Compile date patterns
    compiled['date'] = [re.compile(p, re.IGNORECASE) for p in DATE_PATTERNS]

    # Compile time patterns
    compiled['time'] = [re.compile(p, re.IGNORECASE) for p in TIME_PATTERNS]

    # Compile vehicle patterns
    compiled['vehicle'] = [re.compile(p, re.IGNORECASE) for p in VEHICLE_NUMBER_PATTERNS]

    # Compile weight patterns
    for weight_type, patterns in WEIGHT_PATTERNS.items():
        compiled[f'weight_{weight_type}'] = [re.compile(p, re.IGNORECASE) for p in patterns]

    # Compile customer patterns
    compiled['customer'] = [re.compile(p, re.IGNORECASE) for p in CUSTOMER_PATTERNS]

    # Compile product patterns
    compiled['product'] = [re.compile(p, re.IGNORECASE) for p in PRODUCT_PATTERNS]

    # Compile transaction type patterns
    compiled['transaction_type'] = [re.compile(p, re.IGNORECASE) for p in TRANSACTION_TYPE_PATTERNS]

    # Compile measurement ID patterns
    compiled['measurement_id'] = [re.compile(p, re.IGNORECASE) for p in MEASUREMENT_ID_PATTERNS]

    # Compile location patterns
    compiled['location'] = [re.compile(p, re.IGNORECASE) for p in LOCATION_PATTERNS]

    return compiled


# Precompile patterns for performance
COMPILED_PATTERNS = compile_patterns()
