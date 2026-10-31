# Prepara este computador para rodar o bot. Pode rodar de novo sem problema.
# Uso: abra o PowerShell na pasta do projeto e rode:  .\scripts\instalar.ps1
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python nao encontrado. Instale em python.org (marque 'Add Python to PATH') e rode de novo."
}

Write-Host "1/4 Criando o ambiente do Python (.venv)..."
if (-not (Test-Path ".venv")) { python -m venv .venv }

Write-Host "2/4 Instalando as pecas que o bot usa..."
& ".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
& ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt

Write-Host "3/4 Conferindo arquivos..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "   Criei o .env vazio. Copie para ele as suas chaves (guardadas em lugar seguro)."
}
if (-not (Test-Path "dados\produtos.csv")) {
    Copy-Item "dados\produtos.exemplo.csv" "dados\produtos.csv"
    Write-Host "   Criei dados\produtos.csv de exemplo. Troque pelos seus produtos."
}

Write-Host "4/4 Testando as conexoes (nao posta nada)..."
& ".venv\Scripts\python.exe" -m src.main --testar-conexao
Write-Host "Pronto. Proximo passo: .\scripts\agendar.ps1 (so depois de testar em simulacao)."
