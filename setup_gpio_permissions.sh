#!/bin/bash
# Setup GPIO permissions for Orange Pi 5

echo "Setting up GPIO permissions for current user..."

# Add user to gpio group
sudo usermod -a -G gpio $USER

# Create udev rule for GPIO access
sudo tee /etc/udev/rules.d/99-gpio.rules > /dev/null << 'EOF'
# Orange Pi GPIO permissions
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", MODE="0660", GROUP="gpio"
SUBSYSTEM=="gpio", ACTION=="add", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio'"
SUBSYSTEM=="gpio", ACTION=="add", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/devices/platform/gpio && chmod -R 770 /sys/devices/platform/gpio'"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "GPIO permissions configured!"
echo ""
echo "IMPORTANT: You must log out and log back in for changes to take effect."
echo "Or run: newgrp gpio"
echo ""
echo "After logging back in, you can run the script without sudo:"
echo "  python3 ultrasonic_capture.py"
