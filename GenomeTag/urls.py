from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

app_name = "GenomeTag"
urlpatterns = [
    path("", views.main, name="main"),
    path("authenticate/", views.authenticate, name="authenticate"),
    path("annotations/", views.annotations, name="annotations"),
    path("create/", views.create, name="create")
]