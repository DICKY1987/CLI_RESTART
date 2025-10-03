"""State persistence and management for CLI orchestrator.

Provides centralized state management with:
- State file querying and lifecycle management
- Retention policy enforcement
- State archival and cleanup
- State metadata tracking
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StateMetadata(BaseModel):
    """Metadata for a state file."""

    path: str
    size_bytes: int
    created_at: str
    modified_at: str
    workflow_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class RetentionPolicy(BaseModel):
    """State retention policy configuration."""

    max_age_days: int = 30
    max_size_mb: int = 1000
    archive_before_delete: bool = True
    archive_path: str = "state/archive"
    excluded_patterns: List[str] = Field(default_factory=lambda: ["*.lock", "*.tmp"])


class StateManager:
    """Manages state files with retention policies and archival."""

    def __init__(
        self,
        state_dir: str | Path = "state",
        policy_file: str | Path = "config/state_retention_policy.json",
    ):
        """Initialize state manager.

        Args:
            state_dir: Directory containing state files
            policy_file: Path to retention policy configuration
        """
        self.state_dir = Path(state_dir)
        self.policy_file = Path(policy_file)
        self.policy = self._load_policy()

        # Ensure directories exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        Path(self.policy.archive_path).mkdir(parents=True, exist_ok=True)

    def _load_policy(self) -> RetentionPolicy:
        """Load retention policy from configuration file."""
        if self.policy_file.exists():
            try:
                with open(self.policy_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return RetentionPolicy(**data)
            except Exception:
                pass
        return RetentionPolicy()

    def list_state_files(
        self,
        pattern: str = "*.json",
        workflow_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> List[StateMetadata]:
        """List state files with metadata.

        Args:
            pattern: Glob pattern to filter files
            workflow_id: Filter by workflow ID
            session_id: Filter by session ID

        Returns:
            List of state file metadata
        """
        state_files = []

        for file_path in self.state_dir.rglob(pattern):
            if not file_path.is_file():
                continue

            # Skip excluded patterns
            if any(file_path.match(p) for p in self.policy.excluded_patterns):
                continue

            stat = file_path.stat()
            metadata = StateMetadata(
                path=str(file_path.relative_to(self.state_dir)),
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            )

            # Try to extract workflow/session IDs from file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata.workflow_id = data.get("workflow_id")
                    metadata.session_id = data.get("session_id") or data.get(
                        "coordination_id"
                    )
                    metadata.tags = data.get("tags", [])
            except Exception:
                pass

            # Apply filters
            if workflow_id and metadata.workflow_id != workflow_id:
                continue
            if session_id and metadata.session_id != session_id:
                continue

            state_files.append(metadata)

        return sorted(state_files, key=lambda x: x.modified_at, reverse=True)

    def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve state by ID.

        Args:
            state_id: State identifier (filename without extension)

        Returns:
            State data or None if not found
        """
        state_file = self.state_dir / f"{state_id}.json"
        if not state_file.exists():
            return None

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_state(
        self,
        state_id: str,
        data: Dict[str, Any],
        workflow_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Save state data with metadata.

        Args:
            state_id: State identifier
            data: State data to save
            workflow_id: Optional workflow ID
            session_id: Optional session ID
            tags: Optional tags for categorization

        Returns:
            True if successful
        """
        try:
            # Enrich data with metadata
            enriched_data = {
                **data,
                "workflow_id": workflow_id,
                "session_id": session_id,
                "tags": tags or [],
                "saved_at": datetime.now().isoformat(),
            }

            state_file = self.state_dir / f"{state_id}.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(enriched_data, f, indent=2)

            return True
        except Exception:
            return False

    def delete_state(self, state_id: str, archive: bool = True) -> bool:
        """Delete state file with optional archival.

        Args:
            state_id: State identifier
            archive: Whether to archive before deleting

        Returns:
            True if successful
        """
        state_file = self.state_dir / f"{state_id}.json"
        if not state_file.exists():
            return False

        try:
            if archive and self.policy.archive_before_delete:
                self._archive_file(state_file)

            state_file.unlink()
            return True
        except Exception:
            return False

    def _archive_file(self, file_path: Path) -> bool:
        """Archive a state file.

        Args:
            file_path: Path to file to archive

        Returns:
            True if successful
        """
        try:
            archive_dir = Path(self.policy.archive_path)
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped archive name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            archive_path = archive_dir / archive_name

            shutil.copy2(file_path, archive_path)
            return True
        except Exception:
            return False

    def clean_old_state(
        self, older_than_days: Optional[int] = None, dry_run: bool = False
    ) -> Dict[str, Any]:
        """Clean state files older than specified age.

        Args:
            older_than_days: Age threshold in days (uses policy default if None)
            dry_run: If True, only report what would be deleted

        Returns:
            Cleanup summary with statistics
        """
        age_threshold = older_than_days or self.policy.max_age_days
        cutoff_date = datetime.now() - timedelta(days=age_threshold)

        deleted_files = []
        archived_files = []
        total_space_freed = 0

        for file_path in self.state_dir.rglob("*.json"):
            if not file_path.is_file():
                continue

            # Skip excluded patterns
            if any(file_path.match(p) for p in self.policy.excluded_patterns):
                continue

            stat = file_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime)

            if modified_time < cutoff_date:
                file_size = stat.st_size
                relative_path = str(file_path.relative_to(self.state_dir))

                if not dry_run:
                    if self.policy.archive_before_delete:
                        if self._archive_file(file_path):
                            archived_files.append(relative_path)

                    file_path.unlink()
                    deleted_files.append(relative_path)
                    total_space_freed += file_size
                else:
                    deleted_files.append(relative_path)
                    total_space_freed += file_size

        return {
            "dry_run": dry_run,
            "age_threshold_days": age_threshold,
            "deleted_count": len(deleted_files),
            "archived_count": len(archived_files),
            "space_freed_bytes": total_space_freed,
            "space_freed_mb": round(total_space_freed / (1024 * 1024), 2),
            "deleted_files": deleted_files,
            "archived_files": archived_files,
        }

    def get_disk_usage(self) -> Dict[str, Any]:
        """Calculate total disk usage by state files.

        Returns:
            Disk usage statistics
        """
        total_size = 0
        file_count = 0

        for file_path in self.state_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1

        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "state_dir": str(self.state_dir),
        }

    def enforce_size_limit(self, dry_run: bool = False) -> Dict[str, Any]:
        """Enforce size limit by deleting oldest files.

        Args:
            dry_run: If True, only report what would be deleted

        Returns:
            Enforcement summary
        """
        max_size_bytes = self.policy.max_size_mb * 1024 * 1024
        current_usage = self.get_disk_usage()

        if current_usage["total_size_bytes"] <= max_size_bytes:
            return {
                "action": "none",
                "reason": "under_limit",
                "current_size_mb": current_usage["total_size_mb"],
                "limit_size_mb": self.policy.max_size_mb,
            }

        # Sort files by modification time (oldest first)
        files_by_age = []
        for file_path in self.state_dir.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files_by_age.append(
                    (file_path, stat.st_mtime, stat.st_size)
                )

        files_by_age.sort(key=lambda x: x[1])

        deleted_files = []
        total_freed = 0
        current_size = current_usage["total_size_bytes"]

        for file_path, _, file_size in files_by_age:
            if current_size <= max_size_bytes:
                break

            relative_path = str(file_path.relative_to(self.state_dir))

            if not dry_run:
                if self.policy.archive_before_delete:
                    self._archive_file(file_path)

                file_path.unlink()

            deleted_files.append(relative_path)
            total_freed += file_size
            current_size -= file_size

        return {
            "action": "deleted" if not dry_run else "would_delete",
            "dry_run": dry_run,
            "deleted_count": len(deleted_files),
            "space_freed_mb": round(total_freed / (1024 * 1024), 2),
            "new_size_mb": round(current_size / (1024 * 1024), 2),
            "limit_size_mb": self.policy.max_size_mb,
            "deleted_files": deleted_files,
        }
