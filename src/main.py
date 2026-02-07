#!/usr/bin/env python3
"""
Main entry point for OCR Weighbridge Parser.

This module provides a CLI interface for parsing weighbridge OCR data.
It orchestrates the entire parsing pipeline from raw OCR input to
validated structured output.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .config import Config
from .utils.logger import setup_logger
from .utils.io_handler import IOHandler
from .preprocessing.cleaner import TextCleaner
from .extraction.extractor import FieldExtractor
from .normalization.normalizer import DataNormalizer
from .validation.validator import DataValidator
from .models.schema import WeighbridgeRecord


class OCRParser:
    """
    Main OCR parsing pipeline coordinator.

    This class orchestrates the entire parsing process:
    1. Text cleaning/preprocessing
    2. Field extraction
    3. Data normalization
    4. Validation
    5. Output generation
    """

    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the parser with all components.

        Args:
            log_level: Logging level
        """
        # Set up logging
        self.logger = setup_logger(
            name="ocr_parser",
            level=getattr(logging, log_level.upper(), logging.INFO)
        )

        # Initialize pipeline components
        self.io_handler = IOHandler()
        self.cleaner = TextCleaner()
        self.extractor = FieldExtractor()
        self.normalizer = DataNormalizer()
        self.validator = DataValidator(tolerance_kg=Config.WEIGHT_TOLERANCE_KG)

        self.logger.info(f"Initialized {Config.APP_NAME} v{Config.VERSION}")

    def parse_file(self, input_path: Path) -> Dict[str, Any]:
        """
        Parse a single OCR file.

        Args:
            input_path: Path to input OCR JSON file

        Returns:
            Parsed and validated record dictionary
        """
        self.logger.info(f"Processing file: {input_path}")

        try:
            # Step 1: Load OCR data
            ocr_data = self.io_handler.read_ocr_json(input_path)

            # Step 2: Clean text
            cleaned_text = self.cleaner.clean(ocr_data)
            self.logger.debug(f"Cleaned text preview: {cleaned_text[:200]}...")

            # Step 3: Extract fields
            extracted_data = self.extractor.extract(cleaned_text)

            # Step 4: Normalize data
            normalized_data = self.normalizer.normalize(extracted_data)

            # Step 5: Validate data
            validation_result = self.validator.validate(normalized_data)

            # Step 6: Create structured record
            try:
                record = WeighbridgeRecord(**normalized_data)
                record_dict = record.model_dump(mode='json')
            except Exception as e:
                self.logger.error(f"Failed to create WeighbridgeRecord: {e}")
                record_dict = normalized_data

            # Add metadata
            result = {
                'file_name': input_path.name,
                'processed_at': datetime.now().isoformat(),
                'validation': {
                    'is_valid': validation_result.is_valid,
                    'warnings': validation_result.warnings,
                    'errors': validation_result.errors,
                    'weight_consistency': validation_result.weight_consistency,
                    'computed_net_weight_kg': float(validation_result.computed_net_weight)
                    if validation_result.computed_net_weight else None,
                },
                'data': record_dict
            }

            # Log result
            status = "SUCCESS" if validation_result.is_valid else "WARNING"
            self.logger.info(
                f"{status}: {input_path.name} - "
                f"Warnings: {len(validation_result.warnings)}, "
                f"Errors: {len(validation_result.errors)}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to process {input_path}: {e}", exc_info=True)
            return {
                'file_name': input_path.name,
                'processed_at': datetime.now().isoformat(),
                'error': str(e),
                'validation': {
                    'is_valid': False,
                    'errors': [str(e)]
                }
            }

    def parse_batch(self, input_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Parse multiple OCR files.

        Args:
            input_paths: List of input file paths

        Returns:
            List of parsed records
        """
        self.logger.info(f"Starting batch processing of {len(input_paths)} files")

        results = []
        success_count = 0
        error_count = 0

        for path in input_paths:
            result = self.parse_file(path)
            results.append(result)

            if result.get('validation', {}).get('is_valid', False):
                success_count += 1
            else:
                error_count += 1

        self.logger.info(
            f"Batch processing complete: {success_count} successful, "
            f"{error_count} with errors/warnings"
        )

        return results

    def save_results(
        self,
        results: List[Dict[str, Any]],
        output_format: str = "json",
        output_path: Path = None
    ):
        """
        Save parsing results to file.

        Args:
            results: List of parsed records
            output_format: Output format ('json' or 'csv')
            output_path: Optional custom output path
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Config.get_output_dir()
            output_path = output_dir / f"parsed_results_{timestamp}.{output_format}"

        # Flatten results for CSV (extract data fields)
        if output_format == "csv":
            flattened = []
            for result in results:
                flat_record = {
                    'file_name': result['file_name'],
                    'processed_at': result['processed_at'],
                    'is_valid': result.get('validation', {}).get('is_valid', False),
                    **result.get('data', {})
                }
                # Remove raw_text for CSV to keep it manageable
                flat_record.pop('raw_text', None)
                flattened.append(flat_record)
            self.io_handler.write_csv(flattened, output_path)
        else:
            self.io_handler.write_json(results, output_path)

        self.logger.info(f"Results saved to {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Parse weighbridge OCR data into structured format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single file
  python -m src.main -i data/sample_01.json -o output/result.json

  # Parse multiple files
  python -m src.main -i data/*.json -f csv

  # Enable debug logging
  python -m src.main -i data/*.json --log-level DEBUG
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        nargs='+',
        required=True,
        help='Input OCR JSON file(s) or glob pattern'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: auto-generated in output/)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Initialize parser
    ocr_parser = OCRParser(log_level=args.log_level)

    # Resolve input paths
    input_paths = []
    for input_spec in args.input:
        path = Path(input_spec)
        if path.is_file():
            input_paths.append(path)
        elif '*' in input_spec:
            # Handle glob pattern
            parent = Path(input_spec).parent
            pattern = Path(input_spec).name
            matches = list(parent.glob(pattern))
            input_paths.extend(matches)
        else:
            ocr_parser.logger.error(f"Invalid input: {input_spec}")
            sys.exit(1)

    if not input_paths:
        ocr_parser.logger.error("No valid input files found")
        sys.exit(1)

    # Parse files
    results = ocr_parser.parse_batch(input_paths)

    # Save results
    output_path = Path(args.output) if args.output else None
    ocr_parser.save_results(results, args.format, output_path)

    # Exit with appropriate code
    error_count = sum(
        1 for r in results
        if not r.get('validation', {}).get('is_valid', False)
    )

    if error_count > 0:
        ocr_parser.logger.warning(f"{error_count} file(s) had validation errors/warnings")
        sys.exit(1)
    else:
        ocr_parser.logger.info("All files processed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
