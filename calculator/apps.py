"""
App configuration for the calculator application.
"""

from django.apps import AppConfig


class CalculatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculator'

    def ready(self):
        """
        Called when the app is ready.
        """
        pass
