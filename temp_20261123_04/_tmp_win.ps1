Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WU {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
}
"@
$h = [IntPtr]197728
$r = New-Object WU+RECT
[WU]::GetWindowRect($h, [ref]$r) | Out-Null
Write-Output ("rect=" + $r.Left + "," + $r.Top + "," + $r.Right + "," + $r.Bottom)
Write-Output ("visible=" + [WU]::IsWindowVisible($h) + " iconic=" + [WU]::IsIconic($h))

if ($args[0] -eq "move") {
  [WU]::ShowWindow($h, 9) | Out-Null   # SW_RESTORE
  [WU]::SetWindowPos($h, [IntPtr]::Zero, 20, 20, 1000, 780, 0x0040) | Out-Null
  [WU]::SetForegroundWindow($h) | Out-Null
  Start-Sleep -Milliseconds 600
  $r2 = New-Object WU+RECT
  [WU]::GetWindowRect($h, [ref]$r2) | Out-Null
  Write-Output ("after=" + $r2.Left + "," + $r2.Top + "," + $r2.Right + "," + $r2.Bottom)
}
