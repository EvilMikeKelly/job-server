# Generated by Django 4.1.2 on 2023-01-23 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0010_add_check_constraints_for_paired_release_file_fields"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="releasefilereview",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("created_at__isnull", True), ("created_by__isnull", True)
                    ),
                    models.Q(
                        ("created_at__isnull", False), ("created_by__isnull", False)
                    ),
                    _connector="OR",
                ),
                name="jobserver_releasefilereview_both_created_at_and_created_by_set",
            ),
        ),
    ]
