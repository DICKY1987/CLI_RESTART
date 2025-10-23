#!/usr/bin/env python3
"""
Artifact Manager - Track and manage workflow artifacts

Handles artifact registration, validation, organization, and cleanup.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Artifact:
    """Metadata for a workflow artifact."""

    path: str
    step_id: str
    created_at: str
    size_bytes: int = 0
    exists: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArtifactManager:
    """
    Track and manage workflow artifacts.

    Responsibilities:
    - Register artifacts from steps
    - Validate artifact existence
    - Organize by workflow/step
    - Support cleanup
    """

    def __init__(self, artifacts_dir: str = "artifacts"):
        """
        Initialize artifact manager.

        Args:
            artifacts_dir: Base directory for artifacts
        """
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts: List[Artifact] = []

    def register_artifact(
        self,
        path: str,
        step_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """
        Register a new artifact.

        Args:
            path: Artifact file path
            step_id: ID of step that created it
            metadata: Optional metadata

        Returns:
            Artifact object
        """
        artifact_path = Path(path)

        artifact = Artifact(
            path=str(artifact_path),
            step_id=step_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            size_bytes=artifact_path.stat().st_size if artifact_path.exists() else 0,
            exists=artifact_path.exists(),
            metadata=metadata or {}
        )

        self.artifacts.append(artifact)
        return artifact

    def register_artifacts_batch(
        self,
        paths: List[str],
        step_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Artifact]:
        """
        Register multiple artifacts at once.

        Args:
            paths: List of artifact file paths
            step_id: ID of step that created them
            metadata: Optional metadata applied to all

        Returns:
            List of Artifact objects
        """
        artifacts = []
        for path in paths:
            artifact = self.register_artifact(path, step_id, metadata)
            artifacts.append(artifact)
        return artifacts

    def get_artifact(self, path: str) -> Optional[Artifact]:
        """
        Get artifact by path.

        Args:
            path: Artifact file path

        Returns:
            Artifact object if found, None otherwise
        """
        for artifact in self.artifacts:
            if artifact.path == path:
                return artifact
        return None

    def get_artifacts_by_step(self, step_id: str) -> List[Artifact]:
        """Get all artifacts created by a specific step."""
        return [a for a in self.artifacts if a.step_id == step_id]

    def get_all_artifacts(self) -> List[Artifact]:
        """Get all registered artifacts."""
        return self.artifacts.copy()

    def get_artifacts_by_pattern(self, pattern: str) -> List[Artifact]:
        """
        Get artifacts matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., "*.json", "artifacts/**/*.txt")

        Returns:
            List of matching artifacts
        """
        from fnmatch import fnmatch

        return [a for a in self.artifacts if fnmatch(a.path, pattern)]

    def validate_artifacts(self) -> Dict[str, Any]:
        """
        Validate that all registered artifacts exist.

        Returns:
            Validation report with missing/invalid artifacts
        """
        missing = [a for a in self.artifacts if not Path(a.path).exists()]

        return {
            "total": len(self.artifacts),
            "existing": len(self.artifacts) - len(missing),
            "missing": len(missing),
            "missing_paths": [a.path for a in missing],
            "valid": len(missing) == 0
        }

    def refresh_artifact_status(self) -> Dict[str, Any]:
        """
        Refresh existence status and file sizes for all artifacts.

        Returns:
            Summary of updates made
        """
        updates = {
            "checked": 0,
            "size_updated": 0,
            "status_changed": 0
        }

        for artifact in self.artifacts:
            artifact_path = Path(artifact.path)
            old_exists = artifact.exists

            artifact.exists = artifact_path.exists()
            updates["checked"] += 1

            if artifact.exists:
                new_size = artifact_path.stat().st_size
                if new_size != artifact.size_bytes:
                    artifact.size_bytes = new_size
                    updates["size_updated"] += 1

            if old_exists != artifact.exists:
                updates["status_changed"] += 1

        return updates

    def cleanup_artifacts(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up artifact files.

        Args:
            dry_run: If True, don't actually delete files

        Returns:
            Cleanup report
        """
        deleted = []
        errors = []

        for artifact in self.artifacts:
            artifact_path = Path(artifact.path)

            if not artifact_path.exists():
                continue

            if dry_run:
                deleted.append(artifact.path)
            else:
                try:
                    artifact_path.unlink()
                    deleted.append(artifact.path)
                    artifact.exists = False
                except Exception as e:
                    errors.append({"path": artifact.path, "error": str(e)})

        return {
            "dry_run": dry_run,
            "deleted": len(deleted),
            "errors": len(errors),
            "deleted_paths": deleted,
            "error_details": errors
        }

    def cleanup_artifacts_by_step(
        self,
        step_id: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Clean up artifacts from a specific step.

        Args:
            step_id: Step ID to clean up artifacts for
            dry_run: If True, don't actually delete files

        Returns:
            Cleanup report
        """
        step_artifacts = self.get_artifacts_by_step(step_id)
        deleted = []
        errors = []

        for artifact in step_artifacts:
            artifact_path = Path(artifact.path)

            if not artifact_path.exists():
                continue

            if dry_run:
                deleted.append(artifact.path)
            else:
                try:
                    artifact_path.unlink()
                    deleted.append(artifact.path)
                    artifact.exists = False
                except Exception as e:
                    errors.append({"path": artifact.path, "error": str(e)})

        return {
            "step_id": step_id,
            "dry_run": dry_run,
            "deleted": len(deleted),
            "errors": len(errors),
            "deleted_paths": deleted,
            "error_details": errors
        }

    def remove_artifact(self, path: str) -> bool:
        """
        Remove artifact from tracking (does not delete file).

        Args:
            path: Artifact file path to remove from tracking

        Returns:
            True if artifact was removed, False if not found
        """
        for i, artifact in enumerate(self.artifacts):
            if artifact.path == path:
                self.artifacts.pop(i)
                return True
        return False

    def clear_all(self) -> int:
        """
        Clear all tracked artifacts (does not delete files).

        Returns:
            Number of artifacts cleared
        """
        count = len(self.artifacts)
        self.artifacts.clear()
        return count

    def generate_manifest(self) -> Dict[str, Any]:
        """
        Generate artifact manifest.

        Returns:
            Manifest with all artifact metadata
        """
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "artifacts_dir": str(self.artifacts_dir),
            "total_artifacts": len(self.artifacts),
            "artifacts": [
                {
                    "path": a.path,
                    "step_id": a.step_id,
                    "created_at": a.created_at,
                    "size_bytes": a.size_bytes,
                    "exists": a.exists,
                    "metadata": a.metadata
                }
                for a in self.artifacts
            ]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about tracked artifacts.

        Returns:
            Statistics dictionary
        """
        total_size = sum(a.size_bytes for a in self.artifacts if a.exists)
        existing = sum(1 for a in self.artifacts if a.exists)
        missing = len(self.artifacts) - existing

        # Group by step
        steps = {}
        for artifact in self.artifacts:
            if artifact.step_id not in steps:
                steps[artifact.step_id] = {
                    "count": 0,
                    "size_bytes": 0
                }
            steps[artifact.step_id]["count"] += 1
            if artifact.exists:
                steps[artifact.step_id]["size_bytes"] += artifact.size_bytes

        return {
            "total_artifacts": len(self.artifacts),
            "existing_artifacts": existing,
            "missing_artifacts": missing,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "artifacts_by_step": steps
        }

    def export_manifest(self, output_path: str) -> bool:
        """
        Export manifest to JSON file.

        Args:
            output_path: Path to write manifest JSON

        Returns:
            True if export succeeded, False otherwise
        """
        import json

        try:
            manifest = self.generate_manifest()

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)

            return True
        except Exception:
            return False
