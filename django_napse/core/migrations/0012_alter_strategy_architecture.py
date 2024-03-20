# Generated by Django 4.2.7 on 2024-03-15 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("django_napse_core", "0011_alter_strategy_architecture_alter_strategy_config"),
    ]

    operations = [
        migrations.AlterField(
            model_name="strategy",
            name="architecture",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="strategy", to="django_napse_core.architecture"),
        ),
    ]