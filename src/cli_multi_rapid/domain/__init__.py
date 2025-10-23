#!/usr/bin/env python3
"""
Domain Layer - Business Logic and External Service Integrations

The domain layer contains business logic and external service clients that are
shared across multiple adapters. This promotes code reuse and maintains a clean
separation of concerns.
"""

from .github_client import GitHubClient, GitHubRepository

__all__ = [
    "GitHubClient",
    "GitHubRepository",
]
