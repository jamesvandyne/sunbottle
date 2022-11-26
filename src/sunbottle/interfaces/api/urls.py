from django.urls import path

from . import views

urlpatterns = [
    path("generation_line_chart/", views.get_generation_line_graph, name="generation_line_chart"),
    path("generation_summary/", views.get_generation_summary, name="generation_summary"),
]
