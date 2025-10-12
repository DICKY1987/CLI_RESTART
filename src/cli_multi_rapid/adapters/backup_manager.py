#!/usr/bin/env python3
"""
Backup Manager Adapter

Creates recovery snapshots using git stash, file backups, and other mechanisms
to enable complete rollback if the modification pipeline fails.
"""

import json
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_adapter import AdapterResult, AdapterType, BaseAdapter


class BackupManagerAdapter(BaseAdapter):
    """Adapter for creating and managing recovery snapshots."""

    def __init__(self):
        super().__init__(
            name="backup_manager",
            adapter_type=AdapterType.DETERMINISTIC,
            description="Create recovery snapshots for rollback capability",
        )

    def execute(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        files: Optional[str] = None,
    ) -> AdapterResult:
        """Execute backup creation."""
        self._log_execution_start(step)

        try:
            with_params = self._extract_with_params(step)
            snapshot_type = with_params.get("snapshot_type", "git_stash_plus_files")
            include_untracked = with_params.get("include_untracked", True)
            verify_backup = with_params.get("verify_backup", True)

            recovery_info = {
                "snapshot_timestamp": self._get_timestamp(),
                "snapshot_type": snapshot_type,
                "working_directory": str(Path.cwd()),
                "include_untracked": include_untracked,
                "verification_requested": verify_backup,
            }

            # Create backup based on type
            if snapshot_type == "git_stash_plus_files" or snapshot_type == "git_stash":
                backup_result = self._create_git_stash_backup(include_untracked)
            elif snapshot_type == "file_copy_backup" or snapshot_type == "file_copy":
                backup_result = self._create_file_copy_backup(include_untracked)
            elif snapshot_type == "git_commit_backup" or snapshot_type == "git_commit":
                backup_result = self._create_git_commit_backup(include_untracked)
            else:
                return AdapterResult(
                    success=False, error=f"Unsupported snapshot type: {snapshot_type}"
                )

            recovery_info.update(backup_result)

            # Verify backup if requested
            if verify_backup:
                verification_result = self._verify_backup(recovery_info)
                recovery_info["verification"] = verification_result

                if not verification_result.get("verified", False):
                    return AdapterResult(
                        success=False,
                        error="Backup verification failed",
                        metadata=recovery_info,
                    )

            # Write recovery information
            emit_paths = self._extract_emit_paths(step)
            artifacts = []

            if emit_paths:
                for emit_path in emit_paths:
                    artifact_path = Path(emit_path)
                    artifact_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(artifact_path, "w", encoding="utf-8") as f:
                        json.dump(recovery_info, f, indent=2)

                    artifacts.append(str(artifact_path))
                    self.logger.info(
                        f"Recovery snapshot info written to: {artifact_path}"
                    )

            result = AdapterResult(
                success=True,
                tokens_used=0,  # Deterministic operation
                artifacts=artifacts,
                output=f"Created {snapshot_type} backup with verification: {verify_backup}",
                metadata=recovery_info,
            )

            self._log_execution_complete(result)
            return result

        except Exception as e:
            error_msg = f"Backup creation failed: {str(e)}"
            self.logger.error(error_msg)
            return AdapterResult(
                success=False,
                error=error_msg,
                metadata={"exception_type": type(e).__name__},
            )

    def validate_step(self, step: Dict[str, Any]) -> bool:
        """Validate that this adapter can execute the given step."""
        # Basic validation - flexible parameters
        return True

    def estimate_cost(self, step: Dict[str, Any]) -> int:
        """Estimate token cost (0 for deterministic operations)."""
        return 0

    def is_available(self) -> bool:
        """Check if git is available for backup operations."""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _create_git_stash_backup(self, include_untracked: bool) -> Dict[str, Any]:
        """Create backup using git stash with optional untracked files."""
        backup_info = {"backup_method": "git_stash"}

        try:
            # Check if there are changes to stash
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            has_changes = len(result.stdout.strip()) > 0
            backup_info["had_changes_to_stash"] = has_changes

            if has_changes:
                # Create stash with message
                stash_message = f"CLI Orchestrator backup - {self._get_timestamp()}"

                if include_untracked:
                    stash_cmd = ["git", "stash", "push", "-u", "-m", stash_message]
                else:
                    stash_cmd = ["git", "stash", "push", "-m", stash_message]

                result = subprocess.run(
                    stash_cmd, capture_output=True, text=True, timeout=30
                )

                if result.returncode != 0:
                    backup_info["error"] = f"Git stash failed: {result.stderr}"
                    return backup_info

                backup_info["stash_created"] = True
                backup_info["stash_message"] = stash_message

                # Get stash reference
                result = subprocess.run(
                    ["git", "stash", "list", "-1", "--format=%H"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    backup_info["stash_ref"] = result.stdout.strip()

            else:
                backup_info["stash_created"] = False
                backup_info["reason"] = "No changes to stash"

            # Also capture current commit as fallback
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                backup_info["fallback_commit"] = result.stdout.strip()

            backup_info["success"] = True

        except Exception as e:
            backup_info["success"] = False
            backup_info["error"] = str(e)

        return backup_info

    def _create_file_copy_backup(self, include_untracked: bool) -> Dict[str, Any]:
        """Create backup by copying files to a backup directory."""
        backup_info = {"backup_method": "file_copy"}

        try:
            # Create backup directory (clean if exists)
            backup_dir = Path(".cli_orchestrator_backup")

            # Clean existing backup first
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            # Now create fresh backup directory
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_info["backup_directory"] = str(backup_dir)

            # Get list of files to backup
            files_to_backup = []

            # Get tracked files
            result = subprocess.run(
                ["git", "ls-files"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                files_to_backup.extend(result.stdout.strip().split("\n"))

            # Get untracked files if requested
            if include_untracked:
                result = subprocess.run(
                    ["git", "ls-files", "--others", "--exclude-standard"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    untracked_files = result.stdout.strip().split("\n")
                    files_to_backup.extend([f for f in untracked_files if f.strip()])

            # Copy files
            copied_files = []
            for file_path in files_to_backup:
                if file_path.strip():
                    source_path = Path(file_path)
                    if source_path.exists() and source_path.is_file():
                        dest_path = backup_dir / file_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, dest_path)
                        copied_files.append(file_path)

            backup_info["files_backed_up"] = len(copied_files)
            backup_info["success"] = True

        except Exception as e:
            backup_info["success"] = False
            backup_info["error"] = str(e)

        return backup_info

    def _create_git_commit_backup(self, include_untracked: bool) -> Dict[str, Any]:
        """Create backup by making a temporary commit."""
        backup_info = {"backup_method": "git_commit"}

        try:
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            has_changes = len(result.stdout.strip()) > 0
            backup_info["had_changes_to_commit"] = has_changes

            if has_changes:
                # Add files to staging
                if include_untracked:
                    add_cmd = ["git", "add", "-A"]
                else:
                    add_cmd = ["git", "add", "-u"]

                result = subprocess.run(
                    add_cmd, capture_output=True, text=True, timeout=30
                )
                if result.returncode != 0:
                    backup_info["error"] = f"Git add failed: {result.stderr}"
                    return backup_info

                # Create backup commit
                commit_message = (
                    f"[BACKUP] CLI Orchestrator backup - {self._get_timestamp()}"
                )
                result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    backup_info["error"] = f"Git commit failed: {result.stderr}"
                    return backup_info

                backup_info["backup_commit_created"] = True
                backup_info["commit_message"] = commit_message

                # Get commit hash
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    backup_info["backup_commit_hash"] = result.stdout.strip()

            else:
                backup_info["backup_commit_created"] = False
                backup_info["reason"] = "No changes to commit"

            backup_info["success"] = True

        except Exception as e:
            backup_info["success"] = False
            backup_info["error"] = str(e)

        return backup_info

    def _verify_backup(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Verify that the backup was created successfully."""
        verification = {"verified": False, "checks": []}

        try:
            backup_method = backup_info.get("backup_method")

            if backup_method == "git_stash":
                # Verify stash exists
                if backup_info.get("stash_created"):
                    result = subprocess.run(
                        ["git", "stash", "list"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    stash_exists = backup_info.get("stash_message", "") in result.stdout
                    verification["checks"].append({"stash_exists": stash_exists})
                    verification["verified"] = stash_exists
                else:
                    verification["verified"] = True  # No changes to stash is valid
                    verification["checks"].append({"no_changes_to_stash": True})

            elif backup_method == "file_copy":
                # Verify backup directory exists and has files
                backup_dir = Path(backup_info.get("backup_directory", ""))
                if backup_dir.exists():
                    file_count = len(list(backup_dir.rglob("*")))
                    verification["checks"].append({"backup_files_count": file_count})
                    verification["verified"] = file_count > 0
                else:
                    verification["checks"].append({"backup_directory_exists": False})

            elif backup_method == "git_commit":
                # Verify commit exists
                if backup_info.get("backup_commit_created"):
                    commit_hash = backup_info.get("backup_commit_hash")
                    if commit_hash:
                        result = subprocess.run(
                            ["git", "show", "--name-only", commit_hash],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        commit_exists = result.returncode == 0
                        verification["checks"].append(
                            {"backup_commit_exists": commit_exists}
                        )
                        verification["verified"] = commit_exists
                else:
                    verification["verified"] = True  # No changes to commit is valid
                    verification["checks"].append({"no_changes_to_commit": True})

        except Exception as e:
            verification["error"] = str(e)

        return verification

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"


class BackupManager:
    """
    High-level service for managing snapshots and rollback operations.

    This is a simplified snapshot manager that stores snapshot metadata
    and provides restore capabilities. It works with the BackupManagerAdapter
    for the actual backup creation.
    """

    def __init__(self, snapshots_dir: Optional[Path] = None):
        """Initialize the BackupManager.

        Args:
            snapshots_dir: Directory to store snapshot metadata.
                          Defaults to .cli_orchestrator/snapshots/
        """
        self.snapshots_dir = snapshots_dir or Path.cwd() / ".cli_orchestrator" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.snapshots_dir / "snapshots.json"
        self._ensure_metadata_file()

    def _ensure_metadata_file(self) -> None:
        """Ensure the metadata file exists."""
        if not self.metadata_file.exists():
            self._save_metadata([])

    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Load snapshot metadata from disk."""
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_metadata(self, snapshots: List[Dict[str, Any]]) -> None:
        """Save snapshot metadata to disk."""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(snapshots, f, indent=2)

    def list_snapshots(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List available snapshots.

        Args:
            limit: Maximum number of snapshots to return (most recent first)

        Returns:
            List of snapshot metadata dictionaries
        """
        snapshots = self._load_metadata()
        # Sort by timestamp, most recent first
        snapshots.sort(key=lambda s: s.get("timestamp", ""), reverse=True)

        if limit:
            return snapshots[:limit]
        return snapshots

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific snapshot.

        Args:
            snapshot_id: ID of the snapshot to retrieve

        Returns:
            Snapshot metadata dictionary or None if not found
        """
        snapshots = self._load_metadata()
        for snapshot in snapshots:
            if snapshot.get("id") == snapshot_id:
                return snapshot
        return None

    def create_snapshot(
        self,
        description: str = "",
        snapshot_type: str = "git_stash_plus_files"
    ) -> str:
        """Create a new snapshot.

        Args:
            description: Human-readable description of the snapshot
            snapshot_type: Type of backup to create

        Returns:
            Snapshot ID
        """
        snapshot_id = self._generate_snapshot_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Use BackupManagerAdapter to create the actual backup
        adapter = BackupManagerAdapter()
        step = {
            "with": {
                "snapshot_type": snapshot_type,
                "include_untracked": True,
                "verify_backup": True
            },
            "emits": [str(self.snapshots_dir / f"{snapshot_id}.json")]
        }

        result = adapter.execute(step)

        # Calculate file count
        file_count = 0
        if result.success and result.metadata:
            if snapshot_type == "git_stash_plus_files":
                # Estimate from git status
                try:
                    status_result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    file_count = len([line for line in status_result.stdout.split("\n") if line.strip()])
                except Exception:
                    file_count = 0
            elif snapshot_type == "file_copy":
                file_count = result.metadata.get("files_backed_up", 0)

        # Store metadata
        snapshot = {
            "id": snapshot_id,
            "timestamp": timestamp,
            "description": description or f"Snapshot {snapshot_id}",
            "snapshot_type": snapshot_type,
            "file_count": file_count,
            "success": result.success,
            "backup_info": result.metadata if result.success else None,
            "error": result.error if not result.success else None
        }

        snapshots = self._load_metadata()
        snapshots.append(snapshot)
        self._save_metadata(snapshots)

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> AdapterResult:
        """Restore from a snapshot.

        Args:
            snapshot_id: ID of the snapshot to restore

        Returns:
            AdapterResult indicating success or failure
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return AdapterResult(
                success=False,
                error=f"Snapshot not found: {snapshot_id}"
            )

        if not snapshot.get("success"):
            return AdapterResult(
                success=False,
                error=f"Cannot restore from failed snapshot: {snapshot_id}"
            )

        backup_info = snapshot.get("backup_info", {})
        snapshot_type = backup_info.get("backup_method", "git_stash")

        try:
            if snapshot_type == "git_stash":
                restored_count = self._restore_from_git_stash(backup_info)
            elif snapshot_type == "file_copy":
                restored_count = self._restore_from_file_copy(backup_info)
            elif snapshot_type == "git_commit":
                restored_count = self._restore_from_git_commit(backup_info)
            else:
                return AdapterResult(
                    success=False,
                    error=f"Unsupported snapshot type: {snapshot_type}"
                )

            return AdapterResult(
                success=True,
                output=f"Restored snapshot {snapshot_id}",
                metadata={"restored_count": restored_count, "snapshot_id": snapshot_id}
            )
        except Exception as e:
            return AdapterResult(
                success=False,
                error=f"Restore failed: {str(e)}"
            )

    def _restore_from_git_stash(self, backup_info: Dict[str, Any]) -> int:
        """Restore from a git stash backup."""
        if not backup_info.get("stash_created"):
            # Nothing to restore
            return 0

        stash_ref = backup_info.get("stash_ref")
        stash_message = backup_info.get("stash_message")

        # Find the stash by message
        result = subprocess.run(
            ["git", "stash", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        stash_index = None
        for idx, line in enumerate(result.stdout.split("\n")):
            if stash_message and stash_message in line:
                stash_index = idx
                break

        if stash_index is None:
            raise ValueError("Stash not found in git stash list")

        # Apply the stash
        result = subprocess.run(
            ["git", "stash", "apply", f"stash@{{{stash_index}}}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git stash apply failed: {result.stderr}")

        # Count restored files
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return len([line for line in status_result.stdout.split("\n") if line.strip()])

    def _restore_from_file_copy(self, backup_info: Dict[str, Any]) -> int:
        """Restore from a file copy backup."""
        backup_dir = Path(backup_info.get("backup_directory", ""))
        if not backup_dir.exists():
            raise ValueError(f"Backup directory not found: {backup_dir}")

        # Restore files
        restored_count = 0
        for backup_file in backup_dir.rglob("*"):
            if backup_file.is_file():
                relative_path = backup_file.relative_to(backup_dir)
                target_path = Path.cwd() / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_path)
                restored_count += 1

        return restored_count

    def _restore_from_git_commit(self, backup_info: Dict[str, Any]) -> int:
        """Restore from a git commit backup."""
        if not backup_info.get("backup_commit_created"):
            return 0

        commit_hash = backup_info.get("backup_commit_hash")
        if not commit_hash:
            raise ValueError("No backup commit hash found")

        # Reset to the backup commit
        result = subprocess.run(
            ["git", "reset", "--hard", commit_hash],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"Git reset failed: {result.stderr}")

        # Count files in the commit
        result = subprocess.run(
            ["git", "show", "--name-only", "--format=", commit_hash],
            capture_output=True,
            text=True,
            timeout=10
        )

        return len([line for line in result.stdout.split("\n") if line.strip()])

    def find_old_snapshots(self, days: int = 30) -> List[Dict[str, Any]]:
        """Find snapshots older than the specified number of days.

        Args:
            days: Number of days threshold

        Returns:
            List of old snapshot metadata dictionaries
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        snapshots = self._load_metadata()

        old_snapshots = []
        for snapshot in snapshots:
            timestamp_str = snapshot.get("timestamp", "")
            try:
                # Parse ISO format timestamp
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if timestamp < cutoff_date:
                    old_snapshots.append(snapshot)
            except (ValueError, AttributeError):
                # If we can't parse the timestamp, skip it
                continue

        return old_snapshots

    def delete_snapshots(self, snapshots_to_delete: List[Dict[str, Any]]) -> int:
        """Delete specified snapshots.

        Args:
            snapshots_to_delete: List of snapshot metadata dictionaries to delete

        Returns:
            Number of snapshots deleted
        """
        ids_to_delete = {s.get("id") for s in snapshots_to_delete}
        snapshots = self._load_metadata()

        # Filter out snapshots to delete
        remaining_snapshots = [s for s in snapshots if s.get("id") not in ids_to_delete]
        deleted_count = len(snapshots) - len(remaining_snapshots)

        # Delete associated files
        for snapshot in snapshots_to_delete:
            snapshot_id = snapshot.get("id")
            if snapshot_id:
                snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
                if snapshot_file.exists():
                    snapshot_file.unlink()

        self._save_metadata(remaining_snapshots)
        return deleted_count

    def _generate_snapshot_id(self) -> str:
        """Generate a unique snapshot ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"snapshot_{timestamp}"
