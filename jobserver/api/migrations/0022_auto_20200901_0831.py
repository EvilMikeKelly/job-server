# Generated by Django 3.0.7 on 2020-09-01 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_auto_20200901_0821"),
    ]

    operations = [
        migrations.RenameField(
            model_name="job",
            old_name="action",
            new_name="action_id",
        ),
    ]
