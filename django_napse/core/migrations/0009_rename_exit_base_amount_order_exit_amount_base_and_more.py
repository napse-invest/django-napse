# Generated by Django 4.2.7 on 2024-01-11 22:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_napse_core", "0008_bothistory"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="exit_base_amount",
            new_name="exit_amount_base",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="exit_quote_amount",
            new_name="exit_amount_quote",
        ),
    ]
