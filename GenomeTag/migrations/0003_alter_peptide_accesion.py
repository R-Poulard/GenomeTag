# Generated by Django 5.0 on 2024-02-08 11:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("GenomeTag", "0002_remove_attribution_possition_attribution_possition"),
    ]

    operations = [
        migrations.AlterField(
            model_name="peptide",
            name="accesion",
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
