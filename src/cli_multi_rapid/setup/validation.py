"""
CLI Orchestrator System Validation

Comprehensive validation and health checking for the CLI Orchestrator system.
Validates installation, dependencies, configuration, and provides quick-start setup.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


class SystemValidator:
    """Comprehensive system validation and health checking."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize system validator."""
        self.project_root = project_root or Path.cwd()
        self.issues: list[str] = []
        self.successes: list[str] = []
        self.warnings: list[str] = []

    def run_comprehensive_validation(self) -> dict[str, bool]:
        """Run complete system validation suite."""
        console.print(
            Panel.fit(
                "[bold blue]🔍 CLI Orchestrator System Validation[/bold blue]",
                border_style="blue",
            )
        )

        validation_checks = [
            ("Python Version", self.check_python_version),
            ("Git Repository", self.check_git_repository),
            ("File Structure", self.check_file_structure),
            ("Dependencies", self.check_dependencies),
            ("CLI Installation", self.check_cli_installation),
            ("External Tools", self.check_external_tools),
            ("Schema Validation", self.check_schema_files),
            ("Configuration", self.check_configuration),
        ]

        results = {}
        for check_name, check_func in validation_checks:
            console.print(f"\n[dim]Checking {check_name}...[/dim]")
            try:
                results[check_name] = check_func()
            except Exception as e:
                self.issues.append(f"❌ {check_name}: Validation failed - {e}")
                results[check_name] = False

        self._print_validation_results()
        return results

    def check_python_version(self) -> bool:
        """Validate Python version compatibility."""
        version = sys.version_info

        if version.major == 3 and version.minor >= 9:
            self.successes.append(
                f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible"
            )
            return True
        else:
            self.issues.append(
                f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.9+"
            )
            return False

    def check_git_repository(self) -> bool:
        """Validate git repository setup."""
        git_dir = self.project_root / ".git"

        if not git_dir.exists():
            self.issues.append("❌ Not in a git repository")
            return False

        try:
            # Check for remote origin
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root,
            )

            remote = result.stdout.strip()
            if "cli_multi_rapid" in remote or "CLI" in remote:
                self.successes.append(f"✅ Git repository: {remote}")
                return True
            else:
                self.warnings.append(
                    f"⚠️  Git remote doesn't match expected repo: {remote}"
                )
                return True  # Still valid, just different repo

        except subprocess.CalledProcessError:
            self.warnings.append("⚠️  Git repository exists but no remote configured")
            return True

    def check_file_structure(self) -> bool:
        """Validate required files and directories."""
        required_files = [
            "src/cli_multi_rapid/main.py",
            "src/cli_multi_rapid/workflow_runner.py",
            "src/cli_multi_rapid/router.py",
            "pyproject.toml",
        ]

        required_dirs = [
            "src/cli_multi_rapid/adapters",
            ".ai/schemas",
            ".ai/workflows",
        ]

        missing_files = []
        missing_dirs = []

        # Check files
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        # Check directories
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)

        if missing_files or missing_dirs:
            if missing_files:
                self.issues.append(f"❌ Missing files: {', '.join(missing_files)}")
            if missing_dirs:
                self.issues.append(f"❌ Missing directories: {', '.join(missing_dirs)}")
            return False
        else:
            self.successes.append("✅ All required files and directories present")
            return True

    def check_dependencies(self) -> bool:
        """Validate required Python dependencies."""
        required_packages = [
            "typer",
            "rich",
            "pydantic",
            "yaml",
            "jsonschema",
            "requests",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                if package == "yaml":
                    import yaml
                else:
                    __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.issues.append(f"❌ Missing packages: {', '.join(missing_packages)}")
            self.issues.append("   Run: pip install -e .[dev,ai]")
            return False
        else:
            self.successes.append("✅ All required dependencies installed")
            return True

    def check_cli_installation(self) -> bool:
        """Validate CLI orchestrator installation."""
        try:
            # Try importing the main module
            sys.path.insert(0, str(self.project_root / "src"))
            from cli_multi_rapid.main import app

            self.successes.append("✅ CLI module imports successfully")

            # Try running the CLI help command
            result = subprocess.run(
                [sys.executable, "-m", "cli_multi_rapid.main", "--help"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30,
            )

            if result.returncode == 0:
                self.successes.append("✅ CLI orchestrator responds to commands")
                return True
            else:
                self.issues.append(f"❌ CLI command failed: {result.stderr}")
                return False

        except ImportError as e:
            self.issues.append(f"❌ Failed to import CLI module: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.issues.append("❌ CLI command timed out")
            return False

    def check_external_tools(self) -> dict[str, bool]:
        """Check availability of external tools."""
        tools = {
            "git": ["git", "--version"],
            "ruff": ["ruff", "--version"],
            "mypy": ["mypy", "--version"],
            "pytest": ["pytest", "--version"],
        }

        tool_status = {}
        working_count = 0

        for tool_name, command in tools.items():
            try:
                subprocess.run(
                    command, capture_output=True, text=True, check=True, timeout=10
                )
                tool_status[tool_name] = True
                working_count += 1
                self.successes.append(f"✅ {tool_name} available")
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                tool_status[tool_name] = False
                self.warnings.append(f"⚠️  {tool_name} not available")

        if working_count >= 2:  # At least git and one other tool
            return True
        else:
            self.issues.append("❌ Too few external tools available")
            return False

    def check_schema_files(self) -> bool:
        """Validate JSON schema files."""
        schema_dir = self.project_root / ".ai" / "schemas"

        if not schema_dir.exists():
            self.issues.append("❌ Schema directory not found")
            return False

        schema_files = list(schema_dir.glob("*.schema.json"))

        if len(schema_files) < 3:
            self.warnings.append("⚠️  Few schema files found")
            return True

        # Validate JSON syntax of schemas
        invalid_schemas = []
        for schema_file in schema_files:
            try:
                with open(schema_file, encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError:
                invalid_schemas.append(schema_file.name)

        if invalid_schemas:
            self.issues.append(f"❌ Invalid schema files: {', '.join(invalid_schemas)}")
            return False
        else:
            self.successes.append(f"✅ {len(schema_files)} schema files validated")
            return True

    def check_configuration(self) -> bool:
        """Validate configuration files."""
        config_files = [
            "pyproject.toml",
            ".ai/schemas/workflow.schema.json",
        ]

        missing_configs = []
        for config_file in config_files:
            if not (self.project_root / config_file).exists():
                missing_configs.append(config_file)

        if missing_configs:
            self.issues.append(
                f"❌ Missing configuration files: {', '.join(missing_configs)}"
            )
            return False
        else:
            self.successes.append("✅ Configuration files present")
            return True

    def create_sample_workflow(self) -> bool:
        """Create a sample workflow for testing."""
        workflows_dir = self.project_root / ".ai" / "workflows" / "samples"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        sample_workflow = {
            "name": "System Validation Test",
            "version": "1.0.0",
            "description": "Simple workflow to validate system functionality",
            "inputs": {"files": ["src/**/*.py"]},
            "policy": {"max_tokens": 1000, "prefer_deterministic": True},
            "steps": [
                {
                    "id": "1.001",
                    "name": "Run Basic Analysis",
                    "actor": "vscode_diagnostics",
                    "with": {"analyzers": ["ruff"], "files": "{{ inputs.files }}"},
                    "emits": ["artifacts/validation_test.json"],
                }
            ],
        }

        workflow_file = workflows_dir / "validation_test.yaml"

        try:
            import yaml

            with open(workflow_file, "w", encoding="utf-8") as f:
                yaml.dump(sample_workflow, f, default_flow_style=False, sort_keys=False)
            self.successes.append(f"✅ Created sample workflow: {workflow_file}")
            return True
        except ImportError:
            self.warnings.append(
                "⚠️  PyYAML not available, couldn't create sample workflow"
            )
            return False

    def test_workflow_execution(self) -> bool:
        """Test if workflow execution works."""
        workflow_file = (
            self.project_root / ".ai" / "workflows" / "samples" / "validation_test.yaml"
        )

        if not workflow_file.exists():
            self.warnings.append("⚠️  Sample workflow not found for testing")
            return False

        try:
            # Test dry run execution
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "cli_multi_rapid.main",
                    "run",
                    str(workflow_file),
                    "--dry-run",
                    "--files",
                    "src/cli_multi_rapid/main.py",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60,
            )

            if result.returncode == 0:
                self.successes.append("✅ Workflow dry-run executed successfully")
                return True
            else:
                self.warnings.append(
                    f"⚠️  Workflow execution had issues: {result.stderr}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.warnings.append("⚠️  Workflow test timed out")
            return False
        except Exception as e:
            self.warnings.append(f"⚠️  Workflow test failed: {e}")
            return False

    def generate_quick_start_guide(self) -> Path:
        """Generate a quick start guide based on validation results."""
        guide_dir = self.project_root / "docs" / "setup"
        guide_dir.mkdir(parents=True, exist_ok=True)

        guide_file = guide_dir / "quick_start_validation.md"

        guide_content = f"""# CLI Orchestrator Quick Start Validation

## Validation Results

### ✅ Working Components
{chr(10).join(f"- {success}" for success in self.successes)}

### ⚠️ Warnings
{chr(10).join(f"- {warning}" for warning in self.warnings)}

### ❌ Issues to Address
{chr(10).join(f"- {issue}" for issue in self.issues)}

## Next Steps

{self._get_next_steps_text()}

## Quick Commands

```bash
# Check system status
python -m cli_multi_rapid.main tools doctor

# List available adapters
python -m cli_multi_rapid.main tools list

# Run sample workflow (dry-run)
python -m cli_multi_rapid.main run .ai/workflows/samples/validation_test.yaml --dry-run --files "src/**/*.py"

# Validate workflow
python -m cli_multi_rapid.main verify artifacts/validation_test.json
```

Generated on: {self._get_timestamp()}
"""

        guide_file.write_text(guide_content, encoding="utf-8")
        console.print(f"[green]✅ Quick start guide generated: {guide_file}[/green]")

        return guide_file

    def _get_next_steps_text(self) -> str:
        """Generate appropriate next steps based on validation results."""
        if not self.issues:
            return """
🎉 **CONGRATULATIONS!** Your CLI Orchestrator is ready to use!

### Ready to Use Commands:
1. **System Status**: `python -m cli_multi_rapid.main tools doctor`
2. **Tool Discovery**: `python -m cli_multi_rapid.main tools setup --discover`
3. **Run Workflow**: `python -m cli_multi_rapid.main run <workflow.yaml> --dry-run`
4. **Validate Setup**: `python -m cli_multi_rapid.main setup validate`
"""
        else:
            return """
### 🔧 Setup Incomplete - Please Address Issues:

1. **If dependencies missing**: `pip install -e .[dev,ai]`
2. **If tools missing**: Install missing tools (ruff, mypy, etc.)
3. **If file structure wrong**: Ensure you're in the correct directory
4. **If git issues**: Check repository location and remote

After fixing issues, run validation again:
```bash
python -m cli_multi_rapid.main setup validate --comprehensive
```
"""

    def _print_validation_results(self):
        """Print formatted validation results."""
        console.print("\n" + "=" * 60)
        console.print("[bold blue]📊 VALIDATION RESULTS[/bold blue]")
        console.print("=" * 60)

        if self.successes:
            console.print("\n[bold green]✅ WORKING COMPONENTS:[/bold green]")
            for success in self.successes:
                console.print(f"   {success}")

        if self.warnings:
            console.print("\n[bold yellow]⚠️  WARNINGS:[/bold yellow]")
            for warning in self.warnings:
                console.print(f"   {warning}")

        if self.issues:
            console.print("\n[bold red]❌ ISSUES TO ADDRESS:[/bold red]")
            for issue in self.issues:
                console.print(f"   {issue}")

        # Summary
        total_checks = len(self.successes) + len(self.warnings) + len(self.issues)
        success_rate = (
            len(self.successes) / total_checks * 100 if total_checks > 0 else 0
        )

        console.print("\n[bold]📈 SUMMARY:[/bold]")
        console.print(f"   Success Rate: {success_rate:.1f}%")
        console.print(f"   Working: {len(self.successes)}")
        console.print(f"   Warnings: {len(self.warnings)}")
        console.print(f"   Issues: {len(self.issues)}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
