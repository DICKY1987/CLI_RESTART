"""
Workflow Configuration Panel - Dynamic input form generator for workflows.

Generates Qt widgets based on workflow input requirements and validates
configuration before execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

try:
    from PyQt6 import QtCore, QtWidgets

    PyQt6Available = True
except ImportError:
    PyQt6Available = False


if PyQt6Available:

    class WorkflowConfigPanel(QtWidgets.QWidget):
        """Dynamic configuration panel for workflow inputs."""

        # Signals
        config_changed = QtCore.pyqtSignal(dict)  # configuration
        config_valid = QtCore.pyqtSignal(bool)  # is_valid

        def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
            super().__init__(parent)
            self._workflow_path: Optional[str] = None
            self._workflow_data: Optional[Dict] = None
            self._input_widgets: Dict[str, QtWidgets.QWidget] = {}
            self._setup_ui()

        def _setup_ui(self) -> None:
            """Set up the user interface."""
            layout = QtWidgets.QVBoxLayout(self)

            # Workflow info
            info_group = QtWidgets.QGroupBox("Workflow Information")
            info_layout = QtWidgets.QFormLayout()

            self.name_label = QtWidgets.QLabel("No workflow selected")
            self.name_label.setStyleSheet("font-weight: bold; color: #2d3748;")
            info_layout.addRow("Name:", self.name_label)

            self.description_label = QtWidgets.QLabel("")
            self.description_label.setWordWrap(True)
            info_layout.addRow("Description:", self.description_label)

            info_group.setLayout(info_layout)
            layout.addWidget(info_group)

            # Configuration form (dynamic)
            self.config_group = QtWidgets.QGroupBox("Configuration")
            self.config_layout = QtWidgets.QFormLayout()
            self.config_group.setLayout(self.config_layout)
            layout.addWidget(self.config_group)

            # Execution options
            options_group = QtWidgets.QGroupBox("Execution Options")
            options_layout = QtWidgets.QVBoxLayout()

            self.dry_run_checkbox = QtWidgets.QCheckBox("Dry Run (validate without executing)")
            self.dry_run_checkbox.stateChanged.connect(self._on_config_changed)
            options_layout.addWidget(self.dry_run_checkbox)

            options_group.setLayout(options_layout)
            layout.addWidget(options_group)

            # Spacer
            layout.addStretch()

            # Validation status
            self.validation_label = QtWidgets.QLabel("")
            self.validation_label.setWordWrap(True)
            self.validation_label.setStyleSheet("padding: 8px; border-radius: 4px;")
            layout.addWidget(self.validation_label)

        def load_workflow(self, workflow_path: str) -> bool:
            """Load a workflow and generate configuration form.

            Args:
                workflow_path: Path to workflow YAML file

            Returns:
                True if loaded successfully
            """
            self._workflow_path = workflow_path
            self._input_widgets.clear()

            # Clear existing config form
            while self.config_layout.rowCount() > 0:
                self.config_layout.removeRow(0)

            try:
                # Load workflow
                with open(workflow_path, encoding="utf-8") as f:
                    self._workflow_data = yaml.safe_load(f)

                if not self._workflow_data:
                    self._set_error("Invalid workflow file")
                    return False

                # Update info
                name = self._workflow_data.get("name", "Unnamed Workflow")
                description = self._workflow_data.get("description", "No description")
                self.name_label.setText(name)
                self.description_label.setText(description)

                # Generate input fields
                inputs = self._workflow_data.get("inputs", {})
                if inputs:
                    self._generate_input_fields(inputs)
                else:
                    no_inputs_label = QtWidgets.QLabel("This workflow has no configurable inputs")
                    no_inputs_label.setStyleSheet("color: #666; font-style: italic;")
                    self.config_layout.addRow(no_inputs_label)

                self._validate_config()
                return True

            except Exception as e:
                self._set_error(f"Failed to load workflow: {str(e)}")
                return False

        def _generate_input_fields(self, inputs: Dict[str, Any]) -> None:
            """Generate input fields based on workflow inputs.

            Args:
                inputs: Workflow inputs dictionary
            """
            for key, value in inputs.items():
                # Determine input type and create appropriate widget
                if isinstance(value, bool):
                    widget = QtWidgets.QCheckBox()
                    widget.setChecked(value)
                    widget.stateChanged.connect(self._on_config_changed)
                elif isinstance(value, list):
                    widget = QtWidgets.QLineEdit()
                    widget.setText(", ".join(str(v) for v in value))
                    widget.setPlaceholderText("Comma-separated list")
                    widget.textChanged.connect(self._on_config_changed)
                elif isinstance(value, (int, float)):
                    widget = QtWidgets.QSpinBox()
                    widget.setValue(int(value))
                    widget.setMaximum(999999)
                    widget.valueChanged.connect(self._on_config_changed)
                elif key.lower() in ["file", "files", "path", "directory", "dir"]:
                    # File/directory picker
                    widget = FilePickerWidget(str(value) if value else "")
                    widget.value_changed.connect(self._on_config_changed)
                else:
                    # Default to text input
                    widget = QtWidgets.QLineEdit()
                    widget.setText(str(value) if value else "")
                    widget.textChanged.connect(self._on_config_changed)

                self._input_widgets[key] = widget
                label = key.replace("_", " ").title() + ":"
                self.config_layout.addRow(label, widget)

        def _on_config_changed(self) -> None:
            """Handle configuration change."""
            self._validate_config()
            config = self.get_configuration()
            self.config_changed.emit(config)

        def _validate_config(self) -> bool:
            """Validate current configuration.

            Returns:
                True if configuration is valid
            """
            if not self._workflow_data:
                self._set_validation_status(False, "No workflow loaded")
                return False

            # Check required inputs
            inputs = self._workflow_data.get("inputs", {})
            for key, widget in self._input_widgets.items():
                value = self._get_widget_value(widget)

                # Check if required field is empty
                if key in inputs and not value:
                    self._set_validation_status(False, f"Required field '{key}' is empty")
                    return False

                # Validate file paths if applicable
                if isinstance(widget, FilePickerWidget) and value:
                    path = Path(value)
                    if not path.exists() and not self.dry_run_checkbox.isChecked():
                        self._set_validation_status(False, f"Path does not exist: {value}")
                        return False

            self._set_validation_status(True, "Configuration is valid")
            return True

        def _get_widget_value(self, widget: QtWidgets.QWidget) -> Any:
            """Get value from a widget.

            Args:
                widget: Qt widget

            Returns:
                Widget value
            """
            if isinstance(widget, QtWidgets.QCheckBox):
                return widget.isChecked()
            elif isinstance(widget, QtWidgets.QLineEdit):
                return widget.text().strip()
            elif isinstance(widget, QtWidgets.QSpinBox):
                return widget.value()
            elif isinstance(widget, FilePickerWidget):
                return widget.get_value()
            return None

        def get_configuration(self) -> Dict[str, Any]:
            """Get current configuration values.

            Returns:
                Dictionary of configuration values
            """
            config = {}
            for key, widget in self._input_widgets.items():
                config[key] = self._get_widget_value(widget)

            config["dry_run"] = self.dry_run_checkbox.isChecked()
            return config

        def is_valid(self) -> bool:
            """Check if current configuration is valid.

            Returns:
                True if valid
            """
            return self._validate_config()

        def _set_validation_status(self, valid: bool, message: str) -> None:
            """Set validation status display.

            Args:
                valid: Whether configuration is valid
                message: Status message
            """
            if valid:
                self.validation_label.setText(f"✅ {message}")
                self.validation_label.setStyleSheet(
                    "background-color: #d4edda; color: #155724; padding: 8px; border-radius: 4px; border: 1px solid #c3e6cb;"
                )
            else:
                self.validation_label.setText(f"❌ {message}")
                self.validation_label.setStyleSheet(
                    "background-color: #f8d7da; color: #721c24; padding: 8px; border-radius: 4px; border: 1px solid #f5c6cb;"
                )

            self.config_valid.emit(valid)

        def _set_error(self, message: str) -> None:
            """Set error state.

            Args:
                message: Error message
            """
            self.name_label.setText("Error")
            self.description_label.setText(message)
            self._set_validation_status(False, message)

    class FilePickerWidget(QtWidgets.QWidget):
        """Widget for picking files or directories."""

        value_changed = QtCore.pyqtSignal()

        def __init__(self, initial_value: str = "", parent: Optional[QtWidgets.QWidget] = None):
            super().__init__(parent)
            self._value = initial_value

            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            self.path_input = QtWidgets.QLineEdit(initial_value)
            self.path_input.textChanged.connect(self._on_value_changed)
            layout.addWidget(self.path_input)

            browse_button = QtWidgets.QPushButton("Browse...")
            browse_button.clicked.connect(self._browse)
            browse_button.setMaximumWidth(80)
            layout.addWidget(browse_button)

        def _browse(self) -> None:
            """Open file browser dialog."""
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select File", self.path_input.text()
            )
            if file_path:
                self.path_input.setText(file_path)

        def _on_value_changed(self) -> None:
            """Handle value change."""
            self._value = self.path_input.text()
            self.value_changed.emit()

        def get_value(self) -> str:
            """Get current value.

            Returns:
                File path
            """
            return self.path_input.text().strip()

else:
    # Headless fallback

    class WorkflowConfigPanel:
        """Headless configuration panel fallback."""

        def __init__(self, parent=None):
            pass

        def load_workflow(self, workflow_path: str) -> bool:
            return True

        def get_configuration(self) -> Dict[str, Any]:
            return {}

        def is_valid(self) -> bool:
            return True
