#!/usr/bin/env python3
"""
Tests for GitHub Client

Verifies unified GitHub API client functionality including authentication,
request handling, rate limiting, and common operations.
"""

import json
import os
import subprocess
from unittest.mock import Mock, patch

import pytest
import requests

from cli_multi_rapid.domain.github_client import (
    GitHubClient,
    GitHubRepository,
)


class TestGitHubRepository:
    """Test GitHubRepository dataclass."""

    def test_repository_creation(self):
        """Test creating repository instance."""
        repo = GitHubRepository(
            owner="test-owner",
            name="test-repo",
            full_name="test-owner/test-repo",
            description="Test repository",
            stars=100,
            forks=50,
        )

        assert repo.owner == "test-owner"
        assert repo.name == "test-repo"
        assert repo.full_name == "test-owner/test-repo"
        assert repo.description == "Test repository"
        assert repo.stars == 100
        assert repo.forks == 50
        assert repo.topics == []  # Default from __post_init__

    def test_repository_with_topics(self):
        """Test repository with topics."""
        repo = GitHubRepository(
            owner="test-owner",
            name="test-repo",
            full_name="test-owner/test-repo",
            topics=["python", "cli", "automation"],
        )

        assert repo.topics == ["python", "cli", "automation"]


class TestGitHubClientInitialization:
    """Test GitHub client initialization and configuration."""

    def test_client_initialization_with_token(self):
        """Test client initialization with explicit token."""
        client = GitHubClient(token="test-token-123")

        assert client.token == "test-token-123"
        assert client.api_base == "https://api.github.com"
        assert client.timeout == 30
        assert client.is_authenticated()

    def test_client_initialization_from_env(self):
        """Test client initialization from environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token-456"}):
            client = GitHubClient()

            assert client.token == "env-token-456"
            assert client.is_authenticated()

    def test_client_initialization_without_token(self):
        """Test client initialization without token."""
        with patch.dict(os.environ, {}, clear=True):
            client = GitHubClient()

            assert client.token is None
            assert not client.is_authenticated()

    def test_client_custom_api_base(self):
        """Test client with custom API base URL."""
        client = GitHubClient(token="test", api_base="https://github.example.com/api/v3/")

        assert client.api_base == "https://github.example.com/api/v3"  # Trailing slash removed

    def test_client_custom_user_agent(self):
        """Test client with custom user agent."""
        client = GitHubClient(token="test", user_agent="MyApp/2.0")

        assert client.user_agent == "MyApp/2.0"


class TestGitHubClientHeaders:
    """Test HTTP header generation."""

    def test_get_headers_with_token(self):
        """Test headers include authentication."""
        client = GitHubClient(token="test-token")
        headers = client.get_headers()

        assert headers["Authorization"] == "token test-token"
        assert headers["Accept"] == "application/vnd.github.v3+json"
        assert headers["User-Agent"] == "CLI-Orchestrator/1.0"

    def test_get_headers_without_token(self):
        """Test headers without authentication."""
        with patch.dict(os.environ, {}, clear=True):
            client = GitHubClient()  # No token
            headers = client.get_headers()

            assert "Authorization" not in headers
            assert headers["Accept"] == "application/vnd.github.v3+json"

    def test_get_headers_with_extra_headers(self):
        """Test adding extra headers."""
        client = GitHubClient(token="test-token")
        headers = client.get_headers({"X-Custom-Header": "value"})

        assert headers["X-Custom-Header"] == "value"
        assert headers["Authorization"] == "token test-token"


class TestGitHubClientRequests:
    """Test HTTP request methods."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return GitHubClient(token="test-token")

    @patch("cli_multi_rapid.domain.github_client.requests.get")
    def test_get_request_success(self, mock_get, client):
        """Test successful GET request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"test": "data"}'
        mock_response.json.return_value = {"test": "data"}
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890",
        }
        mock_get.return_value = mock_response

        # Make request
        result = client.get("repos/test/repo")

        assert result == {"test": "data"}
        assert client._rate_limit_remaining == 4999
        mock_get.assert_called_once()

    @patch("cli_multi_rapid.domain.github_client.requests.post")
    def test_post_request_success(self, mock_post, client):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = b'{"created": true}'
        mock_response.json.return_value = {"created": True}
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890",
        }
        mock_post.return_value = mock_response

        result = client.post("repos/test/repo/issues", data={"title": "Test"})

        assert result == {"created": True}
        mock_post.assert_called_once()

    @patch("cli_multi_rapid.domain.github_client.requests.get")
    def test_request_error_response(self, mock_get, client):
        """Test request with error response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.json.return_value = {"message": "Not Found"}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        result = client.get("repos/nonexistent/repo")

        assert "error" in result
        assert "404" in result["error"]

    @patch("cli_multi_rapid.domain.github_client.requests.get")
    def test_request_timeout(self, mock_get, client):
        """Test request timeout handling."""
        mock_get.side_effect = requests.exceptions.Timeout()

        result = client.get("repos/test/repo")

        assert "error" in result
        assert "timeout" in result["error"].lower()

    @patch("cli_multi_rapid.domain.github_client.requests.get")
    def test_request_connection_error(self, mock_get, client):
        """Test connection error handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        result = client.get("repos/test/repo")

        assert "error" in result
        assert "failed" in result["error"].lower()

    def test_request_without_authentication(self):
        """Test request without token."""
        with patch.dict(os.environ, {}, clear=True):
            client = GitHubClient()  # No token
            result = client.get("repos/test/repo")

            assert "error" in result
            assert "token not found" in result["error"].lower()

    def test_unsupported_http_method(self, client):
        """Test unsupported HTTP method."""
        result = client.request("repos/test/repo", method="INVALID")

        assert "error" in result
        assert "Unsupported HTTP method" in result["error"]


class TestGitHubClientRateLimiting:
    """Test rate limit handling."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return GitHubClient(token="test-token")

    @patch("cli_multi_rapid.domain.github_client.requests.get")
    def test_get_rate_limit(self, mock_get, client):
        """Test fetching rate limit status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"rate": {"limit": 5000, "remaining": 4999}}'
        mock_response.json.return_value = {"rate": {"limit": 5000, "remaining": 4999}}
        mock_response.headers = {}
        mock_get.return_value = mock_response

        rate_limit = client.get_rate_limit()

        assert rate_limit["limit"] == 5000
        assert rate_limit["remaining"] == 4999

    def test_check_rate_limit_allows_requests(self, client):
        """Test rate limit check when requests allowed."""
        client._rate_limit_remaining = 100

        assert client.check_rate_limit() is True

    def test_check_rate_limit_blocks_requests(self, client):
        """Test rate limit check when limit exceeded."""
        client._rate_limit_remaining = 0

        assert client.check_rate_limit() is False

    def test_check_rate_limit_unknown_status(self, client):
        """Test rate limit check with unknown status."""
        assert client.check_rate_limit() is True  # Allow by default


class TestGitHubClientRepositoryOperations:
    """Test repository operations."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return GitHubClient(token="test-token")

    def test_parse_github_repo_from_ssh_url(self):
        """Test parsing repo from SSH URL."""
        url = "git@github.com:test-owner/test-repo.git"
        repo = GitHubClient.parse_github_repo_from_url(url)

        assert repo == "test-owner/test-repo"

    def test_parse_github_repo_from_https_url(self):
        """Test parsing repo from HTTPS URL."""
        url = "https://github.com/test-owner/test-repo.git"
        repo = GitHubClient.parse_github_repo_from_url(url)

        assert repo == "test-owner/test-repo"

    def test_parse_github_repo_from_https_url_no_git(self):
        """Test parsing repo from HTTPS URL without .git."""
        url = "https://github.com/test-owner/test-repo"
        repo = GitHubClient.parse_github_repo_from_url(url)

        assert repo == "test-owner/test-repo"

    def test_parse_github_repo_invalid_url(self):
        """Test parsing invalid URL."""
        repo = GitHubClient.parse_github_repo_from_url("invalid-url")

        assert repo is None

    @patch("cli_multi_rapid.domain.github_client.subprocess.run")
    def test_get_repository_from_remote_success(self, mock_run, client):
        """Test getting repository from git remote."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "git@github.com:test-owner/test-repo.git\n"
        mock_run.return_value = mock_result

        repo = client.get_repository_from_remote()

        assert repo == "test-owner/test-repo"

    @patch("cli_multi_rapid.domain.github_client.subprocess.run")
    def test_get_repository_from_remote_failure(self, mock_run, client):
        """Test getting repository when git command fails."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        repo = client.get_repository_from_remote(fallback_repo="fallback/repo")

        assert repo == "fallback/repo"

    @patch("cli_multi_rapid.domain.github_client.subprocess.run")
    def test_get_repository_from_remote_timeout(self, mock_run, client):
        """Test getting repository when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 10)

        repo = client.get_repository_from_remote()

        assert repo == "unknown/unknown"

    @patch.object(GitHubClient, "get")
    def test_get_repository_success(self, mock_get, client):
        """Test fetching repository information."""
        mock_get.return_value = {
            "name": "test-repo",
            "full_name": "test-owner/test-repo",
            "description": "Test repository",
            "owner": {"login": "test-owner"},
            "html_url": "https://github.com/test-owner/test-repo",
            "default_branch": "main",
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
            "size": 1024,
            "language": "Python",
            "topics": ["cli", "automation"],
        }

        repo = client.get_repository("test-owner/test-repo")

        assert repo is not None
        assert repo.name == "test-repo"
        assert repo.owner == "test-owner"
        assert repo.stars == 100
        assert repo.language == "Python"

    @patch.object(GitHubClient, "get")
    def test_get_repository_not_found(self, mock_get, client):
        """Test fetching nonexistent repository."""
        mock_get.return_value = {"error": "Not found"}

        repo = client.get_repository("nonexistent/repo")

        assert repo is None


class TestGitHubClientIssueOperations:
    """Test issue operations."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return GitHubClient(token="test-token")

    @patch.object(GitHubClient, "get")
    def test_list_issues(self, mock_get, client):
        """Test listing issues."""
        mock_get.return_value = [
            {"number": 1, "title": "Issue 1"},
            {"number": 2, "title": "Issue 2"},
        ]

        issues = client.list_issues("test/repo")

        assert len(issues) == 2
        assert issues[0]["title"] == "Issue 1"

    @patch.object(GitHubClient, "get")
    def test_list_issues_filters_pull_requests(self, mock_get, client):
        """Test that list_issues filters out PRs."""
        mock_get.return_value = [
            {"number": 1, "title": "Issue 1"},
            {"number": 2, "title": "PR 1", "pull_request": {}},
        ]

        issues = client.list_issues("test/repo")

        assert len(issues) == 1
        assert issues[0]["number"] == 1

    @patch.object(GitHubClient, "post")
    def test_create_issue(self, mock_post, client):
        """Test creating an issue."""
        mock_post.return_value = {"number": 123, "title": "New Issue"}

        result = client.create_issue(
            "test/repo",
            title="New Issue",
            body="Issue body",
            labels=["bug"],
        )

        assert result["number"] == 123
        mock_post.assert_called_once()

    @patch.object(GitHubClient, "patch")
    def test_update_issue(self, mock_patch, client):
        """Test updating an issue."""
        mock_patch.return_value = {"number": 123, "state": "closed"}

        result = client.update_issue("test/repo", 123, state="closed")

        assert result["state"] == "closed"
        mock_patch.assert_called_once()


class TestGitHubClientPullRequestOperations:
    """Test pull request operations."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return GitHubClient(token="test-token")

    @patch.object(GitHubClient, "get")
    def test_list_pull_requests(self, mock_get, client):
        """Test listing PRs."""
        mock_get.return_value = [
            {"number": 1, "title": "PR 1"},
            {"number": 2, "title": "PR 2"},
        ]

        prs = client.list_pull_requests("test/repo")

        assert len(prs) == 2

    @patch.object(GitHubClient, "get")
    def test_get_pull_request(self, mock_get, client):
        """Test getting PR details."""
        mock_get.return_value = {"number": 123, "title": "Test PR"}

        pr = client.get_pull_request("test/repo", 123)

        assert pr["number"] == 123

    @patch.object(GitHubClient, "post")
    def test_create_pull_request(self, mock_post, client):
        """Test creating a PR."""
        mock_post.return_value = {"number": 456, "title": "New PR"}

        result = client.create_pull_request(
            "test/repo",
            title="New PR",
            head="feature-branch",
            base="main",
            body="PR description",
        )

        assert result["number"] == 456


class TestGitHubClientReleaseOperations:
    """Test release operations."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return GitHubClient(token="test-token")

    @patch.object(GitHubClient, "get")
    def test_list_releases(self, mock_get, client):
        """Test listing releases."""
        mock_get.return_value = [
            {"tag_name": "v1.0.0"},
            {"tag_name": "v0.9.0"},
        ]

        releases = client.list_releases("test/repo")

        assert len(releases) == 2

    @patch.object(GitHubClient, "get")
    def test_get_latest_release(self, mock_get, client):
        """Test getting latest release."""
        mock_get.return_value = {"tag_name": "v1.0.0"}

        release = client.get_latest_release("test/repo")

        assert release["tag_name"] == "v1.0.0"


class TestGitHubClientUtilities:
    """Test utility methods."""

    def test_repr_authenticated(self):
        """Test string representation when authenticated."""
        client = GitHubClient(token="test-token")
        repr_str = repr(client)

        assert "authenticated" in repr_str
        assert "https://api.github.com" in repr_str

    def test_repr_not_authenticated(self):
        """Test string representation when not authenticated."""
        with patch.dict(os.environ, {}, clear=True):
            client = GitHubClient()
            repr_str = repr(client)

            assert "not authenticated" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
