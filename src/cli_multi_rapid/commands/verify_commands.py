#!/usr/bin/env python3
"""
Verify Commands - CLI commands for artifact verification

Provides commands for verifying artifacts against schemas and running quality gates.
Part of Phase 3 CLI modularization.
"""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Artifact verification and quality gate commands")
console = Console()


@app.command("artifact")
def verify_artifact(
    artifact_path: Path = typer.Argument(..., help="Path to artifact file"),
    schema_path: Optional[Path] = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to JSON schema file (auto-detected if not specified)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Verify an artifact against its JSON schema.

    Examples:
        cli-orchestrator verify artifact artifacts/diagnostics.json
        cli-orchestrator verify artifact output.json --schema schema.json
    """
    if not artifact_path.exists():
        console.print(f"[red]Error: Artifact file not found: {artifact_path}[/red]")
        raise typer.Exit(1)

    # Auto-detect schema if not provided
    if schema_path is None:
        schema_dir = Path(".ai/schemas")
        # Try to find matching schema based on artifact name
        artifact_name = artifact_path.stem
        potential_schema = schema_dir / f"{artifact_name}.schema.json"

        if potential_schema.exists():
            schema_path = potential_schema
        else:
            console.print(f"[yellow]Warning: Could not auto-detect schema for {artifact_name}[/yellow]")
            console.print(f"[dim]Looked in: {potential_schema}[/dim]")
            console.print("[yellow]Please specify --schema explicitly[/yellow]")
            raise typer.Exit(1)

    if not schema_path.exists():
        console.print(f"[red]Error: Schema file not found: {schema_path}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Verifying artifact:[/bold] {artifact_path.name}")
    console.print(f"[dim]Schema:[/dim] {schema_path.name}")

    # Import verifier
    from ..verifier import Verifier

    try:
        verifier = Verifier(schema_dir=schema_path.parent)
        result = verifier.verify_artifact(str(artifact_path), str(schema_path))

        if result.get("valid", False):
            console.print("[green]Artifact is valid[/green]")
            if verbose and "details" in result:
                console.print("\n[bold]Details:[/bold]")
                for key, value in result["details"].items():
                    console.print(f"  {key}: {value}")
        else:
            console.print("[red]Artifact is invalid[/red]")
            if "errors" in result:
                console.print("\n[bold]Validation errors:[/bold]")
                for error in result["errors"]:
                    console.print(f"  - {error}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Verification error: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


@app.command("gates")
def run_gates(
    artifact_dir: Path = typer.Option(
        "artifacts",
        "--artifacts",
        "-a",
        help="Directory containing artifacts"
    ),
    gates_file: Optional[Path] = typer.Option(
        None,
        "--gates",
        "-g",
        help="YAML file with gate definitions"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run verification gates on workflow artifacts.

    Gates check for test results, diff limits, schema compliance, etc.

    Examples:
        cli-orchestrator verify gates
        cli-orchestrator verify gates --artifacts output/ --gates gates.yaml
    """
    if not artifact_dir.exists():
        console.print(f"[red]Error: Artifact directory not found: {artifact_dir}[/red]")
        raise typer.Exit(1)

    # Load gates configuration
    if gates_file and not gates_file.exists():
        console.print(f"[red]Error: Gates file not found: {gates_file}[/red]")
        raise typer.Exit(1)

    console.print("[bold]Running verification gates[/bold]")
    console.print(f"[dim]Artifact directory:[/dim] {artifact_dir}")

    # Import gate manager
    from ..core.gate_manager import GateManager

    try:
        gate_manager = GateManager()

        # Get list of artifacts
        artifacts = [str(p) for p in artifact_dir.rglob("*") if p.is_file()]

        if not artifacts:
            console.print(f"[yellow]No artifacts found in {artifact_dir}[/yellow]")
            return

        # Define default gates if no gates file provided
        if gates_file is None:
            gates = [
                {
                    "id": "test_results",
                    "type": "tests_pass",
                    "artifact": str(artifact_dir / "test_report.json")
                },
                {
                    "id": "diff_check",
                    "type": "diff_limits",
                    "max_files": 100,
                    "max_lines": 1000
                }
            ]
        else:
            # Load gates from file
            import yaml
            with open(gates_file) as f:
                gates_config = yaml.safe_load(f)
                gates = gates_config.get("gates", [])

        # Execute gates
        results = gate_manager.execute_gates(gates, artifacts)

        # Display results
        console.print("\n[bold]Gate Results:[/bold]")
        table = Table()
        table.add_column("Gate", style="cyan")
        table.add_column("Type", style="dim")
        table.add_column("Status", style="bold")
        table.add_column("Message")

        for result in results:
            status = "[green]PASS[/green]" if result.success else "[red]FAIL[/red]"
            table.add_row(
                result.gate_id,
                result.gate_type.value,
                status,
                result.message
            )

        console.print(table)

        # Aggregate results
        summary = gate_manager.aggregate_gate_results(results)

        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Total gates: {summary['total_gates']}")
        console.print(f"  Passed: {summary['gates_passed']}")
        console.print(f"  Failed: {summary['gates_failed']}")

        if summary["overall_success"]:
            console.print("\n[green]All gates passed[/green]")
        else:
            console.print("\n[red]Some gates failed[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Gate execution error: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


@app.command("manifest")
def verify_manifest(
    manifest_path: Path = typer.Argument(..., help="Path to artifact manifest JSON"),
    check_existence: bool = typer.Option(
        True,
        "--check-existence/--no-check-existence",
        help="Verify that all artifacts in manifest exist"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Verify an artifact manifest file.

    Checks that all artifacts listed in the manifest exist and match metadata.

    Examples:
        cli-orchestrator verify manifest artifacts/manifest.json
        cli-orchestrator verify manifest manifest.json --no-check-existence
    """
    if not manifest_path.exists():
        console.print(f"[red]Error: Manifest file not found: {manifest_path}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Verifying manifest:[/bold] {manifest_path.name}")

    try:
        import json

        # Load manifest
        with open(manifest_path) as f:
            manifest = json.load(f)

        total_artifacts = manifest.get("total_artifacts", 0)
        artifacts_list = manifest.get("artifacts", [])

        console.print(f"[dim]Total artifacts in manifest:[/dim] {total_artifacts}")

        # Check existence
        if check_existence:
            missing = []
            size_mismatch = []

            for artifact in artifacts_list:
                artifact_path = Path(artifact["path"])

                if not artifact_path.exists():
                    missing.append(artifact["path"])
                elif artifact_path.stat().st_size != artifact.get("size_bytes", 0):
                    size_mismatch.append({
                        "path": artifact["path"],
                        "expected": artifact.get("size_bytes", 0),
                        "actual": artifact_path.stat().st_size
                    })

            if missing:
                console.print(f"\n[red]Missing artifacts ({len(missing)}):[/red]")
                for path in missing:
                    console.print(f"  - {path}")

            if size_mismatch:
                console.print(f"\n[yellow]Size mismatches ({len(size_mismatch)}):[/yellow]")
                for item in size_mismatch:
                    console.print(f"  - {item['path']}")
                    console.print(f"    Expected: {item['expected']} bytes")
                    console.print(f"    Actual: {item['actual']} bytes")

            if missing or size_mismatch:
                raise typer.Exit(1)

        console.print("\n[green]Manifest is valid[/green]")
        console.print(f"  All {total_artifacts} artifacts verified")

        if verbose:
            console.print("\n[bold]Manifest metadata:[/bold]")
            console.print(f"  Generated at: {manifest.get('generated_at', 'unknown')}")
            console.print(f"  Artifacts dir: {manifest.get('artifacts_dir', 'unknown')}")

    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON in manifest: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Manifest verification error: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


@app.command("batch")
def verify_batch(
    artifacts: List[Path] = typer.Argument(..., help="Artifact files to verify"),
    schema_dir: Path = typer.Option(
        ".ai/schemas",
        "--schema-dir",
        "-s",
        help="Directory containing schemas"
    ),
    stop_on_error: bool = typer.Option(
        False,
        "--stop-on-error",
        help="Stop verification on first error"
    ),
):
    """
    Verify multiple artifacts in batch.

    Examples:
        cli-orchestrator verify batch artifacts/*.json
        cli-orchestrator verify batch file1.json file2.json --stop-on-error
    """
    if not schema_dir.exists():
        console.print(f"[red]Error: Schema directory not found: {schema_dir}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Batch verification of {len(artifacts)} artifacts[/bold]")

    # Import verifier
    from ..verifier import Verifier

    verifier = Verifier(schema_dir=schema_dir)

    results = []
    for artifact_path in artifacts:
        if not artifact_path.exists():
            console.print(f"[yellow]Skipping missing file: {artifact_path}[/yellow]")
            continue

        # Try to find matching schema
        artifact_name = artifact_path.stem
        schema_path = schema_dir / f"{artifact_name}.schema.json"

        if not schema_path.exists():
            console.print(f"[yellow]No schema found for {artifact_name}, skipping[/yellow]")
            continue

        # Verify
        console.print(f"Verifying {artifact_path.name}...", end=" ")

        try:
            result = verifier.verify_artifact(str(artifact_path), str(schema_path))

            if result.get("valid", False):
                console.print("[green]OK[/green]")
                results.append(("pass", artifact_path.name))
            else:
                console.print("[red]FAIL[/red]")
                results.append(("fail", artifact_path.name, result.get("errors", [])))

                if stop_on_error:
                    console.print("[red]Stopping on error (--stop-on-error)[/red]")
                    break
        except Exception as e:
            console.print(f"[red]ERROR: {e}[/red]")
            results.append(("error", artifact_path.name, str(e)))

            if stop_on_error:
                break

    # Summary
    passed = sum(1 for r in results if r[0] == "pass")
    failed = sum(1 for r in results if r[0] == "fail")
    errors = sum(1 for r in results if r[0] == "error")

    console.print("\n[bold]Batch Verification Summary:[/bold]")
    console.print(f"  Passed: {passed}")
    console.print(f"  Failed: {failed}")
    console.print(f"  Errors: {errors}")

    if failed > 0 or errors > 0:
        console.print("\n[red]Batch verification failed[/red]")
        raise typer.Exit(1)
    else:
        console.print("\n[green]All artifacts verified successfully[/green]")


if __name__ == "__main__":
    app()
