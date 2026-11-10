"""
Pytest fixtures for Django Calculator test suite.
"""

import pytest
from decimal import Decimal
from django.test import Client
from django.urls import reverse


@pytest.fixture
def calculator_url():
    """Return the URL for the calculator view."""
    return reverse('calculate')


@pytest.fixture
def reset_url():
    """Return the URL for the reset view."""
    return reverse('reset')


@pytest.fixture
def health_url():
    """Return the URL for the health check endpoint."""
    return reverse('health:health')


@pytest.fixture
def valid_calculation_data():
    """Return valid calculation data for form testing."""
    return {
        'operand_a': '10',
        'operand_b': '5',
        'operation': 'add'
    }


@pytest.fixture
def decimal_calculation_data():
    """Return valid decimal calculation data for form testing."""
    return {
        'operand_a': '3.14',
        'operand_b': '2.71',
        'operation': 'add'
    }


@pytest.fixture
def csrf_enforced_client():
    """Return a Django test client with CSRF enforcement enabled."""
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def db_settings(settings):
    """Ensure test database isolation and debug mode for detailed errors."""
    settings.DEBUG = True
    return settings
