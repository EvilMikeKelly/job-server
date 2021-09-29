from staff.views.index import Index

from ....factories import (
    BackendFactory,
    ProjectFactory,
    ProjectMembershipFactory,
    UserFactory,
    WorkspaceFactory,
)


def test_index_without_search(rf, core_developer):
    request = rf.get("/")
    request.user = core_developer

    response = Index.as_view()(request)

    assert response.context_data["q"] is None
    assert response.context_data["results"] == []


def test_index_search(rf, core_developer):
    backend = BackendFactory(name="GHickman's Research Thing")
    BackendFactory.create_batch(2)

    user = UserFactory(username="ghickman")
    UserFactory.create_batch(5)

    workspace = WorkspaceFactory(name="ghickmans-workspace")
    WorkspaceFactory.create_batch(10)

    project1 = ProjectFactory(name="GHickman's First Project")
    ProjectMembershipFactory(project=project1, user=user)

    project2 = ProjectFactory(name="Ghickman's Second Project")
    ProjectMembershipFactory(project=project2, user=user)

    request = rf.get("/?q=ghickman")
    request.user = core_developer

    response = Index.as_view()(request)

    assert response.context_data["q"] == "ghickman"

    results = response.context_data["results"]

    assert len(results) == 4
    assert results == [
        ("Backend", [backend]),
        ("Project", [project1, project2]),
        ("User", [user]),
        ("Workspace", [workspace]),
    ]
