$sig = @'
using System;
using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
}
'@
Add-Type -TypeDefinition $sig

$h = [W]::GetForegroundWindow()
$fgpid = 0
[void][W]::GetWindowThreadProcessId($h, [ref]$fgpid)
$sb = New-Object System.Text.StringBuilder 256
[void][W]::GetWindowTextW($h, $sb, 256)
$r = New-Object W+RECT
[void][W]::GetWindowRect($h, [ref]$r)
$p = Get-Process -Id $fgpid -ErrorAction SilentlyContinue
Write-Output ("fgHwnd=" + $h + " pid=" + $fgpid + " exe=" + $p.ProcessName + " title=" + $sb.ToString() + " rect=" + $r.L + "," + $r.T + "," + $r.R + "," + $r.B)

$target = [IntPtr]197728
$tr = New-Object W+RECT
[void][W]::GetWindowRect($target, [ref]$tr)
Write-Output ("chrome hwnd=197728 rect=" + $tr.L + "," + $tr.T + "," + $tr.R + "," + $tr.B + " visible=" + [W]::IsWindowVisible($target) + " iconic=" + [W]::IsIconic($target))
