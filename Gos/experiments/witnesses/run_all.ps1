# =============================================================================
#  run_all.ps1 -- seven witnesses, one integer, compared by string equality
# =============================================================================
#  chi(T) = 20T - 30T + (10T + 2) = 2, for every T.
#
#  Every witness prints ONE canonical line:
#     <name>|0:2|1:2|2:2|3:2|21:2|147:2|1029:2|7203:2|50421:2|1000000:2
#  so the comparison is `-eq` on a string, not judgement.
#
#  Run:  powershell -ExecutionPolicy Bypass -File run_all.ps1
# =============================================================================

$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $here

$receipts = @{}
function Add-Receipt($line) {
    if ($line -and $line -match '^([a-z-]+)\|(.+)$') {
        $receipts[$Matches[1]] = $Matches[2]
        "  {0,-20} {1}" -f $Matches[1], $Matches[2]
    }
}

Write-Host "== RUNNING THE WITNESSES ==" -ForegroundColor Cyan

# --- 1,2,3: raw machine code / inline asm / safe rust ------------------------
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
if (Get-Command cargo -EA SilentlyContinue) {
    cargo +stable-x86_64-pc-windows-gnu run --quiet -p gos_experiments --manifest-path ..\..\Cargo.toml -- --canon 2>$null |
        ForEach-Object { Add-Receipt $_ }
} else { Write-Host "  cargo not found -- skipping the 3 Rust witnesses" -ForegroundColor Yellow }

# --- 4: Python ---------------------------------------------------------------
if (Get-Command py -EA SilentlyContinue) { Add-Receipt (py -3 chi.py) }
else { Write-Host "  py not found" -ForegroundColor Yellow }

# --- 5: JavaScript (node) ----------------------------------------------------
if (Get-Command node -EA SilentlyContinue) { Add-Receipt (node chi.js) }
else { Write-Host "  node not found" -ForegroundColor Yellow }

# --- 6: C#, compiled with the compiler that ships with Windows ---------------
$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (Test-Path $csc) {
    & $csc -nologo -optimize+ -out:chi_cs.exe chi.cs | Out-Null
    if (Test-Path .\chi_cs.exe) { Add-Receipt (& .\chi_cs.exe) }
} else { Write-Host "  csc.exe not found -- skipping C#" -ForegroundColor Yellow }

# --- 7: the browser ----------------------------------------------------------
Write-Host "`n  witness 7 (browser) is manual:" -ForegroundColor DarkGray
Write-Host "     start chi.html   then paste its receipt line here to compare." -ForegroundColor DarkGray

# --- THE COMPARISON ----------------------------------------------------------
Write-Host "`n== THE VERDICT ==" -ForegroundColor Cyan
# @(...) is not decoration. Without it a single unique receipt collapses to a
# bare [string], and $vals[0] then indexes the first CHARACTER -- "0" -- so a
# passing run reports as a failure. Same family as the case-insensitive
# Select-String that once reported "FAILED" from inside the text "0 failed".
$vals = @($receipts.Values | Sort-Object -Unique)
Write-Host ("  witnesses run     : {0}" -f $receipts.Count)
Write-Host ("  distinct receipts : {0}" -f $vals.Count)

$expected = (@(0,1,2,3,21,147,1029,7203,50421,1000000) | ForEach-Object { "$($_):2" }) -join "|"

if ($vals.Count -eq 1 -and $vals[0] -eq $expected) {
    Write-Host "  ALL WITNESSES AGREE, and agree with chi = 2 everywhere." -ForegroundColor Green
    Write-Host "`n  20 - 30 + 10 = 0.  the T terms cancel.  what is left is 2."
    Pop-Location; exit 0
} elseif ($vals.Count -eq 1) {
    Write-Host "  witnesses agree with EACH OTHER but not with chi=2." -ForegroundColor Red
    Write-Host "  got      : $($vals[0])"
    Write-Host "  expected : $expected"
    Pop-Location; exit 1
} else {
    Write-Host "  *** THE WITNESSES SPLIT -- this is the interesting case ***" -ForegroundColor Red
    foreach ($k in $receipts.Keys) { "    {0,-20} {1}" -f $k, $receipts[$k] }
    Pop-Location; exit 1
}
