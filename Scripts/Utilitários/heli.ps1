# Script para mais facilmente abrir spyder em seu enviroment python pelo terminal

$profilePath = $PROFILE
$scriptContent = 'function Start-Spyder {
    Write-Host "Inicializando env python e Spyder"


    # Path do projeto (Muda conforme Necessário)
    $folderPath = "C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts\"
    Set-Location -Path $folderPath
    
    # Path do venv
    $venvActivateScript = "$folderPath\.venv\Scripts\Activate.ps1" 

    # Check de existência do venv e rodar
    if (Test-Path -Path $venvActivateScript) {
        . $venvActivateScript
        Write-Host "Venv ativado"
    } else {
        Write-Host "Venv não encontrado em $venvActivateScript"
        return
    }

    # Checar se spyder está instalado
    $spyderPath = "$folderPath\.venv\Scripts\spyder.exe"
    if (Test-Path -Path $spyderPath) {

        Start-Process $spyderPath
        Write-Host "Abrindo Spyder... (Pode demorar alguns minutos) "

    } else {
        Write-Host "Spyder não foi encontrado"
    }

}'

# Criar Profile se não existir
if (-Not (Test-Path $profilePath)) {
    Write-Host "Criando Profile em $profilePath"
    New-Item -Path $profilePath -ItemType File -Force
}

# Ler conteudo do Profile
$profileContent = Get-Content $profilePath -Encoding UTF8 | Out-String

# Comparar arquivo para ver se função Start-Spyder existe no Profile já
if ($profileContent -notcontains $scriptContent) {
    Add-Content -Path $profilePath -Value "`n$scriptContent" -Encoding UTF8
    Write-Host "Função Start-Spyder adicionada ao Perfil do PowerShell"
} else {
    Write-Host "Função Start-Spyder já está presente no Perfil do PowerShell"
}
