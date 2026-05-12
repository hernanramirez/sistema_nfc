from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import PaymentLog

class PaymentDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PaymentLog
    template_name = "pagos/dashboard.html"
    context_object_name = "logs"
    paginate_by = 50

    def test_func(self):
        return self.request.user.role in ["cafetin", "administrativo", "direccion"] or self.request.user.is_superuser

class UserBalanceView(LoginRequiredMixin, TemplateView):
    template_name = "pagos/balance.html"
