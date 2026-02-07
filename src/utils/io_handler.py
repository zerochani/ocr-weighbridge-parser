"""Input/Output handling utilities.

This module handles file I/O operations including:
- Reading OCR JSON files
- Writing output to JSON and CSV
- Batch processing
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class IOHandler:
    """
    Handles all file I/O operations for the parser.
    """

    def __init__(self):
        """Initialize IO handler."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def read_ocr_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Read OCR JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded OCR data from {file_path}")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")

    def write_json(
        self,
        data: List[Dict[str, Any]],
        output_path: Path,
        indent: int = 2
    ):
        """
        Write data to JSON file.

        Args:
            data: List of dictionaries to write
            output_path: Output file path
            indent: JSON indentation (default: 2)
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Custom JSON encoder for Decimal and datetime
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, cls=CustomEncoder)

        self.logger.info(f"Wrote {len(data)} records to {output_path}")

    def write_csv(
        self,
        data: List[Dict[str, Any]],
        output_path: Path,
        fieldnames: Optional[List[str]] = None
    ):
        """
        Write data to CSV file.

        Args:
            data: List of dictionaries to write
            output_path: Output file path
            fieldnames: List of field names (if None, inferred from first record)
        """
        if not data:
            self.logger.warning("No data to write to CSV")
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Infer fieldnames if not provided
        if fieldnames is None:
            fieldnames = list(data[0].keys())

        # Convert values for CSV compatibility
        def convert_value(val):
            if isinstance(val, (Decimal, float)):
                return float(val)
            if isinstance(val, datetime):
                return val.isoformat()
            if val is None:
                return ''
            return str(val)

        # Prepare data for CSV
        csv_data = []
        for record in data:
            csv_record = {k: convert_value(v) for k, v in record.items()}
            csv_data.append(csv_record)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

        self.logger.info(f"Wrote {len(data)} records to {output_path}")

    def read_batch(self, input_dir: Path, pattern: str = "*.json") -> List[Path]:
        """
        Find all files matching pattern in directory.

        Args:
            input_dir: Input directory path
            pattern: File pattern (default: *.json)

        Returns:
            List of file paths
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        files = list(input_dir.glob(pattern))
        self.logger.info(f"Found {len(files)} files matching '{pattern}' in {input_dir}")

        return sorted(files)

    def save_processing_report(
        self,
        report: Dict[str, Any],
        output_path: Path
    ):
        """
        Save processing report to JSON.

        Args:
            report: Report dictionary
            output_path: Output file path
        """
        self.write_json([report], output_path, indent=2)
        self.logger.info(f"Saved processing report to {output_path}")
