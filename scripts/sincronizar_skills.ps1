# Manda as skills da pasta skills\ do bot para o repositório privado "Skills-para-o-Claude-".
# Uso (na pasta do bot):  .\scripts\sincronizar_skills.ps1
# Skill nova entra na pasta da sua função; nada é apagado no repositório.
# "Continue": o Git escreve avisos normais (ex.: LF/CRLF) que o PowerShell 5.1 trataria como erro.
$ErrorActionPreference = "Continue"
$raiz = Split-Path -Parent $PSScriptRoot
$origem = Join-Path $raiz "skills"
$destino = Join-Path (Split-Path -Parent $raiz) "skills-claude"
if (-not (Test-Path (Join-Path $destino ".git"))) {
    git clone https://github.com/kawzsilva7-star/Skills-para-o-Claude- $destino
}
# /E copia subpastas; sem /MIR de propósito, para nunca apagar nada no destino.
robocopy $origem $destino /E /XD ".git" "node_modules" "__pycache__" "videos" /XF "*.pyc" /NFL /NDL /NJH /NJS | Out-Null
Set-Location $destino
git -c core.safecrlf=false add -A 2>$null
if (git status --porcelain) {
    git commit -q -m "Atualiza skills"
    git push -q origin main
    if ($LASTEXITCODE -eq 0) { Write-Host "Skills enviadas para o GitHub." }
    else { Write-Host "Falhou ao enviar. Confira a internet e o login do Git." }
} else {
    Write-Host "Nada novo para enviar."
}
