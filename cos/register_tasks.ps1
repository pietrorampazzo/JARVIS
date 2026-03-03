$psScript = "c:\Users\pietr\OneDrive\.vscode\JARVIS\cos\run_briefing.ps1"
$action = New-ScheduledTaskAction -Execute "powershell" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$psScript`""
Register-ScheduledTask -TaskName "COS Morning Brief" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "08:00") -RunLevel Highest -Force
Register-ScheduledTask -TaskName "COS Midday Check" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "13:00") -RunLevel Highest -Force
Register-ScheduledTask -TaskName "COS EOD Audit" -Action $action -Trigger (New-ScheduledTaskTrigger -Daily -At "19:00") -RunLevel Highest -Force
Write-Host "Tarefas configuradas com sucesso! Fechando em 3 segundos..."
Start-Sleep -Seconds 3
