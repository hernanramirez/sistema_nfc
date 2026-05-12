from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import AccessLog

class AccessDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AccessLog
    template_name = "acceso/dashboard.html"
    context_object_name = "logs"
    paginate_by = 50

    def test_func(self):
        return self.request.user.role in ["administrativo", "direccion"] or self.request.user.is_superuser
