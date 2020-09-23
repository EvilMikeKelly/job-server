# Generated by Django 3.0.7 on 2020-08-13 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0015_auto_20200812_1341"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="job",
            name="db",
        ),
        migrations.AddField(
            model_name="workspace",
            name="db",
            field=models.CharField(
                choices=[
                    ("dummy", "Dummy database"),
                    ("slice", "Cut-down (but real) database"),
                    ("full", "Full database"),
                ],
                default="tpp",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="joboutput",
            name="privacy_level",
            field=models.CharField(
                choices=[
                    ("highly_sensitive", "Highly sensitive"),
                    ("moderately_sensitive", "Moderately sensitive"),
                    ("minimally_sensitive", "Minimally sensitive"),
                ],
                max_length=30,
            ),
        ),
    ]
