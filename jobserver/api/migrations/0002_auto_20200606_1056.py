# Generated by Django 3.0.7 on 2020-06-06 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='acked',
            new_name='started',
        ),
    ]
