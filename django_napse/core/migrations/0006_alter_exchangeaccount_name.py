# Generated by Django 4.2.6 on 2023-10-17 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_napse_core", "0005_exchangeaccount_default"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exchangeaccount",
            name="name",
            field=models.CharField(max_length=200),
        ),
    ]
