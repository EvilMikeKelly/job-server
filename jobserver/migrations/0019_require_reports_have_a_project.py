# Generated by Django 4.1.2 on 2023-02-03 10:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0018_backfill_reports_project_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="reports",
                to="jobserver.project",
            ),
        ),
    ]
