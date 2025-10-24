"""
Artifact Viewer - Browse and view workflow execution artifacts.

Provides file browsing, JSON/JSONL syntax highlighting, schema validation
status, and diff viewing for code changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

try:
    from PyQt6 import QtCore, QtGui, QtWidgets

    PyQt6Available = True
except ImportError:
    PyQt6Available = False


if PyQt6Available:

    class ArtifactViewer(QtWidgets.QWidget):
        """Widget for viewing workflow artifacts."""

        def __init__(self, artifacts_dir: Optional[str] = None, parent: Optional[QtWidgets.QWidget] = None):
            super().__init__(parent)
            self.artifacts_dir = Path(artifacts_dir) if artifacts_dir else Path.cwd() / "artifacts"
            self._setup_ui()
            self.refresh_artifacts()

        def _setup_ui(self) -> None:
            """Set up the user interface."""
            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            # Left panel - File browser
            left_panel = QtWidgets.QWidget()
            left_layout = QtWidgets.QVBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)

            # File tree header
            tree_header = QtWidgets.QHBoxLayout()
            tree_label = QtWidgets.QLabel("Artifacts")
            tree_label.setStyleSheet("font-weight: bold;")
            tree_header.addWidget(tree_label)

            refresh_button = QtWidgets.QPushButton("⟳")
            refresh_button.setToolTip("Refresh artifacts")
            refresh_button.setMaximumWidth(30)
            refresh_button.clicked.connect(self.refresh_artifacts)
            tree_header.addWidget(refresh_button)

            left_layout.addLayout(tree_header)

            # File tree
            self.file_tree = QtWidgets.QTreeWidget()
            self.file_tree.setHeaderLabels(["Name", "Size"])
            self.file_tree.setColumnWidth(0, 200)
            self.file_tree.setAlternatingRowColors(True)
            self.file_tree.itemClicked.connect(self._on_file_selected)
            left_layout.addWidget(self.file_tree)

            left_panel.setMaximumWidth(300)
            layout.addWidget(left_panel)

            # Right panel - Content viewer
            right_panel = QtWidgets.QWidget()
            right_layout = QtWidgets.QVBoxLayout(right_panel)
            right_layout.setContentsMargins(0, 0, 0, 0)

            # Viewer header
            header_layout = QtWidgets.QHBoxLayout()

            self.file_path_label = QtWidgets.QLabel("No file selected")
            self.file_path_label.setStyleSheet("font-weight: bold; color: #2d3748;")
            header_layout.addWidget(self.file_path_label)

            header_layout.addStretch()

            self.validation_label = QtWidgets.QLabel("")
            header_layout.addWidget(self.validation_label)

            copy_button = QtWidgets.QPushButton("Copy Content")
            copy_button.clicked.connect(self._copy_content)
            copy_button.setMaximumWidth(120)
            header_layout.addWidget(copy_button)

            right_layout.addLayout(header_layout)

            # Content display
            self.content_text = QtWidgets.QTextEdit()
            self.content_text.setReadOnly(True)
            self.content_text.setFont(QtGui.QFont("Consolas", 10))
            self.content_text.setStyleSheet(
                """
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3d3d3d;
                    border-radius: 4px;
                    padding: 10px;
                }
            """
            )
            right_layout.addWidget(self.content_text)

            # Metadata display
            metadata_label = QtWidgets.QLabel("File Metadata")
            metadata_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            right_layout.addWidget(metadata_label)

            self.metadata_text = QtWidgets.QTextEdit()
            self.metadata_text.setReadOnly(True)
            self.metadata_text.setMaximumHeight(100)
            self.metadata_text.setStyleSheet(
                """
                QTextEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 9pt;
                }
            """
            )
            right_layout.addWidget(self.metadata_text)

            layout.addWidget(right_panel)

        def refresh_artifacts(self) -> None:
            """Refresh the artifact file tree."""
            self.file_tree.clear()

            if not self.artifacts_dir.exists():
                no_artifacts_item = QtWidgets.QTreeWidgetItem(
                    self.file_tree, ["No artifacts directory", ""]
                )
                no_artifacts_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, None)
                self.content_text.setPlainText(f"Artifacts directory not found: {self.artifacts_dir}")
                return

            # Build file tree
            self._populate_tree_item(self.file_tree.invisibleRootItem(), self.artifacts_dir)

        def _populate_tree_item(self, parent_item: QtWidgets.QTreeWidgetItem, path: Path) -> None:
            """Recursively populate tree item with files and directories.

            Args:
                parent_item: Parent tree widget item
                path: Directory path to scan
            """
            try:
                items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))

                for item in items:
                    if item.is_dir():
                        dir_item = QtWidgets.QTreeWidgetItem(parent_item, [item.name, ""])
                        dir_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(item))
                        dir_item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
                        self._populate_tree_item(dir_item, item)
                    else:
                        # File item
                        size = item.stat().st_size
                        size_str = self._format_file_size(size)
                        file_item = QtWidgets.QTreeWidgetItem(parent_item, [item.name, size_str])
                        file_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(item))
                        file_item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon))

            except PermissionError:
                pass

        def _format_file_size(self, size: int) -> str:
            """Format file size in human-readable format.

            Args:
                size: File size in bytes

            Returns:
                Formatted size string
            """
            for unit in ["B", "KB", "MB", "GB"]:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"

        def _on_file_selected(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
            """Handle file selection.

            Args:
                item: Selected tree widget item
                column: Column number
            """
            file_path = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if file_path:
                self._display_file(Path(file_path))

        def _display_file(self, file_path: Path) -> None:
            """Display file content.

            Args:
                file_path: Path to file
            """
            if not file_path.is_file():
                self.content_text.setPlainText("Selected item is a directory")
                return

            self.file_path_label.setText(file_path.name)

            try:
                # Read file content
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Detect file type and apply syntax highlighting
                suffix = file_path.suffix.lower()

                if suffix in [".json", ".jsonl"]:
                    self._display_json_content(content, suffix == ".jsonl")
                elif suffix in [".yaml", ".yml"]:
                    self._display_yaml_content(content)
                elif suffix in [".py", ".js", ".ts", ".sh", ".md"]:
                    self._display_code_content(content, suffix)
                else:
                    self.content_text.setPlainText(content)

                # Display metadata
                self._display_file_metadata(file_path)

                # Validate if JSON
                if suffix == ".json":
                    self._validate_json_schema(file_path, content)

            except Exception as e:
                self.content_text.setPlainText(f"Error reading file: {str(e)}")
                self.validation_label.setText("")

        def _display_json_content(self, content: str, is_jsonl: bool = False) -> None:
            """Display JSON content with syntax highlighting.

            Args:
                content: JSON content
                is_jsonl: Whether content is JSONL (one JSON per line)
            """
            try:
                if is_jsonl:
                    # Parse and pretty-print each line
                    lines = content.strip().split("\n")
                    formatted_lines = []
                    for i, line in enumerate(lines, 1):
                        if line.strip():
                            try:
                                obj = json.loads(line)
                                formatted = json.dumps(obj, indent=2)
                                formatted_lines.append(f"// Line {i}\n{formatted}\n")
                            except json.JSONDecodeError:
                                formatted_lines.append(f"// Line {i} (invalid JSON)\n{line}\n")
                    formatted = "\n".join(formatted_lines)
                else:
                    # Pretty-print single JSON object
                    obj = json.loads(content)
                    formatted = json.dumps(obj, indent=2)

                self.content_text.setPlainText(formatted)

            except json.JSONDecodeError as e:
                self.content_text.setPlainText(f"Invalid JSON:\n\n{content}\n\nError: {str(e)}")

        def _display_yaml_content(self, content: str) -> None:
            """Display YAML content.

            Args:
                content: YAML content
            """
            self.content_text.setPlainText(content)

        def _display_code_content(self, content: str, file_type: str) -> None:
            """Display code content.

            Args:
                content: Code content
                file_type: File extension
            """
            self.content_text.setPlainText(content)

        def _display_file_metadata(self, file_path: Path) -> None:
            """Display file metadata.

            Args:
                file_path: Path to file
            """
            stat = file_path.stat()
            metadata = f"""Path: {file_path}
Size: {self._format_file_size(stat.st_size)}
Modified: {self._format_timestamp(stat.st_mtime)}
Type: {file_path.suffix or 'No extension'}"""

            self.metadata_text.setPlainText(metadata)

        def _format_timestamp(self, timestamp: float) -> str:
            """Format Unix timestamp.

            Args:
                timestamp: Unix timestamp

            Returns:
                Formatted datetime string
            """
            from datetime import datetime

            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        def _validate_json_schema(self, file_path: Path, content: str) -> None:
            """Validate JSON against schema if available.

            Args:
                file_path: Path to JSON file
                content: JSON content
            """
            # Look for corresponding schema file
            schemas_dir = file_path.parent.parent / ".ai" / "schemas"
            schema_name = file_path.stem + ".schema.json"
            schema_path = schemas_dir / schema_name

            if schema_path.exists():
                try:
                    import jsonschema

                    with open(schema_path) as f:
                        schema = json.load(f)

                    data = json.loads(content)
                    jsonschema.validate(data, schema)

                    self.validation_label.setText("✅ Valid")
                    self.validation_label.setStyleSheet("color: #28a745; font-weight: bold;")
                except jsonschema.ValidationError as e:
                    self.validation_label.setText(f"❌ Invalid: {e.message}")
                    self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold;")
                except Exception:
                    self.validation_label.setText("")
            else:
                self.validation_label.setText("")

        def _copy_content(self) -> None:
            """Copy content to clipboard."""
            content = self.content_text.toPlainText()
            if content:
                clipboard = QtWidgets.QApplication.clipboard()
                clipboard.setText(content)

                # Show temporary feedback
                original_text = self.file_path_label.text()
                self.file_path_label.setText(f"{original_text} - Copied!")
                QtCore.QTimer.singleShot(2000, lambda: self.file_path_label.setText(original_text))

else:
    # Headless fallback

    class ArtifactViewer:
        """Headless artifact viewer fallback."""

        def __init__(self, artifacts_dir: Optional[str] = None, parent=None):
            pass

        def refresh_artifacts(self) -> None:
            pass
