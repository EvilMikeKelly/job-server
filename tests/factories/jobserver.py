from datetime import datetime, timezone

import factory
import factory.fuzzy
from social_django.models import UserSocialAuth

from jobserver.models import (
    Backend,
    BackendMembership,
    Job,
    JobRequest,
    Org,
    OrgMembership,
    Project,
    ProjectMembership,
    Snapshot,
    Stats,
    User,
    Workspace,
)


class BackendFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Backend

    slug = factory.Sequence(lambda n: f"backend-{n}")
    name = factory.Sequence(lambda n: f"Backend {n}")
    level_4_url = factory.Sequence(lambda n: f"http://example.com/{n}")
    jobrunner_state = {}


class BackendMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BackendMembership

    backend = factory.SubFactory("tests.factories.BackendFactory")
    user = factory.SubFactory("tests.factories.UserFactory")

    created_by = factory.SubFactory("tests.factories.UserFactory")


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    job_request = factory.SubFactory("tests.factories.JobRequestFactory")

    identifier = factory.Sequence(lambda n: f"identifier-{n}")

    updated_at = factory.fuzzy.FuzzyDateTime(datetime(2020, 1, 1, tzinfo=timezone.utc))


class JobRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobRequest

    backend = factory.SubFactory("tests.factories.BackendFactory")
    created_by = factory.SubFactory("tests.factories.UserFactory")
    workspace = factory.SubFactory("tests.factories.WorkspaceFactory")

    requested_actions = []


class OrgFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Org

    name = factory.Sequence(lambda n: f"Organisation {n}")
    slug = factory.Sequence(lambda n: f"organisation-{n}")


class OrgMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrgMembership

    org = factory.SubFactory("tests.factories.OrgFactory")
    user = factory.SubFactory("tests.factories.UserFactory")


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    org = factory.SubFactory("tests.factories.OrgFactory")

    name = factory.Sequence(lambda n: f"Project {n}")
    slug = factory.Sequence(lambda n: f"project-{n}")


class ProjectMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectMembership

    project = factory.SubFactory("tests.factories.ProjectFactory")
    user = factory.SubFactory("tests.factories.UserFactory")


class SnapshotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Snapshot

    created_by = factory.SubFactory("tests.factories.UserFactory")
    workspace = factory.SubFactory("tests.factories.WorkspaceFactory")


class StatsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Stats

    backend = factory.SubFactory("tests.factories.BackendFactory")

    api_last_seen = factory.Faker("date_time", tzinfo=timezone.utc)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user-{n}")
    email = factory.Sequence(lambda n: f"user-{n}@example.com")
    notifications_email = factory.Sequence(lambda n: f"user-{n}@example.com")


class UserSocialAuthFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSocialAuth

    user = factory.SubFactory("tests.factories.UserFactory")


class WorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Workspace

    project = factory.SubFactory("tests.factories.ProjectFactory")
    created_by = factory.SubFactory("tests.factories.UserFactory")

    name = factory.Sequence(lambda n: f"workspace-{n}")
    repo = factory.Sequence(lambda n: "http://example.com/org-{n}/repo-{n}")
