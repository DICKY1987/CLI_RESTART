"""
Workflow Browser - Browse and select workflows for execution.

Provides a tree view of available workflows with categorization,
search, and metadata display.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import yaml

try:
    from PyQt6 import QtCore, QtGui, QtWidgets

    PyQt6Available = True
except ImportError:
    PyQt6Available = False


if PyQt6Available:

    class WorkflowBrowser(QtWidgets.QWidget):
        """Widget for browsing and selecting workflows."""

        # Signals
        workflow_selected = QtCore.pyqtSignal(str)  # workflow_path
        workflow_double_clicked = QtCore.pyqtSignal(str)  # workflow_path

        def __init__(self, workflows_dir: Optional[str] = None, parent: Optional[QtWidgets.QWidget] = None):
            super().__init__(parent)
            self.workflows_dir = Path(workflows_dir) if workflows_dir else Path.cwd() / ".ai" / "workflows"
            self._workflows: Dict[str, Dict] = {}
            self._setup_ui()
            self.refresh_workflows()

        def _setup_ui(self) -> None:
            """Set up the user interface."""
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            # Search bar
            search_layout = QtWidgets.QHBoxLayout()
            search_label = QtWidgets.QLabel("Search:")
            search_label.setMaximumWidth(60)
            search_layout.addWidget(search_label)

            self.search_input = QtWidgets.QLineEdit()
            self.search_input.setPlaceholderText("Filter workflows...")
            self.search_input.textChanged.connect(self._filter_workflows)
            search_layout.addWidget(self.search_input)

            self.refresh_button = QtWidgets.QPushButton("⟳")
            self.refresh_button.setToolTip("Refresh workflow list")
            self.refresh_button.setMaximumWidth(40)
            self.refresh_button.clicked.connect(self.refresh_workflows)
            search_layout.addWidget(self.refresh_button)

            layout.addLayout(search_layout)

            # Workflow tree
            self.tree = QtWidgets.QTreeWidget()
            self.tree.setHeaderLabels(["Workflow", "Steps", "Type"])
            self.tree.setColumnWidth(0, 300)
            self.tree.setColumnWidth(1, 60)
            self.tree.setColumnWidth(2, 100)
            self.tree.setAlternatingRowColors(True)
            self.tree.itemClicked.connect(self._on_item_clicked)
            self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
            layout.addWidget(self.tree)

            # Details panel
            details_label = QtWidgets.QLabel("Workflow Details:")
            details_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(details_label)

            self.details_text = QtWidgets.QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumHeight(150)
            self.details_text.setStyleSheet(
                """
                QTextEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: 'Consolas', monospace;
                    font-size: 10pt;
                }
            """
            )
            layout.addWidget(self.details_text)

        def refresh_workflows(self) -> None:
            """Refresh the workflow list from disk."""
            self.tree.clear()
            self._workflows.clear()

            if not self.workflows_dir.exists():
                self.details_text.setPlainText(f"Workflows directory not found: {self.workflows_dir}")
                return

            # Scan for workflow files
            workflow_files = list(self.workflows_dir.glob("*.yaml")) + list(self.workflows_dir.glob("*.yml"))

            # Categorize workflows
            categories = {
                "Python": [],
                "DeepSeek": [],
                "GitHub": [],
                "Code Quality": [],
                "Other": [],
            }

            for workflow_file in workflow_files:
                try:
                    # Load workflow metadata
                    with open(workflow_file, encoding="utf-8") as f:
                        workflow_data = yaml.safe_load(f)

                    if not workflow_data:
                        continue

                    workflow_name = workflow_data.get("name", workflow_file.stem)
                    steps = workflow_data.get("steps", [])
                    step_count = len(steps)

                    # Categorize
                    file_name = workflow_file.stem.upper()
                    if "DEEPSEEK" in file_name:
                        category = "DeepSeek"
                    elif "GITHUB" in file_name:
                        category = "GitHub"
                    elif "PY_" in file_name or "PYTHON" in file_name:
                        category = "Python"
                    elif "QUALITY" in file_name or "CODE" in file_name:
                        category = "Code Quality"
                    else:
                        category = "Other"

                    categories[category].append(
                        {
                            "name": workflow_name,
                            "file": workflow_file.name,
                            "path": str(workflow_file),
                            "steps": step_count,
                            "data": workflow_data,
                        }
                    )

                    self._workflows[str(workflow_file)] = workflow_data

                except Exception:
                    # Skip invalid workflows
                    continue

            # Populate tree
            for category, workflows in categories.items():
                if not workflows:
                    continue

                category_item = QtWidgets.QTreeWidgetItem(self.tree, [category, "", ""])
                category_item.setExpanded(True)
                category_item.setFont(0, QtGui.QFont("Arial", 10, QtGui.QFont.Weight.Bold))
                category_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, None)  # No path for category

                for workflow in workflows:
                    workflow_item = QtWidgets.QTreeWidgetItem(
                        category_item,
                        [workflow["name"], str(workflow["steps"]), workflow["file"]],
                    )
                    workflow_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, workflow["path"])
                    workflow_item.setToolTip(0, workflow["path"])

            self.details_text.setPlainText(f"Found {len(self._workflows)} workflows in {len(categories)} categories")

        def _filter_workflows(self, search_text: str) -> None:
            """Filter workflows based on search text."""
            search_lower = search_text.lower()

            for i in range(self.tree.topLevelItemCount()):
                category_item = self.tree.topLevelItem(i)
                if not category_item:
                    continue

                visible_children = 0
                for j in range(category_item.childCount()):
                    workflow_item = category_item.child(j)
                    if not workflow_item:
                        continue

                    # Check if workflow matches search
                    workflow_name = workflow_item.text(0).lower()
                    workflow_file = workflow_item.text(2).lower()
                    matches = search_lower in workflow_name or search_lower in workflow_file

                    workflow_item.setHidden(not matches)
                    if matches:
                        visible_children += 1

                # Hide category if no visible children
                category_item.setHidden(visible_children == 0)

        def _on_item_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
            """Handle item click."""
            workflow_path = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if workflow_path:
                self._display_workflow_details(workflow_path)
                self.workflow_selected.emit(workflow_path)

        def _on_item_double_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
            """Handle item double-click."""
            workflow_path = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if workflow_path:
                self.workflow_double_clicked.emit(workflow_path)

        def _display_workflow_details(self, workflow_path: str) -> None:
            """Display workflow details in the details panel."""
            if workflow_path not in self._workflows:
                self.details_text.setPlainText("Workflow details not available")
                return

            workflow = self._workflows[workflow_path]
            name = workflow.get("name", "Unnamed")
            description = workflow.get("description", "No description available")
            steps = workflow.get("steps", [])
            inputs = workflow.get("inputs", {})
            policy = workflow.get("policy", {})

            # Format details
            details = f"""Name: {name}

Description:
{description}

Steps: {len(steps)}
"""

            if inputs:
                details += "\nInputs:\n"
                for key, value in inputs.items():
                    details += f"  • {key}: {value}\n"

            if policy:
                details += "\nPolicy:\n"
                for key, value in policy.items():
                    details += f"  • {key}: {value}\n"

            if steps:
                details += "\nStep Overview:\n"
                for i, step in enumerate(steps[:5], 1):  # Show first 5 steps
                    step_name = step.get("name", "Unnamed step")
                    actor = step.get("actor", "unknown")
                    details += f"  {i}. {step_name} ({actor})\n"

                if len(steps) > 5:
                    details += f"  ... and {len(steps) - 5} more steps\n"

            self.details_text.setPlainText(details)

        def get_selected_workflow(self) -> Optional[str]:
            """Get the currently selected workflow path.

            Returns:
                Workflow path or None
            """
            current_item = self.tree.currentItem()
            if current_item:
                return current_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            return None

        def get_workflow_count(self) -> int:
            """Get the number of loaded workflows.

            Returns:
                Count of workflows
            """
            return len(self._workflows)

else:
    # Headless fallback

    class WorkflowBrowser:
        """Headless workflow browser fallback."""

        def __init__(self, workflows_dir: Optional[str] = None, parent=None):
            self.workflows_dir = Path(workflows_dir) if workflows_dir else Path.cwd() / ".ai" / "workflows"

        def refresh_workflows(self) -> None:
            pass

        def get_selected_workflow(self) -> Optional[str]:
            return None

        def get_workflow_count(self) -> int:
            return 0
