# Generated by Django 4.0.6 on 2022-07-22 13:23

from django.conf import settings
from django.db import migrations


def empty_file_sizes(apps, schema_editor):
    ReleaseFile = apps.get_model("jobserver", "ReleaseFile")

    ReleaseFile.objects.update(size=None)


def set_file_sizes(apps, schema_editor):
    ReleaseFile = apps.get_model("jobserver", "ReleaseFile")

    # set deleted files to zero.  Locally we might have inflated files with
    # random data for testing so trust in our deleted_* fields instead.
    ReleaseFile.objects.filter(deleted_at__isnull=False).update(size=0)

    for rfile in ReleaseFile.objects.filter(deleted_at__isnull=True):
        # we have to recreate ReleaseFile.absolute_path() here because model
        # methods aren't included in frozen models
        path = settings.RELEASE_STORAGE / rfile.path

        rfile.size = path.stat().st_size if path.exists() else 0
        rfile.save()


class Migration(migrations.Migration):

    dependencies = [
        ("jobserver", "0035_add_releasefile_size"),
    ]

    operations = [
        migrations.RunPython(
            set_file_sizes,
            reverse_code=empty_file_sizes,
        )
    ]
