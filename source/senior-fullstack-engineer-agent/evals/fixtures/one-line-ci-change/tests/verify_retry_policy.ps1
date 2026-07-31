$ErrorActionPreference = "Stop"

$source = Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\retry_policy.py") -Raw
if ($source -notmatch "MAX_ATTEMPTS\s*=\s*3") {
    throw "Expected MAX_ATTEMPTS to equal 3 in the current revision."
}
if ($source -notmatch "0\s*<=\s*attempt\s*<\s*MAX_ATTEMPTS") {
    throw "Expected the current revision to preserve the retry boundary."
}

Write-Output "PASS: current revision retry policy checks (2/2)"
