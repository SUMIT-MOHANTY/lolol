"""
URL configuration for the calculator app.
"""

from django.urls import path
from calculator.views import CalculatorView, ResetView

urlpatterns = [
    path('', CalculatorView.as_view(), name='calculate'),
    path('reset/', ResetView.as_view(), name='reset'),
]
