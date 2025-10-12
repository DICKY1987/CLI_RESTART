# =============================================================================
# AUTOMATION SUITE ENVIRONMENT VARIABLES
# =============================================================================
# This file contains environment-specific variables that override defaults
# Copy this file to .env and customize for your environment
# NEVER commit sensitive values to version control

# =============================================================================
# ENVIRONMENT IDENTIFICATION
# =============================================================================
AUTOMATION_ENVIRONMENT=Production
AUTOMATION_REGION=WestUS2
AUTOMATION_DATACENTER=DC01
AUTOMATION_CLUSTER=PROD-CLUSTER-01

# =============================================================================
# INFRASTRUCTURE ENDPOINTS
# =============================================================================
# Primary Database Server
DATABASE_SERVER=sql-primary.domain.com
DATABASE_NAME=AutomationDB
DATABASE_BACKUP_SERVER=sql-backup.domain.com

# Reporting Database
REPORTING_DATABASE_SERVER=sql-reporting.domain.com
REPORTING_DATABASE_NAME=AutomationReporting

# File Shares
CONFIG_SHARE=\\fileserver\AutomationConfig$
LOG_SHARE=\\fileserver\AutomationLogs$
DEPLOYMENT_SHARE=\\fileserver\Deployments$
BACKUP_SHARE=\\fileserver\Backups$

# Web Services
API_BASE_URL=https://api.automation.domain.com
WEB_PORTAL_URL=https://portal.automation.domain.com
HEALTH_CHECK_URL=https://health.automation.domain.com

# Domain Controllers
PRIMARY_DC=dc01.domain.com
SECONDARY_DC=dc02.domain.com
BACKUP_DC=dc03.domain.com

# =============================================================================
# SECURITY AND AUTHENTICATION
# =============================================================================
# Service Accounts (usernames only - passwords stored in Credential Manager)
PRIMARY_SERVICE_ACCOUNT=DOMAIN\svc-automation-primary
SECONDARY_SERVICE_ACCOUNT=DOMAIN\svc-automation-secondary
DATABASE_SERVICE_ACCOUNT=DOMAIN\svc-automation-db
REPORTING_SERVICE_ACCOUNT=DOMAIN\svc-automation-rpt
MONITORING_SERVICE_ACCOUNT=DOMAIN\svc-automation-monitor

# Certificate Thumbprints
CODE_SIGNING_CERT_THUMBPRINT=1234567890ABCDEF1234567890ABCDEF12345678
SSL_CERT_THUMBPRINT=FEDCBA0987654321FEDCBA0987654321FEDCBA09
ENCRYPTION_CERT_THUMBPRINT=ABCDEF1234567890ABCDEF1234567890ABCDEF12

# API Keys (store actual keys in secure location)
API_KEY_PRIMARY=YOUR_PRIMARY_API_KEY_HERE
API_KEY_SECONDARY=YOUR_SECONDARY_API_KEY_HERE
MONITORING_API_KEY=YOUR_MONITORING_API_KEY_HERE

# =============================================================================
# NETWORK CONFIGURATION
# =============================================================================
# PowerShell Remoting
REMOTING_PORT=5985
REMOTING_SSL_PORT=5986
MAX_CONCURRENT_USERS=10
MAX_SHELLS_PER_USER=25

# Proxy Settings
PROXY_ENABLED=false
PROXY_SERVER=proxy.domain.com
PROXY_PORT=8080
PROXY_BYPASS_LOCAL=true

# Network Timeouts (seconds)
DEFAULT_TIMEOUT=300
REMOTE_TIMEOUT=600
DATABASE_TIMEOUT=30
WEB_TIMEOUT=120

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
# Log Levels: Debug, Info, Warning, Error, Critical
DEFAULT_LOG_LEVEL=Info
CONSOLE_LOG_LEVEL=Info
FILE_LOG_LEVEL=Debug
EVENT_LOG_LEVEL=Warning

# Log Paths
LOG_BASE_PATH=C:\Automation\Logs
TRANSCRIPT_PATH=C:\Automation\Logs\Transcripts
ARCHIVE_LOG_PATH=C:\Automation\Logs\Archive

# Log Retention
MAX_LOG_SIZE_MB=100
MAX_LOG_FILES=30
LOG_RETENTION_DAYS=90

# Remote Logging
REMOTE_LOG_ENABLED=true
REMOTE_LOG_SERVER=log-server.domain.com
REMOTE_LOG_PORT=514
REMOTE_LOG_PROTOCOL=UDP

# Event Log Configuration
EVENT_LOG_SOURCE=AutomationSuite
EVENT_LOG_NAME=Application

# =============================================================================
# DEPLOYMENT CONFIGURATION
# =============================================================================
# Deployment Paths
SOURCE_PATH=\\deployment\source
STAGING_PATH=C:\Automation\Staging
BACKUP_PATH=C:\Automation\Backups
CONFIG_PATH=C:\Automation\Config
MODULES_PATH=C:\Automation\Modules

# Deployment Settings
BACKUP_RETENTION_DAYS=30
REQUIRED_FREE_DISK_SPACE_GB=5
ENABLE_AUTO_ROLLBACK=false
MAX_ROLLBACK_ATTEMPTS=3
ROLLBACK_TIMEOUT=600

# Validation Settings
VALIDATE_CHECKSUMS=true
VALIDATE_SIGNATURES=true
VALIDATE_DEPENDENCIES=true
VALIDATE_TARGET_SPACE=true

# =============================================================================
# MONITORING AND ALERTING
# =============================================================================
# Health Check Settings
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=300
HEALTH_CHECK_TIMEOUT=60
HEALTH_FAILURE_THRESHOLD=3
HEALTH_SUCCESS_THRESHOLD=2

# Performance Thresholds
CPU_ALERT_THRESHOLD=80
MEMORY_ALERT_THRESHOLD=85
DISK_SPACE_ALERT_THRESHOLD=90
NETWORK_ALERT_THRESHOLD=75

# Service Monitoring
CRITICAL_SERVICES=Spooler,BITS,WinRM,W32Time,EventLog
MONITOR_INTERVAL=180
RESTART_FAILED_SERVICES=true
MAX_RESTART_ATTEMPTS=3

# =============================================================================
# NOTIFICATION CONFIGURATION
# =============================================================================
# Email Settings
EMAIL_ENABLED=true
SMTP_SERVER=smtp.domain.com
SMTP_PORT=587
SMTP_USE_SSL=true
EMAIL_FROM=automation@domain.com

# Notification Recipients
CRITICAL_EMAIL_RECIPIENTS=ops-critical@domain.com,manager@domain.com
WARNING_EMAIL_RECIPIENTS=ops-team@domain.com
INFO_EMAIL_RECIPIENTS=ops-reports@domain.com

# Slack Integration
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#automation-alerts
SLACK_USERNAME=AutomationBot

# Microsoft Teams Integration
TEAMS_ENABLED=true
TEAMS_WEBHOOK_URL=https://company.webhook.office.com/webhookb2/YOUR-WEBHOOK-URL

# Custom Webhook
WEBHOOK_ENABLED=false
WEBHOOK_URL=https://api.company.com/automation/webhook
WEBHOOK_TOKEN=YOUR-WEBHOOK-TOKEN
WEBHOOK_TIMEOUT=30

# =============================================================================
# APPLICATION-SPECIFIC SETTINGS
# =============================================================================
# IIS Configuration
IIS_DEFAULT_APP_POOL=AutomationAppPool
IIS_DEFAULT_SITE=AutomationSite
IIS_CONFIG_BACKUP_PATH=C:\Automation\Backups\IIS
IIS_LOG_PATH=C:\inetpub\logs\LogFiles
IIS_MEMORY_LIMIT_KB=2097152
IIS_PRIVATE_MEMORY_LIMIT_KB=1048576

# SQL Server Configuration
SQL_DEFAULT_INSTANCE=MSSQLSERVER
SQL_BACKUP_PATH=C:\Automation\Backups\SQL
SQL_MAINTENANCE_PLAN=AutomationMaintenance
SQL_PAGE_SIZE=1000
SQL_SERVER_TIMEOUT=120

# Active Directory Configuration
AD_DOMAIN=domain.com
AD_SEARCH_BASE=DC=domain,DC=com
AD_PREFERRED_DCS=dc01.domain.com,dc02.domain.com
AD_PAGE_SIZE=1000

# Exchange Configuration
EXCHANGE_MANAGEMENT_SHELL=C:\Program Files\Microsoft\Exchange Server\V15\bin\RemoteExchange.ps1
EXCHANGE_SERVER_FQDN=exchange.domain.com
EXCHANGE_BACKUP_PATH=C:\Automation\Backups\Exchange
EXCHANGE_LOG_TRUNCATION=true

# =============================================================================
# PERFORMANCE AND SCALING
# =============================================================================
# Parallel Processing
MAX_PARALLEL_JOBS=8
PARALLEL_PROCESSING_ENABLED=true
THROTTLE_LIMIT=32

# Batch Processing
BATCH_SIZE=100
BATCH_TIMEOUT=300
MAX_BATCH_RETRIES=3

# Connection Pooling
MIN_POOL_SIZE=5
MAX_POOL_SIZE=100
CONNECTION_LIFETIME=300
CONNECTION_RESET=true

# Cache Settings
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE_MB=512

# =============================================================================
# FEATURE FLAGS
# =============================================================================
# Core Features
ENABLE_ASYNC_PROCESSING=true
ENABLE_PARALLEL_EXECUTION=true
ENABLE_DISTRIBUTED_LOGGING=true
ENABLE_PERFORMANCE_COUNTERS=true

# Advanced Features
ENABLE_ADVANCED_MONITORING=false
ENABLE_MACHINE_LEARNING_ANALYSIS=false
ENABLE_BLOCKCHAIN_LOGGING=false

# Integration Features
ENABLE_SLACK_INTEGRATION=false
ENABLE_TEAMS_INTEGRATION=true
ENABLE_JIRA_INTEGRATION=false
ENABLE_SERVICENOW_INTEGRATION=false

# Security Features
ENABLE_ADVANCED_AUDITING=true
ENABLE_REALTIME_MONITORING=true
ENABLE_THREAT_DETECTION=false
ENABLE_AUTOMATIC_REMEDIATION=false

# =============================================================================
# SCHEDULED TASKS CONFIGURATION
# =============================================================================
# Primary Automation Task
PRIMARY_TASK_NAME=AutomationSuite-Primary
PRIMARY_TASK_SCHEDULE=Daily
PRIMARY_TASK_START_TIME=02:00
PRIMARY_TASK_USER=DOMAIN\svc-automation-primary
PRIMARY_TASK_PRIORITY=High
PRIMARY_TASK_EXECUTION_LIMIT=PT2H

# Secondary Automation Task
SECONDARY_TASK_NAME=AutomationSuite-Secondary
SECONDARY_TASK_SCHEDULE=OnEvent
SECONDARY_TASK_USER=DOMAIN\svc-automation-secondary
SECONDARY_TASK_PRIORITY=Normal
SECONDARY_TASK_EXECUTION_LIMIT=PT1H

# Maintenance Tasks
LOG_CLEANUP_TASK_NAME=AutomationSuite-LogCleanup
LOG_CLEANUP_SCHEDULE=Weekly
LOG_CLEANUP_START_TIME=01:00
LOG_CLEANUP_DAY=Sunday
LOG_CLEANUP_RETENTION_DAYS=30

HEALTH_CHECK_TASK_NAME=AutomationSuite-HealthCheck
HEALTH_CHECK_SCHEDULE=Hourly
HEALTH_CHECK_INTERVAL=1

# =============================================================================
# DISASTER RECOVERY AND BACKUP
# =============================================================================
# Backup Configuration
BACKUP_ENABLED=true
BACKUP_COMPRESSION=true
BACKUP_ENCRYPTION=true
BACKUP_VERIFICATION=true

# Backup Schedules
CONFIG_BACKUP_SCHEDULE=Daily
CONFIG_BACKUP_TIME=01:00
CONFIG_BACKUP_RETENTION_DAYS=30

DATABASE_BACKUP_SCHEDULE=Daily
DATABASE_BACKUP_TIME=23:00
DATABASE_BACKUP_RETENTION_DAYS=14

LOG_BACKUP_SCHEDULE=Weekly
LOG_BACKUP_TIME=03:00
LOG_BACKUP_RETENTION_DAYS=90

# Recovery Settings
ENABLE_AUTO_RECOVERY=true
RECOVERY_TIMEOUT=1800
MAX_RECOVERY_ATTEMPTS=3
RECOVERY_NOTIFICATION=true

# =============================================================================
# DEVELOPMENT AND TESTING
# =============================================================================
# Development Mode Settings
DEV_MODE_ENABLED=false
DEBUG_MODE=false
VERBOSE_LOGGING=false
SKIP_VALIDATION=false

# Testing Configuration
TEST_MODE=false
TEST_DATA_PATH=C:\Automation\TestData
MOCK_EXTERNAL_SERVICES=false
TEST_TIMEOUT=600

# Code Quality
ENABLE_PESTER_TESTS=true
PESTER_OUTPUT_PATH=C:\Automation\TestResults
CODE_COVERAGE_THRESHOLD=80

# =============================================================================
# AZURE/CLOUD INTEGRATION (if applicable)
# =============================================================================
# Azure Configuration
AZURE_ENABLED=false
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=automation-rg
AZURE_KEY_VAULT=automation-kv

# AWS Configuration (if multi-cloud)
AWS_ENABLED=false
AWS_REGION=us-west-2
AWS_PROFILE=automation
AWS_S3_BUCKET=automation-backups

# =============================================================================
# LEGACY SYSTEM INTEGRATION
# =============================================================================
# Mainframe Integration
MAINFRAME_ENABLED=false
MAINFRAME_HOST=mainframe.domain.com
MAINFRAME_PORT=23
MAINFRAME_TIMEOUT=60

# Legacy Database
LEGACY_DB_ENABLED=false
LEGACY_DB_SERVER=legacy-db.domain.com
LEGACY_DB_TYPE=Oracle
LEGACY_DB_PORT=1521

# =============================================================================
# COMPLIANCE AND GOVERNANCE
# =============================================================================
# Compliance Settings
COMPLIANCE_LOGGING=true
PCI_COMPLIANCE=false
HIPAA_COMPLIANCE=false
SOX_COMPLIANCE=true
GDPR_COMPLIANCE=true

# Data Retention Policies
AUDIT_LOG_RETENTION_YEARS=7
TRANSACTION_LOG_RETENTION_MONTHS=12
DEBUG_LOG_RETENTION_DAYS=30
PERFORMANCE_LOG_RETENTION_DAYS=90

# Data Classification
DATA_CLASSIFICATION_ENABLED=true
DEFAULT_DATA_CLASSIFICATION=Internal
SENSITIVE_DATA_ENCRYPTION=true
PII_MASKING=true
