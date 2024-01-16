from django.contrib.auth.models import AbstractUser
from django.db import models
#exemple :

# class User(models.Model):
#     mail = models.CharField(max_length=50)
#     password = models.CharField(max_length=50)
#     role = models.Choices(?)
#     etc. 

class CustomUser(AbstractUser):

    role_choices = [("v", "viewer"), ("a", "annotator"), ("r", "reviewer")]
    role = models.CharField(max_length=1, choices=role_choices, default="v", null=False)
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.username


class Genome(models.Model):
    id = models.CharField(max_length=15, primary_key=True)


class Chromosome(models.Model):
    accession_number = models.CharField(max_length=15, null=False)
    genome = models.ForeignKey(Genome, on_delete=models.PROTECT)
    sequence = models.TextField()
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    unique_together = ["accession_number", "genome"]


class Position(models.Model):
    start = models.IntegerField(default=0, null=False)
    end = models.IntegerField(default=0, null=False)
    start_relative = models.IntegerField(default=0, null=False)
    end_relative = models.IntegerField(default=0, null=False)
    strand_choices = [("+", "+"), ("-", "-")]
    strand = models.CharField(max_length=1, choices=strand_choices, default="+", null=False)
    chromosome = models.ForeignKey(Chromosome, on_delete=models.CASCADE)
    unique_together = ["start", "end", "strand", "chromosome"]
    # is strand really useful?


class Annotation(models.Model):
    # author = models.ForeignKey(User)
    accession = models.CharField(max_length=15, null=False)
    status_choices = [("u", "unreviewed"), ("r", "rejected"), ("v", "validated")]
    status = models.CharField(max_length=1, choices=status_choices, default="u", null=False)
    position = models.ManyToManyField(Position)
#TO DO check if a accesion is alone for a genome


class Review(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    # author = models.ForeignKey(User)


class Peptide(models.Model):
    accesion = models.CharField(max_length=15, null=False,)
    annotation = models.ManyToManyField(Annotation)
    sequence = models.TextField()

#TO DO: link annotation and review to the user (once all is working properly)

#Steps to modify the models:
#1) Add code above
#2) execute "python manage.py makemigrations GenomeTag" to create the modifications of the DBD
#3) do "python manage.py migrate" to apply migrations


