# Generated by Django 4.2.6 on 2023-10-14 21:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_napse_auth", "0003_alter_keypermission_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="napseapikey",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
