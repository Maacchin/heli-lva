function Start-Spyder {
    Write-Host "Inicializando env python e Spyder"


    # Path do projeto
    $folderPath = "C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts\"
    Set-Location -Path $folderPath
    
    # Path do venv
    $venvActivateScript = "$folderPath\.venv\Scripts\Activate.ps1" 

    # Check de exist�ncia do venv e rodar
    if (Test-Path -Path $venvActivateScript) {
        . $venvActivateScript
        Write-Host "Venv ativado"
    } else {
        Write-Host "Venv n�o encontrado em $venvActivateScript"
        return
    }

    # Checar se spyder est� instalado
    $spyderPath = "$folderPath\.venv\Scripts\spyder.exe"
    if (Test-Path -Path $spyderPath) {

        # Start the process but continue showing spinner until it's done
        Start-Process $spyderPath -PassThru | Out-Null
        Write-Host "Abrindo Spyder... (Pode demorar alguns minutos) "

    } else {
        Write-Host "Spyder n�o foi encontrado"
    }

}