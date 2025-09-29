import pytest

from src.cli_multi_rapid.roles.role_manager import RoleManager


def test_role_mapping_basic():
    rm = RoleManager()
    assert rm.get_role_for_operation("plan") == "planning_ai"
    assert rm.get_role_for_operation("edit") == "work_cli_tools"
    assert rm.get_role_for_operation("lint") == "ide_validator"
    assert rm.get_role_for_operation("commit") == "repo_coordinator"
    # default fallback
    assert rm.get_role_for_operation("unknown-op") == "work_cli_tools"


def test_tools_and_fallback_chain():
    rm = RoleManager()
    chain = rm.get_fallback_chain("planning_ai")
    assert isinstance(chain, list) and chain
    # primary tool comes first
    assert chain[0] == rm.get_tools_for_role("planning_ai")[0]
    # availability check is permissive for named tools
    for tool in chain:
        assert rm.check_tool_availability(tool)
