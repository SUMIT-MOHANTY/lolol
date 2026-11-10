"""
Models for the calculator application.
"""

from django.db import models


class OperationType(models.Model):
    """
    Reference data for supported operations.
    """
    name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)

    def __str__(self) -> str:
        return self.display_name


class CalculationRequest(models.Model):
    """
    Stores calculation requests for audit/history purposes.
    """
    operand_a = models.DecimalField(max_digits=25, decimal_places=10)
    operand_b = models.DecimalField(max_digits=25, decimal_places=10)
    operation = models.CharField(max_length=20)
    result = models.DecimalField(max_digits=50, decimal_places=10, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.operand_a} {self.operation} {self.operand_b}"
