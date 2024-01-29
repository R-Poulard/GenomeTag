from django.db.models.signals import post_migrate, post_save
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from GenomeTag.models import CustomUser, userPermission


@receiver(post_migrate)
def create_group(sender, **kwargs):
    viewer_group, created = Group.objects.get_or_create(name="viewer_group")
    annotator_group, created = Group.objects.get_or_create(name="annotator_group")
    reviewer_group, created = Group.objects.get_or_create(name="reviewer_group")

    # Get or create permissions
    content_type = ContentType.objects.get_for_model(
        userPermission
    )  # Adjust with your actual model
    view_permission, created_view = Permission.objects.get_or_create(
        codename="view", name="Can view annotation", content_type=content_type
    )
    annotate_permission, created_annotate = Permission.objects.get_or_create(
        codename="annotate", name="Can annotate sequences", content_type=content_type
    )
    review_permission, created_review = Permission.objects.get_or_create(
        codename="review", name="Can review sequences", content_type=content_type
    )

    # Assign permissions to groups based on user role
    viewer_group.permissions.add(view_permission)
    annotator_group.permissions.add(view_permission, annotate_permission)
    reviewer_group.permissions.add(view_permission, annotate_permission, review_permission)


@receiver(post_save, sender=CustomUser)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        role = instance.role
        if role == "v":
            group = Group.objects.get(name="viewer_group")
            instance.groups.add(group)
        elif role == "a":
            group = Group.objects.get(name="annotator_group")
            instance.groups.add(group)
        elif role == "r":
            group = Group.objects.get(name="reviewer_group")
            instance.groups.add(group)
