# Manda as skills da pasta skills\ do bot para o repositório privado "Skills-para-o-Claude-".
# Uso (na pasta do bot):  .\scripts\sincronizar_skills.ps1
# Skill nova entra na pasta da sua função; nada é apagado no repositório.
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$origem = Join-Path $raiz "skills"
$destino = Join-Path (Split-Path -Parent $raiz) "skills-claude"
if (-not (Test-Path (Join-Path $destino ".git"))) {
    git clone https://github.com/kawzsilva7-star/Skills-para-o-Claude- $destino
}
# /E copia subpastas; sem /MIR de propósito, para nunca apagar nada no destino.
robocopy $origem $destino /E /XD ".git" "node_modules" "__pycache__" "videos" /XF "*.pyc" /NFL /NDL /NJH /NJS | Out-Null
Set-Location $destino
git add -A
if (git status --porcelain) {
    git commit -m "Atualiza skills"
    git push origin main
    Write-Host "Skills enviadas para o GitHub."
} else {
    Write-Host "Nada novo para enviar."
}
