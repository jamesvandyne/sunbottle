from django.urls import path

from . import views

urlpatterns = [
    path("", views.Index.as_view(), name="home"),
    path("savings/", views.Savings.as_view(), name="savings"),
]
