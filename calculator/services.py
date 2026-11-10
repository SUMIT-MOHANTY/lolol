"""
Calculation Service - Pure domain service for arithmetic operations.
Zero Django imports. Fully unit-testable without Django test infrastructure.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Final
from calculator.exceptions import DivisionByZeroError, OverflowResultError

OPERATION_ADD: Final[str] = "add"
OPERATION_SUBTRACT: Final[str] = "subtract"
OPERATION_MULTIPLY: Final[str] = "multiply"
OPERATION_DIVIDE: Final[str] = "divide"

ALLOWED_OPERATIONS: Final[tuple[str, ...]] = (
    OPERATION_ADD,
    OPERATION_SUBTRACT,
    OPERATION_MULTIPLY,
    OPERATION_DIVIDE,
)

MAX_RESULT_THRESHOLD: Final[Decimal] = Decimal("1e30")
RESULT_DECIMAL_PLACES: Final[int] = 10


class CalculationService:
    """
    Pure domain service. Zero Django imports. Fully unit-testable
    without Django test infrastructure.
    """

    @staticmethod
    def calculate(
        operand_a: Decimal,
        operand_b: Decimal,
        operation: str,
    ) -> Decimal:
        """
        Perform arithmetic on two Decimal operands.

        Parameters
        ----------
        operand_a : Decimal
            Left-hand operand. Must be a valid Decimal instance.
        operand_b : Decimal
            Right-hand operand. Must be a valid Decimal instance.
        operation : str
            One of: 'add', 'subtract', 'multiply', 'divide'.

        Returns
        -------
        Decimal
            Computed result rounded to RESULT_DECIMAL_PLACES (10)
            decimal places using ROUND_HALF_UP.

        Raises
        ------
        DivisionByZeroError
            When operation == 'divide' and operand_b == Decimal('0').
        OverflowResultError
            When abs(result) > MAX_RESULT_THRESHOLD (1e30).
        ValueError
            When operation is not in ALLOWED_OPERATIONS.
        """
        raw_result = CalculationService._dispatch(operand_a, operand_b, operation)
        rounded_result = CalculationService._round_result(raw_result)
        
        # Check for overflow after rounding
        if abs(rounded_result) > MAX_RESULT_THRESHOLD:
            raise OverflowResultError()
        
        return rounded_result

    @staticmethod
    def _dispatch(
        operand_a: Decimal,
        operand_b: Decimal,
        operation: str,
    ) -> Decimal:
        """
        Internal strategy dispatcher. Maps operation string to
        arithmetic callable and executes it.

        Parameters
        ----------
        operand_a : Decimal
        operand_b : Decimal
        operation : str

        Returns
        -------
        Decimal
            Raw (unrounded) arithmetic result.

        Raises
        ------
        DivisionByZeroError
            When operation == 'divide' and operand_b is zero.
        ValueError
            When operation is not in ALLOWED_OPERATIONS.
        """
        if operation not in ALLOWED_OPERATIONS:
            raise ValueError(f"Invalid operation: '{operation}'. Allowed operations: {ALLOWED_OPERATIONS}")
        
        if operation == OPERATION_ADD:
            return operand_a + operand_b
        elif operation == OPERATION_SUBTRACT:
            return operand_a - operand_b
        elif operation == OPERATION_MULTIPLY:
            return operand_a * operand_b
        elif operation == OPERATION_DIVIDE:
            if operand_b == Decimal('0'):
                raise DivisionByZeroError()
            return operand_a / operand_b
        
        # This should never be reached due to the check above
        raise ValueError(f"Invalid operation: '{operation}'")

    @staticmethod
    def _round_result(result: Decimal) -> Decimal:
        """
        Round result to RESULT_DECIMAL_PLACES using ROUND_HALF_UP.

        Parameters
        ----------
        result : Decimal

        Returns
        -------
        Decimal
            Rounded result.
        """
        quantize_exp = Decimal(f"1e-{RESULT_DECIMAL_PLACES}")
        return result.quantize(quantize_exp, rounding=ROUND_HALF_UP)
