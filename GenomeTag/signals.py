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
def update_user_role(sender, instance, created, **kwargs):
    if created:
        role = instance.role
        assign_role(instance, role)
    else:
        latest_role = instance.role
        assign_role(instance, latest_role)


def assign_role(user, role):
    if role == "v":
        group_name = "viewer_group"
    elif role == "a":
        group_name = "annotator_group"
    elif role == "r":
        group_name = "reviewer_group"

    group = Group.objects.get(name=group_name)
    user.groups.clear()
    user.groups.add(group)
