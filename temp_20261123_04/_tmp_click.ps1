param([int]$PX = 0, [int]$PY = 0, [switch]$Click)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W2 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
}
"@

[W2]::SetProcessDPIAware() | Out-Null
$h = [IntPtr]197728
$r = New-Object W2+RECT
[W2]::GetWindowRect($h, [ref]$r) | Out-Null
Write-Output ("physRect=" + $r.Left + "," + $r.Top + "," + $r.Right + "," + $r.Bottom + " size=" + ($r.Right - $r.Left) + "x" + ($r.Bottom - $r.Top))

if ($Click) {
  [W2]::ShowWindow($h, 9) | Out-Null
  [W2]::BringWindowToTop($h) | Out-Null
  [W2]::SetForegroundWindow($h) | Out-Null
  Start-Sleep -Milliseconds 500
  $fg = [W2]::GetForegroundWindow()
  Write-Output ("fg=" + $fg + " target=" + $h)
  if ($fg -ne $h) { Write-Output "ABORT: target not foreground"; exit 2 }
  [W2]::SetCursorPos($PX, $PY) | Out-Null
  Start-Sleep -Milliseconds 150
  [W2]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)   # left down
  Start-Sleep -Milliseconds 80
  [W2]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)   # left up
  Write-Output ("clicked at " + $PX + "," + $PY)
}
