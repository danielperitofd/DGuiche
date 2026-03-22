from django.urls import path

from dashboard.views import DashboardHomeView, DemoLandingView

app_name = "dashboard"

urlpatterns = [
    path("", DemoLandingView.as_view(), name="demo"),
    path("dashboard/", DashboardHomeView.as_view(), name="home"),
]
