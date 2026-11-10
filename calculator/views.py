"""
Views for the calculator application.
"""

from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from calculator.forms import CalculatorForm
from calculator.services import CalculationService
from calculator.dtos import CalculationInputDTO, CalculationResultDTO
from calculator.exceptions import DivisionByZeroError, OverflowResultError
from calculator.repositories import CalculationRequestRepository
from decimal import Decimal


class CalculatorView(View):
    """
    Handles GET and POST requests for the calculator form.

    GET  /  → Render blank CalculatorForm with no result or error.
    POST /  → Validate form, compute result, render with result or error.
    """

    template_name: str = "calculator/calculator.html"
    repository: CalculationRequestRepository = CalculationRequestRepository()

    def get(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """
        Render an empty, unbound CalculatorForm.
        """
        form = CalculatorForm()
        context = self._build_context(form)
        return render(request, self.template_name, context)

    def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """
        Validate POST data, invoke CalculationService, render result.
        """
        form = CalculatorForm(data=request.POST)
        result_dto: CalculationResultDTO | None = None

        if form.is_valid():
            # Extract validated data
            operand_a = form.cleaned_data['operand_a']
            operand_b = form.cleaned_data['operand_b']
            operation = form.cleaned_data['operation']

            try:
                # Perform calculation
                result = CalculationService.calculate(operand_a, operand_b, operation)
                result_dto = CalculationResultDTO(
                    result=result,
                    error_message=None
                )
            except DivisionByZeroError as e:
                result_dto = CalculationResultDTO(
                    result=None,
                    error_message=str(e)
                )
            except OverflowResultError as e:
                result_dto = CalculationResultDTO(
                    result=None,
                    error_message=str(e)
                )
            except ValueError as e:
                result_dto = CalculationResultDTO(
                    result=None,
                    error_message=str(e)
                )

        context = self._build_context(form, result_dto)
        return render(request, self.template_name, context)

    def _build_context(
        self,
        form: CalculatorForm,
        result_dto: CalculationResultDTO | None = None,
    ) -> dict:
        """
        Build the template context dictionary.
        """
        context = {
            'form': form,
            'result': None,
            'error_message': None,
        }

        if result_dto:
            context['result'] = result_dto.result
            context['error_message'] = result_dto.error_message

        return context


class ResetView(View):
    """
    Handles GET /reset/ — clears calculator state by redirecting
    to the blank calculator form at /.
    """

    def get(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponseRedirect:
        """
        Redirect to calculator root URL.
        """
        return redirect('calculate')
