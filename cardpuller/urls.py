from django.urls import path
from . import views

urlpatterns = [
    path("", views.BoxInfoView.as_view(), name="box_info"),
    path("results", views.SimulationResultView.as_view(), name="sim_info"),
]