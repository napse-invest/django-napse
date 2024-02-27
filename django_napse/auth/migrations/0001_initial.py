# Generated by Django 4.2.5 on 2023-10-09 15:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("django_napse_core", "0001_initial"),
        ("rest_framework_api_key", "0005_auto_20220110_1102"),
    ]

    operations = [
        migrations.CreateModel(
            name="KeyPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("approved", models.BooleanField(default=False)),
                ("revoked", models.BooleanField(default=False)),
                ("permission_type", models.CharField(max_length=200)),
                (
                    "key",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="permissions",
                        to="rest_framework_api_key.apikey",
                    ),
                ),
                (
                    "space",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_napse_core.napsespace",
                    ),
                ),
            ],
            options={
                "unique_together": {("key", "space", "permission_type")},
            },
        ),
    ]
