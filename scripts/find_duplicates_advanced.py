#!/usr/bin/env python3
"""
Advanced Duplicate Finder
Finds duplicate files by content hash and similar AI config files.
Compares files in user home directory vs CLI_RESTART project.
"""

import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml


class DuplicateFinder:
    """Find duplicate and similar files across directories."""

    def __init__(self, home_dir: Path, project_dir: Path):
        self.home_dir = home_dir
        self.project_dir = project_dir
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.ai_configs: Dict[str, List[Path]] = defaultdict(list)
        self.similar_configs: List[Tuple[Path, Path, float]] = []

        # AI config file patterns
        self.ai_config_patterns = [
            r"\.aider.*",
            r"\.claude.*",
            r"\.opencode.*",
            r"\.continue.*",
            r"\.cursorrules",
            r"\.env.*",
            r"ollama.*config.*",
            r"deepseek.*config.*",
        ]

        # Directories to skip
        self.skip_dirs = {
            ".git", ".venv", "venv", "node_modules", "__pycache__",
            ".pytest_cache", ".mypy_cache", ".ruff_cache",
            "artifacts", "logs", "cost", ".cache", ".local",
            "Downloads", "Documents", "Desktop", "Pictures", "Music",
            "Videos", "Saved Games", "scoop", "AppData"
        }

        # File extensions to skip
        self.skip_extensions = {
            ".pyc", ".pyo", ".so", ".dll", ".exe", ".bin",
            ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4",
            ".zip", ".tar", ".gz", ".bz2", ".db", ".sqlite"
        }

    def is_ai_config_file(self, filepath: Path) -> bool:
        """Check if file matches AI config patterns."""
        filename = filepath.name
        return any(re.match(pattern, filename, re.IGNORECASE) for pattern in self.ai_config_patterns)

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        # Skip by directory name
        if any(skip in path.parts for skip in self.skip_dirs):
            return True

        # Skip by extension
        if path.suffix.lower() in self.skip_extensions:
            return True

        # Skip files larger than 10MB
        try:
            if path.is_file() and path.stat().st_size > 10 * 1024 * 1024:
                return True
        except (OSError, PermissionError):
            return True

        return False

    def get_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file."""
        try:
            hasher = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (OSError, PermissionError):
            return ""

    def normalize_config_content(self, content: str) -> str:
        """Normalize config content for comparison (remove comments, whitespace)."""
        # Remove comments
        lines = []
        for line in content.split('\n'):
            # Remove YAML/Python comments
            line = re.sub(r'#.*$', '', line)
            # Remove trailing whitespace
            line = line.rstrip()
            if line:
                lines.append(line)
        return '\n'.join(lines)

    def calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity ratio between two config files (0.0 to 1.0)."""
        norm1 = self.normalize_config_content(content1)
        norm2 = self.normalize_config_content(content2)

        if not norm1 or not norm2:
            return 0.0

        # Simple line-based similarity
        lines1 = set(norm1.split('\n'))
        lines2 = set(norm2.split('\n'))

        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)

        return intersection / union if union > 0 else 0.0

    def scan_directory(self, root_dir: Path, is_project: bool = False):
        """Scan directory and collect file hashes."""
        print(f"Scanning {'project' if is_project else 'home'}: {root_dir}")

        for item in root_dir.rglob('*'):
            if self.should_skip(item):
                continue

            if not item.is_file():
                continue

            try:
                # Check if AI config file
                if self.is_ai_config_file(item):
                    key = item.name.lower()
                    self.ai_configs[key].append(item)

                # Calculate hash for all files
                file_hash = self.get_file_hash(item)
                if file_hash:
                    self.file_hashes[file_hash].append(item)

            except (OSError, PermissionError) as e:
                print(f"  Skipped (permission denied): {item}")
                continue

    def find_exact_duplicates(self) -> Dict[str, List[Path]]:
        """Find files with identical content."""
        duplicates = {
            h: paths for h, paths in self.file_hashes.items()
            if len(paths) > 1
        }
        return duplicates

    def find_similar_ai_configs(self, threshold: float = 0.7):
        """Find similar AI config files."""
        print("\nComparing AI config files for similarity...")

        for config_name, paths in self.ai_configs.items():
            if len(paths) < 2:
                continue

            # Compare all pairs
            for i, path1 in enumerate(paths):
                for path2 in paths[i+1:]:
                    try:
                        with open(path1, 'r', encoding='utf-8', errors='ignore') as f1:
                            content1 = f1.read()
                        with open(path2, 'r', encoding='utf-8', errors='ignore') as f2:
                            content2 = f2.read()

                        similarity = self.calculate_similarity(content1, content2)

                        if similarity >= threshold:
                            self.similar_configs.append((path1, path2, similarity))

                    except (OSError, UnicodeDecodeError):
                        continue

    def find_duplicate_project_folders(self) -> List[Tuple[Path, str]]:
        """Find folders in home directory that might be duplicates of project folders."""
        project_folder_names = {
            p.name.lower() for p in self.project_dir.iterdir()
            if p.is_dir() and not p.name.startswith('.')
        }

        duplicates = []

        # Check top-level folders in home directory
        for item in self.home_dir.iterdir():
            if not item.is_dir() or item == self.project_dir:
                continue

            if item.name.startswith('.'):
                continue

            if item.name.lower() in project_folder_names:
                duplicates.append((item, f"Matches project folder: {item.name}"))

            # Check for similar names
            for proj_name in project_folder_names:
                if proj_name in item.name.lower() or item.name.lower() in proj_name:
                    if item.name.lower() != proj_name:
                        duplicates.append((item, f"Similar to project folder: {proj_name}"))

        return duplicates

    def generate_report(self, output_file: Path):
        """Generate detailed report of findings."""
        report = {
            "summary": {
                "total_files_scanned": len(self.file_hashes),
                "exact_duplicates_found": sum(1 for paths in self.file_hashes.values() if len(paths) > 1),
                "ai_config_files_found": sum(len(paths) for paths in self.ai_configs.values()),
                "similar_ai_configs": len(self.similar_configs)
            },
            "exact_duplicates": [],
            "similar_ai_configs": [],
            "duplicate_project_folders": [],
            "recommendations": []
        }

        # Exact duplicates
        exact_dupes = self.find_exact_duplicates()
        for file_hash, paths in exact_dupes.items():
            home_paths = [str(p) for p in paths if self.home_dir in p.parents and p != paths[0]]
            project_paths = [str(p) for p in paths if self.project_dir in p.parents]

            if home_paths or project_paths:
                report["exact_duplicates"].append({
                    "hash": file_hash[:16],
                    "size_bytes": paths[0].stat().st_size if paths[0].exists() else 0,
                    "locations": [str(p) for p in paths],
                    "in_home": home_paths,
                    "in_project": project_paths
                })

        # Similar AI configs
        for path1, path2, similarity in self.similar_configs:
            report["similar_ai_configs"].append({
                "file1": str(path1),
                "file2": str(path2),
                "similarity": f"{similarity:.2%}",
                "recommendation": "Review and consolidate - keep project version"
            })

        # Duplicate folders
        dup_folders = self.find_duplicate_project_folders()
        for folder, reason in dup_folders:
            report["duplicate_project_folders"].append({
                "path": str(folder),
                "reason": reason,
                "size_mb": self.get_folder_size(folder)
            })

        # Recommendations
        if report["exact_duplicates"]:
            report["recommendations"].append(
                "Found exact duplicate files. Consider removing duplicates from home directory, keep in CLI_RESTART."
            )

        if report["similar_ai_configs"]:
            report["recommendations"].append(
                "Found similar AI config files. Consolidate to use CLI_RESTART versions and create symlinks if needed."
            )

        if report["duplicate_project_folders"]:
            report["recommendations"].append(
                "Found potential duplicate project folders in home directory. Review and consolidate into CLI_RESTART."
            )

        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        # Also create human-readable version
        self.generate_markdown_report(report, output_file.with_suffix('.md'))

        return report

    def get_folder_size(self, folder: Path) -> float:
        """Get folder size in MB."""
        try:
            total = sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
            return round(total / (1024 * 1024), 2)
        except (OSError, PermissionError):
            return 0.0

    def generate_markdown_report(self, report: dict, output_file: Path):
        """Generate human-readable markdown report."""
        lines = [
            "# Duplicate Files Analysis Report",
            f"\nGenerated: {Path.cwd()}",
            f"\n## Summary\n",
            f"- **Total files scanned**: {report['summary']['total_files_scanned']}",
            f"- **Exact duplicates found**: {report['summary']['exact_duplicates_found']}",
            f"- **AI config files found**: {report['summary']['ai_config_files_found']}",
            f"- **Similar AI configs**: {report['summary']['similar_ai_configs']}",
            "\n---\n"
        ]

        # Exact duplicates
        if report["exact_duplicates"]:
            lines.append("\n## Exact Duplicates\n")
            lines.append("Files with identical content:\n")

            for dup in report["exact_duplicates"][:20]:  # Limit to first 20
                lines.append(f"\n### Hash: {dup['hash']} ({dup['size_bytes']} bytes)\n")
                lines.append("**Locations:**\n")
                for loc in dup["locations"]:
                    in_project = "CLI_RESTART" in loc
                    marker = "✓ (KEEP)" if in_project else "✗ (REMOVE?)"
                    lines.append(f"- {marker} `{loc}`\n")

        # Similar AI configs
        if report["similar_ai_configs"]:
            lines.append("\n## Similar AI Configuration Files\n")
            lines.append("Config files with similar content (≥70% match):\n")

            for cfg in report["similar_ai_configs"]:
                lines.append(f"\n### Similarity: {cfg['similarity']}\n")
                lines.append(f"- File 1: `{cfg['file1']}`\n")
                lines.append(f"- File 2: `{cfg['file2']}`\n")
                lines.append(f"- **Recommendation**: {cfg['recommendation']}\n")

        # Duplicate folders
        if report["duplicate_project_folders"]:
            lines.append("\n## Duplicate/Similar Project Folders\n")
            lines.append("Folders in home directory that may duplicate project structure:\n\n")
            lines.append("| Folder | Reason | Size (MB) |\n")
            lines.append("|--------|--------|----------|\n")

            for folder in report["duplicate_project_folders"]:
                lines.append(f"| `{folder['path']}` | {folder['reason']} | {folder['size_mb']} |\n")

        # Recommendations
        if report["recommendations"]:
            lines.append("\n## Recommendations\n")
            for i, rec in enumerate(report["recommendations"], 1):
                lines.append(f"{i}. {rec}\n")

        lines.append("\n---\n")
        lines.append("\n## Next Steps\n")
        lines.append("1. Review exact duplicates and remove from home directory\n")
        lines.append("2. Consolidate AI config files into CLI_RESTART\n")
        lines.append("3. Move/archive duplicate project folders\n")
        lines.append("4. Create symlinks if global configs are needed\n")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)


def main():
    """Main entry point."""
    home_dir = Path(r"C:\Users\Richard Wilks")
    project_dir = Path(r"C:\Users\Richard Wilks\CLI_RESTART")

    print("=" * 60)
    print("Advanced Duplicate File Finder")
    print("=" * 60)
    print(f"Home directory: {home_dir}")
    print(f"Project directory: {project_dir}")
    print()

    finder = DuplicateFinder(home_dir, project_dir)

    # Scan both directories
    finder.scan_directory(project_dir, is_project=True)
    finder.scan_directory(home_dir, is_project=False)

    # Find similar AI configs
    finder.find_similar_ai_configs(threshold=0.7)

    # Generate report
    output_file = project_dir / "duplicate_analysis_report.json"
    print(f"\nGenerating report: {output_file}")

    report = finder.generate_report(output_file)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  - Exact duplicates: {report['summary']['exact_duplicates_found']}")
    print(f"  - Similar AI configs: {report['summary']['similar_ai_configs']}")
    print(f"  - Duplicate folders: {len(report['duplicate_project_folders'])}")
    print(f"\n📄 Reports generated:")
    print(f"  - JSON: {output_file}")
    print(f"  - Markdown: {output_file.with_suffix('.md')}")
    print()


if __name__ == "__main__":
    main()
