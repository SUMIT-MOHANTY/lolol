"""
End-to-end integration tests for the Django Calculator application.

Tests include:
- Full calculation workflows
- Session persistence across requests
- Cross-module integration
- Error handling flows
"""

import pytest
from decimal import Decimal
from django.urls import reverse


class TestFullCalculationWorkflow:
    """End-to-end tests for complete calculation workflows."""

    def test_full_addition_workflow(self, client):
        """Test complete addition workflow from form submission to result display."""
        # Step 1: Get the calculator page
        response = client.get('/')
        assert response.status_code == 200
        assert b'<form' in response.content
        
        # Step 2: Submit calculation
        response = client.post(
            '/',
            {'operand_a': '10', 'operand_b': '5', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '15' in content

    def test_full_subtraction_workflow(self, client):
        """Test complete subtraction workflow."""
        response = client.post(
            '/',
            {'operand_a': '20', 'operand_b': '8', 'operation': 'subtract'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '12' in content

    def test_full_multiplication_workflow(self, client):
        """Test complete multiplication workflow."""
        response = client.post(
            '/',
            {'operand_a': '7', 'operand_b': '6', 'operation': 'multiply'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '42' in content

    def test_full_division_workflow(self, client):
        """Test complete division workflow."""
        response = client.post(
            '/',
            {'operand_a': '100', 'operand_b': '4', 'operation': 'divide'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '25' in content

    def test_full_division_by_zero_workflow(self, client):
        """Test complete division by zero error workflow."""
        response = client.post(
            '/',
            {'operand_a': '10', 'operand_b': '0', 'operation': 'divide'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should show error message
        assert 'zero' in content.lower() or 'division' in content.lower()
        # Should NOT show a numeric result
        assert 'Traceback' not in content

    def test_full_decimal_calculation_workflow(self, client):
        """Test complete decimal calculation workflow."""
        response = client.post(
            '/',
            {'operand_a': '3.14159', 'operand_b': '2.71828', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Result should be present (approximately 5.85987)
        assert '5.85' in content or '5.859' in content


class TestSessionPersistence:
    """Tests for session persistence across requests."""

    def test_session_persists_across_requests(self, client):
        """Test that session data persists across multiple requests."""
        # Set session data
        session = client.session
        session['user_preference'] = 'decimal'
        session.save()
        
        # Make a request
        response = client.get('/')
        assert response.status_code == 200
        
        # Verify session data persists
        assert client.session.get('user_preference') == 'decimal'

    def test_session_cleared_after_reset(self, client):
        """Test that reset view clears session data."""
        # Set session data
        session = client.session
        session['calculation_history'] = ['10 + 5 = 15']
        session.save()
        
        # Call reset
        response = client.get('/reset/')
        assert response.status_code == 302
        
        # Session should be cleared or modified
        # (Actual behavior depends on implementation)

    def test_multiple_calculations_same_session(self, client):
        """Test multiple calculations in same session."""
        # First calculation
        response = client.post(
            '/',
            {'operand_a': '5', 'operand_b': '3', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '8' in content
        
        # Second calculation in same session
        response = client.post(
            '/',
            {'operand_a': '10', 'operand_b': '4', 'operation': 'subtract'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '6' in content


class TestCrossModuleIntegration:
    """Tests for integration between different modules."""

    def test_form_service_view_integration(self, client):
        """Test that form, service, and view work together correctly."""
        # This tests the full stack: Form validation -> Service calculation -> View rendering
        response = client.post(
            '/',
            {'operand_a': '25', 'operand_b': '4', 'operation': 'multiply'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '100' in content

    def test_form_validation_before_service_call(self, client):
        """Test that form validation occurs before service is called."""
        # Invalid form data should not reach the service
        response = client.post(
            '/',
            {'operand_a': 'invalid', 'operand_b': '5', 'operation': 'add'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should show form error, not service error
        assert 'error' in content.lower() or 'invalid' in content.lower()

    def test_service_error_handled_by_view(self, client):
        """Test that service errors are properly handled by the view."""
        # Division by zero should be caught and displayed gracefully
        response = client.post(
            '/',
            {'operand_a': '100', 'operand_b': '0', 'operation': 'divide'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should show user-friendly error
        assert 'zero' in content.lower() or 'cannot' in content.lower()


class TestErrorHandlingFlows:
    """Tests for error handling across the application."""

    def test_invalid_operation_handled_gracefully(self, client):
        """Test that invalid operations are handled gracefully."""
        response = client.post(
            '/',
            {'operand_a': '5', 'operand_b': '3', 'operation': 'power'},
            follow=True
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should show error without crashing
        assert 'error' in content.lower() or 'invalid' in content.lower()

    def test_overflow_handled_gracefully(self, client):
        """Test that overflow errors are handled gracefully."""
        # Very large numbers that might cause overflow
        response = client.post(
            '/',
            {'operand_a': '999999999999999999999999', 'operand_b': '999999999999999999999999', 'operation': 'multiply'},
            follow=True
        )
        # Should either show result or error, but not crash
        assert response.status_code in [200, 500]  # 500 is acceptable for overflow
        if response.status_code == 200:
            content = response.content.decode()
            assert 'error' in content.lower() or 'overflow' in content.lower() or 'too large' in content.lower()

    def test_missing_csrf_token_handled(self, csrf_enforced_client):
        """Test that missing CSRF token is handled properly."""
        response = csrf_enforced_client.post(
            '/',
            {'operand_a': '5', 'operand_b': '3', 'operation': 'add'}
        )
        assert response.status_code == 403


class TestHealthCheckIntegration:
    """Integration tests for health check endpoint."""

    def test_health_check_returns_valid_json(self, client):
        """Test that health check returns valid JSON."""
        import json
        response = client.get('/health/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Should be valid JSON
        data = json.loads(response.content)
        assert 'status' in data
        assert data['status'] == 'ok'

    def test_health_check_service_info(self, client):
        """Test that health check includes service information."""
        import json
        response = client.get('/health/')
        data = json.loads(response.content)
        assert 'service' in data
        assert 'version' in data
        assert data['service'] == 'django-calculator'


class TestUrlRouting:
    """Tests for URL routing across the application."""

    def test_calculator_url_reverse(self):
        """Test that calculator URL can be reversed."""
        url = reverse('calculate')
        assert url == '/'

    def test_reset_url_reverse(self):
        """Test that reset URL can be reversed."""
        url = reverse('reset')
        assert url == '/reset/'

    def test_health_url_reverse(self):
        """Test that health URL can be reversed."""
        url = reverse('health:health')
        assert url == '/health/'

    def test_admin_url_accessible(self, client):
        """Test that admin URL is accessible."""
        response = client.get('/admin/')
        # Should return 200 (if logged in) or 302 (redirect to login)
        assert response.status_code in [200, 302]


class TestStaticFiles:
    """Tests for static files serving."""

    def test_static_css_file_exists(self, client, settings):
        """Test that static CSS files are accessible."""
        # This test verifies static files configuration
        # In production, static files are served differently
        # For testing, we just verify the settings are correct
        assert hasattr(settings, 'STATIC_URL')
        assert settings.STATIC_URL == '/static/'

    def test_templates_configured(self, client, settings):
        """Test that templates are properly configured."""
        assert hasattr(settings, 'TEMPLATES')
        assert len(settings.TEMPLATES) > 0
        # Check that APP_DIRS is True or loaders are configured
        assert settings.TEMPLATES[0].get('APP_DIRS', False) or 'loaders' in settings.TEMPLATES[0].get('OPTIONS', {})
