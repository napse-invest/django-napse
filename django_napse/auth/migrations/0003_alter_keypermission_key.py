# Generated by Django 4.2.5 on 2023-10-14 14:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("django_napse_auth", "0002_napseapikey"),
    ]

    operations = [
        migrations.AlterField(
            model_name="keypermission",
            name="key",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="permissions",
                to="django_napse_auth.napseapikey",
            ),
        ),
    ]
