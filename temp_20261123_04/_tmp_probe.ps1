Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class W3 {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr SendMessageTimeoutW(IntPtr h, uint msg, IntPtr w, IntPtr l, uint flags, uint timeout, out IntPtr res);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
}
"@
[W3]::SetProcessDPIAware() | Out-Null
$fg = [W3]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 512
[W3]::GetWindowTextW($fg, $sb, 512) | Out-Null
$pid = 0
[W3]::GetWindowThreadProcessId($fg, [ref]$pid) | Out-Null
Write-Output ("fg=" + $fg + " title='" + $sb.ToString() + "' pid=" + $pid + " visible=" + [W3]::IsWindowVisible($fg))

$h = [IntPtr]197728
$res = [IntPtr]::Zero
$r = [W3]::SendMessageTimeoutW($h, 0, [IntPtr]::Zero, [IntPtr]::Zero, 0x0002, 1500, [ref]$res)
Write-Output ("probe197728 ret=" + $r + " res=" + $res + " (0 => hung)")
