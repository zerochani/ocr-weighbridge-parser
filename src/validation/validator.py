"""Data validation utilities.

This module validates normalized data for logical consistency,
completeness, and business rule compliance.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, List
from datetime import datetime

from ..models.schema import ValidationResult

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates normalized weighbridge data.

    Performs:
    - Completeness checks (required fields present)
    - Logical validation (weight relationships)
    - Range validation (reasonable values)
    - Business rule validation
    """

    def __init__(self, tolerance_kg: Decimal = Decimal('1.0')):
        """
        Initialize the validator.

        Args:
            tolerance_kg: Allowed tolerance for weight calculations (in kg)
        """
        self.tolerance_kg = tolerance_kg
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate normalized data.

        Args:
            data: Dictionary of normalized data

        Returns:
            ValidationResult with validation status and messages
        """
        self.logger.debug("Starting data validation")

        warnings: List[str] = []
        errors: List[str] = []
        is_valid = True
        weight_consistency = True
        computed_net = None

        # Check for critical required fields
        critical_fields = ['gross_weight_kg', 'tare_weight_kg', 'net_weight_kg']
        missing_critical = [f for f in critical_fields if data.get(f) is None]

        if missing_critical:
            errors.append(f"Missing critical fields: {', '.join(missing_critical)}")
            is_valid = False

        # Check for important but non-critical fields
        important_fields = ['vehicle_number', 'measurement_date']
        missing_important = [f for f in important_fields if data.get(f) is None]

        if missing_important:
            warnings.append(f"Missing important fields: {', '.join(missing_important)}")

        # Validate weight relationships if all weights are present
        if not missing_critical:
            gross = data['gross_weight_kg']
            tare = data['tare_weight_kg']
            net = data['net_weight_kg']

            # Calculate expected net weight
            computed_net = gross - tare

            # Check if gross > tare (basic sanity)
            if gross <= tare:
                errors.append(
                    f"Gross weight ({gross} kg) must be greater than tare weight ({tare} kg)"
                )
                is_valid = False
                weight_consistency = False

            # Check if net weight matches calculation (within tolerance)
            weight_diff = abs(computed_net - net)
            if weight_diff > self.tolerance_kg:
                warnings.append(
                    f"Net weight discrepancy: recorded={net} kg, "
                    f"calculated={computed_net} kg, difference={weight_diff} kg"
                )
                weight_consistency = False

            # Check for reasonable weight ranges
            max_reasonable_weight = Decimal('100000')  # 100 tons
            min_reasonable_weight = Decimal('1')  # 1 kg

            for weight_name, weight_value in [
                ('gross', gross), ('tare', tare), ('net', net)
            ]:
                if weight_value > max_reasonable_weight:
                    warnings.append(
                        f"{weight_name.capitalize()} weight ({weight_value} kg) "
                        f"exceeds reasonable maximum"
                    )
                if weight_value < min_reasonable_weight:
                    warnings.append(
                        f"{weight_name.capitalize()} weight ({weight_value} kg) "
                        f"below reasonable minimum"
                    )

        # Validate date if present
        if data.get('measurement_date'):
            date = data['measurement_date']
            if isinstance(date, datetime):
                # Check if date is not in the future
                if date > datetime.now():
                    warnings.append(
                        f"Measurement date ({date.strftime('%Y-%m-%d')}) is in the future"
                    )

                # Check if date is not too old (e.g., more than 10 years)
                years_old = (datetime.now() - date).days / 365.25
                if years_old > 10:
                    warnings.append(
                        f"Measurement date ({date.strftime('%Y-%m-%d')}) "
                        f"is unusually old ({int(years_old)} years)"
                    )

        # Validate vehicle number format if present
        if data.get('vehicle_number'):
            vehicle = data['vehicle_number']
            if len(vehicle) < 2:
                warnings.append(f"Vehicle number '{vehicle}' is unusually short")
            if len(vehicle) > 20:
                warnings.append(f"Vehicle number '{vehicle}' is unusually long")

        # Create validation result
        result = ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            computed_net_weight=computed_net,
            weight_consistency=weight_consistency
        )

        # Log validation summary
        self.logger.info(
            f"Validation complete: valid={is_valid}, "
            f"warnings={len(warnings)}, errors={len(errors)}"
        )

        for warning in warnings:
            self.logger.warning(f"Validation warning: {warning}")

        for error in errors:
            self.logger.error(f"Validation error: {error}")

        return result

    def validate_completeness(self, data: Dict[str, Any]) -> float:
        """
        Calculate completeness score (0-1).

        Args:
            data: Normalized data dictionary

        Returns:
            Completeness score (percentage of non-null fields)
        """
        all_fields = [
            'gross_weight_kg', 'tare_weight_kg', 'net_weight_kg',
            'vehicle_number', 'measurement_date', 'customer_name',
            'product_name', 'transaction_type', 'measurement_id', 'location'
        ]

        non_null_count = sum(1 for field in all_fields if data.get(field) is not None)
        completeness = non_null_count / len(all_fields)

        self.logger.debug(f"Completeness score: {completeness:.2%} ({non_null_count}/{len(all_fields)})")

        return completeness
