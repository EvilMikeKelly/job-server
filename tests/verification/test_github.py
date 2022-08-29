import pytest
from environs import Env

from jobserver.github import GitHubAPI

from ..fakes import FakeGitHubAPI


pytestmark = [
    pytest.mark.verification,
]


@pytest.fixture
def github_api():
    """create a new API instance so that we can use a separate token for these tests"""
    return GitHubAPI(token=Env().str("GITHUB_TOKEN_TESTING"))


def compare(fake, real):
    """
    Compare outputs of FakeGitHubAPI instances to those from GitHubAPI

    FakeGitHubAPI returns partial, non-real data from the methods it
    implements.  For tests we haven't found the need to have those responses be
    real data, but we still what their shape and values to be correct in terms
    of GitHub's API response schema.  This function checks the correctness of
    those values.
    """

    assert type(fake) == type(real)

    if isinstance(fake, list):
        for x, y in zip(fake, real):
            compare(x, y)
        return

    if isinstance(fake, str):
        return

    for key, value in fake.items():
        assert key in real
        assert isinstance(value, type(real[key]))

        if isinstance(value, dict):
            compare(fake[key], real[key])


def test_create_issue(enable_network, github_api):
    # use a private repo to test here so we can mirror what the output checkers
    # are doing
    args = [
        "opensafely-testing",
        "github-api-testing-private",
        "Test Issue",
        "test content",
        ["testing"],
    ]

    real = github_api.create_issue(*args)
    fake = FakeGitHubAPI().create_issue(*args)

    compare(fake, real)

    assert real is not None


def test_get_branch(enable_network, github_api):
    args = ["opensafely-testing", "github-api-testing", "main"]

    real = github_api.get_branch(*args)
    fake = FakeGitHubAPI().get_branch(*args)

    compare(fake, real)

    assert real is not None


def test_get_branch_with_missing_branch(enable_network, github_api):
    assert github_api.get_branch("opensafely-testing", "some_repo", "missing") is None


def test_get_branch_sha(enable_network, github_api):
    args = ["opensafely-testing", "github-api-testing", "test-get_branch_sha"]

    real = github_api.get_branch_sha(*args)
    fake = FakeGitHubAPI().get_branch_sha(*args)

    assert real == "71650d527c9288f90aa01d089f5a9884b683f7ed"

    # get_branch_sha is a wrapper for get_branch to extract just the SHA as a
    # string so no need to throw compare() at it
    assert isinstance(fake, str)


def test_get_branch_sha_with_missing_branch(enable_network, github_api):
    sha = github_api.get_branch_sha(
        "opensafely-testing",
        "some_repo",
        "missing",
    )

    assert sha is None


def test_get_commits(enable_network, github_api):
    args = ["opensafely-testing", "github-api-testing"]

    real = github_api.get_commits(*args)
    fake = FakeGitHubAPI().get_commits(*args)

    compare(fake, real)


def test_get_file(enable_network, github_api):
    args = ["opensafely-testing", "github-api-testing", "main"]

    real = github_api.get_file(*args)
    fake = FakeGitHubAPI().get_file(*args)

    compare(fake, real)


def test_get_file_missing_project_yml(enable_network, github_api):
    output = github_api.get_file(
        "opensafely-testing",
        "github-api-testing",
        "missing_project",
    )

    assert output is None


def test_get_repo(enable_network, github_api):
    args = ["opensafely-testing", "github-api-testing"]

    real = github_api.get_repo(*args)
    fake = FakeGitHubAPI().get_repo(*args)

    compare(fake, real)


def test_get_repo_is_private(enable_network, github_api):
    args = ["opensafely-testing", "github-api-testing-private"]

    assert github_api.get_repo_is_private(*args)
    assert FakeGitHubAPI().get_repo_is_private(*args)


def test_get_repo_is_private_with_unknown_repo(enable_network, github_api):
    assert github_api.get_repo_is_private("opensafely-testing", "unknown") is None


def test_get_repo_with_unknown_repo(enable_network, github_api):
    assert github_api.get_repo("opensafely-testing", "unknown") is None


def test_get_repos_with_branches(enable_network, github_api):
    args = ["opensafely-testing"]

    real = list(github_api.get_repos_with_branches(*args))
    fake = FakeGitHubAPI().get_repos_with_branches(*args)

    compare(fake, real)


def test_get_repos_with_dates(enable_network, github_api):
    args = ["opensafely-testing"]

    real = list(github_api.get_repos_with_dates(*args))
    fake = FakeGitHubAPI().get_repos_with_dates(*args)

    compare(fake, real)


def test_graphql_error_handling(enable_network, github_api):
    """
    Are we raising errors around unexpected GraphQL responses?

    Some GraphQL responses, typically to malformed queries, don't return a
    `data` key in their response.
    """
    query = """
    query {
      viewer {
        not_a_real_field
      }
    }
    """

    with pytest.raises(RuntimeError):
        list(github_api._iter_query_results(query))


def test_unauthenticated_request(enable_network):
    assert GitHubAPI().get_repo("opensafely-testing", "github-api-testing")
