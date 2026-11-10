"""
Unit tests for CalculationService.

Tests the pure domain service for arithmetic operations including:
- Basic arithmetic operations (add, subtract, multiply, divide)
- Division by zero handling
- Decimal precision
- Large numbers and edge cases
- Invalid operation codes
"""

import pytest
from decimal import Decimal
from calculator.services import CalculationService
from calculator.exceptions import DivisionByZeroError, OverflowResultError


class TestCalculationServiceAddition:
    """Tests for addition operation."""

    def test_addition_positive_numbers(self):
        """Test addition of two positive numbers."""
        result = CalculationService.calculate(Decimal('4'), Decimal('3'), 'add')
        assert result == Decimal('7')

    def test_addition_negative_numbers(self):
        """Test addition with negative numbers."""
        result = CalculationService.calculate(Decimal('-5'), Decimal('3'), 'add')
        assert result == Decimal('-2')

    def test_addition_both_negative(self):
        """Test addition of two negative numbers."""
        result = CalculationService.calculate(Decimal('-5'), Decimal('-3'), 'add')
        assert result == Decimal('-8')

    def test_addition_with_zero(self):
        """Test addition with zero."""
        result = CalculationService.calculate(Decimal('0'), Decimal('5'), 'add')
        assert result == Decimal('5')

    def test_addition_large_numbers(self):
        """Test addition of large numbers."""
        result = CalculationService.calculate(Decimal('999999999'), Decimal('1'), 'add')
        assert result == Decimal('1000000000')


class TestCalculationServiceSubtraction:
    """Tests for subtraction operation."""

    def test_subtraction_positive_numbers(self):
        """Test subtraction of two positive numbers."""
        result = CalculationService.calculate(Decimal('10'), Decimal('4'), 'subtract')
        assert result == Decimal('6')

    def test_subtraction_negative_result(self):
        """Test subtraction resulting in negative number."""
        result = CalculationService.calculate(Decimal('4'), Decimal('10'), 'subtract')
        assert result == Decimal('-6')

    def test_subtraction_with_zero(self):
        """Test subtraction with zero."""
        result = CalculationService.calculate(Decimal('5'), Decimal('0'), 'subtract')
        assert result == Decimal('5')

    def test_subtraction_negative_operands(self):
        """Test subtraction with negative operands."""
        result = CalculationService.calculate(Decimal('-5'), Decimal('-3'), 'subtract')
        assert result == Decimal('-2')


class TestCalculationServiceMultiplication:
    """Tests for multiplication operation."""

    def test_multiplication_positive_numbers(self):
        """Test multiplication of two positive numbers."""
        result = CalculationService.calculate(Decimal('6'), Decimal('7'), 'multiply')
        assert result == Decimal('42')

    def test_multiplication_with_zero(self):
        """Test multiplication with zero."""
        result = CalculationService.calculate(Decimal('0'), Decimal('5'), 'multiply')
        assert result == Decimal('0')

    def test_multiplication_negative_numbers(self):
        """Test multiplication with negative numbers."""
        result = CalculationService.calculate(Decimal('-5'), Decimal('3'), 'multiply')
        assert result == Decimal('-15')

    def test_multiplication_both_negative(self):
        """Test multiplication of two negative numbers."""
        result = CalculationService.calculate(Decimal('-5'), Decimal('-3'), 'multiply')
        assert result == Decimal('15')


class TestCalculationServiceDivision:
    """Tests for division operation."""

    def test_division_positive_numbers(self):
        """Test division of two positive numbers."""
        result = CalculationService.calculate(Decimal('15'), Decimal('3'), 'divide')
        assert result == Decimal('5')

    def test_division_with_remainder(self):
        """Test division with remainder."""
        result = CalculationService.calculate(Decimal('10'), Decimal('3'), 'divide')
        assert result == Decimal('3.3333333333')  # Rounded to 10 decimal places

    def test_division_negative_numbers(self):
        """Test division with negative numbers."""
        result = CalculationService.calculate(Decimal('-15'), Decimal('3'), 'divide')
        assert result == Decimal('-5')

    def test_division_by_negative(self):
        """Test division by negative number."""
        result = CalculationService.calculate(Decimal('15'), Decimal('-3'), 'divide')
        assert result == Decimal('-5')

    def test_division_by_zero_raises_error(self):
        """Test that division by zero raises DivisionByZeroError."""
        with pytest.raises(DivisionByZeroError):
            CalculationService.calculate(Decimal('9'), Decimal('0'), 'divide')

    def test_division_zero_by_number(self):
        """Test division of zero by a number."""
        result = CalculationService.calculate(Decimal('0'), Decimal('5'), 'divide')
        assert result == Decimal('0')


class TestCalculationServiceDecimalPrecision:
    """Tests for decimal precision handling."""

    def test_decimal_precision_addition(self):
        """Test that 0.1 + 0.2 equals 0.3 (not 0.30000000000000004)."""
        result = CalculationService.calculate(Decimal('0.1'), Decimal('0.2'), 'add')
        assert result == Decimal('0.3')

    def test_decimal_precision_subtraction(self):
        """Test decimal precision in subtraction."""
        result = CalculationService.calculate(Decimal('1.0'), Decimal('0.9'), 'subtract')
        assert result == Decimal('0.1')

    def test_decimal_precision_multiplication(self):
        """Test decimal precision in multiplication."""
        result = CalculationService.calculate(Decimal('0.1'), Decimal('0.2'), 'multiply')
        assert result == Decimal('0.02')

    def test_result_rounding(self):
        """Test that results are rounded to 10 decimal places."""
        result = CalculationService.calculate(Decimal('1'), Decimal('3'), 'divide')
        # 1/3 = 0.333333333333... should be rounded to 0.3333333333
        assert result == Decimal('0.3333333333')


class TestCalculationServiceEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_invalid_operation_code(self):
        """Test that invalid operation code raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            CalculationService.calculate(Decimal('5'), Decimal('3'), 'invalid')
        assert 'Invalid operation' in str(exc_info.value)

    def test_empty_operation_code(self):
        """Test that empty operation code raises ValueError."""
        with pytest.raises(ValueError):
            CalculationService.calculate(Decimal('5'), Decimal('3'), '')

    def test_overflow_result_error(self):
        """Test that results exceeding threshold raise OverflowResultError."""
        # 1e20 * 1e20 = 1e40, which exceeds MAX_RESULT_THRESHOLD of 1e30
        with pytest.raises(OverflowResultError):
            CalculationService.calculate(Decimal('1e20'), Decimal('1e20'), 'multiply')

    def test_very_small_result(self):
        """Test handling of very small results."""
        result = CalculationService.calculate(Decimal('1e-10'), Decimal('1'), 'multiply')
        assert result == Decimal('0.0000000001')

    def test_all_allowed_operations(self):
        """Test that all allowed operations work correctly."""
        operations = ['add', 'subtract', 'multiply', 'divide']
        for op in operations:
            if op == 'divide':
                result = CalculationService.calculate(Decimal('10'), Decimal('2'), op)
            else:
                result = CalculationService.calculate(Decimal('5'), Decimal('3'), op)
            assert isinstance(result, Decimal)


class TestCalculationServiceStaticMethods:
    """Tests for internal static methods."""

    def test_round_result_method(self):
        """Test the _round_result static method."""
        from calculator.services import CalculationService
        result = CalculationService._round_result(Decimal('3.141592653589793'))
        assert result == Decimal('3.1415926536')

    def test_dispatch_method_add(self):
        """Test the _dispatch static method for addition."""
        result = CalculationService._dispatch(Decimal('5'), Decimal('3'), 'add')
        assert result == Decimal('8')

    def test_dispatch_method_invalid_operation(self):
        """Test that _dispatch raises ValueError for invalid operation."""
        with pytest.raises(ValueError):
            CalculationService._dispatch(Decimal('5'), Decimal('3'), 'invalid')
