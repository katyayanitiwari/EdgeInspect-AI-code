[CmdletBinding()]
param(
    [string]$ModelId = 'meta-llama/Llama-3.2-1B-Instruct',
    [string]$Destination = ''
)
$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if ([string]::IsNullOrWhiteSpace($Destination)) {
    $Destination = Join-Path $projectRoot 'LOCAL_ONLY_DO_NOT_UPLOAD\Llama_3_2_1B'
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$hf = Get-Command hf -ErrorAction SilentlyContinue
if (-not $hf) {
    throw 'Hugging Face CLI (hf) not found. Install huggingface_hub and run hf auth login first.'
}
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$needed = @('original\consolidated.00.pth','original\params.json','original\tokenizer.model')
$missing = @($needed | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Destination $_)) })
if ($missing.Count -eq 0) {
    Write-Host "Authorized model files already exist under: $Destination"
    Write-Host 'No model download was needed.'
    exit 0
}
Write-Host "Downloading the authorized Llama checkpoint files to the local-only folder: $Destination"
Write-Host 'Hugging Face approval and login are required. This script does not print or store your token in the project.'
& $hf.Source download $ModelId `
    original/consolidated.00.pth original/params.json original/tokenizer.model `
    --local-dir $Destination
if ($LASTEXITCODE -ne 0) {
    throw 'Download failed. Check Hugging Face approval/login. Do not paste access tokens into chat or commit them.'
}
$missing = @($needed | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Destination $_)) })
if ($missing.Count -gt 0) {
    throw "Download finished but files are missing: $($missing -join ', ')"
}
Write-Host 'All required source files are present. They remain local and excluded from the submission ZIP.'
Write-Host 'Follow deployment/executorch/README.md to configure the exporter and runner.'
