# nudge_popup.ps1 — a center-screen, always-on-top, hard-to-ignore nudge from your AI. (Windows)
#
# Why this exists: passive notifications (corner toasts, a tab, a Notepad window) are too easy to
# scroll past on a rough executive-function day. A modal box in the CENTER of the screen, on top of
# everything, with a sound, is genuinely hard to ignore — which is the whole point for the nudges
# that actually matter (meds, food, water, a break, a hard stop).
#
# It also has a gentle BLUFF-CALL: an "I already did it" button that escalates instead of dismissing,
# for the days your person reflexively swats the reminder. And a DAY-OFF switch so they can mute it
# with one word whenever they need to (autonomy first — the nudge serves them, never the reverse).
#
# USAGE (have your scheduled reminders / cron / Task Scheduler call this):
#   powershell -NoProfile -ExecutionPolicy Bypass -File nudge_popup.ps1 -Message "Water break?" -Escalation "No, really. Go drink something."
#
# To fire it from a sandboxed AI session that can't draw a window directly, launch it detached:
#   Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File','<path>\nudge_popup.ps1'
#
# DAY OFF: create a file `nudge_off.txt` next to this script containing today's date (yyyy-MM-dd),
# or the word ALL, and every nudge is silently skipped. Your AI can write/remove it on request
# ("take a day off from nudges" -> write today's date; "nudges back on" -> delete the file).
#
# NOTE on emoji: Windows PowerShell 5.1 reads .ps1 files as ANSI, which mojibakes literal emoji.
# If you want an emoji, build it at runtime from its codepoint, e.g. [char]::ConvertFromUtf32(0x1F419).
# (Heads-up: classic WinForms labels render color emoji as a tofu box anyway, so plain text is safest.)

param(
    [string]$Message    = "Time for a quick break?",
    [string]$Escalation = "No, really. Step away for a second.",
    [string]$Title      = "A nudge:",
    [string]$DoLabel    = "OK, doing it",
    [string]$BluffLabel = "I already did it"
)

# --- Day-off switch ---
$flag = Join-Path $PSScriptRoot "nudge_off.txt"
if (Test-Path $flag) {
    $off = (Get-Content $flag -Raw).Trim()
    if ($off -eq "ALL" -or $off -eq (Get-Date).ToString("yyyy-MM-dd")) { return }
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text            = $Title
$form.StartPosition   = 'CenterScreen'
$form.TopMost         = $true
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox     = $false
$form.MinimizeBox     = $false
$form.BackColor       = [System.Drawing.Color]::FromArgb(13,10,20)
$form.ClientSize      = New-Object System.Drawing.Size(580,300)

$label = New-Object System.Windows.Forms.Label
$label.Text      = $Message
$label.ForeColor = [System.Drawing.Color]::FromArgb(232,228,240)
$label.Font      = New-Object System.Drawing.Font("Segoe UI", 20, [System.Drawing.FontStyle]::Bold)
$label.TextAlign = 'MiddleCenter'
$label.Dock      = 'Fill'
$label.Padding   = New-Object System.Windows.Forms.Padding(24,24,24,8)

$panel = New-Object System.Windows.Forms.Panel
$panel.Dock      = 'Bottom'
$panel.Height    = 70
$panel.BackColor = [System.Drawing.Color]::FromArgb(13,10,20)

$btnDo = New-Object System.Windows.Forms.Button
$btnDo.Text      = $DoLabel
$btnDo.Font      = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$btnDo.ForeColor = [System.Drawing.Color]::FromArgb(13,10,20)
$btnDo.BackColor = [System.Drawing.Color]::FromArgb(100,255,218)
$btnDo.FlatStyle = 'Flat'
$btnDo.FlatAppearance.BorderSize = 0
$btnDo.Size      = New-Object System.Drawing.Size(230,48)
$btnDo.Location  = New-Object System.Drawing.Point(40,12)
$btnDo.Add_Click({ $form.Close() })

$btnBluff = New-Object System.Windows.Forms.Button
$btnBluff.Text      = $BluffLabel
$btnBluff.Font      = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$btnBluff.ForeColor = [System.Drawing.Color]::FromArgb(232,228,240)
$btnBluff.BackColor = [System.Drawing.Color]::FromArgb(40,32,58)
$btnBluff.FlatStyle = 'Flat'
$btnBluff.FlatAppearance.BorderSize = 1
$btnBluff.Size      = New-Object System.Drawing.Size(230,48)
$btnBluff.Location  = New-Object System.Drawing.Point(300,12)
$btnBluff.Add_Click({
    $label.Text      = $Escalation
    $label.ForeColor = [System.Drawing.Color]::FromArgb(255,128,171)
    try { [System.Media.SystemSounds]::Hand.Play() } catch {}
    $btnBluff.Visible = $false
    $btnDo.Location   = New-Object System.Drawing.Point(175,12)
    $form.Activate(); $form.BringToFront()
})

$panel.Controls.Add($btnDo)
$panel.Controls.Add($btnBluff)
$form.Controls.Add($label)
$form.Controls.Add($panel)
$form.AcceptButton = $btnDo

try { [System.Media.SystemSounds]::Exclamation.Play() } catch {}
$form.Add_Shown({ $form.Activate(); $form.BringToFront() })
[void]$form.ShowDialog()
