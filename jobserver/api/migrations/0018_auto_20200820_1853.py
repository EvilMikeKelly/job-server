# Generated by Django 3.0.7 on 2020-08-20 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0017_auto_20200813_1317"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="joboutput",
            name="name",
        ),
        migrations.RemoveField(
            model_name="joboutput",
            name="privacy_level",
        ),
    ]
