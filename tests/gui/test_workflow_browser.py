"""Tests for workflow browser component."""

import pytest
from pathlib import Path

try:
    from PyQt6 import QtWidgets
    from gui_terminal.ui.workflow_browser import WorkflowBrowser

    PyQt6Available = True
except ImportError:
    PyQt6Available = False


@pytest.mark.skipif(not PyQt6Available, reason="PyQt6 not available")
class TestWorkflowBrowser:
    """Tests for WorkflowBrowser widget."""

    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])
        return app

    @pytest.fixture
    def browser(self, app, tmp_path):
        """Create WorkflowBrowser instance with temp directory."""
        # Create mock workflows directory
        workflows_dir = tmp_path / ".ai" / "workflows"
        workflows_dir.mkdir(parents=True)

        # Create a mock workflow file
        mock_workflow = workflows_dir / "test_workflow.yaml"
        mock_workflow.write_text(
            """
name: Test Workflow
description: A test workflow
steps:
  - id: "1.001"
    name: Test Step
    actor: test_actor
"""
        )

        browser = WorkflowBrowser(workflows_dir=str(workflows_dir))
        return browser

    def test_initialization(self, browser):
        """Test browser initializes correctly."""
        assert browser is not None
        assert hasattr(browser, "tree")
        assert hasattr(browser, "search_input")
        assert hasattr(browser, "details_text")

    def test_refresh_workflows(self, browser):
        """Test workflow refresh."""
        browser.refresh_workflows()
        assert browser.tree.topLevelItemCount() > 0

    def test_get_workflow_count(self, browser):
        """Test workflow count."""
        browser.refresh_workflows()
        count = browser.get_workflow_count()
        assert count > 0

    def test_workflow_selection(self, browser):
        """Test workflow selection."""
        browser.refresh_workflows()

        # Find first workflow item
        for i in range(browser.tree.topLevelItemCount()):
            category_item = browser.tree.topLevelItem(i)
            if category_item and category_item.childCount() > 0:
                workflow_item = category_item.child(0)
                browser.tree.setCurrentItem(workflow_item)
                selected = browser.get_selected_workflow()
                assert selected is not None
                break

    def test_search_filter(self, browser):
        """Test search filtering."""
        browser.refresh_workflows()
        initial_visible = self._count_visible_items(browser.tree)

        # Apply filter
        browser.search_input.setText("nonexistent")
        browser._filter_workflows("nonexistent")

        filtered_visible = self._count_visible_items(browser.tree)
        assert filtered_visible < initial_visible

    def _count_visible_items(self, tree):
        """Count visible items in tree."""
        count = 0
        for i in range(tree.topLevelItemCount()):
            category = tree.topLevelItem(i)
            if category and not category.isHidden():
                for j in range(category.childCount()):
                    child = category.child(j)
                    if child and not child.isHidden():
                        count += 1
        return count


@pytest.mark.skipif(PyQt6Available, reason="Testing headless fallback")
def test_headless_fallback():
    """Test headless fallback when PyQt6 not available."""
    # This would test the headless fallback if PyQt6 wasn't installed
    pass
