from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import SignUpView

app_name = "GenomeTag"

urlpatterns = [
    path("", views.main, name="main"),
    path("userPermission/", views.userPermission, name="userPermission"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("annotations/", views.annotations, name="annotations"),
    path("create/", views.create, name="create"),
    path("search/", views.search, name="search"),
    path("result/", views.result, name="result"),
    path("create/create_annotation/<int:attribution_id>/", views.create_annotation, name="create_annotation")

]
