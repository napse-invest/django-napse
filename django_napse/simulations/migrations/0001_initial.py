# Generated by Django 4.1.7 on 2023-08-10 11:32

from django.db import migrations, models
import django.db.models.deletion
import django_napse.utils.constants
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("django_napse_core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Simulation",
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
                    "simulation_reference",
                    models.UUIDField(editable=False, null=True, unique=True),
                ),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "bot",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="simulation",
                        to="django_napse_core.bot",
                    ),
                ),
                (
                    "space",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_napse_core.napsespace",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SimulationDataPoint",
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
                ("date", models.DateTimeField()),
                ("value", models.FloatField()),
                ("action", models.CharField(max_length=10)),
                (
                    "simulation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_points",
                        to="django_napse_simulations.simulation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SimulationQueue",
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
                    "simulation_reference",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("canceled", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        default=django_napse.utils.constants.SIMULATION_STATUS["IDLE"],
                        max_length=12,
                    ),
                ),
                ("completion", models.FloatField(default=0.0)),
                ("eta", models.DurationField(blank=True, null=True)),
                ("error", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "bot",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_napse_core.bot",
                    ),
                ),
                (
                    "space",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_napse_core.napsespace",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SimulationDataPointExtraInfo",
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
                ("key", models.CharField(max_length=64)),
                ("value", models.CharField(max_length=64)),
                ("target_type", models.CharField(max_length=64)),
                (
                    "data_point",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_info",
                        to="django_napse_simulations.simulationdatapoint",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DataSetQueue",
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
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "controller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dataset_queues",
                        to="django_napse_core.controller",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DataSet",
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
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                ("last_update", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        default=django_napse.utils.constants.DOWNLOAD_STATUS["IDLE"],
                        max_length=12,
                    ),
                ),
                ("completion", models.FloatField(default=0.0)),
                ("eta", models.DurationField(blank=True, null=True)),
                (
                    "controller",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dataset",
                        to="django_napse_core.controller",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Candle",
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
                ("open_time", models.DateTimeField()),
                ("open", models.FloatField()),
                ("high", models.FloatField()),
                ("low", models.FloatField()),
                ("close", models.FloatField()),
                ("volume", models.FloatField()),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="candles",
                        to="django_napse_simulations.dataset",
                    ),
                ),
            ],
            options={
                "unique_together": {("dataset", "open_time")},
            },
        ),
    ]
