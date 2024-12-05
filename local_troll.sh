#!/bin/bash

# Create temp directory for our cleanup script
mkdir -p /tmp/troll_cleanup

# Backup original files
cp ~/.bashrc ~/.bashrc.bak 2>/dev/null
cp /etc/motd /tmp/troll_cleanup/motd.bak 2>/dev/null

# Try X11 commands first
export DISPLAY=:0
if xrandr &>/dev/null; then
    echo "X11 available, running GUI commands..."
    
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

    # Open random harmless websites in new tabs
    firefox --new-tab "https://beesbeesbees.com" &
    firefox --new-tab "https://cat-bounce.com" &

    # Change wallpaper temporarily
    wget https://i.imgur.com/URLHERE.jpg -O /tmp/temp.jpg;
    gsettings set org.mate.background picture-filename /tmp/temp.jpg;
    sleep 30;
    gsettings reset org.mate.background picture-filename;

    # Change desktop background color
    gsettings set org.gnome.desktop.background primary-color "#$(openssl rand -hex 3)";
fi

# Non-X11 commands
echo "Running non-GUI commands..."

# Unmute system sound
amixer set Master unmute &>/dev/null
amixer set Speaker unmute &>/dev/null
amixer set Headphone unmute &>/dev/null

# Play sound effects
paplay /usr/share/sounds/freedesktop/stereo/complete.oga &

# Randomly change terminal prompt color
echo "PS1='\[\e[38;5;$((RANDOM%256))m\]\u@\h:\w\$ \[\e[0m\]'" >> ~/.bashrc;
source ~/.bashrc;

# Randomly play sounds from a list
sounds=(/usr/share/sounds/freedesktop/stereo/*.oga);
paplay "${sounds[RANDOM % ${#sounds[@]}]}" &

# Create random files in /tmp
for i in {1..5}; do
    echo "¯\_(ツ)_/¯" > "/tmp/surprise_$i.txt";
done

# Add temporary aliases
echo "alias ls=\"echo \'¯\_(ツ)_/¯ where did the files go?\' && ls\"" >> ~/.bashrc;
echo "alias cd=\"echo \'Walking to directory...\' && cd\"" >> ~/.bashrc;

# Add fun to the motd
echo "You have been visited by the friendly network ghost 👻" | sudo tee -a /etc/motd &>/dev/null;

# Create a small script that randomly changes terminal colors
echo "printf \"\033[3\$((RANDOM % 8))m\"" > ~/.random_color.sh;
echo "source ~/.random_color.sh" >> ~/.bashrc;

# Add a cowsay fortune if available
if command -v fortune &>/dev/null && command -v cowsay &>/dev/null; then
    fortune | cowsay >> ~/.bashrc;
fi

# Reverse text input
stty iuclc;

# Create cleanup script
echo "#!/bin/bash
# Wait 20 seconds
sleep 20

# Restore bashrc
mv ~/.bashrc.bak ~/.bashrc 2>/dev/null

# Restore motd
if [ -f /tmp/troll_cleanup/motd.bak ]; then
    sudo mv /tmp/troll_cleanup/motd.bak /etc/motd 2>/dev/null
fi

# Remove temporary files
rm -f /tmp/surprise_*.txt
rm -f ~/.random_color.sh
rm -rf /tmp/troll_cleanup

# Reset terminal settings
stty -iuclc

# Reset terminal colors
printf \"\033[0m\"

# Kill any remaining sound processes
pkill -f paplay

# Cleanup complete notification
paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
" > /tmp/troll_cleanup/cleanup.sh

# Make cleanup script executable and run it in background
chmod +x /tmp/troll_cleanup/cleanup.sh
nohup /tmp/troll_cleanup/cleanup.sh &>/dev/null &

echo "Troll script running! Everything will reset in 20 seconds..." 