from django.urls import path
from . import views

app_name = "pagos"

urlpatterns = [
    path("dashboard/", views.PaymentDashboardView.as_view(), name="dashboard"),
    path("mi-saldo/", views.UserBalanceView.as_view(), name="balance"),
]
