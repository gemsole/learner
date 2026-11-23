param([int]$PX = 0, [int]$PY = 0, [switch]$Click)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W4 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@

[W4]::SetProcessDPIAware() | Out-Null
$h = [IntPtr]197728

$fg = [W4]::GetForegroundWindow()
$fgPid = 0
$fgThread = [W4]::GetWindowThreadProcessId($fg, [ref]$fgPid)
Write-Output ("curFg=" + $fg + " fgPid=" + $fgPid + " fgThread=" + $fgThread)

$myThread = [W4]::GetCurrentThreadId()
[W4]::AttachThreadInput($myThread, $fgThread, $true) | Out-Null
[W4]::ShowWindow($h, 9) | Out-Null
[W4]::BringWindowToTop($h) | Out-Null
[W4]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 300
[W4]::SetForegroundWindow($h) | Out-Null
[W4]::AttachThreadInput($myThread, $fgThread, $false) | Out-Null
Start-Sleep -Milliseconds 400

$now = [W4]::GetForegroundWindow()
Write-Output ("nowFg=" + $now + " target=" + $h + " ok=" + ($now -eq $h))

if ($Click) {
  if ($now -ne $h) { Write-Output "ABORT_NOT_FOREGROUND"; exit 2 }
  [W4]::SetCursorPos($PX, $PY) | Out-Null
  Start-Sleep -Milliseconds 200
  [W4]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 80
  [W4]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
  Write-Output ("clicked " + $PX + "," + $PY)
}
