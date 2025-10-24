"""
Execution Dashboard - Real-time workflow execution monitoring.

Displays live execution progress, step-by-step status, output streaming,
and execution history.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

try:
    from PyQt6 import QtCore, QtGui, QtWidgets

    PyQt6Available = True
except ImportError:
    PyQt6Available = False

if PyQt6Available:
    from ..core.execution_manager import (
        ExecutionManager,
        ExecutionState,
    )


if PyQt6Available:

    class ExecutionDashboard(QtWidgets.QWidget):
        """Dashboard for monitoring workflow executions."""

        def __init__(self, execution_manager: Optional[ExecutionManager] = None, parent: Optional[QtWidgets.QWidget] = None):
            super().__init__(parent)
            self.execution_manager = execution_manager or ExecutionManager()
            self._setup_ui()
            self._connect_signals()

        def _setup_ui(self) -> None:
            """Set up the user interface."""
            layout = QtWidgets.QVBoxLayout(self)

            # Execution history
            history_label = QtWidgets.QLabel("Execution History")
            history_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            layout.addWidget(history_label)

            self.history_list = QtWidgets.QListWidget()
            self.history_list.setMaximumHeight(120)
            self.history_list.setAlternatingRowColors(True)
            self.history_list.currentItemChanged.connect(self._on_history_selection_changed)
            layout.addWidget(self.history_list)

            # Current execution details
            details_label = QtWidgets.QLabel("Execution Details")
            details_label.setStyleSheet("font-weight: bold; font-size: 12pt; margin-top: 10px;")
            layout.addWidget(details_label)

            # Progress bar
            self.progress_bar = QtWidgets.QProgressBar()
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat("%p% - Step %v of %m")
            layout.addWidget(self.progress_bar)

            # Status and metadata
            metadata_layout = QtWidgets.QGridLayout()

            metadata_layout.addWidget(QtWidgets.QLabel("Status:"), 0, 0)
            self.status_label = QtWidgets.QLabel("Idle")
            self.status_label.setStyleSheet("font-weight: bold;")
            metadata_layout.addWidget(self.status_label, 0, 1)

            metadata_layout.addWidget(QtWidgets.QLabel("Workflow:"), 1, 0)
            self.workflow_label = QtWidgets.QLabel("None")
            metadata_layout.addWidget(self.workflow_label, 1, 1)

            metadata_layout.addWidget(QtWidgets.QLabel("Duration:"), 0, 2)
            self.duration_label = QtWidgets.QLabel("0s")
            metadata_layout.addWidget(self.duration_label, 0, 2)

            metadata_layout.addWidget(QtWidgets.QLabel("Tokens:"), 1, 2)
            self.tokens_label = QtWidgets.QLabel("0")
            metadata_layout.addWidget(self.tokens_label, 1, 3)

            layout.addLayout(metadata_layout)

            # Output log
            output_label = QtWidgets.QLabel("Execution Output")
            output_label.setStyleSheet("font-weight: bold; font-size: 12pt; margin-top: 10px;")
            layout.addWidget(output_label)

            self.output_text = QtWidgets.QTextEdit()
            self.output_text.setReadOnly(True)
            self.output_text.setFont(QtGui.QFont("Consolas", 9))
            self.output_text.setStyleSheet(
                """
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 8px;
                }
            """
            )
            layout.addWidget(self.output_text)

            # Control buttons
            button_layout = QtWidgets.QHBoxLayout()

            self.clear_button = QtWidgets.QPushButton("Clear Output")
            self.clear_button.clicked.connect(self.output_text.clear)
            button_layout.addWidget(self.clear_button)

            self.clear_completed_button = QtWidgets.QPushButton("Clear Completed")
            self.clear_completed_button.clicked.connect(self._clear_completed_executions)
            button_layout.addWidget(self.clear_completed_button)

            button_layout.addStretch()

            self.cancel_button = QtWidgets.QPushButton("Cancel Execution")
            self.cancel_button.setEnabled(False)
            self.cancel_button.clicked.connect(self._cancel_current_execution)
            self.cancel_button.setStyleSheet("background-color: #dc3545; color: white;")
            button_layout.addWidget(self.cancel_button)

            layout.addLayout(button_layout)

            # Update timer
            self.update_timer = QtCore.QTimer()
            self.update_timer.timeout.connect(self._update_display)
            self.update_timer.start(500)  # Update every 500ms

        def _connect_signals(self) -> None:
            """Connect execution manager signals."""
            self.execution_manager.execution_queued.connect(self._on_execution_queued)
            self.execution_manager.execution_started.connect(self._on_execution_started)
            self.execution_manager.execution_progress.connect(self._on_execution_progress)
            self.execution_manager.execution_completed.connect(self._on_execution_completed)
            self.execution_manager.state_changed.connect(self._on_state_changed)

        def _on_execution_queued(self, execution_id: str) -> None:
            """Handle execution queued event."""
            self._refresh_history()
            self._append_output(f"[{execution_id}] Execution queued", "info")

        def _on_execution_started(self, execution_id: str) -> None:
            """Handle execution started event."""
            execution = self.execution_manager.get_execution(execution_id)
            if execution:
                self.workflow_label.setText(Path(execution.workflow_path).stem)
                self.cancel_button.setEnabled(True)
                self._append_output(f"\n[{execution_id}] Execution started", "success")
                self._refresh_history()

        def _on_execution_progress(self, execution_id: str, current_step: int, total_steps: int) -> None:
            """Handle execution progress event."""
            self.progress_bar.setMaximum(total_steps)
            self.progress_bar.setValue(current_step)
            self._append_output(f"[{execution_id}] Step {current_step}/{total_steps}", "info")

        def _on_execution_completed(self, execution_id: str, success: bool) -> None:
            """Handle execution completed event."""
            execution = self.execution_manager.get_execution(execution_id)
            if execution:
                status = "completed successfully" if success else "failed"
                color = "success" if success else "error"
                self._append_output(f"\n[{execution_id}] Execution {status}", color)

                if execution.error_message:
                    self._append_output(f"Error: {execution.error_message}", "error")

                self.cancel_button.setEnabled(False)
                self._refresh_history()

        def _on_state_changed(self, execution_id: str, new_state: str) -> None:
            """Handle state change event."""
            self._update_status_display(new_state)
            self._refresh_history()

        def _on_history_selection_changed(self, current: QtWidgets.QListWidgetItem, previous: QtWidgets.QListWidgetItem) -> None:
            """Handle history selection change."""
            if current:
                execution_id = current.data(QtCore.Qt.ItemDataRole.UserRole)
                if execution_id:
                    self._display_execution(execution_id)

        def _display_execution(self, execution_id: str) -> None:
            """Display execution details."""
            execution = self.execution_manager.get_execution(execution_id)
            if not execution:
                return

            self.workflow_label.setText(Path(execution.workflow_path).stem)
            self._update_status_display(execution.state.value)

            if execution.duration:
                self.duration_label.setText(f"{execution.duration:.1f}s")

            self.tokens_label.setText(str(execution.tokens_used))

            self.progress_bar.setMaximum(execution.total_steps or 100)
            self.progress_bar.setValue(execution.current_step)

        def _update_display(self) -> None:
            """Update display with current execution info."""
            active_executions = self.execution_manager.get_active_executions()
            if active_executions:
                execution = active_executions[0]  # Show first active
                if execution.duration:
                    self.duration_label.setText(f"{execution.duration:.1f}s")

        def _update_status_display(self, state: str) -> None:
            """Update status label with color coding."""
            self.status_label.setText(state.title())

            if state == ExecutionState.RUNNING.value:
                self.status_label.setStyleSheet("color: #007bff; font-weight: bold;")
            elif state == ExecutionState.COMPLETED.value:
                self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            elif state == ExecutionState.FAILED.value:
                self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            elif state == ExecutionState.CANCELLED.value:
                self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
            else:
                self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")

        def _append_output(self, text: str, msg_type: str = "output") -> None:
            """Append text to output display.

            Args:
                text: Text to append
                msg_type: Message type (info, success, error, output)
            """
            cursor = self.output_text.textCursor()
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

            timestamp = datetime.now().strftime("%H:%M:%S")

            if msg_type == "info":
                cursor.insertHtml(f'<span style="color: #00bfff;">[{timestamp}] {text}</span><br>')
            elif msg_type == "success":
                cursor.insertHtml(f'<span style="color: #00ff00; font-weight: bold;">[{timestamp}] {text}</span><br>')
            elif msg_type == "error":
                cursor.insertHtml(f'<span style="color: #ff4444; font-weight: bold;">[{timestamp}] {text}</span><br>')
            else:
                cursor.insertHtml(f'<span style="color: #d4d4d4;">[{timestamp}] {text}</span><br>')

            self.output_text.ensureCursorVisible()

        def _refresh_history(self) -> None:
            """Refresh execution history list."""
            self.history_list.clear()

            for execution in self.execution_manager.get_execution_history(limit=20):
                # Format display text
                workflow_name = Path(execution.workflow_path).stem
                status_icon = self._get_status_icon(execution.state)
                duration_text = f"{execution.duration:.1f}s" if execution.duration else "Running..."

                display_text = f"{status_icon} {workflow_name} - {duration_text}"

                item = QtWidgets.QListWidgetItem(display_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, execution.id)

                # Color code by status
                if execution.state == ExecutionState.COMPLETED:
                    item.setForeground(QtGui.QColor("#28a745"))
                elif execution.state == ExecutionState.FAILED:
                    item.setForeground(QtGui.QColor("#dc3545"))
                elif execution.state == ExecutionState.RUNNING:
                    item.setForeground(QtGui.QColor("#007bff"))

                self.history_list.addItem(item)

        def _get_status_icon(self, state: ExecutionState) -> str:
            """Get icon for execution state."""
            icons = {
                ExecutionState.IDLE: "⭕",
                ExecutionState.QUEUED: "⏸",
                ExecutionState.RUNNING: "▶",
                ExecutionState.PAUSED: "⏸",
                ExecutionState.COMPLETED: "✅",
                ExecutionState.FAILED: "❌",
                ExecutionState.CANCELLED: "🚫",
            }
            return icons.get(state, "❓")

        def _clear_completed_executions(self) -> None:
            """Clear completed executions from history."""
            count = self.execution_manager.clear_completed()
            self._append_output(f"Cleared {count} completed executions", "info")
            self._refresh_history()

        def _cancel_current_execution(self) -> None:
            """Cancel currently running execution."""
            active_executions = self.execution_manager.get_active_executions()
            if active_executions:
                execution = active_executions[0]
                self.execution_manager.cancel_execution(execution.id)
                self._append_output(f"Cancelling execution {execution.id}", "info")

else:
    # Headless fallback

    class ExecutionDashboard:
        """Headless execution dashboard fallback."""

        def __init__(self, execution_manager=None, parent=None):
            pass


# For import convenience
from pathlib import Path
