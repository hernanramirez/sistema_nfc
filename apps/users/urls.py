from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view
from .views import UserListView, UserCreateView, UserUpdateAdminView, UserDeleteView, user_toggle_active_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("list/", view=UserListView.as_view(), name="list"),
    path("create/", view=UserCreateView.as_view(), name="create"),
    path("<int:pk>/update-admin/", view=UserUpdateAdminView.as_view(), name="update_admin"),
    path("<int:pk>/delete/", view=UserDeleteView.as_view(), name="delete"),
    path("<int:pk>/toggle-active/", view=user_toggle_active_view, name="toggle_active"),
]
