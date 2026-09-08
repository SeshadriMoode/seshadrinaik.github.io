# Build main.pdf for the JTG double-column article (cas-dc).
#
#   .\build.ps1
#   .\build.ps1 -Clean

param([switch]$Clean)

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

$job = "main"
$aux = @("$job.aux", "$job.bbl", "$job.blg", "$job.log", "$job.out",
         "$job.spl", "$job.fls", "$job.fdb_latexmk", "$job.brf")

if ($Clean) {
    $aux | ForEach-Object { Remove-Item $_ -ErrorAction SilentlyContinue }
    Remove-Item "$job.pdf" -ErrorAction SilentlyContinue
    Remove-Item "pass1.log","pass2.log","pass3.log","bibtex.log" -ErrorAction SilentlyContinue
}

# If Adobe has main.pdf open, pdflatex cannot overwrite it: close the PDF and re-run.
pdflatex -interaction=nonstopmode "$job.tex" *> pass1.log
if (Select-String -Path pass1.log -Pattern "I can't write on file" -Quiet) {
    Write-Host "main.pdf is locked. Close the PDF viewer and re-run .\build.ps1"
    exit 1
}

cmd /c "bibtex main" *> bibtex.log
pdflatex -interaction=nonstopmode "$job.tex" *> pass2.log
pdflatex -interaction=nonstopmode "$job.tex" *> pass3.log

if (-not (Test-Path "$job.pdf")) {
    Write-Error "$job.pdf was not produced. Inspect $job.log."
    exit 1
}

Remove-Item pass1.log, pass2.log, pass3.log, bibtex.log -ErrorAction SilentlyContinue

Write-Host "`n--- Errors ---"
$errors = Select-String -Path "$job.log" -Pattern "^! |Emergency stop|Fatal error"
if ($errors) { $errors | ForEach-Object { $_.Line.Trim() } } else { Write-Host "none" }

Write-Host "`n--- Undefined references and citations ---"
$undef = Select-String -Path "$job.log" -Pattern "LaTeX Warning: (Citation|Reference).*undefined"
if ($undef) { $undef | ForEach-Object { $_.Line.Trim() } } else { Write-Host "none" }

Write-Host "`n--- Result ---"
$m = Select-String -Path "$job.log" -Pattern "Output written on $job\.pdf \((\d+) pages"
if ($m) { Write-Host "$job.pdf, $($m.Matches[0].Groups[1].Value) pages" }
else { Write-Host "$job.pdf written" }
