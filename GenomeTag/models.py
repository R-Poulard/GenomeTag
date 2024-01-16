from django.contrib.auth.models import AbstractUser
from django.db import models

# exemple :

# class User(models.Model):
#     mail = models.CharField(max_length=50)
#     password = models.CharField(max_length=50)
#     role = models.Choices(?)
#     etc.


class CustomUser(AbstractUser):
    role_choices = [("v", "viewer"), ("a", "annotator"), ("r", "reviewer")]
    role = models.CharField(choices=role_choices, default="v", null=False, max_length=9)
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.username


# Ordre des étapes pour modifications des modèles :
# 1) ajouter les modèles ici
# 2) faire "python manage.py makemigrations GenomeTag" pour créer les modifications de la BDD
# 3) puis "python manage.py migrate" pour appliquer les migrations
