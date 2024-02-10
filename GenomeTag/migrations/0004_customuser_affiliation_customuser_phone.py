# Generated by Django 5.0 on 2024-02-09 13:35

import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("GenomeTag", "0003_alter_peptide_accesion"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="affiliation",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
    ]
