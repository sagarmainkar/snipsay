-- Whisper Hotkey - Hammerspoon Configuration
--
-- Global hotkey to toggle voice recording.
-- Transcribed text is automatically copied to clipboard.
--
-- CUSTOMIZATION:
-- Edit ~/whisper-hotkey/config.lua to change hotkey and settings.
--

local SOCKET_PATH = "/tmp/whisper_hotkey.sock"

-- Load configuration
local config = dofile(os.getenv("HOME") .. "/whisper-hotkey/config.lua")

local isRecording = false

-- Menu bar indicator
local menubar = hs.menubar.new()
menubar:setTitle("🎙")
menubar:setTooltip("Whisper Hotkey — idle")

local function updateMenubar(recording)
    if recording then
        menubar:setTitle("🔴")
        menubar:setTooltip("Whisper Hotkey — RECORDING")
    else
        menubar:setTitle("🎙")
        menubar:setTooltip("Whisper Hotkey — idle")
    end
end

local function sendCommand(cmd)
    local output, status, _, rc = hs.execute(
        string.format("echo '%s' | nc -U '%s' -w 2", cmd, SOCKET_PATH)
    )
    return output, rc
end

local function toggle()
    local output, rc = sendCommand("toggle")
    if not output then
        hs.alert.show("Whisper Hotkey: backend not running!\nStart with: ./start.sh")
        return
    end

    output = output:gsub("%s+", "")

    if output == "recording_started" then
        isRecording = true
        updateMenubar(true)
        hs.alert.show("🎙 Recording...", 1.5)
        
    elseif output == "recording_stopped" then
        isRecording = false
        updateMenubar(false)
        hs.alert.show("⏳ Transcribing...", 2)
        
    else
        hs.alert.show("Whisper Hotkey: unexpected response")
    end
end

-- ===========================================
-- HOTKEY (from config.lua)
-- ===========================================
hs.hotkey.bind(config.hotkey_modifiers, config.hotkey_key, toggle)

-- Right-click menu
local hotkeyLabel = table.concat(config.hotkey_modifiers, "+") .. "+" .. config.hotkey_key
menubar:setMenu({
    { title = "Toggle Recording (" .. hotkeyLabel .. ")", fn = toggle },
    { title = "-" },
    { title = "Reload Config", fn = hs.reload },
    { title = "Quit Backend", fn = function() sendCommand("quit") end },
})

print("Whisper Hotkey loaded — " .. hotkeyLabel .. " to toggle")
