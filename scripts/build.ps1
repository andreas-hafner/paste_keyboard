param(
    [string]$Python = "python",
    [string]$SpecFile = "PasteKeyboard.spec",
    [string]$OutputFile = "dist\PasteKeyboard.exe",
    [string]$Thumbprint = "",
    [string]$TimestampUrl = "http://timestamp.digicert.com",
    [string]$SignTool = "",
    [switch]$SkipSigning,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function Assert-UnderRepo {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $fullPath.StartsWith($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify path outside repository: $fullPath"
    }
}

function Remove-RepoPath {
    param([string]$Path)

    $fullPath = Resolve-RepoPath $Path
    Assert-UnderRepo $fullPath
    if (Test-Path -LiteralPath $fullPath) {
        Remove-Item -LiteralPath $fullPath -Recurse -Force
    }
}

function Find-SignTool {
    if ($SignTool) {
        $resolved = Resolve-RepoPath $SignTool
        if (Test-Path -LiteralPath $resolved) {
            return $resolved
        }
        return $SignTool
    }

    $command = Get-Command signtool.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $kitRoot = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
    if (Test-Path -LiteralPath $kitRoot) {
        $candidate = Get-ChildItem -LiteralPath $kitRoot -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match "\\x64\\signtool\.exe$" } |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($candidate) {
            return $candidate.FullName
        }
    }

    throw "signtool.exe was not found. Install Windows SDK or pass -SignTool <path>."
}

function Invoke-PyInstaller {
    param(
        [string]$WorkPath,
        [string]$DistPath
    )

    & $Python -m PyInstaller --noconfirm --clean --workpath $WorkPath --distpath $DistPath $SpecPath
}

function Invoke-PyInstallerResourceFallback {
    param(
        [string]$WorkPath,
        [string]$DistPath
    )

    $env:PASTE_KEYBOARD_SPEC = $SpecPath
    $env:PASTE_KEYBOARD_WORKPATH = $WorkPath
    $env:PASTE_KEYBOARD_DISTPATH = $DistPath

    $pythonCode = @'
import os
import sys

import PyInstaller.__main__
from PyInstaller.utils.win32 import icon, versioninfo, winmanifest, winresource, winutils

winresource.remove_all_resources = lambda filename: None
icon.CopyIcons = lambda dstpath, srcpath: None
versioninfo.write_version_info_to_executable = lambda filename, versioninfo: None
winmanifest.write_manifest_to_executable = lambda filename, manifest: None
winutils.set_exe_build_timestamp = lambda filename, timestamp: None
winutils.update_exe_pe_checksum = lambda filename: None

sys.argv = [
    "pyinstaller",
    "--noconfirm",
    "--clean",
    "--workpath",
    os.environ["PASTE_KEYBOARD_WORKPATH"],
    "--distpath",
    os.environ["PASTE_KEYBOARD_DISTPATH"],
    os.environ["PASTE_KEYBOARD_SPEC"],
]
PyInstaller.__main__.run()
'@

    $pythonCode | & $Python -
}

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$SpecPath = Resolve-RepoPath $SpecFile
$OutputPath = Resolve-RepoPath $OutputFile
$OutputDir = Split-Path -Parent $OutputPath
$BuildWorkPath = Resolve-RepoPath "build\script-work"
$BuildDistPath = Resolve-RepoPath "build\script-dist"
$BuiltExe = Join-Path $BuildDistPath "PasteKeyboard.exe"
$EffectiveThumbprint = $Thumbprint
if (-not $EffectiveThumbprint) {
    $EffectiveThumbprint = $env:CODESIGN_THUMBPRINT
}

Assert-UnderRepo $BuildWorkPath
Assert-UnderRepo $BuildDistPath
Assert-UnderRepo $OutputPath

if (-not (Test-Path -LiteralPath $SpecPath)) {
    throw "Spec file not found: $SpecPath"
}

if (-not $SkipTests) {
    Write-Host "Running unit tests..."
    & $Python -m unittest discover -s tests -v
}

Write-Host "Preparing build directories..."
Remove-RepoPath $BuildWorkPath
Remove-RepoPath $BuildDistPath

Write-Host "Building EXE with PyInstaller..."
$normalBuildFailed = $false
try {
    Invoke-PyInstaller -WorkPath $BuildWorkPath -DistPath $BuildDistPath
} catch {
    $normalBuildFailed = $true
    Write-Warning "Normal PyInstaller build failed: $($_.Exception.Message)"
}

if ($normalBuildFailed -or -not (Test-Path -LiteralPath $BuiltExe)) {
    Write-Host "Retrying build with Windows resource-update fallback..."
    Remove-RepoPath $BuildWorkPath
    Remove-RepoPath $BuildDistPath
    Invoke-PyInstallerResourceFallback -WorkPath $BuildWorkPath -DistPath $BuildDistPath
}

if (-not (Test-Path -LiteralPath $BuiltExe)) {
    throw "Build did not produce expected EXE: $BuiltExe"
}

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
Copy-Item -LiteralPath $BuiltExe -Destination $OutputPath -Force
Write-Host "Built: $OutputPath"

if (-not $SkipSigning -and $EffectiveThumbprint) {
    $signtoolPath = Find-SignTool
    Write-Host "Signing with certificate thumbprint $EffectiveThumbprint..."
    & $signtoolPath sign /sha1 $EffectiveThumbprint /fd SHA256 /tr $TimestampUrl /td SHA256 $OutputPath
    Write-Host "Verifying signature..."
    & $signtoolPath verify /pa /v $OutputPath
} elseif (-not $SkipSigning) {
    Write-Host "Skipping signing because no thumbprint was provided. Pass -Thumbprint or set CODESIGN_THUMBPRINT."
}

Write-Host "Build finished successfully."
