from django.urls import path

from . import views

urlpatterns = [path("generation_line_chart/", views.get_generation_line_graph, name="generation_line_chart")]
