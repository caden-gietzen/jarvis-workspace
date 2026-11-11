# Close the running Jarvis (python + its hosting PowerShell window) after a delay. No new Jarvis is started.
# Reads the window identity Jarvis saved at startup. Logs to <jarvis repo>\logs\end_session.log.
param([int]$Delay = 60)
$jarvisDir = if ($env:JARVIS_REPO) { $env:JARVIS_REPO } else { Join-Path (Split-Path $PSScriptRoot) 'jarvis' }
$log = Join-Path $jarvisDir 'logs\end_session.log'
function Log($m) { Add-Content -Path $log -Value ("{0} [end] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) -Encoding UTF8 }
Add-Type -Namespace Win -Name Native -MemberDefinition @'
[DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
[DllImport("kernel32.dll")] public static extern bool TerminateProcess(IntPtr h, uint code);
[DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
'@
function Stop-Clean([int]$p) {
    $h = [Win.Native]::OpenProcess(0x0001, $false, $p)
    if ($h -eq [IntPtr]::Zero) { Log "  OpenProcess($p) failed (gone or denied)"; return }
    $ok = [Win.Native]::TerminateProcess($h, 0); [Win.Native]::CloseHandle($h) | Out-Null
    Log "  terminated pid $p exit=0 ok=$ok"
}
try {
    Log "scheduled; waiting $Delay s"
    Start-Sleep -Seconds $Delay
    $info = Get-Content (Join-Path $jarvisDir '.jarvis_window.json') -Raw | ConvertFrom-Json
    $jp = [int]$info.pid; $sp = [int]$info.shell_pid
    $all = @(Get-CimInstance Win32_Process)
    if (-not ($all | Where-Object ProcessId -eq $jp)) { Log "Jarvis pid $jp not running; nothing to close"; exit 0 }
    $q = New-Object System.Collections.Queue; $q.Enqueue($(if ($sp) { $sp } else { $jp }))
    $victims = New-Object System.Collections.ArrayList
    while ($q.Count) { $c = $q.Dequeue(); [void]$victims.Add($c); foreach ($k in ($all | Where-Object { $_.ParentProcessId -eq $c -and $_.ProcessId -ne $PID })) { $q.Enqueue([int]$k.ProcessId) } }
    $ordered = @($victims | Where-Object { $_ -ne $PID }); [array]::Reverse($ordered)
    Log "Jarvis pid=$jp shell=$sp; closing: $($ordered -join ',')"
    foreach ($v in $ordered) { Stop-Clean $v }
    Log "done"
} catch { Log "ERROR: $($_ | Out-String)" ; exit 2 }
