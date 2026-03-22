from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.SaaSLogoutView.as_view(), name="logout"),
    path("preview/common/", views.start_common_preview, name="preview_common"),
    path("preview/normal/", views.stop_common_preview, name="preview_normal"),
    path("usuarios/", views.UserListView.as_view(), name="list"),
    path("usuarios/novo/", views.UserCreateView.as_view(), name="create"),
    path("usuarios/<int:pk>/editar/", views.UserUpdateView.as_view(), name="update"),
    path("usuarios/<int:pk>/excluir/", views.UserDeleteView.as_view(), name="delete"),
]

