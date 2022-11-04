from datetime import datetime, timezone

import pytest
from django.core.exceptions import PermissionDenied

from staff.views.dashboards.copiloting import Copiloting

from .....factories import (
    JobFactory,
    JobRequestFactory,
    ProjectFactory,
    ReleaseFileFactory,
    UserFactory,
    WorkspaceFactory,
)


def test_copiloting_success(rf, core_developer):
    project = ProjectFactory()
    workspace = WorkspaceFactory(project=project)
    ReleaseFileFactory.create_batch(15, workspace=workspace)

    job_request1 = JobRequestFactory(workspace=workspace)
    JobFactory(
        job_request=job_request1, started_at=datetime(2020, 7, 31, tzinfo=timezone.utc)
    )
    job_request2 = JobRequestFactory(workspace=workspace)
    JobFactory(
        job_request=job_request2, started_at=datetime(2021, 9, 3, tzinfo=timezone.utc)
    )

    request = rf.get("/")
    request.user = core_developer

    response = Copiloting.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["projects"])

    project = response.context_data["projects"][0]
    assert project["date_first_run"] == datetime(
        2020, 7, 31, 0, 0, 0, tzinfo=timezone.utc
    )
    assert project["files_released_count"] == 15
    assert project["job_request_count"] == 2
    assert project["workspace_count"] == 1


def test_copiloting_unauthorized(rf):
    request = rf.get("/")
    request.user = UserFactory()

    with pytest.raises(PermissionDenied):
        Copiloting.as_view()(request)
