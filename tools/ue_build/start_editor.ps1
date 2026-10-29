# Start the UE 5.8 editor on TheKeepr_Demo (no restore dialog) and wait until the MCP server answers.
$proj = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'TheKeepr_Demo'
# an editor that is still shutting down (e.g. after -ExecutePythonScript) must be gone first
for ($i = 0; $i -lt 30 -and (Get-Process UnrealEditor -ErrorAction SilentlyContinue) -and -not (Get-Process UnrealEditor | Where-Object MainWindowTitle -like '*Unreal Editor*'); $i++) { Start-Sleep 1 }
if (-not (Get-Process UnrealEditor -ErrorAction SilentlyContinue)) {
    Get-ChildItem -LiteralPath "$proj\Saved\Autosaves" -Recurse -File -ErrorAction SilentlyContinue | Remove-Item -Force
    Start-Process 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList "`"$proj\TheKeepr_Demo.uproject`""
}
for ($i = 0; $i -lt 300; $i++) {
    try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/mcp' -Method Post -Body '{}' -ContentType 'application/json' -TimeoutSec 2 -ErrorAction Stop | Out-Null; break }
    catch { if ($_.Exception.Response) { break }; Start-Sleep 2 }
}
Start-Sleep 10
'editor ready'
