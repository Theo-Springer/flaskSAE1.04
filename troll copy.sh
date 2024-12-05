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
# Open Rick Roll in Firefox
firefox --new-window "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --kiosk &

# Screen rotation sequence
xrandr --output HDMI-2 --rotate inverted;
sleep 5;
xrandr --output HDMI-2 --rotate left;
sleep 5;
xrandr --output HDMI-2 --rotate right;
sleep 5;
xrandr --output HDMI-2 --rotate normal;

# Change mouse speed temporarily
xinput --set-prop "pointer:USB Optical Mouse" "libinput Accel Speed" -0.8;
sleep 20;
xinput --set-prop "pointer:USB Optical Mouse" "libinput Accel Speed" 0;

# Play sound effects
paplay /usr/share/sounds/freedesktop/stereo/complete.oga &

# Open random harmless websites in new tabs
firefox --new-tab "https://beesbeesbees.com" &
firefox --new-tab "https://cat-bounce.com" &

# Change wallpaper temporarily (requires imagemagick)
wget https://i.imgur.com/URLHERE.jpg -O /tmp/temp.jpg;
gsettings set org.mate.background picture-filename /tmp/temp.jpg;
sleep 30;
gsettings reset org.mate.background picture-filename;

# Randomly change terminal prompt color
echo "PS1='\[\e[38;5;$((RANDOM%256))m\]\u@\h:\w\$ \[\e[0m\]'" >> ~/.bashrc;
source ~/.bashrc;

# Randomly change desktop background color
gsettings set org.gnome.desktop.background primary-color "#$(openssl rand -hex 3)";

# Randomly open a terminal with a fun message
mate-terminal -- bash -c "echo 'Hello from the other side!'; exec bash" &

# Randomly play a sound from a list
sounds=(/usr/share/sounds/freedesktop/stereo/*.oga);
paplay "${sounds[RANDOM % ${#sounds[@]}]}" &

# Randomly open a new tab with a fun fact
firefox --new-tab "https://www.thefactsite.com/1000-interesting-facts/" &
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