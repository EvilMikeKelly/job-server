# Generated by Django 5.0.7 on 2024-07-23 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0002_add_short_data_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="studyinformationpage",
            name="read_analytic_methods_policy",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")], null=True
            ),
        ),
    ]
