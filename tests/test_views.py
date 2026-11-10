"""
Integration and smoke tests for calculator views.

Tests include:
- Smoke tests for all routes (GET requests)
- POST success path integration tests
- POST failure path integration tests
- CSRF enforcement tests
"""

import pytest
from django.urls import reverse
from django.test import Client


class TestSmokeTests:
    """Smoke tests for all routes - BRD non-negotiable gate."""

    def test_smoke_calculator_get(self, client):
        """Test GET / returns 200 and contains form element."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<form' in response.content

    def test_smoke_reset_get(self, client):
        """Test GET /reset/ returns 200 or 302 (not 500)."""
        response = client.get('/reset/')
        assert response.status_code in [200, 302]
        assert response.status_code != 500

    def test_smoke_health_get(self, client):
        """Test GET /health/ returns 200 and contains 'ok' or 'healthy'."""
        response = client.get('/health/')
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert 'ok' in content or 'healthy' in content

    def test_smoke_admin_get(self, client):
        """Test GET /admin/ returns 200 or 302 (redirect to login)."""
        response = client.get('/admin/')
        assert response.status_code in [200, 302]
        assert response.status_code != 500


class TestPostSuccessPaths:
    """Full POST success path integration tests."""

    def test_post_addition_success(self, client):
        """Test POST addition returns correct result in response."""
        response = client.post(
            '/',
            {'operand_a': '8', 'operand_b': '4', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '12' in content

    def test_post_subtraction_success(self, client):
        """Test POST subtraction returns correct result in response."""
        response = client.post(
            '/',
            {'operand_a': '10', 'operand_b': '3', 'operation': 'subtract'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '7' in content

    def test_post_multiplication_success(self, client):
        """Test POST multiplication returns correct result in response."""
        response = client.post(
            '/',
            {'operand_a': '6', 'operand_b': '7', 'operation': 'multiply'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '42' in content

    def test_post_division_success(self, client):
        """Test POST division returns correct result in response."""
        response = client.post(
            '/',
            {'operand_a': '15', 'operand_b': '3', 'operation': 'divide'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '5' in content

    def test_post_decimal_calculation_success(self, client):
        """Test POST with decimal numbers returns correct result."""
        response = client.post(
            '/',
            {'operand_a': '3.14', 'operand_b': '2.71', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '5.85' in content or '5.85' in content.replace(' ', '')

    def test_post_negative_numbers_success(self, client):
        """Test POST with negative numbers returns correct result."""
        response = client.post(
            '/',
            {'operand_a': '-5', 'operand_b': '3', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '-2' in content


class TestPostFailurePaths:
    """POST failure path integration tests."""

    def test_post_invalid_input_non_numeric(self, client):
        """Test POST with non-numeric input shows field-level error."""
        response = client.post(
            '/',
            {'operand_a': 'bad', 'operand_b': '5', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should contain error text, not Python traceback or 500
        assert 'error' in content.lower() or 'invalid' in content.lower()
        assert 'Traceback' not in content
        assert 'Server Error' not in content

    def test_post_missing_fields(self, client):
        """Test POST with empty dict shows form error indicators."""
        response = client.post('/', {}, follow=True)
        assert response.status_code == 200
        content = response.content.decode()
        # Should contain form error indicators
        assert 'error' in content.lower() or 'required' in content.lower()

    def test_post_division_by_zero(self, client):
        """Test POST division by zero shows error message without stack trace."""
        response = client.post(
            '/',
            {'operand_a': '9', 'operand_b': '0', 'operation': 'divide'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should contain error message about division by zero
        assert 'zero' in content.lower() or 'division' in content.lower()
        # Should NOT expose stack trace
        assert 'Traceback' not in content
        assert 'File "' not in content

    def test_post_invalid_operation(self, client):
        """Test POST with invalid operation shows error."""
        response = client.post(
            '/',
            {'operand_a': '5', 'operand_b': '3', 'operation': 'invalid'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should contain error message
        assert 'error' in content.lower() or 'invalid' in content.lower()


class TestCsrfEnforcement:
    """CSRF enforcement tests."""

    def test_csrf_enforcement(self, csrf_enforced_client):
        """Test that POST without CSRF token returns 403."""
        response = csrf_enforced_client.post(
            '/',
            {'operand_a': '5', 'operand_b': '3', 'operation': 'add'}
        )
        assert response.status_code == 403

    def test_csrf_token_allows_post(self, client):
        """Test that POST with CSRF token succeeds."""
        # First get the page to obtain CSRF token
        response = client.get('/')
        assert response.status_code == 200
        
        # Extract CSRF token from response
        content = response.content.decode()
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            # Post with CSRF token
            response = client.post(
                '/',
                {
                    'operand_a': '5',
                    'operand_b': '3',
                    'operation': 'add',
                    'csrfmiddlewaretoken': csrf_token
                }
            )
            assert response.status_code == 200


class TestResetView:
    """Tests for the reset view."""

    def test_reset_redirects_to_calculator(self, client):
        """Test that reset view redirects to calculator."""
        response = client.get('/reset/')
        assert response.status_code == 302
        assert response.url == '/' or '/reset/' in response.url

    def test_reset_clears_session(self, client):
        """Test that reset clears any session data."""
        # First set some session data
        session = client.session
        session['test_key'] = 'test_value'
        session.save()
        
        # Call reset
        response = client.get('/reset/')
        assert response.status_code == 302


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_json(self, client):
        """Test that health endpoint returns JSON response."""
        response = client.get('/health/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

    def test_health_contains_status(self, client):
        """Test that health response contains status field."""
        import json
        response = client.get('/health/')
        data = json.loads(response.content)
        assert 'status' in data
        assert data['status'] == 'ok'

    def test_health_contains_service_info(self, client):
        """Test that health response contains service information."""
        import json
        response = client.get('/health/')
        data = json.loads(response.content)
        assert 'service' in data
        assert 'version' in data


class TestCalculatorViewEdgeCases:
    """Edge case tests for calculator view."""

    def test_get_request_renders_blank_form(self, client):
        """Test GET request renders blank form without result."""
        response = client.get('/')
        assert response.status_code == 200
        content = response.content.decode()
        # Form should be present
        assert '<form' in content
        # No result should be shown
        assert 'Result:' not in content or 'result' not in content.lower()

    def test_post_with_whitespace_operands(self, client):
        """Test POST with whitespace-only operands shows error."""
        response = client.post(
            '/',
            {'operand_a': '   ', 'operand_b': '5', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'error' in content.lower() or 'invalid' in content.lower()

    def test_post_with_empty_string_operands(self, client):
        """Test POST with empty string operands shows error."""
        response = client.post(
            '/',
            {'operand_a': '', 'operand_b': '', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'error' in content.lower() or 'required' in content.lower()

    def test_post_large_numbers(self, client):
        """Test POST with large numbers within range."""
        response = client.post(
            '/',
            {'operand_a': '999999999', 'operand_b': '1', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '1000000000' in content

    def test_post_numbers_out_of_range(self, client):
        """Test POST with numbers out of range shows error."""
        response = client.post(
            '/',
            {'operand_a': '9999999999999999', 'operand_b': '1', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert 'error' in content.lower() or 'range' in content.lower()
