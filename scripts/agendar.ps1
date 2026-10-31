# Cria as 3 tarefas diarias no Agendador de Tarefas do Windows.
# Uso:  .\scripts\agendar.ps1            (horarios padrao 08:00, 14:00 e 20:00)
#       .\scripts\agendar.ps1 -Horarios "09:00","15:00","21:00"
#       .\scripts\agendar.ps1 -Remover   (apaga as tarefas)
param(
    [string[]]$Horarios = @("08:00", "14:00", "20:00"),
    [switch]$Remover
)
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$python = Join-Path $raiz ".venv\Scripts\python.exe"
$prefixo = "BotRedeSociais"

if ($Remover) {
    Get-ScheduledTask -TaskName "$prefixo-*" -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
    Write-Host "Tarefas removidas."
    return
}
if (-not (Test-Path $python)) { throw "Rode primeiro .\scripts\instalar.ps1" }

foreach ($hora in $Horarios) {
    $nome = "$prefixo-" + ($hora -replace ":", "h")
    $acao = New-ScheduledTaskAction -Execute $python -Argument "-m src.main" -WorkingDirectory $raiz
    $gatilho = New-ScheduledTaskTrigger -Daily -At $hora
    # Se o PC estava desligado na hora, roda assim que ligar; nao empilha execucoes.
    $config = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 20)
    Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gatilho -Settings $config -Force | Out-Null
    Write-Host "Criada: $nome as $hora"
}
Write-Host "Pronto. O PC precisa estar ligado e sem suspensao nesses horarios."
Write-Host "O modo (simulacao ou real) vem do DRY_RUN no .env."
