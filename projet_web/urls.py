"""
URL configuration for projet_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.urls import include
from django.views.generic import RedirectView


urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("GenomeTag/", include("GenomeTag.urls")),
    path("GenomeTag/", include("django.contrib.auth.urls")),
]

# Add annotator url to the site and default the page to annotator
urlpatterns += [
    path("annotator/", include("annotator.urls")),
    path("", RedirectView.as_view(url="annotator/")),
]