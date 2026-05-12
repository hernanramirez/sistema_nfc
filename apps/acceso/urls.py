from django.urls import path
from . import views

app_name = "acceso"

urlpatterns = [
    path("dashboard/", views.AccessDashboardView.as_view(), name="dashboard"),
]
