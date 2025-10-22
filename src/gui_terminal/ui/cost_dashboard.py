"""
Cost Dashboard - Token usage tracking and budget monitoring.

Displays real-time token usage, cost breakdowns, budget alerts,
and spending trends.
"""

from __future__ import annotations

from typing import Optional

try:
    from PyQt6 import QtCore, QtGui, QtWidgets

    PyQt6Available = True
except ImportError:
    PyQt6Available = False

if PyQt6Available:
    from ..gui_bridge import CostTrackerBridge


if PyQt6Available:

    class CostDashboard(QtWidgets.QWidget):
        """Dashboard for monitoring token usage and costs."""

        def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
            super().__init__(parent)
            self.cost_bridge = CostTrackerBridge(self)
            self._setup_ui()
            self._connect_signals()

        def _setup_ui(self) -> None:
            """Set up the user interface."""
            layout = QtWidgets.QVBoxLayout(self)

            # Header
            header_label = QtWidgets.QLabel("Token Usage & Cost Tracking")
            header_label.setStyleSheet("font-weight: bold; font-size: 14pt; margin-bottom: 10px;")
            layout.addWidget(header_label)

            # Budget overview card
            budget_card = self._create_budget_card()
            layout.addWidget(budget_card)

            # Usage metrics grid
            metrics_grid = self._create_metrics_grid()
            layout.addLayout(metrics_grid)

            # Provider breakdown
            provider_group = QtWidgets.QGroupBox("Cost by Provider")
            provider_layout = QtWidgets.QVBoxLayout()

            self.provider_table = QtWidgets.QTableWidget(0, 3)
            self.provider_table.setHorizontalHeaderLabels(["Provider", "Tokens", "Est. Cost"])
            self.provider_table.horizontalHeader().setStretchLastSection(True)
            self.provider_table.setAlternatingRowColors(True)
            self.provider_table.setMaximumHeight(150)
            provider_layout.addWidget(self.provider_table)

            provider_group.setLayout(provider_layout)
            layout.addWidget(provider_group)

            # Recent activity
            activity_group = QtWidgets.QGroupBox("Recent Token Usage")
            activity_layout = QtWidgets.QVBoxLayout()

            self.activity_list = QtWidgets.QListWidget()
            self.activity_list.setMaximumHeight(150)
            self.activity_list.setAlternatingRowColors(True)
            activity_layout.addWidget(self.activity_list)

            activity_group.setLayout(activity_layout)
            layout.addWidget(activity_group)

            # Refresh button
            refresh_button = QtWidgets.QPushButton("Refresh")
            refresh_button.clicked.connect(self.refresh_data)
            refresh_button.setMaximumWidth(100)
            layout.addWidget(refresh_button)

            layout.addStretch()

        def _create_budget_card(self) -> QtWidgets.QGroupBox:
            """Create budget overview card."""
            budget_card = QtWidgets.QGroupBox("Budget Overview")
            layout = QtWidgets.QVBoxLayout()

            # Progress bar
            self.budget_progress = QtWidgets.QProgressBar()
            self.budget_progress.setTextVisible(True)
            self.budget_progress.setFormat("%p% of budget used")
            self.budget_progress.setStyleSheet(
                """
                QProgressBar {
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #28a745;
                }
            """
            )
            layout.addWidget(self.budget_progress)

            # Details layout
            details_layout = QtWidgets.QGridLayout()

            details_layout.addWidget(QtWidgets.QLabel("Total Tokens:"), 0, 0)
            self.total_tokens_label = QtWidgets.QLabel("0")
            self.total_tokens_label.setStyleSheet("font-weight: bold; color: #2d3748;")
            details_layout.addWidget(self.total_tokens_label, 0, 1)

            details_layout.addWidget(QtWidgets.QLabel("Budget Limit:"), 1, 0)
            self.budget_limit_label = QtWidgets.QLabel("0")
            self.budget_limit_label.setStyleSheet("font-weight: bold; color: #2d3748;")
            details_layout.addWidget(self.budget_limit_label, 1, 1)

            details_layout.addWidget(QtWidgets.QLabel("Remaining:"), 0, 2)
            self.remaining_label = QtWidgets.QLabel("0")
            self.remaining_label.setStyleSheet("font-weight: bold; color: #28a745;")
            details_layout.addWidget(self.remaining_label, 0, 3)

            details_layout.addWidget(QtWidgets.QLabel("Est. Cost:"), 1, 2)
            self.cost_label = QtWidgets.QLabel("$0.00")
            self.cost_label.setStyleSheet("font-weight: bold; color: #2d3748;")
            details_layout.addWidget(self.cost_label, 1, 3)

            layout.addLayout(details_layout)

            # Alert label
            self.alert_label = QtWidgets.QLabel("")
            self.alert_label.setWordWrap(True)
            self.alert_label.setStyleSheet("padding: 8px; border-radius: 4px; margin-top: 10px;")
            layout.addWidget(self.alert_label)

            budget_card.setLayout(layout)
            return budget_card

        def _create_metrics_grid(self) -> QtWidgets.QGridLayout:
            """Create metrics grid layout."""
            grid = QtWidgets.QGridLayout()

            # Metric cards
            metrics = [
                ("This Session", "0", "session_label"),
                ("Today", "0", "today_label"),
                ("This Week", "0", "week_label"),
                ("This Month", "0", "month_label"),
            ]

            for i, (title, value, attr_name) in enumerate(metrics):
                card = self._create_metric_card(title, value)
                grid.addWidget(card, 0, i)
                setattr(self, attr_name, card.findChild(QtWidgets.QLabel, "value"))

            return grid

        def _create_metric_card(self, title: str, value: str) -> QtWidgets.QGroupBox:
            """Create a metric display card."""
            card = QtWidgets.QGroupBox(title)
            card.setStyleSheet(
                """
                QGroupBox {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #f8f9fa;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """
            )

            layout = QtWidgets.QVBoxLayout()

            value_label = QtWidgets.QLabel(value)
            value_label.setObjectName("value")
            value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #007bff;")
            layout.addWidget(value_label)

            card.setLayout(layout)
            return card

        def _connect_signals(self) -> None:
            """Connect cost tracker signals."""
            self.cost_bridge.cost_updated.connect(self._on_cost_updated)

        def _on_cost_updated(self, total: int, budget: int, percentage: int) -> None:
            """Handle cost update event."""
            self.total_tokens_label.setText(f"{total:,}")
            self.budget_limit_label.setText(f"{budget:,}")
            self.remaining_label.setText(f"{max(0, budget - total):,}")

            self.budget_progress.setMaximum(budget)
            self.budget_progress.setValue(total)

            # Update progress bar color based on usage
            if percentage >= 90:
                chunk_color = "#dc3545"  # Red
                self.alert_label.setText("⚠️ Critical: Budget usage above 90%!")
                self.alert_label.setStyleSheet(
                    "background-color: #f8d7da; color: #721c24; padding: 8px; border-radius: 4px; border: 1px solid #f5c6cb; margin-top: 10px;"
                )
                self.remaining_label.setStyleSheet("font-weight: bold; color: #dc3545;")
            elif percentage >= 75:
                chunk_color = "#ffc107"  # Yellow
                self.alert_label.setText("⚠️ Warning: Budget usage above 75%")
                self.alert_label.setStyleSheet(
                    "background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 4px; border: 1px solid #ffeeba; margin-top: 10px;"
                )
                self.remaining_label.setStyleSheet("font-weight: bold; color: #ffc107;")
            else:
                chunk_color = "#28a745"  # Green
                self.alert_label.setText("")
                self.alert_label.setStyleSheet("")
                self.remaining_label.setStyleSheet("font-weight: bold; color: #28a745;")

            self.budget_progress.setStyleSheet(
                f"""
                QProgressBar {{
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                }}
                QProgressBar::chunk {{
                    background-color: {chunk_color};
                }}
            """
            )

            # Estimate cost (rough approximation)
            est_cost = self._estimate_cost(total)
            self.cost_label.setText(f"${est_cost:.2f}")

        def _estimate_cost(self, tokens: int) -> float:
            """Estimate cost based on token count.

            Rough approximation using Claude Sonnet pricing as baseline.
            """
            # Approximate: $3 per million input tokens, $15 per million output tokens
            # Average: $9 per million tokens
            return (tokens / 1_000_000) * 9.0

        def refresh_data(self) -> None:
            """Refresh cost data."""
            total = self.cost_bridge.get_total_tokens()
            budget = self.cost_bridge.get_budget_limit()
            percentage = self.cost_bridge.get_percentage_used()

            self._on_cost_updated(total, budget, percentage)

            # Update provider breakdown (mock data for now)
            self._update_provider_table()

            # Update recent activity (mock data)
            self._update_activity_list()

        def _update_provider_table(self) -> None:
            """Update provider breakdown table."""
            # Mock data - in real implementation, get from cost tracker
            providers = [
                ("Claude (Anthropic)", 45000, 0.405),
                ("GPT-4 (OpenAI)", 12000, 0.36),
                ("DeepSeek (Local)", 8000, 0.0),  # Free!
            ]

            self.provider_table.setRowCount(len(providers))

            for row, (provider, tokens, cost) in enumerate(providers):
                self.provider_table.setItem(row, 0, QtWidgets.QTableWidgetItem(provider))
                self.provider_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{tokens:,}"))

                cost_item = QtWidgets.QTableWidgetItem(f"${cost:.2f}" if cost > 0 else "Free")
                if cost == 0:
                    cost_item.setForeground(QtGui.QColor("#28a745"))
                self.provider_table.setItem(row, 2, cost_item)

        def _update_activity_list(self) -> None:
            """Update recent activity list."""
            # Mock data - in real implementation, get from logs
            activities = [
                "DEEPSEEK_ANALYSIS.yaml: 2,400 tokens (Free)",
                "GITHUB_REPO_ANALYSIS.yaml: 8,500 tokens",
                "PY_EDIT_TRIAGE.yaml: 6,200 tokens",
                "CODE_QUALITY.yaml: 3,100 tokens",
            ]

            self.activity_list.clear()
            for activity in activities:
                item = QtWidgets.QListWidgetItem(activity)
                if "(Free)" in activity:
                    item.setForeground(QtGui.QColor("#28a745"))
                self.activity_list.addItem(item)

else:
    # Headless fallback

    class CostDashboard:
        """Headless cost dashboard fallback."""

        def __init__(self, parent=None):
            pass

        def refresh_data(self) -> None:
            pass
