from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
from .views import SignUpView
from . import views

app_name = "GenomeTag"

urlpatterns = [
    
    path("", views.main, name="main"),
    path("userPermission/", views.userPermission, name="userPermission"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("annotations/", views.annotations, name="annotations"),
    path("create/", views.create, name="create"),
    path("search/", views.search, name="search"),
    path("review/<str:id>/", views.review_add, name="display_review"),
    path("result/", views.result, name="result"),
    path("create/create_annotation/<int:attribution_id>/", views.create_annotation, name="create_annotation"),
    path('create/modify_annotation/<str:annotation_id>/', views.modify_annotation, name='modify_annotation'),
    path('delete_annotation/<int:attribution_id>/', views.delete_annotation, name='delete_annotation'),
    path("result/Genome/<str:id>/", views.genome, name="display_genome"),
    path("result/Genome/<str:genome_id>/<str:id>/", views.chromosome, name="display_chromosome"),
    path("result/Peptide/<str:id>/", views.peptide, name="display_peptide"),
    path("result/Annotation/<str:id>/", views.annotation, name="display_annotation"),
    path("result/Tag/<str:id>/", views.tag, name="display_tag"),
    path('download_fasta/<str:genome_id>/', views.download_fasta, name='download_fasta'),
    path('download_peptide_fasta/<int:peptide_id>/', views.download_peptide_fasta, name='download_peptide_fasta'),
]
