from django.urls import path

from importacao import views

app_name = "importacao"

urlpatterns = [
    path("", views.ImportacaoListView.as_view(), name="list"),
    path("nova/", views.ImportacaoCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ImportacaoDetailView.as_view(), name="detail"),
]
