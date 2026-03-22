from django.urls import path

from atendimento import panel_views, views

app_name = "atendimento"

urlpatterns = [
    path("", views.AtendimentoListView.as_view(), name="list"),
    path("checkin/<int:pk>/", views.CheckInView.as_view(), name="checkin"),
    path("encaixe/novo/", views.EncaixeCreateView.as_view(), name="encaixe_create"),
    path("chamar-proximo/", views.ChamarProximoView.as_view(), name="chamar_proximo"),
    path("painel/", panel_views.ChamadaPainelView.as_view(), name="painel"),
    path("<int:pk>/concluir/", views.ConcluirAtendimentoView.as_view(), name="concluir"),
    path("<int:pk>/ausente/", views.MarcarAusenteView.as_view(), name="ausente"),
]
