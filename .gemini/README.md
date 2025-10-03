# Gemini CLI Configuration

This directory contains the configuration files for Gemini CLI with full GitHub integration, matching the setup of Claude Code and Codex.

## Directory Structure

```
.gemini/
├── README.md                   # This file
├── GEMINI.md                   # Project context and guidelines
├── GITHUB_INTEGRATION.md       # GitHub integration documentation
├── settings.json               # Main configuration file
├── settings.json.template      # Template for new configurations
├── config.toml                 # Project trust and permissions (TOML format)
├── user_preferences.json       # User-specific preferences
├── oauth_creds.json           # Google OAuth credentials
├── google_accounts.json       # Google account information
├── installation_id            # Gemini installation identifier
├── sessions/                   # Session history (JSONL format)
│   └── YYYY/MM/DD/            # Organized by date
└── tmp/                       # Temporary files and cache

```

## Configuration Files

### Core Configuration

#### `settings.json`
Main configuration file containing:
- Security and authentication settings
- GitHub integration configuration
- Local environment settings
- Project-specific settings
- User preferences
- Feature flags
- API configuration

**Key Sections:**
- `security.auth`: OAuth authentication settings
- `user`: User information (email, display name, organization)
- `github.integration`: GitHub token, permissions, and API settings
- `local_environment`: Working directory and operation permissions
- `projects`: Per-project trust levels and enabled features
- `preferences`: UI and behavior preferences
- `features`: Feature toggles (web search, code execution, etc.)
- `api_config`: Google AI API settings

#### `config.toml`
Project trust and permissions in TOML format:
- Project trust levels
- Per-project permission settings
- GitHub repository shortcuts
- API preferences
- Session management settings

#### `user_preferences.json`
User-specific preferences:
- Editor settings
- Git configuration
- GitHub preferences
- Workspace settings
- Notification preferences
- Performance settings
- UI preferences

### Authentication Files

#### `oauth_creds.json`
Google OAuth credentials including:
- Access token
- Refresh token
- Token scopes
- Token expiration

#### `google_accounts.json`
Active Google account information

## GitHub Integration

The Gemini CLI is configured with full GitHub integration:

### Credentials
- **Token**: Environment variable `GITHUB_TOKEN`
- **Username**: DICKY1987
- **Email**: richgwilks@gmail.com

### Permissions
- Full repository access (`repo`)
- Workflow access (`workflow`)
- Organization read access (`read:org`)
- Gist management (`gist`)

### Enabled Operations
- ✅ Clone and manage repositories
- ✅ Create and manage pull requests
- ✅ Create and manage issues
- ✅ Modify files and create commits
- ✅ Trigger and monitor workflows
- ✅ Read organization information

See `GITHUB_INTEGRATION.md` for detailed documentation.

## Quick Start

### 1. Verify Configuration
```bash
# Check GitHub authentication
gh auth status

# Verify Gemini configuration
cat ~/.gemini/settings.json | jq '.github'
```

### 2. Test GitHub Integration
```bash
# View a repository
gh repo view DICKY1987/CLI_RESTART

# List pull requests
gh pr list

# List issues
gh issue list
```

### 3. Use with CLI Orchestrator
```bash
# Run GitHub repository analysis
cli-orchestrator run .ai/workflows/GITHUB_REPO_ANALYSIS.yaml --repo DICKY1987/CLI_RESTART

# Automate issue triage
cli-orchestrator run .ai/workflows/GITHUB_ISSUE_AUTOMATION.yaml --repo DICKY1987/CLI_RESTART
```

## Trusted Projects

The following projects are configured as trusted:

1. **C:\Users\Richard Wilks**
   - Base working directory
   - Git and file operations enabled
   - Web search enabled

2. **C:\Users\Richard Wilks\CLI_RESTART**
   - Main CLI orchestrator project
   - All features enabled
   - Workflow execution enabled

3. **C:\Users\Richard Wilks\cli_multi_rapid_DEV**
   - Development environment
   - Git and file operations enabled

## Features

### Enabled Features
- ✅ **Web Search**: Google-powered web search
- ✅ **Code Execution**: Run code with 30s timeout
- ✅ **File Search**: Search files with max 100 results
- ✅ **GitHub Integration**: Full GitHub API access
- ✅ **Workflow Execution**: CLI orchestrator workflows
- ✅ **Session Management**: Auto-save and history tracking

### Preferences
- ✅ Auto-updates enabled
- ✅ Always-thinking mode enabled
- ✅ Enhanced status line with git info
- ✅ Session auto-save
- ✅ History tracking (100 items)

## Session Management

Sessions are automatically saved in `.gemini/sessions/` organized by date:

```
sessions/
├── 2025/
│   ├── 09/
│   │   ├── 30/
│   │   │   └── rollout-2025-09-30T*.jsonl
│   └── 10/
│       ├── 01/
│       │   └── rollout-2025-10-01T*.jsonl
│       └── 03/
│           └── rollout-2025-10-03T*.jsonl
```

Each session is stored in JSONL format for easy parsing and analysis.

## Maintenance

### Update GitHub Token
1. Generate new token at https://github.com/settings/tokens
2. Update `settings.json`:
   ```json
   {
     "github": {
       "integration": {
         "token": "NEW_TOKEN_HERE"
       }
     }
   }
   ```
3. Update environment variable:
   ```bash
   export GITHUB_TOKEN="NEW_TOKEN_HERE"
   ```
4. Verify:
   ```bash
   gh auth status
   ```

### Clean Old Sessions
Sessions older than 30 days are automatically cleaned. Manual cleanup:
```bash
# Remove sessions older than 30 days
find ~/.gemini/sessions -type f -mtime +30 -delete
```

### Backup Configuration
```bash
# Backup configuration files
tar -czf gemini-config-backup-$(date +%Y%m%d).tar.gz ~/.gemini/*.json ~/.gemini/*.toml

# Restore from backup
tar -xzf gemini-config-backup-YYYYMMDD.tar.gz -C ~/
```

## Troubleshooting

### GitHub Authentication Issues
```bash
# Re-authenticate
gh auth login

# Verify token permissions
gh auth status

# Test API access
gh api user
```

### Configuration Validation
```bash
# Validate JSON configuration
cat ~/.gemini/settings.json | jq '.'

# Check TOML configuration
cat ~/.gemini/config.toml
```

### Permission Issues
```bash
# Fix file permissions (Windows)
icacls "%USERPROFILE%\.gemini" /inheritance:r /grant:r "%USERNAME%:F"
```

## Related Documentation

- **Project Context**: See `GEMINI.md` for project-specific guidelines
- **GitHub Integration**: See `GITHUB_INTEGRATION.md` for detailed GitHub setup
- **Claude Code Config**: See `CLAUDE.md` in repository root
- **Environment Variables**: See `.env.template` in repository root

## Support

For issues or questions:
1. Check the documentation files in this directory
2. Review session logs in `.gemini/sessions/`
3. Consult the CLI_RESTART repository documentation
4. Create an issue in the repository if needed

## Version Information

- **Configuration Version**: 1.0
- **Last Updated**: 2025-10-03
- **Compatible With**:
  - Gemini CLI 2.0+
  - GitHub CLI 2.0+
  - CLI Orchestrator 1.0+
