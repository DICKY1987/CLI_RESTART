#!/usr/bin/env python3
"""
Tests for core.artifact_manager module

Test coverage for ArtifactManager class and artifact tracking logic.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.cli_multi_rapid.core.artifact_manager import ArtifactManager, Artifact


# Fixtures

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test artifacts."""
    import tempfile
    import shutil

    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def artifact_manager(temp_dir):
    """Create an ArtifactManager instance."""
    return ArtifactManager(artifacts_dir=temp_dir)


@pytest.fixture
def temp_artifact_file(temp_dir):
    """Create a temporary artifact file."""
    file_path = Path(temp_dir) / "test_artifact.json"
    file_path.write_text('{"test": "data"}')
    return str(file_path)


# Test Initialization

def test_artifact_manager_initialization(temp_dir):
    """Test ArtifactManager initialization."""
    manager = ArtifactManager(artifacts_dir=temp_dir)

    assert manager.artifacts_dir == Path(temp_dir)
    assert len(manager.artifacts) == 0


def test_artifact_manager_default_dir():
    """Test ArtifactManager with default directory."""
    manager = ArtifactManager()

    assert manager.artifacts_dir == Path("artifacts")


# Test Artifact Registration

def test_register_artifact_existing_file(artifact_manager, temp_artifact_file):
    """Test registering an existing artifact file."""
    artifact = artifact_manager.register_artifact(
        temp_artifact_file,
        step_id="1.001",
        metadata={"key": "value"}
    )

    assert artifact.path == temp_artifact_file
    assert artifact.step_id == "1.001"
    assert artifact.exists is True
    assert artifact.size_bytes > 0
    assert artifact.metadata == {"key": "value"}
    assert len(artifact_manager.artifacts) == 1


def test_register_artifact_nonexistent_file(artifact_manager):
    """Test registering a non-existent artifact file."""
    artifact = artifact_manager.register_artifact(
        "nonexistent.json",
        step_id="1.001"
    )

    assert artifact.path == "nonexistent.json"
    assert artifact.exists is False
    assert artifact.size_bytes == 0


def test_register_artifact_without_metadata(artifact_manager, temp_artifact_file):
    """Test registering artifact without metadata."""
    artifact = artifact_manager.register_artifact(
        temp_artifact_file,
        step_id="1.001"
    )

    assert artifact.metadata == {}


def test_register_artifacts_batch(artifact_manager, temp_dir):
    """Test registering multiple artifacts at once."""
    # Create test files
    file1 = Path(temp_dir) / "artifact1.json"
    file2 = Path(temp_dir) / "artifact2.json"
    file1.write_text("{}")
    file2.write_text("{}")

    artifacts = artifact_manager.register_artifacts_batch(
        [str(file1), str(file2)],
        step_id="1.001",
        metadata={"batch": True}
    )

    assert len(artifacts) == 2
    assert len(artifact_manager.artifacts) == 2
    assert all(a.metadata == {"batch": True} for a in artifacts)


# Test Artifact Retrieval

def test_get_artifact_by_path(artifact_manager, temp_artifact_file):
    """Test retrieving artifact by path."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")

    found = artifact_manager.get_artifact(temp_artifact_file)

    assert found is not None
    assert found.path == temp_artifact_file


def test_get_artifact_not_found(artifact_manager):
    """Test retrieving non-existent artifact."""
    found = artifact_manager.get_artifact("nonexistent.json")

    assert found is None


def test_get_artifacts_by_step(artifact_manager, temp_dir):
    """Test retrieving artifacts by step ID."""
    file1 = Path(temp_dir) / "artifact1.json"
    file2 = Path(temp_dir) / "artifact2.json"
    file1.write_text("{}")
    file2.write_text("{}")

    artifact_manager.register_artifact(str(file1), "1.001")
    artifact_manager.register_artifact(str(file2), "1.001")
    artifact_manager.register_artifact(str(file1), "1.002")  # Different step

    artifacts = artifact_manager.get_artifacts_by_step("1.001")

    assert len(artifacts) == 2
    assert all(a.step_id == "1.001" for a in artifacts)


def test_get_all_artifacts(artifact_manager, temp_artifact_file):
    """Test retrieving all artifacts."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")
    artifact_manager.register_artifact(temp_artifact_file, "1.002")

    all_artifacts = artifact_manager.get_all_artifacts()

    assert len(all_artifacts) == 2


def test_get_artifacts_by_pattern(artifact_manager, temp_dir):
    """Test retrieving artifacts by glob pattern."""
    json_file = Path(temp_dir) / "data.json"
    txt_file = Path(temp_dir) / "notes.txt"
    json_file.write_text("{}")
    txt_file.write_text("notes")

    artifact_manager.register_artifact(str(json_file), "1.001")
    artifact_manager.register_artifact(str(txt_file), "1.002")

    json_artifacts = artifact_manager.get_artifacts_by_pattern("*.json")

    assert len(json_artifacts) == 1
    assert json_artifacts[0].path == str(json_file)


# Test Artifact Validation

def test_validate_artifacts_all_exist(artifact_manager, temp_artifact_file):
    """Test validating artifacts when all exist."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")

    report = artifact_manager.validate_artifacts()

    assert report["valid"] is True
    assert report["total"] == 1
    assert report["existing"] == 1
    assert report["missing"] == 0
    assert len(report["missing_paths"]) == 0


def test_validate_artifacts_some_missing(artifact_manager, temp_artifact_file):
    """Test validating artifacts with some missing."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")
    artifact_manager.register_artifact("nonexistent.json", "1.002")

    report = artifact_manager.validate_artifacts()

    assert report["valid"] is False
    assert report["total"] == 2
    assert report["existing"] == 1
    assert report["missing"] == 1
    assert "nonexistent.json" in report["missing_paths"]


def test_validate_artifacts_empty(artifact_manager):
    """Test validating with no artifacts registered."""
    report = artifact_manager.validate_artifacts()

    assert report["valid"] is True
    assert report["total"] == 0


# Test Artifact Status Refresh

def test_refresh_artifact_status(artifact_manager, temp_dir):
    """Test refreshing artifact existence and size."""
    file_path = Path(temp_dir) / "dynamic.txt"
    file_path.write_text("initial")

    artifact_manager.register_artifact(str(file_path), "1.001")

    # Modify file
    file_path.write_text("modified with more content")

    updates = artifact_manager.refresh_artifact_status()

    assert updates["checked"] == 1
    assert updates["size_updated"] == 1


def test_refresh_artifact_status_deleted_file(artifact_manager, temp_dir):
    """Test refreshing status when file is deleted."""
    file_path = Path(temp_dir) / "temp.txt"
    file_path.write_text("content")

    artifact = artifact_manager.register_artifact(str(file_path), "1.001")
    assert artifact.exists is True

    # Delete file
    file_path.unlink()

    updates = artifact_manager.refresh_artifact_status()

    assert updates["status_changed"] == 1
    # Check artifact status updated
    updated_artifact = artifact_manager.get_artifact(str(file_path))
    assert updated_artifact.exists is False


# Test Cleanup

def test_cleanup_artifacts_dry_run(artifact_manager, temp_artifact_file):
    """Test cleanup in dry-run mode."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")

    report = artifact_manager.cleanup_artifacts(dry_run=True)

    assert report["dry_run"] is True
    assert report["deleted"] == 1
    assert len(report["deleted_paths"]) == 1
    # File should still exist
    assert Path(temp_artifact_file).exists()


def test_cleanup_artifacts_actual(artifact_manager, temp_dir):
    """Test actual cleanup (deleting files)."""
    file_path = Path(temp_dir) / "to_delete.txt"
    file_path.write_text("delete me")

    artifact_manager.register_artifact(str(file_path), "1.001")

    report = artifact_manager.cleanup_artifacts(dry_run=False)

    assert report["dry_run"] is False
    assert report["deleted"] == 1
    # File should be deleted
    assert not file_path.exists()


def test_cleanup_artifacts_by_step(artifact_manager, temp_dir):
    """Test cleanup artifacts for specific step."""
    file1 = Path(temp_dir) / "step1.txt"
    file2 = Path(temp_dir) / "step2.txt"
    file1.write_text("step 1")
    file2.write_text("step 2")

    artifact_manager.register_artifact(str(file1), "1.001")
    artifact_manager.register_artifact(str(file2), "1.002")

    report = artifact_manager.cleanup_artifacts_by_step("1.001", dry_run=False)

    assert report["step_id"] == "1.001"
    assert report["deleted"] == 1
    assert not file1.exists()
    assert file2.exists()  # Should not be deleted


def test_cleanup_nonexistent_artifacts(artifact_manager):
    """Test cleanup when artifacts don't exist."""
    artifact_manager.register_artifact("nonexistent.json", "1.001")

    report = artifact_manager.cleanup_artifacts(dry_run=False)

    assert report["deleted"] == 0
    assert report["errors"] == 0


# Test Artifact Removal

def test_remove_artifact(artifact_manager, temp_artifact_file):
    """Test removing artifact from tracking."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")
    assert len(artifact_manager.artifacts) == 1

    removed = artifact_manager.remove_artifact(temp_artifact_file)

    assert removed is True
    assert len(artifact_manager.artifacts) == 0


def test_remove_artifact_not_found(artifact_manager):
    """Test removing non-existent artifact."""
    removed = artifact_manager.remove_artifact("nonexistent.json")

    assert removed is False


def test_clear_all(artifact_manager, temp_artifact_file):
    """Test clearing all tracked artifacts."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")
    artifact_manager.register_artifact(temp_artifact_file, "1.002")

    count = artifact_manager.clear_all()

    assert count == 2
    assert len(artifact_manager.artifacts) == 0


# Test Manifest Generation

def test_generate_manifest(artifact_manager, temp_artifact_file):
    """Test generating artifact manifest."""
    artifact_manager.register_artifact(
        temp_artifact_file,
        "1.001",
        metadata={"type": "json"}
    )

    manifest = artifact_manager.generate_manifest()

    assert "generated_at" in manifest
    assert manifest["total_artifacts"] == 1
    assert len(manifest["artifacts"]) == 1
    assert manifest["artifacts"][0]["path"] == temp_artifact_file
    assert manifest["artifacts"][0]["step_id"] == "1.001"


def test_export_manifest(artifact_manager, temp_artifact_file, temp_dir):
    """Test exporting manifest to file."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")

    output_path = Path(temp_dir) / "manifest.json"
    success = artifact_manager.export_manifest(str(output_path))

    assert success is True
    assert output_path.exists()

    # Verify content
    with open(output_path) as f:
        data = json.load(f)
    assert data["total_artifacts"] == 1


def test_export_manifest_creates_directory(artifact_manager, temp_artifact_file, temp_dir):
    """Test export creates parent directories if needed."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")

    output_path = Path(temp_dir) / "subdir" / "manifest.json"
    success = artifact_manager.export_manifest(str(output_path))

    assert success is True
    assert output_path.exists()


# Test Statistics

def test_get_statistics(artifact_manager, temp_dir):
    """Test getting artifact statistics."""
    file1 = Path(temp_dir) / "file1.txt"
    file2 = Path(temp_dir) / "file2.txt"
    file1.write_text("a" * 100)
    file2.write_text("b" * 200)

    artifact_manager.register_artifact(str(file1), "1.001")
    artifact_manager.register_artifact(str(file2), "1.001")
    artifact_manager.register_artifact(str(file1), "1.002")

    stats = artifact_manager.get_statistics()

    assert stats["total_artifacts"] == 3
    assert stats["existing_artifacts"] == 3
    assert stats["missing_artifacts"] == 0
    assert stats["total_size_bytes"] == 400  # 100 + 200 + 100
    assert "artifacts_by_step" in stats
    assert stats["artifacts_by_step"]["1.001"]["count"] == 2
    assert stats["artifacts_by_step"]["1.002"]["count"] == 1


def test_get_statistics_with_missing(artifact_manager, temp_artifact_file):
    """Test statistics with missing artifacts."""
    artifact_manager.register_artifact(temp_artifact_file, "1.001")
    artifact_manager.register_artifact("nonexistent.json", "1.002")

    stats = artifact_manager.get_statistics()

    assert stats["total_artifacts"] == 2
    assert stats["existing_artifacts"] == 1
    assert stats["missing_artifacts"] == 1


def test_get_statistics_empty(artifact_manager):
    """Test statistics with no artifacts."""
    stats = artifact_manager.get_statistics()

    assert stats["total_artifacts"] == 0
    assert stats["existing_artifacts"] == 0
    assert stats["total_size_bytes"] == 0
