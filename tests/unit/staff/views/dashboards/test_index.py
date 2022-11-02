import pytest
from django.core.exceptions import PermissionDenied

from staff.views.dashboards.index import DashboardIndex

from .....factories import UserFactory


def test_dashboardindex_success(rf, core_developer):
    request = rf.get("/")
    request.user = core_developer

    response = DashboardIndex.as_view()(request)

    assert response.status_code == 200


def test_dashboardindex_unauthorized(rf):
    request = rf.get("/")
    request.user = UserFactory()

    with pytest.raises(PermissionDenied):
        DashboardIndex.as_view()(request)
