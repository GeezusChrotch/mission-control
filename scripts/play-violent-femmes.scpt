tell application "Music"
    play (first track whose artist contains "Violent Femmes")
    delay 2
    
    set deviceList to {}
    
    tell application "Music"
        try
            set end of deviceList to AirPlay device "Kitchen Speaker"
        end try
    end tell
    
    tell application "Music"
        try
            set end of deviceList to AirPlay device "Bathroom Speaker"
        end try
    end tell
    
    tell application "Music"
        try
            set end of deviceList to AirPlay device "Bedroom Speaker"
        end try
    end tell
    
    tell application "Music"
        try
            set end of deviceList to AirPlay device "Maeby's Speaker"
        end try
    end tell
    
    tell application "Music"
        if deviceList is not {} then
            set current AirPlay devices to deviceList
        end if
    end tell
end tell