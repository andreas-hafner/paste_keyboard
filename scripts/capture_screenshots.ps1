Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$screensDir = Join-Path $root 'docs\screenshots'
${appDataRoot} = Join-Path $root 'build\screenshot-appdata'
${appDataDir} = Join-Path $appDataRoot 'PasteKeyboard'
${settingsPath} = Join-Path $appDataDir 'settings.json'
New-Item -ItemType Directory -Force -Path $screensDir | Out-Null
New-Item -ItemType Directory -Force -Path $appDataDir | Out-Null

$python = 'python.exe'
$main = Join-Path $root 'main.py'

Get-Process | Where-Object { $_.MainWindowTitle -eq 'Paste Keyboard' } | Stop-Process -Force -ErrorAction SilentlyContinue

@'
{
  "hotkey": "Ctrl+Shift+F8",
  "layout_id": "de-DE",
  "start_delay_ms": 250,
  "key_delay_ms": 25,
  "skip_unsupported": false
}
'@ | Set-Content -LiteralPath $settingsPath -Encoding UTF8

$originalAppData = $env:APPDATA
$env:APPDATA = $appDataRoot
$proc = Start-Process -FilePath $python -ArgumentList "`"$main`"" -PassThru

try {
    Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class Win32Capture {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

    $process = $null
    for ($i = 0; $i -lt 40 -and -not $process; $i++) {
        Start-Sleep -Milliseconds 500
        $process = Get-Process | Where-Object { $_.ProcessName -like 'python*' -and $_.MainWindowTitle -eq 'Paste Keyboard' } | Select-Object -First 1
    }

    if (-not $process) {
        throw 'Paste Keyboard-Fenster wurde nicht gefunden.'
    }

    [void][Win32Capture]::SetForegroundWindow($process.MainWindowHandle)
    Start-Sleep -Milliseconds 700

    $rect = New-Object Win32Capture+RECT
    [void][Win32Capture]::GetWindowRect($process.MainWindowHandle, [ref]$rect)

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
    $bitmap.Save((Join-Path $screensDir '01-main-window.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()

    Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class UserInput {
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
}
"@

    $x = $rect.Left + 220
    $y = $rect.Top + 455
    [void][UserInput]::SetCursorPos($x, $y)
    [UserInput]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [UserInput]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("Beispieltext aus der Anleitung")
    Start-Sleep -Milliseconds 500

    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
    $bitmap.Save((Join-Path $screensDir '02-text-loaded.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
}
finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
    }
    $env:APPDATA = $originalAppData
}
