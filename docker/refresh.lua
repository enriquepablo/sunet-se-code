function executeShellCommand(command)
    local handle = io.popen(command, "r") -- Open the command for reading
    handle:read("*a") -- Read the entire output of the command
    local output = {handle:close()} -- Close the handle, automatically waits for the command to exit
    return output -- Return the captured output
end

local command = "update_site.sh"
local exit_status = executeShellCommand(command)

if exit_status[3] == 0 then
    -- Success
    ngx.say("Ok")
else
    -- Failure
    ngx.say("Error: Something went wrong.")
end
