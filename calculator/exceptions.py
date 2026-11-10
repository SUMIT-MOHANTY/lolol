"""
Domain exceptions for the calculator application.
"""


class DivisionByZeroError(ValueError):
    """
    Raised by CalculationService when operand_b is zero and
    operation is 'divide'. Caught by CalculatorView.post() and
    surfaced as error_message in template context.
    """
    def __init__(self) -> None:
        super().__init__("Cannot divide by zero.")


class OverflowResultError(ValueError):
    """
    Raised by CalculationService when the computed result
    exceeds the absolute threshold of 1e30.
    """
    def __init__(self) -> None:
        super().__init__("Result exceeds maximum representable value (1e30).")
