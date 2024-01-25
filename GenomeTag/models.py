from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    role_choices = [("v", "viewer"), ("a", "annotator"), ("r", "reviewer")]
    role = models.CharField(choices=role_choices, default="v", null=False, max_length=9)
    is_active = models.BooleanField(default=False)
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


class Tag(models.Model):
    tag_id = models.CharField(max_length=10, primary_key=True)
    text = models.TextField()


class Annotation(models.Model):
    # author = models.ForeignKey(User)
    accession = models.CharField(max_length=15, null=False)
    status_choices = [("u", "unreviewed"), ("r", "rejected"), ("v", "validated")]
    status = models.CharField(max_length=1, choices=status_choices, default="u", null=False)
    position = models.ManyToManyField(Position)
    tags = models.ManyToManyField(Tag)
# TO DO check if a accesion is alone for a genome


class Review(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE)
    # author = models.ForeignKey(User)


class Peptide(models.Model):
    accesion = models.CharField(max_length=15, null=False,)
    annotation = models.ManyToManyField(Annotation)
    sequence = models.TextField()
    tags = models.ManyToManyField(Tag)


class Attribution(models.Model):
    annotator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    possition = models.ForeignKey(Position, on_delete=models.CASCADE)
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='planner')
    unique_together = ["annotator", "possition"]

#TO DO: link annotation and review to the user (once all is working properly)

#Steps to modify the models:
#1) Add code above
#2) execute "python manage.py makemigrations GenomeTag" to create the modifications of the DBD
#3) do "python manage.py migrate" to apply migrations


class userPermission(models.Model):
    class Meta:
        managed = False

        default_permissions = ()

        permissions = [
            ("view", "Can view annotation"),
            ("annotate", "Can annotate sequences"),
            ("review", "Can review sequences"),
        ]


@receiver(post_migrate)
def create_group(sender, **kwargs):
    viewer_group, created = Group.objects.get_or_create(name="viewer_group")
    annotator_group, created = Group.objects.get_or_create(name="annotator_group")
    reviewer_group, created = Group.objects.get_or_create(name="reviewer_group")

    # Get or create permissions
    view_permission, created_view = Permission.objects.get_or_create(
        codename="view", name="Can view annotation"
    )
    annotate_permission, created_annotate = Permission.objects.get_or_create(
        codename="annotate", name="Can annotate sequences"
    )
    review_permission, created_review = Permission.objects.get_or_create(
        codename="review", name="Can review sequences"
    )

    # Assign permissions to groups based on user role
    viewer_group.permissions.add(view_permission)
    annotator_group.permissions.add(view_permission, annotate_permission)
    reviewer_group.permissions.add(view_permission, annotate_permission, review_permission)


@receiver(post_save, sender=CustomUser)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        role = instance.role
        if role == 'v':
            group = Group.objects.get(name="viewer_group")
            instance.groups.add(group)
        elif role == 'a':
            group = Group.objects.get(name="annotator_group")
            instance.groups.add(group)
        elif role == 'r':
            group = Group.objects.get(name="reviewer_group")
            instance.groups.add(group)
