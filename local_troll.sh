#!/bin/bash

# Backup current wallpaper
current_wallpaper=$(gsettings get org.mate.background picture-filename)
echo "$current_wallpaper" > /tmp/current_wallpaper.txt

# Try X11 commands first
export DISPLAY=:0
if xrandr &>/dev/null; then
    echo "X11 available, running GUI commands..."
    
    # Open Rick Roll in Firefox
    firefox --new-window "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --kiosk &

    # Open cat background website
    firefox --new-tab "https://cat-bounce.com" &
fi

# Non-X11 commands
echo "Running non-GUI commands..."

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

# Restore original wallpaper
if [ -f /tmp/current_wallpaper.txt ]; then
    original_wallpaper=\$(cat /tmp/current_wallpaper.txt)
    gsettings set org.mate.background picture-filename \"\$original_wallpaper\"
fi

# Cleanup complete notification
paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
" > /tmp/cleanup.sh

# Make cleanup script executable and run it in background
chmod +x /tmp/cleanup.sh
nohup /tmp/cleanup.sh &>/dev/null &

echo "Troll script running! Everything will reset in 20 seconds..." 