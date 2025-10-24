#!/usr/bin/env python3
"""
GitHub Client - Unified GitHub API Integration

Consolidates GitHub API interactions from multiple adapters into a single,
reusable client. Provides authentication, request handling, rate limiting,
and common GitHub operations.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


@dataclass
class GitHubRepository:
    """GitHub repository information."""

    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    url: Optional[str] = None
    default_branch: Optional[str] = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    size: int = 0
    language: Optional[str] = None
    topics: list[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = []


class GitHubClient:
    """
    Unified GitHub API client with authentication, rate limiting, and common operations.

    Consolidates GitHub API logic previously duplicated across git_ops and github_integration adapters.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        api_base: str = "https://api.github.com",
        timeout: int = 30,
        user_agent: str = "CLI-Orchestrator/1.0",
    ):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token (defaults to GITHUB_TOKEN env var)
            api_base: GitHub API base URL
            timeout: Request timeout in seconds
            user_agent: User-Agent header for requests
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent

        # Rate limit tracking
        self._rate_limit_remaining: Optional[int] = None
        self._rate_limit_reset: Optional[int] = None

    # ========== Authentication & Configuration ==========

    def is_authenticated(self) -> bool:
        """Check if client has a valid GitHub token."""
        return bool(self.token)

    def get_headers(self, extra_headers: Optional[dict] = None) -> dict[str, str]:
        """
        Build request headers with authentication.

        Args:
            extra_headers: Additional headers to include

        Returns:
            Headers dictionary
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
        }

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        if extra_headers:
            headers.update(extra_headers)

        return headers

    # ========== HTTP Request Methods ==========

    def request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make authenticated GitHub API request.

        Args:
            endpoint: API endpoint (e.g., "repos/owner/repo")
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            data: JSON body data for POST/PUT/PATCH
            params: Query parameters
            headers: Additional headers

        Returns:
            API response as dictionary (includes "error" key on failure)
        """
        if not self.is_authenticated():
            logger.warning("GitHub request without authentication token")
            return {"error": "GitHub token not found in environment"}

        # Build URL
        endpoint = endpoint.lstrip("/")
        url = f"{self.api_base}/{endpoint}"

        # Build headers
        request_headers = self.get_headers(headers)

        try:
            # Make request
            if method == "GET":
                response = requests.get(
                    url, headers=request_headers, params=params, timeout=self.timeout
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    headers=request_headers,
                    json=data,
                    params=params,
                    timeout=self.timeout,
                )
            elif method == "PUT":
                response = requests.put(
                    url,
                    headers=request_headers,
                    json=data,
                    params=params,
                    timeout=self.timeout,
                )
            elif method == "PATCH":
                response = requests.patch(
                    url,
                    headers=request_headers,
                    json=data,
                    params=params,
                    timeout=self.timeout,
                )
            elif method == "DELETE":
                response = requests.delete(
                    url, headers=request_headers, params=params, timeout=self.timeout
                )
            else:
                return {"error": f"Unsupported HTTP method: {method}"}

            # Track rate limits
            self._rate_limit_remaining = int(
                response.headers.get("X-RateLimit-Remaining", -1)
            )
            self._rate_limit_reset = int(
                response.headers.get("X-RateLimit-Reset", 0)
            )

            # Handle response
            if response.status_code < 400:
                # Success
                if response.content:
                    return response.json()
                else:
                    return {"success": True, "status_code": response.status_code}
            else:
                # Error
                error_msg = f"GitHub API error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', response.text)}"
                except Exception:
                    error_msg += f": {response.text}"

                logger.error(error_msg)
                return {
                    "error": error_msg,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout:
            error = f"GitHub API request timeout after {self.timeout}s"
            logger.error(error)
            return {"error": error}
        except requests.exceptions.RequestException as e:
            error = f"GitHub API request failed: {str(e)}"
            logger.error(error)
            return {"error": error}
        except Exception as e:
            error = f"Unexpected error in GitHub request: {str(e)}"
            logger.exception(error)
            return {"error": error}

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict[str, Any]:
        """Make GET request."""
        return self.request(endpoint, method="GET", params=params)

    def post(self, endpoint: str, data: Optional[dict] = None) -> dict[str, Any]:
        """Make POST request."""
        return self.request(endpoint, method="POST", data=data)

    def put(self, endpoint: str, data: Optional[dict] = None) -> dict[str, Any]:
        """Make PUT request."""
        return self.request(endpoint, method="PUT", data=data)

    def patch(self, endpoint: str, data: Optional[dict] = None) -> dict[str, Any]:
        """Make PATCH request."""
        return self.request(endpoint, method="PATCH", data=data)

    def delete(self, endpoint: str) -> dict[str, Any]:
        """Make DELETE request."""
        return self.request(endpoint, method="DELETE")

    # ========== Rate Limiting ==========

    def get_rate_limit(self) -> dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            Rate limit information including remaining requests and reset time
        """
        response = self.get("rate_limit")
        if "error" not in response:
            return response.get("rate", {})
        return response

    def check_rate_limit(self) -> bool:
        """
        Check if rate limit allows more requests.

        Returns:
            True if requests can be made, False if rate limited
        """
        if self._rate_limit_remaining is not None:
            if self._rate_limit_remaining <= 0:
                logger.warning("GitHub rate limit exceeded")
                return False
        return True

    # ========== Repository Operations ==========

    def get_repository_from_remote(
        self, fallback_repo: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract GitHub repository from git remote origin.

        Args:
            fallback_repo: Fallback repository name if detection fails

        Returns:
            Repository name in "owner/repo" format, or fallback
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                url = result.stdout.strip()
                return self.parse_github_repo_from_url(url)

        except subprocess.TimeoutExpired:
            logger.warning("Git remote command timed out")
        except FileNotFoundError:
            logger.warning("Git command not found")
        except Exception as e:
            logger.warning(f"Failed to get git remote: {e}")

        return fallback_repo or "unknown/unknown"

    @staticmethod
    def parse_github_repo_from_url(url: str) -> Optional[str]:
        """
        Parse GitHub repository from URL.

        Supports both SSH and HTTPS formats:
        - git@github.com:owner/repo.git
        - https://github.com/owner/repo.git
        - https://github.com/owner/repo

        Args:
            url: GitHub URL

        Returns:
            Repository name in "owner/repo" format
        """
        if not url:
            return None

        url = url.strip()

        # SSH format: git@github.com:owner/repo.git
        if url.startswith("git@github.com:"):
            repo = url.replace("git@github.com:", "").replace(".git", "")
            return repo

        # HTTPS format: https://github.com/owner/repo.git
        if "github.com/" in url:
            repo = url.split("github.com/")[-1].replace(".git", "")
            return repo

        return None

    def get_repository(self, repo: str) -> Optional[GitHubRepository]:
        """
        Get repository information.

        Args:
            repo: Repository in "owner/repo" format

        Returns:
            GitHubRepository object or None on error
        """
        response = self.get(f"repos/{repo}")

        if "error" in response:
            return None

        return GitHubRepository(
            owner=response.get("owner", {}).get("login", ""),
            name=response.get("name", ""),
            full_name=response.get("full_name", repo),
            description=response.get("description"),
            url=response.get("html_url"),
            default_branch=response.get("default_branch", "main"),
            stars=response.get("stargazers_count", 0),
            forks=response.get("forks_count", 0),
            open_issues=response.get("open_issues_count", 0),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at"),
            size=response.get("size", 0),
            language=response.get("language"),
            topics=response.get("topics", []),
        )

    # ========== Issue Operations ==========

    def list_issues(
        self,
        repo: str,
        state: str = "open",
        labels: Optional[list[str]] = None,
        assignee: Optional[str] = None,
        since: Optional[str] = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """
        List repository issues.

        Args:
            repo: Repository in "owner/repo" format
            state: Issue state (open, closed, all)
            labels: Filter by labels
            assignee: Filter by assignee
            since: Only issues updated after this timestamp
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            List of issues
        """
        params = {
            "state": state,
            "per_page": min(per_page, 100),
            "page": page,
        }

        if labels:
            params["labels"] = ",".join(labels)
        if assignee:
            params["assignee"] = assignee
        if since:
            params["since"] = since

        response = self.get(f"repos/{repo}/issues", params=params)

        if "error" in response:
            return []

        # Filter out pull requests (GitHub API returns PRs as issues)
        return [issue for issue in response if "pull_request" not in issue]

    def create_issue(
        self,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[list[str]] = None,
        assignees: Optional[list[str]] = None,
        milestone: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Create a new issue.

        Args:
            repo: Repository in "owner/repo" format
            title: Issue title
            body: Issue body (markdown)
            labels: Labels to apply
            assignees: Users to assign
            milestone: Milestone number

        Returns:
            Created issue data or error dictionary
        """
        data = {"title": title}

        if body:
            data["body"] = body
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone

        return self.post(f"repos/{repo}/issues", data=data)

    def update_issue(
        self,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Update an existing issue.

        Args:
            repo: Repository in "owner/repo" format
            issue_number: Issue number
            title: New title
            body: New body
            state: New state (open, closed)
            labels: New labels

        Returns:
            Updated issue data or error dictionary
        """
        data = {}

        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        if labels is not None:  # Allow empty list
            data["labels"] = labels

        return self.patch(f"repos/{repo}/issues/{issue_number}", data=data)

    # ========== Pull Request Operations ==========

    def list_pull_requests(
        self,
        repo: str,
        state: str = "open",
        head: Optional[str] = None,
        base: Optional[str] = None,
        sort: str = "created",
        direction: str = "desc",
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """
        List pull requests.

        Args:
            repo: Repository in "owner/repo" format
            state: PR state (open, closed, all)
            head: Filter by head branch
            base: Filter by base branch
            sort: Sort by (created, updated, popularity, long-running)
            direction: Sort direction (asc, desc)
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            List of pull requests
        """
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),
            "page": page,
        }

        if head:
            params["head"] = head
        if base:
            params["base"] = base

        response = self.get(f"repos/{repo}/pulls", params=params)

        if "error" in response:
            return []

        return response if isinstance(response, list) else []

    def get_pull_request(self, repo: str, pr_number: int) -> dict[str, Any]:
        """
        Get pull request details.

        Args:
            repo: Repository in "owner/repo" format
            pr_number: Pull request number

        Returns:
            Pull request data or error dictionary
        """
        return self.get(f"repos/{repo}/pulls/{pr_number}")

    def create_pull_request(
        self,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: Optional[str] = None,
        draft: bool = False,
    ) -> dict[str, Any]:
        """
        Create a pull request.

        Args:
            repo: Repository in "owner/repo" format
            title: PR title
            head: Head branch name
            base: Base branch name
            body: PR body (markdown)
            draft: Create as draft PR

        Returns:
            Created PR data or error dictionary
        """
        data = {
            "title": title,
            "head": head,
            "base": base,
            "draft": draft,
        }

        if body:
            data["body"] = body

        return self.post(f"repos/{repo}/pulls", data=data)

    # ========== Release Operations ==========

    def list_releases(
        self, repo: str, per_page: int = 30, page: int = 1
    ) -> list[dict[str, Any]]:
        """
        List repository releases.

        Args:
            repo: Repository in "owner/repo" format
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            List of releases
        """
        params = {"per_page": min(per_page, 100), "page": page}

        response = self.get(f"repos/{repo}/releases", params=params)

        if "error" in response:
            return []

        return response if isinstance(response, list) else []

    def get_latest_release(self, repo: str) -> dict[str, Any]:
        """
        Get latest release.

        Args:
            repo: Repository in "owner/repo" format

        Returns:
            Latest release data or error dictionary
        """
        return self.get(f"repos/{repo}/releases/latest")

    # ========== Utility Methods ==========

    def __repr__(self) -> str:
        """String representation."""
        auth_status = "authenticated" if self.is_authenticated() else "not authenticated"
        return f"GitHubClient(api_base={self.api_base}, {auth_status})"
