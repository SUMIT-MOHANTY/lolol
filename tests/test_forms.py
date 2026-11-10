"""
Unit tests for CalculatorForm.

Tests form validation logic including:
- Valid decimal and integer inputs
- Missing required fields
- Non-numeric inputs
- Empty string operands
"""

import pytest
from decimal import Decimal
from calculator.forms import CalculatorForm


class TestCalculatorFormValidInputs:
    """Tests for valid form inputs."""

    def test_valid_decimal_inputs(self):
        """Test that decimal inputs are validated and converted to Decimal."""
        data = {
            'operand_a': '3.14',
            'operand_b': '2.71',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is True
        assert form.cleaned_data['operand_a'] == Decimal('3.14')
        assert form.cleaned_data['operand_b'] == Decimal('2.71')
        assert form.cleaned_data['operation'] == 'add'

    def test_valid_integer_inputs(self):
        """Test that integer inputs are validated correctly."""
        data = {
            'operand_a': '10',
            'operand_b': '5',
            'operation': 'multiply'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is True
        assert form.cleaned_data['operand_a'] == Decimal('10')
        assert form.cleaned_data['operand_b'] == Decimal('5')
        assert form.cleaned_data['operation'] == 'multiply'

    def test_valid_negative_numbers(self):
        """Test that negative number inputs are validated correctly."""
        data = {
            'operand_a': '-5',
            'operand_b': '-3',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is True
        assert form.cleaned_data['operand_a'] == Decimal('-5')
        assert form.cleaned_data['operand_b'] == Decimal('-3')

    def test_valid_zero_operands(self):
        """Test that zero values are validated correctly."""
        data = {
            'operand_a': '0',
            'operand_b': '0',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is True
        assert form.cleaned_data['operand_a'] == Decimal('0')
        assert form.cleaned_data['operand_b'] == Decimal('0')


class TestCalculatorFormMissingFields:
    """Tests for missing required fields."""

    def test_missing_operand_a(self):
        """Test that missing operand_a causes validation error."""
        data = {
            'operand_b': '5',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors

    def test_missing_operand_b(self):
        """Test that missing operand_b causes validation error."""
        data = {
            'operand_a': '5',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_b' in form.errors

    def test_missing_operation(self):
        """Test that missing operation causes validation error."""
        data = {
            'operand_a': '5',
            'operand_b': '3'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operation' in form.errors

    def test_all_fields_missing(self):
        """Test that empty form data causes validation errors for all fields."""
        data = {}
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors
        assert 'operand_b' in form.errors
        assert 'operation' in form.errors


class TestCalculatorFormInvalidInputs:
    """Tests for invalid form inputs."""

    def test_non_numeric_operand_a(self):
        """Test that non-numeric operand_a causes validation error."""
        data = {
            'operand_a': 'abc',
            'operand_b': '5',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors

    def test_non_numeric_operand_b(self):
        """Test that non-numeric operand_b causes validation error."""
        data = {
            'operand_a': '5',
            'operand_b': 'xyz',
            'operation': 'subtract'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_b' in form.errors

    def test_both_fields_non_numeric(self):
        """Test that both non-numeric operands cause validation errors."""
        data = {
            'operand_a': 'abc',
            'operand_b': 'xyz',
            'operation': 'multiply'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors
        assert 'operand_b' in form.errors

    def test_empty_string_operands(self):
        """Test that empty string values cause validation errors."""
        data = {
            'operand_a': '',
            'operand_b': '',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors
        assert 'operand_b' in form.errors

    def test_whitespace_only_operands(self):
        """Test that whitespace-only values cause validation errors."""
        data = {
            'operand_a': '   ',
            'operand_b': '   ',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors
        assert 'operand_b' in form.errors

    def test_invalid_operation_choice(self):
        """Test that invalid operation choice causes validation error."""
        data = {
            'operand_a': '5',
            'operand_b': '3',
            'operation': 'invalid_operation'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operation' in form.errors


class TestCalculatorFormEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_large_numbers(self):
        """Test that very large numbers within range are accepted."""
        data = {
            'operand_a': '999999999999999',
            'operand_b': '1',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is True

    def test_very_small_numbers(self):
        """Test that very small decimal numbers are accepted."""
        data = {
            'operand_a': '0.0000000001',
            'operand_b': '0.0000000002',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is True

    def test_number_out_of_range_high(self):
        """Test that numbers above max range cause validation error."""
        data = {
            'operand_a': '9999999999999999',  # Above 1e15
            'operand_b': '1',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors

    def test_number_out_of_range_low(self):
        """Test that numbers below min range cause validation error."""
        data = {
            'operand_a': '-9999999999999999',  # Below -1e15
            'operand_b': '1',
            'operation': 'add'
        }
        form = CalculatorForm(data=data)
        assert form.is_valid() is False
        assert 'operand_a' in form.errors

    def test_all_operations_valid(self):
        """Test that all valid operations are accepted."""
        operations = ['add', 'subtract', 'multiply', 'divide']
        for op in operations:
            data = {
                'operand_a': '10',
                'operand_b': '5',
                'operation': op
            }
            form = CalculatorForm(data=data)
            assert form.is_valid() is True, f"Operation '{op}' should be valid"
