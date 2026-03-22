from django.urls import path

from guiches import views

app_name = "guiches"

urlpatterns = [
    path("", views.GuicheListView.as_view(), name="list"),
    path("novo/", views.GuicheCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.GuicheUpdateView.as_view(), name="update"),
    path("<int:pk>/excluir/", views.GuicheDeleteView.as_view(), name="delete"),
]
