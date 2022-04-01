import pytest
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404

from jobserver.authorization import (
    OutputPublisher,
    ProjectCollaborator,
    ProjectCoordinator,
    TechnicalReviewer,
)
from jobserver.utils import set_from_qs
from staff.views.users import UserDetail, UserList, UserSetOrgs

from ....factories import (
    BackendFactory,
    BackendMembershipFactory,
    OrgFactory,
    OrgMembershipFactory,
    ProjectFactory,
    ProjectMembershipFactory,
    UserFactory,
)


def test_userdetail_get_success(rf, core_developer):
    org = OrgFactory()
    project1 = ProjectFactory(org=org)
    project2 = ProjectFactory(org=org)
    user = UserFactory(roles=[OutputPublisher, TechnicalReviewer])

    # link the user to some Backends
    BackendMembershipFactory(user=user)
    BackendMembershipFactory(user=user)

    # link the user to the Org
    OrgMembershipFactory(org=org, user=user)

    # link the user to the Projects
    ProjectMembershipFactory(project=project1, user=user, roles=[ProjectCoordinator])
    ProjectMembershipFactory(project=project2, user=user, roles=[ProjectCollaborator])

    request = rf.get("/")
    request.user = core_developer

    response = UserDetail.as_view()(request, username=user.username)

    assert response.status_code == 200

    assert response.context_data["orgs"] == [
        {
            "name": org.name,
            "roles": [],
            "staff_url": org.get_staff_url(),
        },
    ]

    assert response.context_data["projects"] == [
        {
            "name": project1.name,
            "roles": ["Project Coordinator"],
            "staff_url": project1.get_staff_url(),
        },
        {
            "name": project2.name,
            "roles": ["Project Collaborator"],
            "staff_url": project2.get_staff_url(),
        },
    ]

    assert response.context_data["user"] == user


def test_userdetail_post_success(rf, core_developer):
    backend = BackendFactory()

    org = OrgFactory()
    project1 = ProjectFactory(org=org)
    project2 = ProjectFactory(org=org)
    user = UserFactory(roles=[OutputPublisher, TechnicalReviewer])

    # link the user to some Backends
    BackendMembershipFactory(user=user)
    BackendMembershipFactory(user=user)

    # link the user to the Org
    OrgMembershipFactory(org=org, user=user)

    # link the user to the Projects
    ProjectMembershipFactory(project=project1, user=user)
    ProjectMembershipFactory(project=project2, user=user)

    data = {
        "backends": [backend.slug],
        "is_superuser": ["on"],
        "roles": ["jobserver.authorization.roles.OutputPublisher"],
    }
    request = rf.post("/", data)
    request.user = core_developer

    response = UserDetail.as_view()(request, username=user.username)

    assert response.status_code == 302, response.context_data["form"].errors
    assert response.url == user.get_staff_url()

    user.refresh_from_db()
    assert set_from_qs(user.backends.all()) == {backend.pk}
    assert user.roles == [OutputPublisher]
    assert user.is_superuser


def test_userdetail_post_with_unknown_backend(rf, core_developer):
    org = OrgFactory()
    project1 = ProjectFactory(org=org)
    project2 = ProjectFactory(org=org)
    user = UserFactory(roles=[OutputPublisher, TechnicalReviewer])

    # link the user to some Backends
    BackendMembershipFactory(user=user)
    BackendMembershipFactory(user=user)

    # link the user to the Org
    OrgMembershipFactory(org=org, user=user)

    # link the user to the Projects
    ProjectMembershipFactory(project=project1, user=user)
    ProjectMembershipFactory(project=project2, user=user)

    data = {
        "backends": ["not-a-real-backend"],
        "is_superuser": [""],
        "roles": ["jobserver.authorization.roles.OutputPublisher"],
    }
    request = rf.post("/", data)
    request.user = core_developer

    response = UserDetail.as_view()(request, username=user.username)

    assert response.status_code == 200, response.url

    # check we get an error from the form, and thus are passing in the
    # submitted data correctly
    expected = {
        "backends": [
            "Select a valid choice. not-a-real-backend is not one of the available choices."
        ]
    }
    assert response.context_data["form"].errors == expected

    # check we're rendering the appropriate error in the template
    assert (
        "not-a-real-backend is not one of the available choices."
        in response.rendered_content
    )


def test_userdetail_post_with_unknown_role(rf, core_developer):

    org = OrgFactory()
    project1 = ProjectFactory(org=org)
    project2 = ProjectFactory(org=org)
    user = UserFactory(roles=[OutputPublisher, TechnicalReviewer])

    # link the user to some Backends
    BackendMembershipFactory(user=user)
    BackendMembershipFactory(user=user)

    # link the user to the Org
    OrgMembershipFactory(org=org, user=user)

    # link the user to the Projects
    ProjectMembershipFactory(project=project1, user=user)
    ProjectMembershipFactory(project=project2, user=user)

    data = {
        "backends": list(user.backends.values_list("slug", flat=True)),
        "is_superuser": ["on"],
        "roles": ["not-a-real-role"],
    }
    request = rf.post("/", data)
    request.user = core_developer

    response = UserDetail.as_view()(request, username=user.username)

    assert response.status_code == 200, response.url

    # check we get an error from the form, and thus are passing in the
    # submitted data correctly
    expected = {
        "roles": [
            "Select a valid choice. not-a-real-role is not one of the available choices."
        ]
    }
    assert response.context_data["form"].errors == expected

    # check we're rendering the appropriate error in the template
    assert (
        "not-a-real-role is not one of the available choices."
        in response.rendered_content
    )


def test_userdetail_with_unknown_user(rf, core_developer):
    request = rf.get("/")
    request.user = core_developer

    with pytest.raises(Http404):
        UserDetail.as_view()(request, username="test")


def test_userdetail_without_core_dev_role(rf):
    request = rf.get("/")
    request.user = UserFactory()

    with pytest.raises(PermissionDenied):
        UserDetail.as_view()(request, username="test")


def test_userlist_filter_by_backend(rf, core_developer):
    backend = BackendFactory()

    BackendMembershipFactory(user=UserFactory(), backend=backend)
    BackendMembershipFactory(user=UserFactory())

    request = rf.get(f"/?backend={backend.pk}")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert len(response.context_data["object_list"]) == 1


def test_userlist_filter_by_invalid_backend(rf, core_developer):
    request = rf.get("/?backend=test")
    request.user = core_developer

    with pytest.raises(BadRequest):
        UserList.as_view()(request)


def test_userlist_filter_by_invalid_missing(rf, core_developer):
    request = rf.get("/?missing=test")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert list(response.context_data["object_list"]) == [core_developer]


def test_userlist_filter_by_missing(rf, core_developer):
    backend = BackendFactory()

    BackendMembershipFactory(
        user=UserFactory(),
        created_by=core_developer,
        backend=backend,
    )

    user = UserFactory()

    request = rf.get("/?missing=backend")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert list(response.context_data["object_list"]) == [core_developer, user]


def test_userlist_filter_by_org(rf, core_developer):
    org1 = OrgFactory()
    org2 = OrgFactory()

    OrgMembershipFactory(user=UserFactory(), org=org1)
    OrgMembershipFactory(user=UserFactory(), org=org2)

    request = rf.get(f"/?org={org1.slug}")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert len(response.context_data["object_list"]) == 1


def test_userlist_filter_by_invalid_org(rf, core_developer):
    request = rf.get("/?org=test")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert len(response.context_data["object_list"]) == 0


def test_userlist_filter_by_role(rf, core_developer):
    UserFactory(roles=[OutputPublisher])
    UserFactory(roles=[TechnicalReviewer])

    request = rf.get("/?role=OutputPublisher")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert len(response.context_data["object_list"]) == 1


def test_userlist_filter_by_invalid_role(rf, core_developer):
    request = rf.get("/?role=unknown")
    request.user = core_developer

    with pytest.raises(Exception, match="^Unknown Roles:"):
        UserList.as_view()(request)


def test_userlist_find_by_username(rf, core_developer):
    UserFactory(username="ben")
    UserFactory(first_name="ben")
    UserFactory(username="seb")

    request = rf.get("/?q=ben")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert response.status_code == 200

    assert len(response.context_data["object_list"]) == 2


def test_userlist_success(rf, core_developer):
    UserFactory.create_batch(5)

    request = rf.get("/")
    request.user = core_developer

    response = UserList.as_view()(request)

    assert response.status_code == 200

    # the core_developer fixture creates a User object as well as the 5 we
    # created in the batch call above
    assert len(response.context_data["object_list"]) == 6


def test_usersetorgs_get_success(rf, core_developer):
    org1 = OrgFactory()
    org2 = OrgFactory()
    user = UserFactory()

    OrgMembershipFactory(org=org1, user=user)
    OrgMembershipFactory(org=org2, user=user)

    request = rf.get("/")
    request.user = core_developer

    response = UserSetOrgs.as_view()(request, username=user.username)

    assert response.status_code == 200
    assert response.context_data["user"] == user


def test_usersetorgs_post_success(rf, core_developer):
    existing_org = OrgFactory()
    new_org1 = OrgFactory()
    new_org2 = OrgFactory()

    user = UserFactory()

    OrgMembershipFactory(org=existing_org, user=user)

    request = rf.post("/", {"orgs": [new_org1.pk, new_org2.pk]})
    request.user = core_developer

    response = UserSetOrgs.as_view()(request, username=user.username)

    assert response.status_code == 302
    assert response.url == user.get_staff_url()

    user.refresh_from_db()
    assert set_from_qs(user.orgs.all()) == {new_org1.pk, new_org2.pk}


def test_usersetorgs_unknown_user(rf, core_developer):
    request = rf.get("/")
    request.user = core_developer
    with pytest.raises(Http404):
        UserSetOrgs.as_view()(request, username="")
