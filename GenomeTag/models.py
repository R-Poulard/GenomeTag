from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    role_choices = [("v", "viewer"), ("a", "annotator"), ("r", "reviewer")]
    role = models.CharField(choices=role_choices, default="v", null=False, max_length=9)
    is_active = models.BooleanField(default=False)
    phone = PhoneNumberField(blank=True, null=True)
    affiliation = models.CharField(null=True, max_length=20)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Set is_active to True for superuser
        if self.is_superuser:
            self.is_active = True

        super().save(*args, **kwargs)


class RoleChangeRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    new_role = models.CharField(choices=CustomUser.role_choices, max_length=9)
    reason = models.TextField()
    is_approved = models.BooleanField(default=False)


class Genome(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    DOI = models.CharField(max_length=30, default="")
    species = models.CharField(max_length=30, default="")
    commentary = models.TextField(default="")
    annotable = models.BooleanField(default=True)

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


class Tag(models.Model):
    tag_id = models.CharField(max_length=10, primary_key=True)
    text = models.TextField()


class Annotation(models.Model):
    accession = models.CharField(max_length=15, null=False,primary_key=False, unique=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status_choices = [("u", "unreviewed"), ("r", "rejected"), ("v", "validated")]
    status = models.CharField(max_length=1, choices=status_choices, default="u", null=False)
    position = models.ManyToManyField(Position)
    tags = models.ManyToManyField(Tag)
    commentary = models.TextField(default="")
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,related_name="reviewer")
# TO DO check if a accesion is alone for a genome


class Review(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    commentary = models.TextField(default="")
    posted_date = models.DateField(default=timezone.now)


class Peptide(models.Model):
    accesion = models.CharField(
        max_length=15,
        null=False, unique=True
    )
    annotation = models.ManyToManyField(Annotation)
    sequence = models.TextField()
    tags = models.ManyToManyField(Tag)
    commentary = models.TextField(default="")


class Attribution(models.Model):
    annotator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    possition = models.ManyToManyField(Position)
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="planner")


class userPermission(models.Model):
    class Meta:
        managed = False

        default_permissions = ()

        permissions = [
            ("view", "Can view annotation"),
            ("annotate", "Can annotate sequences"),
            ("review", "Can review sequences"),
        ]


class Mailbox(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    sender = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Topic(models.Model):
    Name=models.CharField(max_length=30)
    Creator=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    Closed=models.BooleanField(default=False)
    creation_date = models.DateField(default=timezone.now)


class Message(models.Model):
    Topic=models.ForeignKey(Topic,on_delete=models.CASCADE)
    Content=models.TextField(max_length=250,null=False)
    Author=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    likes=models.ManyToManyField(CustomUser,related_name="liked")
    posted_date= models.DateField(default=timezone.now)
