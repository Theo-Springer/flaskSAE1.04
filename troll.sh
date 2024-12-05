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

# Split commands into X11-dependent and independent commands
x11_commands='
# Open Rick Roll in Firefox
firefox --new-window "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --kiosk &

# Open cat background website
firefox --new-tab "https://cat-bounce.com" &
'

non_x11_commands='
# Unmute and maximize system sound
amixer set Master unmute &>/dev/null
amixer set Speaker unmute &>/dev/null
amixer set Headphone unmute &>/dev/null
amixer set Master 100% &>/dev/null
amixer set Speaker 100% &>/dev/null
amixer set Headphone 100% &>/dev/null
pactl set-sink-volume @DEFAULT_SINK@ 100% &>/dev/null

# Create cleanup script
echo "#!/bin/bash
# Wait 20 seconds
sleep 20

# Cleanup complete notification
paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
" > /tmp/cleanup.sh

# Make cleanup script executable and run it in background
chmod +x /tmp/cleanup.sh
nohup /tmp/cleanup.sh &>/dev/null &
'

# Read each IP from file
while IFS= read -r ip; do
    mate-terminal -- bash -c "
        echo 'Attempting connection to $ip...';
        sshpass -p '$password' ssh -X -t -o StrictHostKeyChecking=no -o ConnectTimeout=5 $username@$ip '
            # Try to set up X display with basic check
            if export DISPLAY=:0 && xrandr &>/dev/null; then
                # X11 is working, run all commands
                $x11_commands
                $non_x11_commands
            else
                echo \"X11 not available, running non-X11 commands only...\"
                $non_x11_commands
            fi
            exec bash
        ' || echo 'Connection failed to $ip';
        read -p 'Press Enter to close this window...'"
done < "$output_file"

echo "All SSH connections have been launched."