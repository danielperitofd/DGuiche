from django.urls import path

from tenants import views

app_name = "tenants"

urlpatterns = [
    path("", views.TenantListView.as_view(), name="list"),
    path("novo/", views.TenantCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.TenantUpdateView.as_view(), name="update"),
    path("<int:pk>/excluir/", views.TenantDeleteView.as_view(), name="delete"),
]
