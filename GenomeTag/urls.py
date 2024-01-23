from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import SignUpView

app_name = "GenomeTag"

urlpatterns = [
    path("", views.main, name="main"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("authenticate/", views.authenticate, name="authenticate"),
    path("annotations/", views.annotations, name="annotations"),
    path("create/", views.create, name="create"),
    path("search/", views.search, name="search"),
]
