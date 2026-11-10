"""
Repository pattern for calculator data access.
"""

from calculator.models import CalculationRequest


class CalculationRequestRepository:
    """
    Repository for CalculationRequest entities.
    """

    def save(self, request: CalculationRequest) -> CalculationRequest:
        """
        Save a CalculationRequest to the database.
        """
        request.save()
        return request

    def get_by_session_key(self, session_key: str):
        """
        Get all calculation requests for a session.
        """
        return CalculationRequest.objects.filter(session_key=session_key).order_by('-created_at')
