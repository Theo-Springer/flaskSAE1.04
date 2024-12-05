#!/bin/bash

# Output file for responding IPs
output_file="ip-ping-response.txt"

# Clear output file if it exists
> "$output_file"

# Scan IP range 172.20.20.1 to 172.20.20.254
for i in {1..254}; do
    ip="172.20.20.$i"
    ping -c 1 -W 0.1 "$ip" &> /dev/null
    if [ $? -eq 0 ]; then
        echo "IP responding: $ip"
        echo "$ip" >> "$output_file"
    fi
done

echo "Responding IPs have been saved to '$output_file'."

# SSH credentials
username="user"
password="disket"

# Check if IP file exists
if [ ! -f "$output_file" ]; then
    echo "File '$output_file' doesn't exist. Please run the ping script first."
    exit 1
fi

# Commands to execute on remote machine
remote_commands='
firefox --new-window "https://www.youtube.com/watch?v=U_Wr7TKBnq8&autoplay=1" --kiosk --new-tab "javascript:document.querySelector(\"video\").requestFullscreen();" &
xrandr --output HDMI-2 --rotate inverted;
sleep 15;
xrandr --output HDMI-2 --rotate normal;
'

# Read each IP from file
while IFS= read -r ip; do
    mate-terminal -- bash -c "
        echo 'Attempting connection to $ip...';
        sshpass -p '$password' ssh -t -o StrictHostKeyChecking=no -o ConnectTimeout=5 $username@$ip '
            export DISPLAY=:0;
            $remote_commands
            exec bash
        ' || echo 'Connection failed to $ip';
        read -p 'Press Enter to close this window...'"
done < "$output_file"

echo "All SSH connections have been launched."