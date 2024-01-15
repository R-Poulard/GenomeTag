from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

app_name = "GenomeTag"
urlpatterns = [
    path("", views.IndexView.as_view(), name="main"),
]