$psScript = "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\heartbeat\jarvis_pulse.py"
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument $psScript
$trigger = New-ScheduledTaskTrigger -At (Get-Date) -Once -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Remove tarefas antigas se existirem
Unregister-ScheduledTask -TaskName "COS Morning Brief" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "COS Midday Check" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "COS EOD Audit" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "JARVIS Heartbeat" -Confirm:$false -ErrorAction SilentlyContinue

# Registra a nova tarefa de Heartbeat
Register-ScheduledTask -TaskName "JARVIS Heartbeat" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force

Write-Host "💓 Heartbeat do JARVIS configurado para cada 1 hora!"
Write-Host "🚀 Antigas tarefas desativadas."
Start-Sleep -Seconds 3
