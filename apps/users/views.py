from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, CreateView, DeleteView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from apps.users.models import User
from .forms import UserAdminForm

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


# --- CRUD ADMIN ---

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.role in [User.Role.ADMINISTRATIVO, User.Role.DIRECCION] or self.request.user.is_superuser
        )

class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "user_list"
    paginate_by = 10

class UserCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserAdminForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")
    success_message = _("Usuario creado correctamente")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password("Nfc2024*")
        return super().form_valid(form)

class UserUpdateAdminView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserAdminForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")
    success_message = _("Usuario actualizado correctamente")

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users:list")
    
    def form_valid(self, form):
        messages.success(self.request, _("Usuario eliminado correctamente"))
        return super().form_valid(form)

def user_toggle_active_view(request, pk):
    if not request.user.is_authenticated or (request.user.role not in [User.Role.ADMINISTRATIVO, User.Role.DIRECCION] and not request.user.is_superuser):
        return redirect("home")
    
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = "desbloqueado" if user.is_active else "bloqueado"
        messages.success(request, f"Usuario {status} correctamente.")
    return redirect("users:list")
