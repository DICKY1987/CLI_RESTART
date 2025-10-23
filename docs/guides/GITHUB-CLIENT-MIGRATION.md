# GitHub Client Migration Guide

## Overview

This guide helps you migrate from the legacy adapter-specific GitHub API code to the unified `GitHubClient` from the domain layer.

## What Changed

### Before Refactoring

Previously, GitHub API interactions were duplicated across multiple adapters:
- `git_ops.py` - ~50 LOC of GitHub API code
- `github_integration.py` - ~55 LOC of GitHub API code

Each adapter had its own:
- `self.github_token` and `self.github_api_base` attributes
- `_github_api_request()` method
- `_get_github_repo()` method

### After Refactoring

All GitHub API interactions now use the unified `GitHubClient` from `cli_multi_rapid.domain.github_client`:
- Single source of truth (~585 LOC with comprehensive features)
- Centralized authentication, rate limiting, and error handling
- Easier to test and maintain
- Consistent API across all consumers

## Migration Steps

### 1. Import GitHubClient

**Before:**
```python
import requests
import os

class MyAdapter:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.github_api_base = "https://api.github.com"
```

**After:**
```python
from ..domain.github_client import GitHubClient

class MyAdapter:
    def __init__(self):
        self.github = GitHubClient()  # Automatically reads GITHUB_TOKEN from env
```

### 2. Replace Authentication Checks

**Before:**
```python
def is_available(self) -> bool:
    return bool(self.github_token)
```

**After:**
```python
def is_available(self) -> bool:
    return self.github.is_authenticated()
```

### 3. Replace API Requests

**Before:**
```python
def _github_api_request(self, endpoint: str, method: str = "GET", data: dict | None = None):
    headers = {
        "Authorization": f"token {self.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"{self.github_api_base}/{endpoint.lstrip('/')}"

    if method == "GET":
        response = requests.get(url, headers=headers, timeout=30)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data, timeout=30)
    # ... more methods

    if response.status_code < 400:
        return response.json() if response.content else {"success": True}
    else:
        return {"error": f"GitHub API error {response.status_code}"}
```

**After:**
```python
# No method needed! Use GitHubClient directly:

# GET request
data = self.github.get(f"repos/{repo}")

# POST request
result = self.github.post(f"repos/{repo}/issues", data={"title": "New Issue"})

# PATCH request
updated = self.github.patch(f"repos/{repo}/issues/123", data={"state": "closed"})

# DELETE request
deleted = self.github.delete(f"repos/{repo}/issues/123")
```

### 4. Replace Repository Detection

**Before:**
```python
def _get_github_repo(self) -> str:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if url.startswith("git@github.com:"):
                return url.replace("git@github.com:", "").replace(".git", "")
            elif "github.com/" in url:
                return url.split("github.com/")[-1].replace(".git", "")
    except Exception:
        pass
    return "unknown/unknown"
```

**After:**
```python
def _get_github_repo(self) -> str:
    return self.github.get_repository_from_remote(fallback_repo="unknown/unknown")
```

## New Features Available

The unified `GitHubClient` provides many features not available before:

### Rate Limiting

```python
# Check if rate limit allows more requests
if self.github.check_rate_limit():
    data = self.github.get("repos/owner/repo")
else:
    print("Rate limit exceeded")

# Get detailed rate limit info
rate_limit = self.github.get_rate_limit()
print(f"Remaining: {rate_limit.get('remaining')}")
```

### Repository Operations

```python
# Get structured repository info
repo = self.github.get_repository("owner/repo")
if repo:
    print(f"Stars: {repo.stars}, Forks: {repo.forks}")
    print(f"Language: {repo.language}")
    print(f"Topics: {', '.join(repo.topics)}")

# Parse repo from URL
repo_name = GitHubClient.parse_github_repo_from_url("https://github.com/owner/repo.git")
# Returns: "owner/repo"
```

### Issue Operations

```python
# List issues with filters
issues = self.github.list_issues(
    "owner/repo",
    state="open",
    labels=["bug", "high-priority"],
    since="2024-01-01T00:00:00Z",
)

# Create issue
new_issue = self.github.create_issue(
    "owner/repo",
    title="Bug Report",
    body="Description",
    labels=["bug"],
    assignees=["username"],
)

# Update issue
updated = self.github.update_issue(
    "owner/repo",
    issue_number=123,
    state="closed",
    labels=["resolved"],
)
```

### Pull Request Operations

```python
# List PRs
prs = self.github.list_pull_requests(
    "owner/repo",
    state="open",
    base="main",
    sort="created",
)

# Get PR details
pr = self.github.get_pull_request("owner/repo", 456)

# Create PR
new_pr = self.github.create_pull_request(
    "owner/repo",
    title="New Feature",
    head="feature-branch",
    base="main",
    body="PR description",
    draft=False,
)
```

### Release Operations

```python
# List releases
releases = self.github.list_releases("owner/repo", per_page=10)

# Get latest release
latest = self.github.get_latest_release("owner/repo")
print(f"Latest: {latest.get('tag_name')}")
```

## Error Handling

The unified client provides consistent error handling:

```python
# All methods return dict with "error" key on failure
result = self.github.get("repos/nonexistent/repo")

if "error" in result:
    print(f"Error: {result['error']}")
    print(f"Status: {result.get('status_code')}")
else:
    # Success - process result
    print(f"Repo: {result['name']}")
```

## Testing with GitHubClient

### Mocking in Tests

```python
from unittest.mock import Mock, patch
from cli_multi_rapid.domain.github_client import GitHubClient

def test_my_adapter():
    adapter = MyAdapter()

    # Mock GitHubClient.get()
    with patch.object(adapter.github, 'get') as mock_get:
        mock_get.return_value = {"name": "test-repo", "stars": 100}

        result = adapter.some_method()

        assert result["stars"] == 100
        mock_get.assert_called_once_with("repos/test/repo")
```

### Testing Authentication

```python
def test_adapter_availability():
    # With token
    adapter = MyAdapter()  # Uses GITHUB_TOKEN from env
    assert adapter.is_available()

    # Without token
    with patch.dict(os.environ, {}, clear=True):
        adapter = MyAdapter()
        assert not adapter.is_available()
```

## Configuration

### Environment Variables

The `GitHubClient` automatically reads from environment:

- `GITHUB_TOKEN` - Personal access token (required for authenticated requests)

### Custom Configuration

```python
# Custom API base (for GitHub Enterprise)
github = GitHubClient(
    api_base="https://github.company.com/api/v3",
    timeout=60,
    user_agent="MyApp/2.0",
)

# Explicit token (not recommended - use environment variable)
github = GitHubClient(token="explicit-token")
```

## Complete Migration Example

### Before (Old Code)

```python
class MyGitHubAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="my_adapter", adapter_type=AdapterType.DETERMINISTIC)
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.github_api_base = "https://api.github.com"

    def is_available(self) -> bool:
        return bool(self.github_token)

    def _github_api_request(self, endpoint, method="GET", data=None):
        if not self.github_token:
            return {"error": "No token"}
        headers = {"Authorization": f"token {self.github_token}"}
        url = f"{self.github_api_base}/{endpoint}"
        # ... request handling ...

    def get_issues(self, repo):
        return self._github_api_request(f"repos/{repo}/issues")
```

### After (New Code)

```python
from ..domain.github_client import GitHubClient

class MyGitHubAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="my_adapter", adapter_type=AdapterType.DETERMINISTIC)
        self.github = GitHubClient()

    def is_available(self) -> bool:
        return self.github.is_authenticated()

    def get_issues(self, repo):
        return self.github.list_issues(repo)  # Uses built-in method
        # OR for custom queries:
        # return self.github.get(f"repos/{repo}/issues")
```

## Benefits

1. **Less Code**: ~100 LOC reduced across adapters
2. **Single Source of Truth**: One place for GitHub API logic
3. **Better Features**: Rate limiting, structured responses, comprehensive error handling
4. **Easier Testing**: Mock one client instead of multiple methods
5. **Consistent API**: Same interface across all GitHub consumers
6. **Future-Proof**: Easy to add new features (caching, retries, etc.) in one place

## Migration Checklist

- [ ] Replace `self.github_token` and `self.github_api_base` with `self.github = GitHubClient()`
- [ ] Update `is_available()` to use `self.github.is_authenticated()`
- [ ] Replace `_github_api_request()` calls with `self.github.get/post/patch/delete()`
- [ ] Replace `_get_github_repo()` with `self.github.get_repository_from_remote()`
- [ ] Remove duplicate `_github_api_request()` and `_get_github_repo()` methods
- [ ] Update tests to mock `GitHubClient` methods
- [ ] Verify adapter still works with manual testing

## Support

For questions or issues with the migration:
1. Review the `GitHubClient` source code in `src/cli_multi_rapid/domain/github_client.py`
2. Check test examples in `tests/domain/test_github_client.py`
3. Look at migrated adapters: `git_ops.py` and `github_integration.py`

## See Also

- [GitHubClient API Reference](../architecture/github-client-api.md)
- [Domain Layer Architecture](../architecture/domain-layer.md)
- [Testing Guidelines](../guides/testing-guide.md)
