Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$screensDir = Join-Path $root 'docs\screenshots'
${appDataRoot} = Join-Path $root 'build\screenshot-appdata'
${appDataDir} = Join-Path $appDataRoot 'PasteKeyboard'
${settingsPath} = Join-Path $appDataDir 'settings.json'
$python = 'python.exe'
$screenshotApp = Join-Path $root 'scripts\screenshot_app.py'

New-Item -ItemType Directory -Force -Path $screensDir | Out-Null
New-Item -ItemType Directory -Force -Path $appDataDir | Out-Null

Get-Process | Where-Object { $_.ProcessName -like 'python*' -and $_.MainWindowTitle -like 'Paste Keyboard*' } |
    Stop-Process -Force -ErrorAction SilentlyContinue

$settingsJson = @'
{
  "hotkey": "Ctrl+Shift+F8",
  "layout_id": "de-DE",
  "start_delay_ms": 0,
  "key_delay_ms": 10,
  "skip_unsupported": false,
  "clipboard_typing_limit": 10000,
  "notify_on_finish": true
}
'@
[System.IO.File]::WriteAllText($settingsPath, $settingsJson, [System.Text.UTF8Encoding]::new($false))

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class Win32Capture {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
"@

function Find-AppWindow {
    param([int]$ProcessId)

    $script:targetHwnd = [IntPtr]::Zero
    for ($i = 0; $i -lt 40 -and $script:targetHwnd -eq [IntPtr]::Zero; $i++) {
        Start-Sleep -Milliseconds 500
        [Win32Capture]::EnumWindows({
            param([IntPtr]$hwnd, [IntPtr]$lparam)
            $windowProcessId = 0
            [void][Win32Capture]::GetWindowThreadProcessId($hwnd, [ref]$windowProcessId)
            if ($windowProcessId -ne $script:captureProcessId -or -not [Win32Capture]::IsWindowVisible($hwnd)) {
                return $true
            }

            $candidateRect = New-Object Win32Capture+RECT
            if (-not [Win32Capture]::GetWindowRect($hwnd, [ref]$candidateRect)) {
                return $true
            }

            if (($candidateRect.Right - $candidateRect.Left) -lt 400 -or ($candidateRect.Bottom - $candidateRect.Top) -lt 300) {
                return $true
            }

            $script:targetHwnd = $hwnd
            return $false
        }, [IntPtr]::Zero) | Out-Null
    }

    if ($script:targetHwnd -eq [IntPtr]::Zero) {
        throw 'Paste Keyboard-Fenster wurde nicht gefunden.'
    }
    return $script:targetHwnd
}

function Save-WindowImage {
    param(
        [IntPtr]$Hwnd,
        [string]$Path
    )

    [void][Win32Capture]::SetForegroundWindow($Hwnd)
    Start-Sleep -Milliseconds 700

    $rect = New-Object Win32Capture+RECT
    [void][Win32Capture]::GetWindowRect($Hwnd, [ref]$rect)
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $hdc = $graphics.GetHdc()
        try {
            if (-not [Win32Capture]::PrintWindow($Hwnd, $hdc, 0)) {
                throw 'Fensterinhalt konnte nicht gerendert werden.'
            }
        }
        finally {
            $graphics.ReleaseHdc($hdc)
        }
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

function Capture-App {
    param(
        [string]$OutputName,
        [switch]$WithText
    )

    $arguments = @("`"$screenshotApp`"")
    if ($WithText) {
        $arguments += '--with-text'
    }

    $proc = Start-Process -FilePath $python -ArgumentList $arguments -PassThru
    try {
        $script:captureProcessId = $proc.Id
        $hwnd = Find-AppWindow -ProcessId $proc.Id
        Save-WindowImage -Hwnd $hwnd -Path (Join-Path $screensDir $OutputName)
    }
    finally {
        if ($proc -and -not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force
        }
    }
}

$originalAppData = $env:APPDATA
$env:APPDATA = $appDataRoot
try {
    Capture-App -OutputName '01-main-window.png'
    Capture-App -OutputName '02-text-loaded.png' -WithText
}
finally {
    $env:APPDATA = $originalAppData
}
