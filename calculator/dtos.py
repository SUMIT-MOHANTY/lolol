"""
Data Transfer Objects for the calculator application.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CalculationInputDTO:
    """
    Immutable DTO carrying validated inputs from the form layer
    to the service layer.

    Attributes
    ----------
    operand_a : Decimal
        Validated left-hand operand.
    operand_b : Decimal
        Validated right-hand operand.
    operation : str
        Validated operation string.
    session_key : Optional[str]
        Django session key for associating the request with a session.
    """
    operand_a: Decimal
    operand_b: Decimal
    operation: str
    session_key: Optional[str] = field(default=None)


@dataclass(frozen=True)
class CalculationResultDTO:
    """
    Immutable DTO carrying the computation outcome from the service
    layer back to the view layer.

    Attributes
    ----------
    result : Optional[Decimal]
        Computed result. None when an error occurred.
    error_message : Optional[str]
        Human-readable error string. None on success.
    is_success : bool
        True when result is populated and error_message is None.
    """
    result: Optional[Decimal] = field(default=None)
    error_message: Optional[str] = field(default=None)

    @property
    def is_success(self) -> bool:
        return self.result is not None and self.error_message is None
