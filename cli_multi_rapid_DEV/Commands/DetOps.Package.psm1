# DetOps.Package.psm1
# Minimal, consistent wrappers that unify package operations across providers.
# Requires: PowerShell 7+ recommended, PackageManagement module available.

# region Helpers
function Write-DPX {
    param([string]$Message)
    Write-Verbose "[DetOps.Package] $Message"
}

function Invoke-Checked {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][scriptblock]$Script,
        [string]$Action = "Invoke"
    )
    try {
        & $Script
    } catch {
        $msg = "Failed to $Action: $($_.Exception.Message)"
        Write-Error $msg
        throw
    }
}
# endregion

# region Package (apps)
function Search-Pkg {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name,
        [string]$Source
    )
    $sb = {
        if ($using:Source) {
            Find-Package -Name $using:Name -Source $using:Source -ErrorAction Stop
        } else {
            Find-Package -Name $using:Name -ErrorAction Stop
        }
    }
    Invoke-Checked -Script $sb -Action "search package"
}

function Install-Pkg {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name,
        [string]$Version,
        [string]$Source,
        [string]$ProviderName,
        [switch]$Force
    )
    if ($PSCmdlet.ShouldProcess($Name, "Install-Package")) {
        $sb = {
            $params = @{
                Name = $using:Name
                ErrorAction = 'Stop'
            }
            if ($using:Version) { $params['RequiredVersion'] = $using:Version }
            if ($using:Source) { $params['Source'] = $using:Source }
            if ($using:ProviderName) { $params['ProviderName'] = $using:ProviderName }
            if ($using:Force) { $params['Force'] = $true }
            Install-Package @params
        }
        Invoke-Checked -Script $sb -Action "install package"
    }
}

function Upgrade-Pkg {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string]$Name
    )
    if ($PSCmdlet.ShouldProcess($Name ?? "<all>", "Update-Package")) {
        $sb = {
            if ($using:Name) {
                Update-Package -Name $using:Name -ErrorAction Stop
            } else {
                Update-Package -ErrorAction Stop
            }
        }
        Invoke-Checked -Script $sb -Action "upgrade package(s)"
    }
}

function Uninstall-Pkg {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name
    )
    if ($PSCmdlet.ShouldProcess($Name, "Uninstall-Package")) {
        $sb = { Uninstall-Package -Name $using:Name -Force -ErrorAction Stop }
        Invoke-Checked -Script $sb -Action "uninstall package"
    }
}

function List-Pkg {
    [CmdletBinding()]
    param(
        [string]$ProviderName
    )
    $sb = {
        if ($using:ProviderName) {
            Get-Package -ProviderName $using:ProviderName -ErrorAction Stop
        } else {
            Get-Package -ErrorAction Stop
        }
    }
    Invoke-Checked -Script $sb -Action "list packages"
}

function Save-Pkg {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Path
    )
    if ($PSCmdlet.ShouldProcess($Name, "Save-Package -> $Path")) {
        $sb = { Save-Package -Name $using:Name -Path $using:Path -ErrorAction Stop }
        Invoke-Checked -Script $sb -Action "download package"
    }
}

# endregion

# region Sources
function Get-PkgSource {
    [CmdletBinding()]
    param()
    Invoke-Checked -Script { Get-PackageSource -ErrorAction Stop } -Action "list sources"
}

function Add-PkgSource {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Location,
        [string]$ProviderName = "NuGet",
        [switch]$Trusted
    )
    if ($PSCmdlet.ShouldProcess("$Name<$ProviderName>", "Register-PackageSource")) {
        $sb = {
            Register-PackageSource -Name $using:Name -Location $using:Location -ProviderName $using:ProviderName `
                -Trusted:$using:Trusted -ErrorAction Stop
        }
        Invoke-Checked -Script $sb -Action "add package source"
    }
}

function Set-PkgSourceTrusted {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name,
        [switch]$Trusted = $true
    )
    if ($PSCmdlet.ShouldProcess($Name, "Set-PackageSource (Trusted=$Trusted)")) {
        $sb = {
            Set-PackageSource -Name $using:Name -Trusted:$using:Trusted -ErrorAction Stop
        }
        Invoke-Checked -Script $sb -Action "set package source"
    }
}

function Remove-PkgSource {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name
    )
    if ($PSCmdlet.ShouldProcess($Name, "Unregister-PackageSource")) {
        $sb = { Unregister-PackageSource -Name $using:Name -ErrorAction Stop }
        Invoke-Checked -Script $sb -Action "remove package source"
    }
}
# endregion

# region Modules
function Search-PSModule {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Name)
    Invoke-Checked -Script { Find-Module -Name $using:Name -ErrorAction Stop } -Action "search module"
}

function Install-PSModule {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Name,
        [ValidateSet('CurrentUser','AllUsers')] [string]$Scope = 'CurrentUser',
        [switch]$Force, [switch]$AcceptLicense
    )
    if ($PSCmdlet.ShouldProcess($Name, "Install-Module")) {
        $sb = {
            Install-Module -Name $using:Name -Scope $using:Scope -Force:$using:Force.IsPresent `
                -AcceptLicense:$using:AcceptLicense.IsPresent -ErrorAction Stop
        }
        Invoke-Checked -Script $sb -Action "install module"
    }
}

function Update-PSModule {
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)][string]$Name)
    if ($PSCmdlet.ShouldProcess($Name, "Update-Module")) {
        Invoke-Checked -Script { Update-Module -Name $using:Name -ErrorAction Stop } -Action "update module"
    }
}

function Uninstall-PSModule {
    [CmdletBinding(SupportsShouldProcess)]
    param([Parameter(Mandatory)][string]$Name,[switch]$AllVersions)
    if ($PSCmdlet.ShouldProcess($Name, "Uninstall-Module")) {
        $sb = { Uninstall-Module -Name $using:Name -AllVersions:$using:AllVersions.IsPresent -ErrorAction Stop }
        Invoke-Checked -Script $sb -Action "uninstall module"
    }
}
# endregion

Export-ModuleMember -Function *-Pkg,*-PkgSource,*-PSModule