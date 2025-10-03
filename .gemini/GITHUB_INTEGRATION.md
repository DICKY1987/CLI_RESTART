# GitHub Integration for Gemini CLI

This document describes the GitHub integration configuration for Gemini CLI, matching the setup of Claude Code and Codex.

## Configuration Overview

The Gemini CLI is now configured with comprehensive GitHub integration that matches Claude Code and Codex:

### Authentication
- **GitHub Token**: `${GITHUB_TOKEN}` (set via environment variable)
- **GitHub Username**: `DICKY1987`
- **Email**: `richgwilks@gmail.com`
- **Authentication Method**: GitHub CLI + Environment Token

### Token Permissions
The configured GitHub token has the following scopes:
- `repo` - Full repository access
- `workflow` - GitHub Actions workflow access
- `read:org` - Read organization information
- `gist` - Gist management

### Enabled Features
1. **Repository Operations**
   - Clone, pull, push repositories
   - Create and manage branches
   - View repository information

2. **Pull Request Management**
   - Create pull requests
   - Review and comment on PRs
   - Merge pull requests
   - View PR status and checks

3. **Issue Management**
   - Create and edit issues
   - Add labels and assignees
   - Comment on issues
   - Close and reopen issues

4. **File Operations**
   - Read and write files in repositories
   - Create commits
   - Push changes to remote

5. **Workflow Operations**
   - Trigger GitHub Actions workflows
   - View workflow runs and logs
   - Monitor workflow status

## Configuration Files

### Main Configuration: `.gemini/settings.json`
Contains the primary GitHub integration settings:
```json
{
  "github": {
    "integration": {
      "enabled": true,
      "api_url": "https://api.github.com",
      "token": "${GITHUB_TOKEN}",
      "username": "DICKY1987",
      "permissions": {
        "full_repo_access": true,
        "create_pull_requests": true,
        "create_issues": true,
        "modify_files": true,
        "workflow_access": true,
        "read_org": true
      }
    }
  }
}
```

### Project Trust: `.gemini/config.toml`
Manages project-level trust and permissions:
```toml
[projects.'C:\Users\Richard Wilks\CLI_RESTART']
trust_level = "trusted"
enable_git_operations = true
enable_file_operations = true
enable_workflow_execution = true

[github]
enabled = true
default_username = "DICKY1987"
api_url = "https://api.github.com"
```

### User Preferences: `.gemini/user_preferences.json`
Contains GitHub-specific user preferences:
```json
{
  "github": {
    "default_repo_visibility": "private",
    "auto_create_pr": false,
    "pr_template_enabled": true,
    "issue_template_enabled": true,
    "default_pr_branch": "main",
    "enable_actions": true
  },
  "git": {
    "auto_fetch": true,
    "auto_pull": false,
    "auto_push": false,
    "default_branch": "main",
    "signed_commits": true
  }
}
```

## Usage Examples

### Working with Repositories

```bash
# Clone a repository
gh repo clone DICKY1987/CLI_RESTART

# View repository details
gh repo view DICKY1987/CLI_RESTART

# List your repositories
gh repo list DICKY1987
```

### Managing Pull Requests

```bash
# Create a new pull request
gh pr create --title "Add new feature" --body "Description of changes"

# List open pull requests
gh pr list --state open

# Review a pull request
gh pr view 123
gh pr review 123 --approve

# Merge a pull request
gh pr merge 123 --squash
```

### Managing Issues

```bash
# Create an issue
gh issue create --title "Bug report" --body "Description"

# List issues
gh issue list --state open

# Add labels to an issue
gh issue edit 456 --add-label "bug,priority:high"

# Close an issue
gh issue close 456
```

### Working with Workflows

```bash
# List workflows
gh workflow list

# Run a workflow
gh workflow run "CI Pipeline"

# View workflow runs
gh run list

# Watch a workflow run
gh run watch
```

## Integration with CLI Orchestrator

The Gemini CLI GitHub integration works seamlessly with the CLI Orchestrator workflows:

### Repository Analysis
```bash
cli-orchestrator run .ai/workflows/GITHUB_REPO_ANALYSIS.yaml --repo DICKY1987/CLI_RESTART
```

### Issue Automation
```bash
cli-orchestrator run .ai/workflows/GITHUB_ISSUE_AUTOMATION.yaml \
  --repo DICKY1987/CLI_RESTART \
  --state open \
  --create-report-issue true
```

### PR Review Automation
```bash
cli-orchestrator run .ai/workflows/GITHUB_PR_REVIEW.yaml \
  --repo DICKY1987/CLI_RESTART \
  --create-summary-issue true
```

## Security Best Practices

1. **Token Storage**: GitHub token is stored in configuration files. Ensure proper file permissions:
   ```bash
   # Windows: Restrict access to configuration directory
   icacls "C:\Users\Richard Wilks\.gemini" /inheritance:r /grant:r "%USERNAME%:F"
   ```

2. **Token Rotation**: Regularly rotate GitHub tokens for security
   - Update `.gemini/settings.json` with new token
   - Update environment variable `GITHUB_TOKEN`
   - Verify with `gh auth status`

3. **Scope Minimization**: Only grant necessary permissions
   - Review token scopes regularly
   - Revoke unused permissions

4. **Audit Logging**: All GitHub operations are logged in session files
   - Location: `.gemini/sessions/YYYY/MM/DD/`
   - Format: JSONL for easy parsing

## Troubleshooting

### Common Issues

#### Token Authentication Fails
```bash
# Verify token is set correctly
echo $GITHUB_TOKEN

# Re-authenticate with GitHub CLI
gh auth login --with-token < token.txt

# Verify authentication
gh auth status
```

#### Permission Denied
```bash
# Check token permissions
gh auth status

# Verify repository access
gh repo view DICKY1987/CLI_RESTART
```

#### API Rate Limiting
```bash
# Check rate limit status
gh api rate_limit

# Wait for rate limit reset or use authenticated requests
```

### Configuration Validation

```bash
# Verify Gemini configuration
cat ~/.gemini/settings.json | jq '.github'

# Test GitHub API connectivity
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Verify repository access
gh api repos/DICKY1987/CLI_RESTART
```

## Comparison with Claude Code and Codex

### Feature Parity

| Feature | Claude Code | Codex | Gemini CLI |
|---------|-------------|-------|------------|
| GitHub Token | ✅ | ✅ | ✅ |
| OAuth Integration | ✅ | ✅ | ✅ |
| Repository Operations | ✅ | ✅ | ✅ |
| PR Management | ✅ | ✅ | ✅ |
| Issue Management | ✅ | ✅ | ✅ |
| Workflow Execution | ✅ | ✅ | ✅ |
| Project Trust Levels | ✅ | ✅ | ✅ |
| Session Management | ✅ | ✅ | ✅ |

### Configuration Alignment

All three tools now share:
- Same GitHub token: `${GITHUB_TOKEN}` (from environment variable)
- Same username: `DICKY1987`
- Same email: `richgwilks@gmail.com`
- Same working directory: `C:\Users\Richard Wilks`
- Same trusted projects: CLI_RESTART, cli_multi_rapid_DEV

## Next Steps

1. **Test Integration**
   ```bash
   # Verify GitHub connectivity
   gh auth status

   # Test repository access
   gh repo view DICKY1987/CLI_RESTART

   # Run a test workflow
   cli-orchestrator run .ai/workflows/GITHUB_REPO_ANALYSIS.yaml --repo DICKY1987/CLI_RESTART --dry-run
   ```

2. **Configure Additional Repositories**
   - Add more repositories to `.gemini/config.toml`
   - Set appropriate trust levels
   - Enable required features per project

3. **Set Up Automation**
   - Configure workflow triggers
   - Set up scheduled tasks
   - Enable notifications

4. **Monitor and Maintain**
   - Review session logs regularly
   - Monitor API usage and rate limits
   - Update tokens before expiration
   - Review and update permissions as needed

## Support and Documentation

- **Claude Code Docs**: See `CLAUDE.md` in repository root
- **Gemini CLI Docs**: See `GEMINI.md` in `.gemini/` directory
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **GitHub API Docs**: https://docs.github.com/en/rest

For issues or questions, consult the respective tool documentation or create an issue in the CLI_RESTART repository.
