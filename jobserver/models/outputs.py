from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from ulid import ULID

from jobserver.models.common import new_ulid_str


def absolute_file_path(path):
    abs_path = settings.RELEASE_STORAGE / path
    return abs_path


class Release(models.Model):
    """A set of reviewed and redacted outputs from a Workspace"""

    class Statuses(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    id = models.CharField(  # noqa: A003
        default=new_ulid_str, max_length=26, primary_key=True, editable=False
    )

    @property
    def ulid(self):
        return ULID.from_str(self.id)

    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.PROTECT,
        related_name="releases",
    )
    backend = models.ForeignKey(
        "Backend",
        on_delete=models.PROTECT,
        related_name="releases",
    )
    created_at = models.DateTimeField(default=timezone.now)
    # the user who requested the release
    created_by = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="releases",
    )
    status = models.TextField(choices=Statuses.choices, default=Statuses.REQUESTED)

    # list of files requested for release
    requested_files = models.JSONField()

    def get_absolute_url(self):
        return reverse(
            "release-detail",
            kwargs={
                "org_slug": self.workspace.project.org.slug,
                "project_slug": self.workspace.project.slug,
                "workspace_slug": self.workspace.name,
                "pk": self.id,
            },
        )

    def get_api_url(self):
        return reverse("api:release", kwargs={"release_id": self.id})

    def get_download_url(self):
        return reverse(
            "release-download",
            kwargs={
                "org_slug": self.workspace.project.org.slug,
                "project_slug": self.workspace.project.slug,
                "workspace_slug": self.workspace.name,
                "pk": self.id,
            },
        )


class ReleaseFile(models.Model):
    """Individual files in a Release.

    We store these in the file system to avoid db bloat and so that we can
    serve them via nginx.
    """

    id = models.CharField(  # noqa: A003
        default=new_ulid_str, max_length=26, primary_key=True, editable=False
    )

    @property
    def ulid(self):
        return ULID.from_str(self.id)

    deleted_by = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        null=True,
        related_name="deleted_files",
    )
    release = models.ForeignKey(
        "Release",
        on_delete=models.PROTECT,
        related_name="files",
    )
    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.PROTECT,
        related_name="files",
    )
    # the user who approved the release
    created_by = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="released_files",
    )

    # name is path from the POV of the researcher, e.g "outputs/file1.txt"
    name = models.TextField()
    # path is from the POV of the system e.g. "workspace/releases/RELEASE_ID/file1.txt"
    path = models.TextField()
    # the sha256 hash of the file
    filehash = models.TextField()
    size = models.IntegerField()  # bytes
    mtime = models.DateTimeField()

    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_deleted_fields_both_set",
                check=(
                    Q(
                        deleted_at__isnull=True,
                        deleted_by__isnull=True,
                    )
                    | Q(
                        deleted_at__isnull=False,
                        deleted_by__isnull=False,
                    )
                ),
            )
        ]

    def __format__(self, format_spec):
        match format_spec:
            case "b":
                return f"{self.size:,}b"
            case "Kb":
                value = round(self.size / 1024, 2)
                return f"{value:,}Kb"
            case "Mb":
                value = round(self.size / (1024 * 1024), 2)
                return f"{value:,}Mb"
            case _:
                return super().__format__(format_spec)

    def absolute_path(self):
        return absolute_file_path(self.path)

    def get_absolute_url(self):
        return reverse(
            "release-detail",
            kwargs={
                "org_slug": self.release.workspace.project.org.slug,
                "project_slug": self.release.workspace.project.slug,
                "workspace_slug": self.release.workspace.name,
                "pk": self.release.id,
                "path": self.name,
            },
        )

    def get_api_url(self):
        """The API url that will serve up this file."""
        if getattr(self, "is_published", False):
            # This is a hack so the view for viewing a published ReleaseFile
            # can pass down the knowledge that a ReleaseFile has been
            # published, avoid O(N) queries on views which aren't expecting to
            # have to add `.select_related("snapshot")` to a QuerySet.
            return reverse(
                "published-file",
                kwargs={
                    "org_slug": self.workspace.project.org.slug,
                    "project_slug": self.workspace.project.slug,
                    "workspace_slug": self.workspace.name,
                    "file_id": self.id,
                },
            )

        return reverse("api:release-file", kwargs={"file_id": self.id})

    def get_delete_url(self):
        return reverse(
            "release-file-delete",
            kwargs={
                "org_slug": self.release.workspace.project.org.slug,
                "project_slug": self.release.workspace.project.slug,
                "workspace_slug": self.release.workspace.name,
                "pk": self.release.id,
                "release_file_id": self.id,
            },
        )

    def get_latest_url(self):
        return reverse(
            "workspace-latest-outputs-detail",
            kwargs={
                "org_slug": self.release.workspace.project.org.slug,
                "project_slug": self.release.workspace.project.slug,
                "workspace_slug": self.release.workspace.name,
                "path": f"{self.release.backend.slug}/{self.name}",
            },
        )

    @property
    def is_deleted(self):
        """Has the file on disk been deleted?"""
        return not self.absolute_path().exists()


class Snapshot(models.Model):
    """A "frozen" copy of the ReleaseFiles for a Workspace."""

    class Statuses(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    created_by = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="snapshots",
    )
    files = models.ManyToManyField(
        "ReleaseFile",
        related_name="snapshots",
    )
    published_by = models.ForeignKey(
        "User",
        null=True,
        on_delete=models.PROTECT,
        related_name="published_snapshots",
    )
    workspace = models.ForeignKey(
        "Workspace",
        on_delete=models.PROTECT,
        related_name="snapshots",
    )

    created_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(null=True)

    def __str__(self):
        status = "Published" if self.published_at else "Draft"
        return f"{status} Snapshot made by {self.created_by.username}"

    def get_absolute_url(self):
        return reverse(
            "workspace-snapshot-detail",
            kwargs={
                "org_slug": self.workspace.project.org.slug,
                "project_slug": self.workspace.project.slug,
                "workspace_slug": self.workspace.name,
                "pk": self.pk,
            },
        )

    def get_api_url(self):
        return reverse(
            "api:snapshot",
            kwargs={
                "workspace_id": self.workspace.name,
                "snapshot_id": self.pk,
            },
        )

    def get_download_url(self):
        return reverse(
            "workspace-snapshot-download",
            kwargs={
                "org_slug": self.workspace.project.org.slug,
                "project_slug": self.workspace.project.slug,
                "workspace_slug": self.workspace.name,
                "pk": self.pk,
            },
        )

    def get_publish_api_url(self):
        return reverse(
            "api:snapshot-publish",
            kwargs={
                "workspace_id": self.workspace.name,
                "snapshot_id": self.pk,
            },
        )

    @property
    def is_draft(self):
        return self.published_at is None

    @property
    def is_published(self):
        return self.published_at
