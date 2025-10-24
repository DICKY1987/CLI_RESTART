"""
Integration Tests for Workflow Templates

Comprehensive end-to-end tests for all workflow templates to ensure they
execute correctly and produce expected results.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from src.cli_multi_rapid.router import Router

# Import workflow runner and related components
from src.cli_multi_rapid.workflow_runner import WorkflowRunner


class TestWorkflowTemplates:
    """Test all workflow templates with integration tests."""

    @pytest.fixture
    def workflow_runner(self):
        """Create a workflow runner instance."""
        return WorkflowRunner()

    @pytest.fixture
    def workflow_templates_dir(self):
        """Get the workflow templates directory."""
        return Path(__file__).parent.parent.parent / ".ai" / "workflows"

    @pytest.fixture
    def test_files_dir(self, tmp_path):
        """Create temporary test files directory."""
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()

        # Create sample Python file
        sample_py = test_dir / "sample.py"
        sample_py.write_text("""
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""")

        return test_dir

    def load_workflow_template(self, template_path: Path) -> Dict[str, Any]:
        """Load a workflow template from YAML file."""
        import yaml

        if not template_path.exists():
            pytest.skip(f"Workflow template not found: {template_path}")

        with open(template_path) as f:
            return yaml.safe_load(f)

    # ===== Test Individual Workflow Templates =====

    @pytest.mark.integration
    def test_py_edit_triage_workflow(self, workflow_runner, workflow_templates_dir, test_files_dir):
        """Test PY_EDIT_TRIAGE workflow template."""
        template_path = workflow_templates_dir / "PY_EDIT_TRIAGE.yaml"
        workflow = self.load_workflow_template(template_path)

        # Override inputs for testing
        workflow['inputs'] = {
            'files': [str(test_files_dir / "*.py")],
            'lane': 'test/integration'
        }

        # Run workflow in dry-run mode
        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True,
            files=str(test_files_dir / "*.py")
        )

        assert result.success, f"Workflow failed: {result.error}"
        assert result.steps_completed > 0, "No steps were executed"

    @pytest.mark.integration
    def test_simple_py_fix_workflow(self, workflow_runner, workflow_templates_dir, test_files_dir):
        """Test SIMPLE_PY_FIX workflow template."""
        template_path = workflow_templates_dir / "SIMPLE_PY_FIX.yaml"

        if not template_path.exists():
            pytest.skip("SIMPLE_PY_FIX template not found")

        workflow = self.load_workflow_template(template_path)

        # Override for testing
        workflow['inputs'] = {'files': [str(test_files_dir / "*.py")]}

        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True,
            files=str(test_files_dir / "*.py")
        )

        assert result.success, f"Workflow failed: {result.error}"

    @pytest.mark.integration
    def test_code_quality_workflow(self, workflow_runner, workflow_templates_dir, test_files_dir):
        """Test CODE_QUALITY workflow template."""
        template_path = workflow_templates_dir / "CODE_QUALITY.yaml"

        if not template_path.exists():
            pytest.skip("CODE_QUALITY template not found")

        workflow = self.load_workflow_template(template_path)

        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True,
            files=str(test_files_dir / "*.py")
        )

        assert result.success, f"Workflow failed: {result.error}"

    @pytest.mark.integration
    @pytest.mark.skipif(
        not Path(".git").exists(),
        reason="Requires git repository"
    )
    def test_github_repo_analysis_workflow(self, workflow_runner, workflow_templates_dir):
        """Test GITHUB_REPO_ANALYSIS workflow template."""
        template_path = workflow_templates_dir / "GITHUB_REPO_ANALYSIS.yaml"

        if not template_path.exists():
            pytest.skip("GITHUB_REPO_ANALYSIS template not found")

        workflow = self.load_workflow_template(template_path)

        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True
        )

        assert result.success, f"Workflow failed: {result.error}"

    @pytest.mark.integration
    def test_github_issue_automation_workflow(self, workflow_runner, workflow_templates_dir):
        """Test GITHUB_ISSUE_AUTOMATION workflow template."""
        template_path = workflow_templates_dir / "GITHUB_ISSUE_AUTOMATION.yaml"

        if not template_path.exists():
            pytest.skip("GITHUB_ISSUE_AUTOMATION template not found")

        workflow = self.load_workflow_template(template_path)

        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True
        )

        assert result.success, f"Workflow failed: {result.error}"

    @pytest.mark.integration
    def test_github_pr_review_workflow(self, workflow_runner, workflow_templates_dir):
        """Test GITHUB_PR_REVIEW workflow template."""
        template_path = workflow_templates_dir / "GITHUB_PR_REVIEW.yaml"

        if not template_path.exists():
            pytest.skip("GITHUB_PR_REVIEW template not found")

        workflow = self.load_workflow_template(template_path)

        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True
        )

        assert result.success, f"Workflow failed: {result.error}"

    @pytest.mark.integration
    def test_github_release_management_workflow(self, workflow_runner, workflow_templates_dir):
        """Test GITHUB_RELEASE_MANAGEMENT workflow template."""
        template_path = workflow_templates_dir / "GITHUB_RELEASE_MANAGEMENT.yaml"

        if not template_path.exists():
            pytest.skip("GITHUB_RELEASE_MANAGEMENT template not found")

        workflow = self.load_workflow_template(template_path)

        result = workflow_runner._execute_workflow(
            workflow,
            dry_run=True
        )

        assert result.success, f"Workflow failed: {result.error}"

    # ===== DeepSeek Workflow Tests =====

    @pytest.mark.integration
    @pytest.mark.skipif(
        True,  # Skip by default as it requires Ollama
        reason="Requires Ollama with DeepSeek model"
    )
    def test_deepseek_workflows(self, workflow_runner, workflow_templates_dir, test_files_dir):
        """Test DeepSeek workflow templates."""
        deepseek_templates = [
            "DEEPSEEK_CODE_REVIEW.yaml",
            "DEEPSEEK_REFACTOR.yaml",
            "DEEPSEEK_ANALYSIS.yaml",
            "DEEPSEEK_TEST_GEN.yaml",
        ]

        for template_name in deepseek_templates:
            template_path = workflow_templates_dir / template_name

            if not template_path.exists():
                continue

            workflow = self.load_workflow_template(template_path)

            result = workflow_runner._execute_workflow(
                workflow,
                dry_run=True,
                files=str(test_files_dir / "*.py")
            )

            assert result.success, f"{template_name} failed: {result.error}"

    # ===== Multi-Workflow Coordination Tests =====

    @pytest.mark.integration
    def test_coordinated_workflows(self, workflow_runner, workflow_templates_dir, test_files_dir):
        """Test coordinated execution of multiple workflows."""
        # Load two simple workflows
        templates = ["SIMPLE_PY_FIX.yaml", "CODE_QUALITY.yaml"]
        workflows = []

        for template_name in templates:
            template_path = workflow_templates_dir / template_name
            if template_path.exists():
                workflow = self.load_workflow_template(template_path)
                workflow['inputs'] = {'files': [str(test_files_dir / "*.py")]}
                workflows.append(workflow)

        if len(workflows) < 2:
            pytest.skip("Not enough workflow templates for coordination test")

        # Test coordination (dry-run)
        # In a full implementation, you'd use WorkflowRunner.coordinate_workflows
        # For now, test sequential execution
        for workflow in workflows:
            result = workflow_runner._execute_workflow(
                workflow,
                dry_run=True,
                files=str(test_files_dir / "*.py")
            )
            assert result.success, f"Coordinated workflow failed: {result.error}"

    # ===== Workflow Validation Tests =====

    @pytest.mark.integration
    def test_all_workflow_templates_validate(self, workflow_templates_dir):
        """Validate all workflow templates against schema."""
        import yaml

        templates = list(workflow_templates_dir.glob("*.yaml"))

        if not templates:
            pytest.skip("No workflow templates found")

        for template_path in templates:
            try:
                with open(template_path) as f:
                    workflow = yaml.safe_load(f)

                # Basic validation
                assert 'name' in workflow, f"{template_path.name}: Missing 'name' field"
                assert 'steps' in workflow or 'inputs' in workflow, \
                    f"{template_path.name}: Missing 'steps' or 'inputs' field"

                # If has steps, validate structure
                if 'steps' in workflow:
                    for i, step in enumerate(workflow['steps']):
                        assert 'actor' in step, \
                            f"{template_path.name} step {i}: Missing 'actor' field"

            except Exception as e:
                pytest.fail(f"Template validation failed for {template_path.name}: {e}")

    # ===== Performance Tests =====

    @pytest.mark.integration
    @pytest.mark.performance
    def test_workflow_execution_performance(self, workflow_runner, workflow_templates_dir, test_files_dir):
        """Test workflow execution performance metrics."""
        from src.cli_multi_rapid.benchmarking import PerformanceProfiler

        profiler = PerformanceProfiler()
        template_path = workflow_templates_dir / "SIMPLE_PY_FIX.yaml"

        if not template_path.exists():
            pytest.skip("SIMPLE_PY_FIX template not found")

        workflow = self.load_workflow_template(template_path)
        workflow['inputs'] = {'files': [str(test_files_dir / "*.py")]}

        # Profile execution
        result, metrics = profiler.profile_execution(
            "simple_py_fix",
            workflow_runner._execute_workflow,
            workflow,
            dry_run=True,
            files=str(test_files_dir / "*.py")
        )

        assert metrics.success, "Profiled workflow execution failed"
        assert metrics.duration > 0, "Execution duration should be positive"

    # ===== Error Handling Tests =====

    @pytest.mark.integration
    def test_workflow_error_handling(self, workflow_runner):
        """Test workflow error handling with invalid inputs."""
        # Test with invalid workflow
        invalid_workflow = {
            'name': 'Invalid Workflow',
            'steps': [
                {
                    'id': '1',
                    'actor': 'nonexistent_adapter',
                    'with': {}
                }
            ]
        }

        result = workflow_runner._execute_workflow(invalid_workflow, dry_run=True)

        # Should handle error gracefully
        assert not result.success or result.steps_completed == 0, \
            "Should handle invalid adapter gracefully"

    @pytest.mark.integration
    def test_workflow_timeout_handling(self, workflow_runner, test_files_dir):
        """Test workflow timeout handling."""
        workflow = {
            'name': 'Timeout Test',
            'timeouts': {
                'per_phase_seconds': 1  # Very short timeout
            },
            'steps': [
                {
                    'id': '1',
                    'actor': 'code_fixers',
                    'with': {'tools': ['black']},
                }
            ]
        }

        # This may timeout or succeed depending on system speed
        # Just ensure it doesn't crash
        try:
            result = workflow_runner._execute_workflow(
                workflow,
                dry_run=True,
                files=str(test_files_dir / "*.py")
            )
            # Should either succeed or fail gracefully
            assert isinstance(result.success, bool)
        except Exception as e:
            pytest.fail(f"Workflow should handle timeout gracefully: {e}")


# ===== Test Fixtures and Utilities =====

@pytest.fixture
def sample_workflow():
    """Create a sample workflow for testing."""
    return {
        'name': 'Test Workflow',
        'policy': {
            'max_tokens': 10000,
            'prefer_deterministic': True
        },
        'steps': [
            {
                'id': '1.001',
                'name': 'Lint Python files',
                'actor': 'code_fixers',
                'with': {
                    'tools': ['ruff']
                },
                'emits': ['artifacts/lint_results.json']
            }
        ]
    }


@pytest.fixture
def coordination_test_workflows():
    """Create multiple workflows for coordination testing."""
    return [
        {
            'id': 'wf1',
            'name': 'Workflow 1',
            'steps': [
                {'id': '1', 'actor': 'code_fixers', 'files': ['file1.py']}
            ]
        },
        {
            'id': 'wf2',
            'name': 'Workflow 2',
            'steps': [
                {'id': '1', 'actor': 'pytest_runner', 'files': ['file2.py']}
            ]
        }
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
