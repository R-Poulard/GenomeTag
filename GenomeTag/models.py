from django.db import models

# Create your models here.

#Ici il faut ajouter tous les modèles de notre schéma de BDD

#exemple :

# class User(models.Model):
#     mail = models.CharField(max_length=50)
#     password = models.CharField(max_length=50)
#     role = models.Choices(?)
#     etc. 




#Ordre des étapes pour modifications des modèles :
#1) ajouter les modèles ici
#2) faire "python manage.py makemigrations GenomeTag" pour créer les modifications de la BDD
#3) puis "python manage.py migrate" pour appliquer les migrations


