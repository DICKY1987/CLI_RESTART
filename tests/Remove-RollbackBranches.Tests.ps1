<#
Pester tests for Remove-RollbackBranches.ps1
These tests create isolated temporary git repositories and never touch real repos.
#>

param()

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path (Split-Path -Parent $here) 'Remove-RollbackBranches.ps1'

Describe 'Remove-RollbackBranches - Local branch cleanup' -Tag 'Local' {
    $testRoot = Join-Path $env:TEMP ("rrb-tests-" + ([Guid]::NewGuid().ToString('N')))
    $repo = Join-Path $testRoot 'repo-local'

    BeforeAll {
        New-Item -Path $repo -ItemType Directory -Force | Out-Null
        Push-Location $repo
        git init | Out-Null
        Set-Content -Path .gitignore -Value "# test" -NoNewline
        git add . | Out-Null
        git -c user.email=test@example.com -c user.name=test commit -m "init" | Out-Null

        # Create rollback branches
        git branch rollback/a | Out-Null
        git branch rollback/b | Out-Null
        git branch rollback/safe-c | Out-Null
        Pop-Location
    }

    AfterAll {
        if (Test-Path $testRoot) { Remove-Item -Path $testRoot -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'Deletes matching local rollback branches and preserves excluded ones' {
        $result = & $scriptPath -RepositoryPath $repo -LocalOnly -Force -Exclude 'rollback/safe-*' -PassThru -Verify
        $result | Should -Not -BeNullOrEmpty
        $result.DeletedLocal | Should -Contain 'rollback/a'
        $result.DeletedLocal | Should -Contain 'rollback/b'
        $result.DeletedLocal | Should -Not -Contain 'rollback/safe-c'

        # Ensure branches are gone
        Push-Location $repo
        $remaining = (git for-each-ref --format=%(refname:short) refs/heads/rollback/*)
        Pop-Location
        $remaining | Should -BeNullOrEmpty
    }

    It 'BatchLocal succeeds and falls back gracefully if needed' {
        # Recreate branches
        Push-Location $repo
        git branch rollback/a | Out-Null
        git branch rollback/b | Out-Null
        Pop-Location

        $result = & $scriptPath -RepositoryPath $repo -LocalOnly -Force -BatchLocal -PassThru -Verify
        $result.DeletedLocal | Should -Contain 'rollback/a'
        $result.DeletedLocal | Should -Contain 'rollback/b'
    }
}

Describe 'Remove-RollbackBranches - Remote branch cleanup' -Tag 'Remote' {
    $testRoot = Join-Path $env:TEMP ("rrb-tests-" + ([Guid]::NewGuid().ToString('N')))
    $repo = Join-Path $testRoot 'repo-remote'
    $bare = Join-Path $testRoot 'remote.git'

    BeforeAll {
        New-Item -Path $repo -ItemType Directory -Force | Out-Null
        New-Item -Path $bare -ItemType Directory -Force | Out-Null

        Push-Location $bare
        git init --bare | Out-Null
        Pop-Location

        Push-Location $repo
        git init | Out-Null
        Set-Content -Path README.md -Value "test" -NoNewline
        git add . | Out-Null
        git -c user.email=test@example.com -c user.name=test commit -m "init" | Out-Null
        git remote add origin $bare | Out-Null

        # Create remote rollback branches
        git branch rollback/x | Out-Null
        git branch rollback/y | Out-Null
        git push -u origin rollback/x | Out-Null
        git push -u origin rollback/y | Out-Null
        Pop-Location
    }

    AfterAll {
        if (Test-Path $testRoot) { Remove-Item -Path $testRoot -Recurse -Force -ErrorAction SilentlyContinue }
    }

    It 'Deletes remote rollback branches (batched) and verifies removal' {
        $result = & $scriptPath -RepositoryPath $repo -RemoteOnly -RemoteName origin -PassThru -Verify
        $result | Should -Not -BeNullOrEmpty
        @('rollback/x','rollback/y') | ForEach-Object { $_ | Should -BeIn $result.DeletedRemote }

        # Verify remote has no rollback/* heads
        Push-Location $repo
        git fetch origin --prune | Out-Null
        $remaining = (git for-each-ref --format=%(refname:short) refs/remotes/origin/rollback/*)
        Pop-Location
        $remaining | Should -BeNullOrEmpty
    }
}

