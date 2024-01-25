# Generated by Django 5.0 on 2024-01-25 11:58

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="userPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
            ],
            options={
                "permissions": [
                    ("view", "Can view annotation"),
                    ("annotate", "Can annotate sequences"),
                    ("review", "Can review sequences"),
                ],
                "managed": False,
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Genome",
            fields=[
                ("id", models.CharField(max_length=15, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("tag_id", models.CharField(max_length=10, primary_key=True, serialize=False)),
                ("text", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Chromosome",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("accession_number", models.CharField(max_length=15)),
                ("sequence", models.TextField()),
                ("start", models.IntegerField(default=0)),
                ("end", models.IntegerField(default=0)),
                (
                    "genome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="GenomeTag.genome"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("start", models.IntegerField(default=0)),
                ("end", models.IntegerField(default=0)),
                ("start_relative", models.IntegerField(default=0)),
                ("end_relative", models.IntegerField(default=0)),
                (
                    "strand",
                    models.CharField(choices=[("+", "+"), ("-", "-")], default="+", max_length=1),
                ),
                (
                    "chromosome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="GenomeTag.chromosome"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Annotation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("accession", models.CharField(max_length=15)),
                (
                    "status",
                    models.CharField(
                        choices=[("u", "unreviewed"), ("r", "rejected"), ("v", "validated")],
                        default="u",
                        max_length=1,
                    ),
                ),
                ("position", models.ManyToManyField(to="GenomeTag.position")),
                ("tags", models.ManyToManyField(to="GenomeTag.tag")),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "annotation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="GenomeTag.annotation"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Peptide",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("accesion", models.CharField(max_length=15)),
                ("sequence", models.TextField()),
                ("annotation", models.ManyToManyField(to="GenomeTag.annotation")),
                ("tags", models.ManyToManyField(to="GenomeTag.tag")),
            ],
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="email address"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("v", "viewer"), ("a", "annotator"), ("r", "reviewer")],
                        default="v",
                        max_length=9,
                    ),
                ),
                ("is_active", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Attribution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "possition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="GenomeTag.position"
                    ),
                ),
                (
                    "annotator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "requester",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="planner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
