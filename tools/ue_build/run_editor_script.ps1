# Restart the UE 5.8 editor on TheKeepr_Demo, run an editor Python script at startup, wait for its log to say DONE.
# Usage: powershell -File run_editor_script.ps1 -Script <path.py> -Log <path.log> [-TimeoutSec 900]
param([Parameter(Mandatory)][string]$Script, [Parameter(Mandatory)][string]$Log, [int]$TimeoutSec = 900)

$proj = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'TheKeepr_Demo'
Get-Process UnrealEditor -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 3
Get-ChildItem -LiteralPath "$proj\Saved\Autosaves" -Recurse -File -ErrorAction SilentlyContinue | Remove-Item -Force
if (Test-Path -LiteralPath $Log) { Remove-Item -LiteralPath $Log -Force }

Start-Process 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList "`"$proj\TheKeepr_Demo.uproject`"", "-ExecutePythonScript=`"$Script`""
$deadline = (Get-Date).AddSeconds($TimeoutSec)
while ((Get-Date) -lt $deadline) {
    if ((Test-Path -LiteralPath $Log) -and (Select-String -LiteralPath $Log -Pattern '^DONE' -Quiet)) { Get-Content -LiteralPath $Log -Encoding utf8; exit 0 }
    if (-not (Get-Process UnrealEditor -ErrorAction SilentlyContinue)) { 'EDITOR EXITED'; if (Test-Path -LiteralPath $Log) { Get-Content -LiteralPath $Log -Encoding utf8 }; exit 1 }
    Start-Sleep 2
}
'TIMEOUT'; if (Test-Path -LiteralPath $Log) { Get-Content -LiteralPath $Log -Encoding utf8 }
exit 1
