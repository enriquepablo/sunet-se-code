function executeShellCommand(command)
    local handle = io.popen(command, "r") -- Open the command for reading
    local output = handle:read("*a") -- Read the entire output of the command
    handle:close() -- Close the handle, automatically waits for the command to exit
    return output -- Return the captured output
end

-- Example usage
local command = "echo Hello, World!"
local output = executeShellCommand(command)
ngx.say("Command output:", output)
