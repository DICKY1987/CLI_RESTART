@echo off
REM OpenCode wrapper script to use DeepSeek via Ollama
REM Usage: opencode-deepseek.cmd [project] [options]

opencode -m ollama/deepseek-coder-v2:lite %*
