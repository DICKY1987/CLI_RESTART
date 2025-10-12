@echo off
REM OpenCode run wrapper for quick commands with DeepSeek
REM Usage: opencode-deepseek-run.cmd "your message here"

opencode run -m ollama/deepseek-coder-v2:lite %*
