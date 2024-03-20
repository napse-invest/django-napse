# Generated by Django 4.2.5 on 2023-10-14 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("rest_framework_api_key", "0005_auto_20220110_1102"),
        ("django_napse_auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NapseAPIKey",
            fields=[
                (
                    "apikey_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="rest_framework_api_key.apikey",
                    ),
                ),
                ("is_master_key", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "API key",
                "verbose_name_plural": "API keys",
                "ordering": ("-created",),
                "abstract": False,
            },
            bases=("rest_framework_api_key.apikey",),
        ),
    ]
