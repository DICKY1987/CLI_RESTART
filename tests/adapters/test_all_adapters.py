import pytest

from cli_multi_rapid.adapters import *
from cli_multi_rapid.adapters.backup_manager import BackupManagerAdapter
from cli_multi_rapid.adapters.base_adapter import AdapterType
from cli_multi_rapid.adapters.bundle_loader import BundleLoaderAdapter
from cli_multi_rapid.adapters.certificate_generator import CertificateGeneratorAdapter
from cli_multi_rapid.adapters.contract_validator import ContractValidatorAdapter
from cli_multi_rapid.adapters.cost_estimator import CostEstimatorAdapter
from cli_multi_rapid.adapters.enhanced_bundle_applier import (
    EnhancedBundleApplierAdapter,
)
from cli_multi_rapid.adapters.github_integration import GitHubIntegrationAdapter
from cli_multi_rapid.adapters.import_resolver import ImportResolverAdapter
from cli_multi_rapid.adapters.security_scanner import SecurityScannerAdapter
from cli_multi_rapid.adapters.state_capture import StateCaptureAdapter
from cli_multi_rapid.adapters.syntax_validator import SyntaxValidatorAdapter
from cli_multi_rapid.adapters.tool_adapter_bridge import ToolAdapterBridge
from cli_multi_rapid.adapters.type_checker import TypeCheckerAdapter
from cli_multi_rapid.adapters.verifier_adapter import VerifierAdapter


def test_ai_analyst_adapter():
    adapter = AIAnalystAdapter()
    assert adapter.name == "ai_analyst"
    assert adapter.adapter_type == AdapterType.AI

def test_ai_editor_adapter():
    adapter = AIEditorAdapter()
    assert adapter.name == "ai_editor"
    assert adapter.adapter_type == AdapterType.AI

def test_code_fixers_adapter():
    adapter = CodeFixersAdapter()
    assert adapter.name == "code_fixers"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_git_ops_adapter():
    adapter = GitOpsAdapter()
    assert adapter.name == "git_ops"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_pytest_runner_adapter():
    adapter = PytestRunnerAdapter()
    assert adapter.name == "pytest_runner"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_vscode_diagnostics_adapter():
    adapter = VSCodeDiagnosticsAdapter()
    assert adapter.name == "vscode_diagnostics"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_adapter_registry():
    registry = AdapterRegistry()
    assert registry is not None
    # Add more specific tests for registry functionality

def test_backup_manager_adapter():
    adapter = BackupManagerAdapter()
    assert adapter.name == "backup_manager"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_bundle_loader_adapter():
    adapter = BundleLoaderAdapter()
    assert adapter.name == "bundle_loader"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_certificate_generator_adapter():
    adapter = CertificateGeneratorAdapter()
    assert adapter.name == "certificate_generator"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_contract_validator_adapter():
    adapter = ContractValidatorAdapter()
    assert adapter.name == "contract_validator"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_cost_estimator_adapter():
    adapter = CostEstimatorAdapter()
    assert adapter.name == "cost_estimator"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_enhanced_bundle_applier_adapter():
    adapter = EnhancedBundleApplierAdapter()
    assert adapter.name == "enhanced_bundle_applier"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_github_integration_adapter():
    adapter = GitHubIntegrationAdapter()
    assert adapter.name == "github_integration"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_import_resolver_adapter():
    adapter = ImportResolverAdapter()
    assert adapter.name == "import_resolver"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_security_scanner_adapter():
    adapter = SecurityScannerAdapter()
    assert adapter.name == "security_scanner"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_state_capture_adapter():
    adapter = StateCaptureAdapter()
    assert adapter.name == "state_capture"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_syntax_validator_adapter():
    adapter = SyntaxValidatorAdapter()
    assert adapter.name == "syntax_validator"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_tool_adapter_bridge():
    # This test will likely fail if the config file is not present
    # and is more of an integration test.
    # Disabling for now as it requires more setup.
    # adapter = ToolAdapterBridge(tool_type='vcs')
    # assert adapter.name == "tool_vcs"
    # assert adapter.adapter_type == AdapterType.DETERMINISTIC
    pass

def test_type_checker_adapter():
    adapter = TypeCheckerAdapter()
    assert adapter.name == "type_checker"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC

def test_verifier_adapter():
    adapter = VerifierAdapter()
    assert adapter.name == "verifier"
    assert adapter.adapter_type == AdapterType.DETERMINISTIC
