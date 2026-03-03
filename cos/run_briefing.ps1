$hour = (Get-Date).Hour
$basePath = "c:\Users\pietr\OneDrive\.vscode\JARVIS"

if ($hour -lt 11) {
    python "$basePath\cos\briefings\morning_brief.py" --save
} elseif ($hour -lt 17) {
    python "$basePath\cos\briefings\midday_check.py"
} else {
    python "$basePath\cos\briefings\eod_audit.py" --save
}
