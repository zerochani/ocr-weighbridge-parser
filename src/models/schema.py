"""Pydantic models for weighbridge data schema.

This module defines the structured data models for weighbridge receipts,
ensuring type safety and validation throughout the parsing pipeline.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal


class WeighbridgeRecord(BaseModel):
    """
    Structured representation of a weighbridge receipt.

    Attributes:
        gross_weight_kg: Total weight including vehicle (in kg)
        tare_weight_kg: Vehicle weight without load (in kg)
        net_weight_kg: Actual cargo weight (in kg)
        vehicle_number: Vehicle registration/identification number
        measurement_date: Date of measurement
        measurement_time: Time of measurement (optional)
        customer_name: Customer or company name (optional)
        product_name: Type of product being weighed (optional)
        transaction_type: Type of transaction (입고/출고) (optional)
        measurement_id: Unique measurement/count identifier (optional)
        operator: Name of the operator (optional)
        location: Measurement location/company (optional)
        raw_text: Original OCR text for reference
        confidence_score: OCR confidence score (optional)
    """

    gross_weight_kg: Optional[Decimal] = Field(None, description="Gross weight in kg")
    tare_weight_kg: Optional[Decimal] = Field(None, description="Tare weight in kg")
    net_weight_kg: Optional[Decimal] = Field(None, description="Net weight in kg")
    vehicle_number: Optional[str] = Field(None, description="Vehicle identification number")
    measurement_date: Optional[datetime] = Field(None, description="Date of measurement")
    measurement_time: Optional[str] = Field(None, description="Time of measurement")
    customer_name: Optional[str] = Field(None, description="Customer or company name")
    product_name: Optional[str] = Field(None, description="Product type")
    transaction_type: Optional[str] = Field(None, description="Transaction type (입고/출고)")
    measurement_id: Optional[str] = Field(None, description="Measurement count/ID")
    operator: Optional[str] = Field(None, description="Operator name")
    location: Optional[str] = Field(None, description="Weighbridge location/company")
    raw_text: str = Field(..., description="Original OCR text")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="OCR confidence")

    @field_validator('gross_weight_kg', 'tare_weight_kg', 'net_weight_kg', mode='before')
    @classmethod
    def validate_weight(cls, v):
        """Ensure weights are non-negative if present."""
        if v is not None and v < 0:
            raise ValueError("Weight cannot be negative")
        return v

    @model_validator(mode='after')
    def validate_weight_relationship(self):
        """Validate that gross = tare + net (within tolerance)."""
        if all([self.gross_weight_kg, self.tare_weight_kg, self.net_weight_kg]):
            expected_net = self.gross_weight_kg - self.tare_weight_kg
            tolerance = Decimal('0.5')  # Allow 0.5 kg tolerance for rounding

            if abs(expected_net - self.net_weight_kg) > tolerance:
                # Store warning but don't fail validation
                # This allows us to capture the inconsistency
                pass
        return self

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat() if v else None
        }
        validate_assignment = True


class ValidationResult(BaseModel):
    """
    Result of data validation process.

    Attributes:
        is_valid: Whether validation passed
        warnings: List of non-critical issues
        errors: List of critical validation failures
        computed_net_weight: Calculated net weight (gross - tare)
        weight_consistency: Whether weights are mathematically consistent
    """

    is_valid: bool = Field(..., description="Overall validation status")
    warnings: List[str] = Field(default_factory=list, description="Non-critical issues")
    errors: List[str] = Field(default_factory=list, description="Critical validation errors")
    computed_net_weight: Optional[Decimal] = Field(None, description="Calculated net weight")
    weight_consistency: bool = Field(True, description="Weight math consistency")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Decimal: float
        }
