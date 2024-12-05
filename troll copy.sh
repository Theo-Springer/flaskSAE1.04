#!/bin/bash

# Check if an IP address is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <IP_ADDRESS>"
    exit 1
fi

# Specific IP address
ip="$1"

# SSH credentials
username="user"
password="disket"

# Commands to execute on remote machine
remote_commands='
firefox --new-window "https://www.youtube.com/watch?v=U_Wr7TKBnq8&autoplay=1" --kiosk --new-tab "javascript:document.querySelector(\"video\").requestFullscreen();" &
xrandr --output HDMI-2 --rotate inverted;
sleep 15;
xrandr --output HDMI-2 --rotate normal;
'

# Attempt SSH connection
mate-terminal -- bash -c "
    echo 'Attempting connection to $ip...';
    sshpass -p '$password' ssh -t -o StrictHostKeyChecking=no -o ConnectTimeout=5 $username@$ip '
        export DISPLAY=:0;
        $remote_commands
        exec bash
    ' || echo 'Connection failed to $ip';
    read -p 'Press Enter to close this window...'"