from datetime import timedelta

from django.utils import timezone

from staff.views.repos import RepoList

from ....factories import JobFactory, JobRequestFactory, WorkspaceFactory
from ....fakes import FakeGitHubAPI
from ....utils import minutes_ago


def test_repolist_success(rf, core_developer):
    eleven_months_ago = timezone.now() - timedelta(days=30 * 11)

    workspace1 = WorkspaceFactory(repo="https://github.com/opensafely-core/job-server")
    jr_1 = JobRequestFactory(workspace=workspace1)
    JobFactory(job_request=jr_1, started_at=minutes_ago(eleven_months_ago, 3))
    JobFactory(job_request=jr_1, started_at=minutes_ago(eleven_months_ago, 2))
    JobFactory(job_request=jr_1, started_at=minutes_ago(eleven_months_ago, 1))

    workspace2 = WorkspaceFactory(repo="https://github.com/opensafely-core/job-runner")
    jr_2 = JobRequestFactory(workspace=workspace2)
    JobFactory(job_request=jr_2, started_at=minutes_ago(eleven_months_ago, 2))

    workspace3 = WorkspaceFactory(repo="https://github.com/opensafely-core/job-server")
    jr_3 = JobRequestFactory(workspace=workspace3)
    JobFactory(job_request=jr_3, started_at=minutes_ago(eleven_months_ago, 10))

    workspace4 = WorkspaceFactory(repo="https://github.com/opensafely-core/job-server")
    jr_4 = JobRequestFactory(workspace=workspace4)
    JobFactory(job_request=jr_4, started_at=None)

    workspace5 = WorkspaceFactory(repo="test-url")
    JobRequestFactory(workspace=workspace5)

    request = rf.get("/")
    request.user = core_developer

    response = RepoList.as_view(get_github_api=FakeGitHubAPI)(request)

    assert response.status_code == 200

    job_runner, job_server, _ = sorted(
        response.context_data["repos"], key=lambda r: r["name"]
    )
    assert job_runner["workspace"].first_run == minutes_ago(eleven_months_ago, 2)
    assert job_server["workspace"].first_run == minutes_ago(eleven_months_ago, 10)
