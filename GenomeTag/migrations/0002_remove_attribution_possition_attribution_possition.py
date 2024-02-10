# Generated by Django 5.0 on 2024-02-06 16:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("GenomeTag", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="attribution",
            name="possition",
        ),
        migrations.AddField(
            model_name="attribution",
            name="possition",
            field=models.ManyToManyField(to="GenomeTag.position"),
        ),
    ]
