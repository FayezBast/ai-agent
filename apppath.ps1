param([string]$AppName)

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

function Get-AllApps {
    $apps = @()


    $startMenuPaths = @(
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
    )

    foreach ($path in $startMenuPaths) {
        if (Test-Path $path) {
            Get-ChildItem -Path $path -Recurse -Include *.lnk | ForEach-Object {
                $shell = New-Object -ComObject WScript.Shell
                $shortcut = $shell.CreateShortcut($_.FullName)
                if ($shortcut.TargetPath -and (Test-Path $shortcut.TargetPath)) {
                    [PSCustomObject]@{
                        Name = $_.BaseName
                        Path = $shortcut.TargetPath
                    }
                }
            }
        }
    }

    $env:Path.Split(";") | Where-Object { $_ -and $_.Trim() -ne "" } | ForEach-Object {
        if (Test-Path $_) {
            Get-ChildItem -Path $_ -Filter *.exe -ErrorAction SilentlyContinue | ForEach-Object {
                [PSCustomObject]@{
                    Name = $_.BaseName
                    Path = $_.FullName
                }
            }
        }
    }

    return $apps
}

if (-not $AppName) {
    # List all apps as JSON
    Get-AllApps | ConvertTo-Json -Compress
    exit 0
}

# Lookup specific app
$apps = Get-AllApps
$found = $apps | Where-Object { $_.Name -like "*$AppName*" }

if ($found) {
    
    $found[0].Path
    exit 0
} else {
    Write-Output "NOT_FOUND"
    exit 1
}
