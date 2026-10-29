# Switch the ACE LLM model and restart the UE 5.8 editor without the Restore Packages dialog.
# Usage: powershell -File switch_model.ps1 <gguf file name in TheKeepr_Demo/Plugins>
param([Parameter(Mandatory)][string]$Model)

$proj = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'TheKeepr_Demo'
if (-not (Test-Path -LiteralPath "$proj\Plugins\$Model")) { throw "Model not found: $Model" }

$ini = "$proj\Config\DefaultGame.ini"
$text = [IO.File]::ReadAllText($ini)
$text = [regex]::Replace($text, 'ModelFile=\(FilePath="[^"]*"\)', "ModelFile=(FilePath=`"../Plugins/$Model`")")
[IO.File]::WriteAllText($ini, $text, (New-Object Text.UTF8Encoding $false))
Select-String -LiteralPath $ini -Pattern 'ModelFile' | ForEach-Object Line

Get-Process UnrealEditor -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 3
Get-ChildItem -LiteralPath "$proj\Saved\Autosaves" -Recurse -File -ErrorAction SilentlyContinue | Remove-Item -Force

Start-Process 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList "`"$proj\TheKeepr_Demo.uproject`""
Start-Sleep 20
for ($i = 0; $i -lt 150; $i++) {
    try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/mcp' -Method Post -Body '{}' -ContentType 'application/json' -TimeoutSec 2 -ErrorAction Stop | Out-Null; break }
    catch { if ($_.Exception.Response) { break } ; Start-Sleep 2 }
}
Start-Sleep 15
'editor ready'
