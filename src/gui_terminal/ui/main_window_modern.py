"""
Modern Main Window - Tabbed interface for CLI Orchestrator GUI.

Integrates workflow browser, execution dashboard, cost tracking,
artifact viewing, and terminal interface in a unified tabbed layout.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from PyQt6 import QtCore, QtGui, QtWidgets

    PyQt6Available = True
except ImportError:
    PyQt6Available = False


if PyQt6Available:
    from .artifact_viewer import ArtifactViewer
    from .cost_dashboard import CostDashboard
    from .execution_dashboard import ExecutionDashboard
    from .workflow_browser import WorkflowBrowser
    from .workflow_config import WorkflowConfigPanel
    from .cli_interface import CLIExecutionInterface
    from ..core.execution_manager import ExecutionManager
    from ..gui_bridge import WorkflowExecutor


if PyQt6Available:

    class ModernMainWindow(QtWidgets.QMainWindow):
        """Modern main window with tabbed interface for full orchestrator control."""

        def __init__(self, config: Optional[dict] = None):
            super().__init__()
            self.config = config or {}
            self.execution_manager = ExecutionManager(self)
            self.workflow_executor = WorkflowExecutor(self)
            self._current_workflow: Optional[str] = None

            self._setup_ui()
            self._connect_signals()

        def _setup_ui(self) -> None:
            """Set up the user interface."""
            self.setWindowTitle("CLI Orchestrator - Professional Workflow Management")
            self.setGeometry(100, 100, 1400, 900)

            # Central widget with tabs
            self.tabs = QtWidgets.QTabWidget()
            self.tabs.setDocumentMode(True)
            self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
            self.setCentralWidget(self.tabs)

            # Create tabs
            self._create_workflows_tab()
            self._create_execution_tab()
            self._create_artifacts_tab()
            self._create_cost_tab()
            self._create_terminal_tab()
            self._create_settings_tab()

            # Create menu bar
            self._create_menu_bar()

            # Create toolbar
            self._create_toolbar()

            # Create status bar
            self._create_status_bar()

        def _create_workflows_tab(self) -> None:
            """Create workflows tab with browser and configuration."""
            workflows_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(workflows_widget)

            # Left: Workflow browser
            browser_container = QtWidgets.QWidget()
            browser_layout = QtWidgets.QVBoxLayout(browser_container)
            browser_layout.setContentsMargins(0, 0, 0, 0)

            browser_label = QtWidgets.QLabel("Available Workflows")
            browser_label.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 8px;")
            browser_layout.addWidget(browser_label)

            self.workflow_browser = WorkflowBrowser()
            browser_layout.addWidget(self.workflow_browser)

            browser_container.setMaximumWidth(450)
            layout.addWidget(browser_container)

            # Right: Configuration and execution
            config_container = QtWidgets.QWidget()
            config_layout = QtWidgets.QVBoxLayout(config_container)
            config_layout.setContentsMargins(0, 0, 0, 0)

            config_label = QtWidgets.QLabel("Workflow Configuration")
            config_label.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 8px;")
            config_layout.addWidget(config_label)

            self.workflow_config = WorkflowConfigPanel()
            config_layout.addWidget(self.workflow_config)

            # Execution button
            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addStretch()

            self.execute_button = QtWidgets.QPushButton("▶ Execute Workflow")
            self.execute_button.setEnabled(False)
            self.execute_button.clicked.connect(self._execute_workflow)
            self.execute_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    font-weight: bold;
                    font-size: 12pt;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """
            )
            button_layout.addWidget(self.execute_button)

            config_layout.addLayout(button_layout)
            layout.addWidget(config_container)

            self.tabs.addTab(workflows_widget, "📋 Workflows")

        def _create_execution_tab(self) -> None:
            """Create execution monitoring tab."""
            self.execution_dashboard = ExecutionDashboard(self.execution_manager)
            self.tabs.addTab(self.execution_dashboard, "▶ Execution")

        def _create_artifacts_tab(self) -> None:
            """Create artifacts viewing tab."""
            self.artifact_viewer = ArtifactViewer()
            self.tabs.addTab(self.artifact_viewer, "📦 Artifacts")

        def _create_cost_tab(self) -> None:
            """Create cost tracking tab."""
            self.cost_dashboard = CostDashboard()
            self.tabs.addTab(self.cost_dashboard, "💰 Cost Tracking")

        def _create_terminal_tab(self) -> None:
            """Create terminal interface tab."""
            self.terminal_interface = CLIExecutionInterface()
            self.tabs.addTab(self.terminal_interface, "💻 Terminal")

        def _create_settings_tab(self) -> None:
            """Create settings tab."""
            settings_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(settings_widget)

            header = QtWidgets.QLabel("Settings")
            header.setStyleSheet("font-weight: bold; font-size: 14pt; margin-bottom: 10px;")
            layout.addWidget(header)

            # Paths group
            paths_group = QtWidgets.QGroupBox("Paths")
            paths_layout = QtWidgets.QFormLayout()

            self.workflows_path_input = QtWidgets.QLineEdit(str(Path.cwd() / ".ai" / "workflows"))
            paths_layout.addRow("Workflows Directory:", self.workflows_path_input)

            self.artifacts_path_input = QtWidgets.QLineEdit(str(Path.cwd() / "artifacts"))
            paths_layout.addRow("Artifacts Directory:", self.artifacts_path_input)

            paths_group.setLayout(paths_layout)
            layout.addWidget(paths_group)

            # Preferences group
            prefs_group = QtWidgets.QGroupBox("Preferences")
            prefs_layout = QtWidgets.QVBoxLayout()

            self.auto_refresh_checkbox = QtWidgets.QCheckBox("Auto-refresh workflows on tab change")
            self.auto_refresh_checkbox.setChecked(True)
            prefs_layout.addWidget(self.auto_refresh_checkbox)

            self.confirm_execution_checkbox = QtWidgets.QCheckBox("Confirm before workflow execution")
            self.confirm_execution_checkbox.setChecked(True)
            prefs_layout.addWidget(self.confirm_execution_checkbox)

            prefs_group.setLayout(prefs_layout)
            layout.addWidget(prefs_group)

            layout.addStretch()

            # Save button
            save_button = QtWidgets.QPushButton("Save Settings")
            save_button.clicked.connect(self._save_settings)
            save_button.setMaximumWidth(150)
            layout.addWidget(save_button)

            self.tabs.addTab(settings_widget, "⚙ Settings")

        def _create_menu_bar(self) -> None:
            """Create menu bar."""
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("&File")

            refresh_action = QtGui.QAction("&Refresh Workflows", self)
            refresh_action.setShortcut("F5")
            refresh_action.triggered.connect(self.workflow_browser.refresh_workflows)
            file_menu.addAction(refresh_action)

            file_menu.addSeparator()

            exit_action = QtGui.QAction("E&xit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # View menu
            view_menu = menubar.addMenu("&View")

            for i in range(self.tabs.count()):
                tab_name = self.tabs.tabText(i)
                action = QtGui.QAction(f"Show {tab_name}", self)
                action.triggered.connect(lambda checked, idx=i: self.tabs.setCurrentIndex(idx))
                view_menu.addAction(action)

            # Help menu
            help_menu = menubar.addMenu("&Help")

            about_action = QtGui.QAction("&About", self)
            about_action.triggered.connect(self._show_about)
            help_menu.addAction(about_action)

            docs_action = QtGui.QAction("&Documentation", self)
            docs_action.triggered.connect(self._show_documentation)
            help_menu.addAction(docs_action)

        def _create_toolbar(self) -> None:
            """Create toolbar."""
            toolbar = self.addToolBar("Main Toolbar")
            toolbar.setMovable(False)

            # Quick actions
            refresh_action = toolbar.addAction("⟳ Refresh")
            refresh_action.triggered.connect(self._refresh_all)

            toolbar.addSeparator()

            execute_action = toolbar.addAction("▶ Execute")
            execute_action.triggered.connect(self._execute_workflow)

            toolbar.addSeparator()

            cost_action = toolbar.addAction("💰 Cost Report")
            cost_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.cost_dashboard))

        def _create_status_bar(self) -> None:
            """Create status bar."""
            self.statusBar().showMessage("Ready")

            # Add widgets to status bar
            self.status_workflow_label = QtWidgets.QLabel("No workflow selected")
            self.statusBar().addPermanentWidget(self.status_workflow_label)

            self.status_execution_label = QtWidgets.QLabel("Idle")
            self.statusBar().addPermanentWidget(self.status_execution_label)

        def _connect_signals(self) -> None:
            """Connect signals between components."""
            # Workflow browser signals
            self.workflow_browser.workflow_selected.connect(self._on_workflow_selected)
            self.workflow_browser.workflow_double_clicked.connect(self._on_workflow_double_clicked)

            # Workflow config signals
            self.workflow_config.config_valid.connect(self.execute_button.setEnabled)

            # Workflow executor signals
            self.workflow_executor.workflow_started.connect(self._on_workflow_started)
            self.workflow_executor.workflow_completed.connect(self._on_workflow_completed)
            self.workflow_executor.output_received.connect(self.execution_dashboard._append_output)

        def _on_workflow_selected(self, workflow_path: str) -> None:
            """Handle workflow selection."""
            self._current_workflow = workflow_path
            self.workflow_config.load_workflow(workflow_path)
            self.status_workflow_label.setText(f"Selected: {Path(workflow_path).stem}")

        def _on_workflow_double_clicked(self, workflow_path: str) -> None:
            """Handle workflow double-click (switch to execution tab)."""
            self._on_workflow_selected(workflow_path)
            self.tabs.setCurrentWidget(self.execution_dashboard)

        def _execute_workflow(self) -> None:
            """Execute the currently selected workflow."""
            if not self._current_workflow:
                QtWidgets.QMessageBox.warning(self, "No Workflow", "Please select a workflow first.")
                return

            if not self.workflow_config.is_valid():
                QtWidgets.QMessageBox.warning(
                    self, "Invalid Configuration", "Please fix the configuration errors before executing."
                )
                return

            # Confirm execution
            if self.confirm_execution_checkbox.isChecked():
                workflow_name = Path(self._current_workflow).stem
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "Confirm Execution",
                    f"Execute workflow: {workflow_name}?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                )
                if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                    return

            # Get configuration
            config = self.workflow_config.get_configuration()
            files = config.get("files", None)
            dry_run = config.get("dry_run", False)

            # Create execution
            execution_id = self.execution_manager.create_execution(
                self._current_workflow, files=files, dry_run=dry_run
            )

            # Start execution
            self.execution_manager.start_execution(execution_id)

            # Execute via workflow executor
            self.workflow_executor.execute_workflow(self._current_workflow, files=files, dry_run=dry_run)

            # Switch to execution tab
            self.tabs.setCurrentWidget(self.execution_dashboard)

            self.statusBar().showMessage(f"Executing workflow: {Path(self._current_workflow).stem}")

        def _on_workflow_started(self, workflow_path: str) -> None:
            """Handle workflow execution start."""
            self.status_execution_label.setText("Running")
            self.status_execution_label.setStyleSheet("color: #007bff; font-weight: bold;")

        def _on_workflow_completed(self, success: bool, message: str) -> None:
            """Handle workflow execution completion."""
            if success:
                self.status_execution_label.setText("Completed")
                self.status_execution_label.setStyleSheet("color: #28a745; font-weight: bold;")
                self.statusBar().showMessage(f"Workflow completed: {message}", 5000)
            else:
                self.status_execution_label.setText("Failed")
                self.status_execution_label.setStyleSheet("color: #dc3545; font-weight: bold;")
                QtWidgets.QMessageBox.critical(self, "Execution Failed", message)

            # Refresh artifacts
            self.artifact_viewer.refresh_artifacts()
            self.cost_dashboard.refresh_data()

        def _refresh_all(self) -> None:
            """Refresh all components."""
            self.workflow_browser.refresh_workflows()
            self.artifact_viewer.refresh_artifacts()
            self.cost_dashboard.refresh_data()
            self.statusBar().showMessage("Refreshed", 2000)

        def _save_settings(self) -> None:
            """Save settings."""
            # In real implementation, save to config file
            QtWidgets.QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")

        def _show_about(self) -> None:
            """Show about dialog."""
            about_text = """<h2>CLI Orchestrator GUI</h2>
            <p>Version 1.1.0</p>
            <p>Professional workflow management and orchestration for developer tools and AI agents.</p>
            <p><b>Features:</b></p>
            <ul>
            <li>Visual workflow browser and execution</li>
            <li>Real-time execution monitoring</li>
            <li>Cost tracking and budget management</li>
            <li>Artifact viewing with schema validation</li>
            <li>Integrated terminal interface</li>
            </ul>
            <p>Built with PyQt6 and Python</p>"""

            QtWidgets.QMessageBox.about(self, "About CLI Orchestrator", about_text)

        def _show_documentation(self) -> None:
            """Show documentation link."""
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("Documentation")
            msg.setText("CLI Orchestrator Documentation")
            msg.setInformativeText("View the complete documentation in docs/gui/GUI_USER_GUIDE.md")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            msg.exec()

else:
    # Headless fallback

    class ModernMainWindow:
        """Headless main window fallback."""

        def __init__(self, config: Optional[dict] = None):
            print("[Modern Main Window] Running in headless mode")

        def show(self) -> None:
            pass

        def widget(self):
            return None
