#!/usr/bin/env python3
"""
DeepSeek Adapter

Integrates DeepSeek Coder V2 Lite via Ollama for local AI-powered code assistance.
Supports Aider, Continue, and OpenCode CLI tools configured with DeepSeek.
Runs locally with no API costs, complete privacy, and offline capability.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

import requests

from .base_adapter import (
    AdapterPerformanceProfile,
    AdapterResult,
    AdapterType,
    BaseAdapter,
)

logger = logging.getLogger(__name__)


class DeepSeekAdapter(BaseAdapter):
    """DeepSeek Coder V2 adapter using Ollama for local AI inference."""

    def __init__(self):
        super().__init__(
            name="deepseek",
            adapter_type=AdapterType.AI,
            description="Local AI code assistance with DeepSeek Coder V2 Lite via Ollama",
        )
        self.ollama_endpoint = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        self.model_name = "deepseek-coder-v2:lite"
        self._environment_validated = False
        self._ollama_available = None

    def get_performance_profile(self) -> AdapterPerformanceProfile:
        """Get performance profile for DeepSeek operations."""
        return AdapterPerformanceProfile(
            complexity_threshold=1.0,  # Handles all complexity levels
            preferred_file_types=["*"],  # Works with all code files
            max_files=30,  # Reasonable limit for local inference
            max_file_size=1000000,  # 1MB total for local processing
            operation_types=["edit", "analyze", "review", "generate", "refactor", "explain"],
            avg_execution_time=10.0,  # Local inference is reasonably fast
            success_rate=0.90,  # High reliability with local model
            cost_efficiency=1.0,  # Free local inference
            parallel_capable=False,  # Single local model instance
            requires_network=False,  # Fully local
            requires_api_key=False  # No API key needed
        )

    def execute(
        self,
        step: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        files: Optional[str] = None,
    ) -> AdapterResult:
        """Execute DeepSeek AI workflow step."""
        self._log_execution_start(step)

        # Validate environment before execution
        if not self._validate_environment():
            return AdapterResult(
                success=False,
                error="DeepSeek environment validation failed. Check Ollama installation and model availability.",
                metadata=self.get_health_status(),
            )

        try:
            # Extract parameters
            with_params = self._extract_with_params(step)
            emit_paths = self._extract_emit_paths(step)

            # Get tool and operation
            tool = with_params.get("tool", "aider")
            operation = with_params.get("operation", "edit")
            prompt = with_params.get("prompt", "")
            max_tokens = with_params.get("max_tokens", 4000)
            read_only = with_params.get("read_only", False)

            if not prompt:
                return AdapterResult(
                    success=False,
                    error="DeepSeek adapter requires 'prompt' parameter",
                )

            # Execute based on tool
            if tool == "aider":
                result = self._execute_aider(
                    files=files,
                    prompt=prompt,
                    operation=operation,
                    read_only=read_only,
                    emit_paths=emit_paths,
                )
            elif tool == "opencode":
                result = self._execute_opencode(
                    files=files,
                    prompt=prompt,
                    operation=operation,
                    emit_paths=emit_paths,
                )
            elif tool == "ollama_direct":
                result = self._execute_ollama_direct(
                    prompt=prompt,
                    files=files,
                    max_tokens=max_tokens,
                    emit_paths=emit_paths,
                )
            else:
                return AdapterResult(
                    success=False,
                    error=f"Unsupported tool: {tool}. Supported: aider, opencode, ollama_direct",
                )

            self._log_execution_complete(result)
            return result

        except Exception as e:
            error_msg = f"DeepSeek execution failed: {str(e)}"
            logger.error(error_msg)
            return AdapterResult(success=False, error=error_msg)

    def _execute_aider(
        self,
        files: Optional[str],
        prompt: str,
        operation: str,
        read_only: bool,
        emit_paths: list[str],
    ) -> AdapterResult:
        """Execute aider with DeepSeek model (auto-configured via .aider.conf.yml)."""

        # Build aider command
        cmd = [
            "aider",
            "--no-git",  # Don't auto-commit
            "--yes",  # Auto-confirm
        ]

        if read_only:
            cmd.append("--read-only")
        else:
            cmd.append("--quiet")  # Reduce output for edit mode

        # Add files to edit
        file_list = []
        if files:
            file_list = self._resolve_file_pattern(files)
            if not file_list:
                return AdapterResult(
                    success=False,
                    error=f"No files found matching pattern: {files}",
                )
            cmd.extend(file_list)

        try:
            # Execute aider with the prompt (uses DeepSeek from config)
            process = subprocess.run(
                cmd + ["--message", prompt],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse output
            tokens_used = self._estimate_tokens_from_text(prompt + process.stdout)

            if process.returncode == 0:
                # Generate diff artifact if files were modified
                artifacts = []
                if not read_only and file_list:
                    artifacts = self._generate_diff_artifacts(emit_paths, file_list)

                return AdapterResult(
                    success=True,
                    tokens_used=tokens_used,
                    artifacts=artifacts,
                    output=process.stdout,
                    metadata={
                        "tool": "aider",
                        "model": self.model_name,
                        "ollama_endpoint": self.ollama_endpoint,
                        "files_analyzed": len(file_list),
                        "read_only": read_only,
                        "operation": operation,
                    },
                )
            else:
                return AdapterResult(
                    success=False,
                    error=f"Aider failed: {process.stderr}",
                    output=process.stdout,
                )

        except subprocess.TimeoutExpired:
            return AdapterResult(
                success=False,
                error="Aider execution timed out after 5 minutes",
            )
        except Exception as e:
            return AdapterResult(
                success=False,
                error=f"Aider execution error: {str(e)}",
            )

    def _execute_opencode(
        self,
        files: Optional[str],
        prompt: str,
        operation: str,
        emit_paths: list[str],
    ) -> AdapterResult:
        """Execute OpenCode wrapper script with DeepSeek."""

        # Use the wrapper script that automatically sets DeepSeek model
        script_dir = Path(__file__).parent.parent.parent.parent / "scripts"
        wrapper_script = script_dir / "opencode-deepseek-run.ps1"

        if not wrapper_script.exists():
            # Fallback to user directory
            wrapper_script = Path.home() / "opencode-deepseek-run.ps1"

        if not wrapper_script.exists():
            return AdapterResult(
                success=False,
                error=f"OpenCode wrapper script not found: {wrapper_script}",
            )

        try:
            # Build command
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(wrapper_script), prompt]

            # Execute OpenCode
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.getcwd(),
            )

            tokens_used = self._estimate_tokens_from_text(prompt + process.stdout)

            if process.returncode == 0:
                return AdapterResult(
                    success=True,
                    tokens_used=tokens_used,
                    output=process.stdout,
                    metadata={
                        "tool": "opencode",
                        "model": self.model_name,
                        "operation": operation,
                    },
                )
            else:
                return AdapterResult(
                    success=False,
                    error=f"OpenCode failed: {process.stderr}",
                    output=process.stdout,
                )

        except subprocess.TimeoutExpired:
            return AdapterResult(
                success=False,
                error="OpenCode execution timed out after 5 minutes",
            )
        except Exception as e:
            return AdapterResult(
                success=False,
                error=f"OpenCode execution error: {str(e)}",
            )

    def _execute_ollama_direct(
        self,
        prompt: str,
        files: Optional[str],
        max_tokens: int,
        emit_paths: list[str],
    ) -> AdapterResult:
        """Execute direct Ollama API call with DeepSeek model."""

        try:
            # Prepare context from files if provided
            context = ""
            if files:
                file_list = self._resolve_file_pattern(files)
                context = self._read_files_for_context(file_list[:10])  # Limit to 10 files

            # Build full prompt with context
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            # Call Ollama API
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                    }
                },
                timeout=300,
            )

            if response.status_code == 200:
                result_data = response.json()
                ai_response = result_data.get("response", "")
                tokens_used = self._estimate_tokens_from_text(full_prompt + ai_response)

                # Save response to artifacts
                artifacts = self._save_ollama_response(emit_paths, ai_response, prompt)

                return AdapterResult(
                    success=True,
                    tokens_used=tokens_used,
                    artifacts=artifacts,
                    output=ai_response,
                    metadata={
                        "tool": "ollama_direct",
                        "model": self.model_name,
                        "endpoint": self.ollama_endpoint,
                        "prompt_length": len(full_prompt),
                    },
                )
            else:
                return AdapterResult(
                    success=False,
                    error=f"Ollama API error: {response.status_code} - {response.text}",
                )

        except requests.exceptions.ConnectionError:
            return AdapterResult(
                success=False,
                error=f"Cannot connect to Ollama at {self.ollama_endpoint}. Is Ollama running?",
            )
        except requests.exceptions.Timeout:
            return AdapterResult(
                success=False,
                error="Ollama API request timed out after 5 minutes",
            )
        except Exception as e:
            return AdapterResult(
                success=False,
                error=f"Ollama API error: {str(e)}",
            )

    def _resolve_file_pattern(self, pattern: str) -> list[str]:
        """Resolve glob pattern to list of actual files."""
        try:
            from glob import glob

            files = glob(pattern, recursive=True)
            # Filter to common code files
            return [
                f for f in files
                if f.endswith((
                    ".py", ".ts", ".js", ".jsx", ".tsx", ".md", ".yaml", ".yml",
                    ".json", ".toml", ".sh", ".ps1", ".cmd", ".bat",
                    ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp"
                ))
            ]
        except Exception as e:
            logger.warning(f"Failed to resolve file pattern {pattern}: {e}")
            return []

    def _read_files_for_context(self, file_paths: list[str]) -> str:
        """Read file contents to provide context to the AI."""
        context_parts = []
        for file_path in file_paths:
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                    context_parts.append(f"File: {file_path}\n```\n{content}\n```\n")
            except Exception as e:
                logger.warning(f"Failed to read {file_path}: {e}")
                continue

        return "\n".join(context_parts)

    def _estimate_tokens_from_text(self, text: str) -> int:
        """Estimate token count from text (rough approximation)."""
        # Conservative estimate: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)

    def _generate_diff_artifacts(
        self, emit_paths: list[str], modified_files: list[str]
    ) -> list[str]:
        """Generate diff artifacts for modified files."""
        artifacts = []

        for emit_path in emit_paths:
            try:
                # Generate git diff for the modified files
                diff_result = subprocess.run(
                    ["git", "diff", "--no-color"] + modified_files,
                    capture_output=True,
                    text=True,
                )

                if diff_result.returncode == 0 and diff_result.stdout:
                    # Save diff to artifact file
                    Path(emit_path).parent.mkdir(parents=True, exist_ok=True)

                    diff_data = {
                        "type": "deepseek_edit_diff",
                        "model": self.model_name,
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

    def _save_ollama_response(
        self, emit_paths: list[str], response: str, prompt: str
    ) -> list[str]:
        """Save Ollama API response to artifact files."""
        artifacts = []

        for emit_path in emit_paths:
            try:
                Path(emit_path).parent.mkdir(parents=True, exist_ok=True)

                response_data = {
                    "type": "deepseek_response",
                    "model": self.model_name,
                    "prompt": prompt,
                    "response": response,
                    "timestamp": self._get_timestamp(),
                }

                with open(emit_path, "w") as f:
                    json.dump(response_data, f, indent=2)

                artifacts.append(emit_path)

            except Exception as e:
                logger.warning(f"Failed to save response artifact {emit_path}: {e}")

        return artifacts

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def validate_step(self, step: dict[str, Any]) -> bool:
        """Validate that this adapter can execute the given step."""
        with_params = self._extract_with_params(step)

        # Check required parameters
        if "prompt" not in with_params:
            return False

        # Check supported tools
        tool = with_params.get("tool", "aider")
        supported_tools = ["aider", "opencode", "ollama_direct"]

        return tool in supported_tools

    def estimate_cost(self, step: dict[str, Any]) -> int:
        """Estimate token cost (always 0 for local inference)."""
        # Local inference is free, but we can estimate tokens for tracking
        with_params = self._extract_with_params(step)
        prompt = with_params.get("prompt", "")
        max_tokens = with_params.get("max_tokens", 4000)

        # Estimate tokens for monitoring purposes
        prompt_tokens = len(prompt.split()) * 1.3
        return int(prompt_tokens + max_tokens * 0.5)

    def is_available(self) -> bool:
        """Check if Ollama and DeepSeek model are available."""
        if self._ollama_available is not None:
            return self._ollama_available

        try:
            # Check Ollama connectivity
            response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=5)

            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get("models", [])

                # Check if DeepSeek model is available
                has_deepseek = any(
                    "deepseek" in model.get("name", "").lower()
                    for model in models
                )

                if has_deepseek:
                    self.logger.info(f"DeepSeek model available via Ollama at {self.ollama_endpoint}")
                    self._ollama_available = True
                else:
                    self.logger.warning("DeepSeek model not found. Run: ollama pull deepseek-coder-v2:lite")
                    self._ollama_available = False

                return self._ollama_available

        except requests.exceptions.ConnectionError:
            self.logger.warning(f"Cannot connect to Ollama at {self.ollama_endpoint}")
            self._ollama_available = False
        except Exception as e:
            self.logger.error(f"Error checking Ollama availability: {e}")
            self._ollama_available = False

        return False

    def _validate_environment(self) -> bool:
        """Perform comprehensive environment validation."""
        if self._environment_validated:
            return True

        validation_results = []

        # Check Ollama availability
        try:
            response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                validation_results.append("✅ Ollama service running")

                models_data = response.json()
                models = models_data.get("models", [])

                # Find DeepSeek model
                deepseek_models = [
                    model for model in models
                    if "deepseek" in model.get("name", "").lower()
                ]

                if deepseek_models:
                    model_name = deepseek_models[0].get("name", "")
                    model_size = deepseek_models[0].get("size", 0) / (1024**3)  # GB
                    validation_results.append(f"✅ DeepSeek model found: {model_name} ({model_size:.2f} GB)")
                else:
                    validation_results.append("❌ DeepSeek model not found")
                    validation_results.append("   Run: ollama pull deepseek-coder-v2:lite")
            else:
                validation_results.append("❌ Ollama service not responding properly")
        except requests.exceptions.ConnectionError:
            validation_results.append(f"❌ Cannot connect to Ollama at {self.ollama_endpoint}")
            validation_results.append("   Ensure Ollama is running")
        except Exception as e:
            validation_results.append(f"❌ Ollama check failed: {str(e)}")

        # Check aider availability (optional)
        try:
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                validation_results.append("✅ Aider available")
            else:
                validation_results.append("⚠️ Aider not available (optional)")
        except:
            validation_results.append("⚠️ Aider not found (optional tool)")

        # Check opencode availability (optional)
        try:
            result = subprocess.run(
                ["opencode", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                validation_results.append("✅ OpenCode available")
            else:
                validation_results.append("⚠️ OpenCode not available (optional)")
        except:
            validation_results.append("⚠️ OpenCode not found (optional tool)")

        # Log validation results
        self.logger.info("DeepSeek environment validation:")
        for result in validation_results:
            self.logger.info(f"  {result}")

        # Environment is valid if Ollama and DeepSeek model are available
        self._environment_validated = self.is_available()

        return self._environment_validated

    def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status for DeepSeek integration."""
        self._validate_environment()

        health = {
            "adapter_name": self.name,
            "ollama_endpoint": self.ollama_endpoint,
            "model_name": self.model_name,
            "ollama_available": self._ollama_available or False,
            "environment_valid": self._environment_validated,
            "cost": "Free (local inference)",
            "requires_api_key": False,
            "supported_tools": ["aider", "opencode", "ollama_direct"],
            "supported_operations": [
                "edit", "analyze", "review", "generate", "refactor", "explain"
            ],
        }

        # Get model details if available
        if self._ollama_available:
            try:
                response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    models = models_data.get("models", [])
                    deepseek_models = [
                        model for model in models
                        if "deepseek" in model.get("name", "").lower()
                    ]
                    if deepseek_models:
                        health["model_info"] = deepseek_models[0]
            except:
                pass

        return health

    def get_supported_operations(self) -> list[str]:
        """Get list of supported operations."""
        return [
            "edit",  # Code editing
            "analyze",  # Code analysis
            "review",  # Code review
            "generate",  # Code generation
            "refactor",  # Refactoring
            "explain",  # Code explanation
            "fix",  # Bug fixing
            "optimize",  # Optimization
            "document",  # Documentation
            "test",  # Test generation
        ]
