# Generated by Django 5.0.2 on 2024-02-26 11:41

from django.db import migrations

import jobserver.models.job_request


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0025_require_repo_for_workspace"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="jobrequest",
            managers=[
                ("objects", jobserver.models.job_request.JobRequestManager()),
            ],
        ),
    ]
