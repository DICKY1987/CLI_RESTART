#!/usr/bin/env python3
"""
AI Editor Adapter

Integrates AI-powered code editing tools like aider for intelligent code modifications.
Supports multiple AI backends (Claude, GPT, Gemini) with cost tracking and safety gates.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_adapter import AdapterResult, AdapterType, BaseAdapter, AdapterPerformanceProfile

logger = logging.getLogger(__name__)


class AIEditorAdapter(BaseAdapter):
    """AI-powered code editing adapter using aider and other AI tools."""

    def __init__(self):
        super().__init__(
            name="ai_editor",
            adapter_type=AdapterType.AI,
            description="AI-powered code editing with aider integration",
        )
        self._aider_config = self._validate_aider_configuration()
        self._environment_validated = False

    def get_performance_profile(self) -> AdapterPerformanceProfile:
        """Get performance profile for AI editing operations."""
        return AdapterPerformanceProfile(
            complexity_threshold=1.0,  # Handles all complexity levels
            preferred_file_types=["*"],  # Works with all file types
            max_files=50,  # Limited by context window
            max_file_size=2000000,  # 2MB total due to token limits
            operation_types=["edit", "refactor", "generate", "analyze"],
            avg_execution_time=15.0,  # AI calls take longer
            success_rate=0.85,  # Good but dependent on AI model
            cost_efficiency=0.7,  # Moderate token cost
            parallel_capable=False,  # API rate limits
            requires_network=True,
            requires_api_key=True
        )

    def execute(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        files: Optional[str] = None,
    ) -> AdapterResult:
        """Execute AI editing workflow step."""
        self._log_execution_start(step)

        # Validate environment before execution
        if not self._validate_environment():
            return AdapterResult(
                success=False,
                error="AI editor environment validation failed. Check aider installation and API keys.",
                metadata=self.get_aider_health_status(),
            )

        try:
            # Extract parameters
            with_params = self._extract_with_params(step)
            emit_paths = self._extract_emit_paths(step)

            # Get AI tool and operation
            tool = with_params.get("tool", "aider")
            operation = with_params.get("operation", "edit")
            prompt = with_params.get("prompt", "")
            model = with_params.get("model", "claude-3-5-sonnet-20241022")
            max_tokens = with_params.get("max_tokens", 4000)

            if not prompt:
                return AdapterResult(
                    success=False,
                    error="AI editor requires 'prompt' parameter",
                )

            # Execute AI editing based on tool
            if tool == "aider":
                result = self._execute_aider_edit(
                    files=files,
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    operation=operation,
                    emit_paths=emit_paths,
                )
            elif tool == "claude_direct":
                result = self._execute_claude_direct(
                    files=files,
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    emit_paths=emit_paths,
                )
            else:
                return AdapterResult(
                    success=False,
                    error=f"Unsupported AI tool: {tool}",
                )

            self._log_execution_complete(result)
            return result

        except Exception as e:
            error_msg = f"AI editing failed: {str(e)}"
            logger.error(error_msg)
            return AdapterResult(success=False, error=error_msg)

    def _execute_aider_edit(
        self,
        files: Optional[str],
        prompt: str,
        model: str,
        max_tokens: int,
        operation: str,
        emit_paths: List[str],
    ) -> AdapterResult:
        """Execute aider-based AI editing."""

        # Build aider command
        cmd = [
            "aider",
            "--model",
            model,
            "--no-git",  # Don't auto-commit
            "--yes",  # Auto-confirm
            "--quiet",  # Reduce output
        ]

        # Add files to edit
        if files:
            # Convert glob pattern to actual files
            file_list = self._resolve_file_pattern(files)
            if not file_list:
                return AdapterResult(
                    success=False,
                    error=f"No files found matching pattern: {files}",
                )
            cmd.extend(file_list)

        # Create temporary file for the prompt
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as prompt_file:
            prompt_file.write(prompt)
            prompt_file_path = prompt_file.name

        try:
            # Execute aider with the prompt
            process = subprocess.run(
                cmd + ["--message", prompt],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse aider output
            tokens_used = self._extract_tokens_from_aider_output(process.stdout)

            if process.returncode == 0:
                # Generate diff artifact
                artifacts = self._generate_diff_artifacts(
                    emit_paths, file_list if files else []
                )

                return AdapterResult(
                    success=True,
                    tokens_used=tokens_used,
                    artifacts=artifacts,
                    output=process.stdout,
                    metadata={
                        "tool": "aider",
                        "model": model,
                        "files_modified": len(file_list) if files else 0,
                        "prompt_length": len(prompt),
                    },
                )
            else:
                return AdapterResult(
                    success=False,
                    error=f"Aider failed: {process.stderr}",
                    output=process.stdout,
                )

        finally:
            # Clean up prompt file
            Path(prompt_file_path).unlink(missing_ok=True)

    def _execute_claude_direct(
        self,
        files: Optional[str],
        prompt: str,
        model: str,
        max_tokens: int,
        emit_paths: List[str],
    ) -> AdapterResult:
        """Execute direct Claude API integration (placeholder for future implementation)."""

        # This would integrate directly with Anthropic's API
        # For now, return a helpful error suggesting to use aider
        return AdapterResult(
            success=False,
            error="Direct Claude integration not yet implemented. Use 'aider' tool instead.",
            metadata={
                "suggestion": "Use 'tool: aider' with 'model: claude-3-5-sonnet-20241022'",
            },
        )

    def _resolve_file_pattern(self, pattern: str) -> List[str]:
        """Resolve glob pattern to list of actual files."""
        try:
            from glob import glob

            files = glob(pattern, recursive=True)
            # Filter to only Python files for safety
            return [
                f
                for f in files
                if f.endswith((".py", ".ts", ".js", ".md", ".yaml", ".yml"))
            ]
        except Exception as e:
            logger.warning(f"Failed to resolve file pattern {pattern}: {e}")
            return []

    def _extract_tokens_from_aider_output(self, output: str) -> int:
        """Extract token usage from aider output."""
        # Aider typically shows token usage in its output
        # Look for patterns like "Tokens: 1234"
        import re

        patterns = [
            r"Tokens:\s*(\d+)",
            r"(\d+)\s*tokens",
            r"Token usage:\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))

        # Estimate tokens if not found (rough approximation)
        return len(output.split()) * 1.3  # Conservative estimate

    def _generate_diff_artifacts(
        self, emit_paths: List[str], modified_files: List[str]
    ) -> List[str]:
        """Generate diff artifacts for modified files."""
        artifacts = []

        for emit_path in emit_paths:
            try:
                # Generate git diff for the modified files
                if modified_files:
                    diff_result = subprocess.run(
                        ["git", "diff", "--no-color"] + modified_files,
                        capture_output=True,
                        text=True,
                    )

                    if diff_result.returncode == 0:
                        # Save diff to artifact file
                        Path(emit_path).parent.mkdir(parents=True, exist_ok=True)

                        diff_data = {
                            "type": "ai_edit_diff",
                            "files_modified": modified_files,
                            "diff": diff_result.stdout,
                            "timestamp": self._get_timestamp(),
                        }

                        with open(emit_path, "w") as f:
                            json.dump(diff_data, f, indent=2)

                        artifacts.append(emit_path)

            except Exception as e:
                logger.warning(f"Failed to generate diff artifact {emit_path}: {e}")

        return artifacts

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()

    def validate_step(self, step: Dict[str, Any]) -> bool:
        """Validate that this adapter can execute the given step."""
        with_params = self._extract_with_params(step)

        # Check required parameters
        if "prompt" not in with_params:
            return False

        # Check supported tools
        tool = with_params.get("tool", "aider")
        supported_tools = ["aider", "claude_direct"]

        return tool in supported_tools

    def estimate_cost(self, step: Dict[str, Any]) -> int:
        """Estimate token cost for AI editing operation."""
        with_params = self._extract_with_params(step)

        # Base cost for the prompt
        prompt = with_params.get("prompt", "")
        base_tokens = len(prompt.split()) * 1.3  # Conservative token estimate

        # Add estimated tokens for file content
        max_tokens = with_params.get("max_tokens", 4000)

        # AI editing typically uses 2-3x the input tokens for output
        estimated_total = base_tokens + max_tokens * 2

        return int(estimated_total)

    def is_available(self) -> bool:
        """Check if aider or other AI tools are available."""
        try:
            # Check if aider is installed
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            available = result.returncode == 0
            if available:
                self.logger.info(f"Aider available: {result.stdout.strip()}")
            else:
                self.logger.warning("Aider not available or not working properly")
            return available
        except FileNotFoundError:
            self.logger.warning("Aider command not found in PATH")
            return False
        except subprocess.TimeoutExpired:
            self.logger.warning("Aider version check timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error checking aider availability: {e}")
            return False

    def get_supported_models(self) -> List[str]:
        """Get list of supported AI models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "gpt-4-turbo-preview",
            "gpt-4",
            "gemini-1.5-pro",
        ]

    def get_supported_operations(self) -> List[str]:
        """Get list of supported editing operations."""
        return [
            "edit",  # General editing
            "refactor",  # Code refactoring
            "fix",  # Bug fixing
            "optimize",  # Performance optimization
            "document",  # Add documentation
            "test",  # Add tests
        ]

    def _validate_aider_configuration(self) -> Dict[str, Any]:
        """Validate aider configuration and environment setup."""
        config = {
            "aider_path": None,
            "api_keys_available": {},
            "default_model": "claude-3-5-sonnet-20241022",
            "max_retries": 3,
            "timeout": 300,
            "safety_checks": True,
        }

        # Check for aider installation
        try:
            import shutil
            config["aider_path"] = shutil.which("aider")
            if not config["aider_path"]:
                self.logger.warning("Aider not found in PATH")
        except Exception as e:
            self.logger.error(f"Error checking aider installation: {e}")

        # Check for API keys
        api_key_vars = {
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY"
        }

        for service, env_var in api_key_vars.items():
            key_available = bool(os.getenv(env_var))
            config["api_keys_available"][service] = key_available
            if key_available:
                self.logger.debug(f"{service} API key found")
            else:
                self.logger.debug(f"{service} API key not found ({env_var})")

        return config

    def _validate_environment(self) -> bool:
        """Perform comprehensive environment validation."""
        if self._environment_validated:
            return True

        validation_results = []

        # Check aider availability
        if not self._aider_config["aider_path"]:
            validation_results.append("❌ Aider not installed or not in PATH")
        else:
            validation_results.append("✅ Aider found")

        # Check for at least one API key
        if not any(self._aider_config["api_keys_available"].values()):
            validation_results.append("❌ No AI service API keys found")
        else:
            available_services = [k for k, v in self._aider_config["api_keys_available"].items() if v]
            validation_results.append(f"✅ API keys available for: {', '.join(available_services)}")

        # Check git repository (aider works better in git repos)
        try:
            git_result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if git_result.returncode == 0:
                validation_results.append("✅ Git repository detected")
            else:
                validation_results.append("⚠️ Not in a git repository (aider works better with git)")
        except Exception:
            validation_results.append("⚠️ Could not check git status")

        # Log validation results
        self.logger.info("Aider environment validation:")
        for result in validation_results:
            self.logger.info(f"  {result}")

        # Environment is valid if aider is available and at least one API key exists
        self._environment_validated = (
            self._aider_config["aider_path"] is not None and
            any(self._aider_config["api_keys_available"].values())
        )

        return self._environment_validated

    def get_aider_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for aider integration."""
        self._validate_environment()

        return {
            "adapter_name": self.name,
            "aider_available": self._aider_config["aider_path"] is not None,
            "aider_path": self._aider_config["aider_path"],
            "environment_valid": self._environment_validated,
            "api_keys": self._aider_config["api_keys_available"],
            "default_model": self._aider_config["default_model"],
            "supported_models": self.get_supported_models(),
            "supported_operations": self.get_supported_operations(),
        }
