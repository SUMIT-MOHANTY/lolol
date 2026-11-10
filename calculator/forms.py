"""
Calculator Form - Validates and coerces raw HTTP POST data into typed Decimal
operands and a whitelisted operation string.
"""

from django import forms
from decimal import Decimal

OPERATION_CHOICES: list[tuple[str, str]] = [
    ("add", "Addition (+)"),
    ("subtract", "Subtraction (−)"),
    ("multiply", "Multiplication (×)"),
    ("divide", "Division (÷)"),
]

OPERAND_MAX_DIGITS: int = 25
OPERAND_DECIMAL_PLACES: int = 10
OPERAND_MIN_VALUE: Decimal = Decimal("-1e15")
OPERAND_MAX_VALUE: Decimal = Decimal("1e15")


class CalculatorForm(forms.Form):
    """
    Validates and coerces raw HTTP POST data into typed Decimal
    operands and a whitelisted operation string.

    Fields
    ------
    operand_a : DecimalField
        Left-hand numeric operand. Required. Range: [-1e15, 1e15].
        Max 10 decimal places.
    operand_b : DecimalField
        Right-hand numeric operand. Required. Range: [-1e15, 1e15].
        Max 10 decimal places.
    operation : ChoiceField
        Arithmetic operation. One of: add, subtract, multiply, divide.
        Defaults to 'add'.

    Methods
    -------
    clean_operand_a() -> Decimal
        Field-level validator enforcing range constraint on operand_a.
    clean_operand_b() -> Decimal
        Field-level validator enforcing range constraint on operand_b.
    """

    operand_a: forms.DecimalField = forms.DecimalField(
        max_digits=OPERAND_MAX_DIGITS,
        decimal_places=OPERAND_DECIMAL_PLACES,
        label="First Number",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
        error_messages={
            "required": "First number is required.",
            "invalid": "Enter a valid number for the first operand.",
        },
    )

    operand_b: forms.DecimalField = forms.DecimalField(
        max_digits=OPERAND_MAX_DIGITS,
        decimal_places=OPERAND_DECIMAL_PLACES,
        label="Second Number",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
        error_messages={
            "required": "Second number is required.",
            "invalid": "Enter a valid number for the second operand.",
        },
    )

    operation: forms.ChoiceField = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        label="Operation",
        initial="add",
        widget=forms.Select(attrs={"class": "form-select"}),
        error_messages={
            "required": "Please select an arithmetic operation.",
            "invalid_choice": "Invalid operation selected.",
        },
    )

    def clean_operand_a(self) -> Decimal:
        """
        Enforce range constraint [-1e15, 1e15] on operand_a.

        Returns
        -------
        Decimal
            Validated operand_a value.

        Raises
        ------
        forms.ValidationError
            When value is outside the allowed range.
        """
        value = self.cleaned_data.get('operand_a')
        if value is not None:
            if value < OPERAND_MIN_VALUE or value > OPERAND_MAX_VALUE:
                raise forms.ValidationError(
                    f"Value must be between {OPERAND_MIN_VALUE} and {OPERAND_MAX_VALUE}."
                )
        return value

    def clean_operand_b(self) -> Decimal:
        """
        Enforce range constraint [-1e15, 1e15] on operand_b.

        Returns
        -------
        Decimal
            Validated operand_b value.

        Raises
        ------
        forms.ValidationError
            When value is outside the allowed range.
        """
        value = self.cleaned_data.get('operand_b')
        if value is not None:
            if value < OPERAND_MIN_VALUE or value > OPERAND_MAX_VALUE:
                raise forms.ValidationError(
                    f"Value must be between {OPERAND_MIN_VALUE} and {OPERAND_MAX_VALUE}."
                )
        return value
