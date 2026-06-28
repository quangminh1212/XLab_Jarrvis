# Jarrvis MCP notification hook (Windows)
# Reads hook JSON from stdin and shows a Windows toast notification + permission prompt

param()

$input_data = $Input | Out-String
if (-not $input_data) {
    $input_data = [Console]::In.ReadToEnd()
}

try {
    $json = $input_data | ConvertFrom-Json
    $tool_name = $json.tool_name
    $event = $json.hook_event_name
} catch {
    exit 0
}

function Show-Toast {
    param([string]$Title, [string]$Message)
    try {
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(3000, $Title, $Message, [System.Windows.Forms.ToolTipIcon]::None)
        Start-Sleep -Milliseconds 200
        $notify.Dispose()
    } catch {
        # Silently ignore if toast fails (no UI session, etc.)
    }
}

switch ($event) {
    "PreToolUse" {
        switch ($tool_name) {
            "mcp__jarrvis__voice_listen" {
                Show-Toast -Title "Jarrvis - Dang nghe..." -Message "Hay noi chuyen di!"
                # Require explicit permission before accessing microphone
                @{
                    hookSpecificOutput = @{
                        hookEventName        = "PreToolUse"
                        permissionDecision   = "ask"
                        permissionDecisionReason = "Jarrvis muon truy cap microphone de nghe ban noi"
                    }
                } | ConvertTo-Json -Compress
            }
            "mcp__jarrvis__voice_speak" {
                $text = ""
                try { $text = $json.tool_input.text.Substring(0, [Math]::Min(80, $json.tool_input.text.Length)) } catch {}
                Show-Toast -Title "Jarrvis - Dang noi..." -Message $text
            }
            "mcp__jarrvis__voice_ask" {
                $q = ""
                try { $q = $json.tool_input.question.Substring(0, [Math]::Min(80, $json.tool_input.question.Length)) } catch {}
                Show-Toast -Title "Jarrvis - Dang hoi..." -Message $q
                @{
                    hookSpecificOutput = @{
                        hookEventName        = "PreToolUse"
                        permissionDecision   = "ask"
                        permissionDecisionReason = "Jarrvis muon dat cau hoi va nghe cau tra loi cua ban"
                    }
                } | ConvertTo-Json -Compress
            }
        }
    }
    "PostToolUse" {
        switch ($tool_name) {
            "mcp__jarrvis__voice_listen" {
                $heard = ""
                try { $heard = $json.tool_response.content[0].text.Substring(0, [Math]::Min(80, $json.tool_response.content[0].text.Length)) } catch {}
                Show-Toast -Title "Jarrvis - Da nghe duoc!" -Message $heard
            }
        }
    }
}

exit 0
