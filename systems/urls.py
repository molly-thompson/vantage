from django.urls import path

from . import views

app_name = "systems"

urlpatterns = [
    path("", views.index, name="index"),
]
