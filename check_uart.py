#!/usr/bin/env python3
"""
Check available UART devices on Orange Pi 5
"""
import os
import glob

print("Orange Pi 5 UART Device Check")
print("=" * 60)

# Check for UART devices
uart_patterns = ['/dev/ttyS*', '/dev/ttyAMA*', '/dev/ttyFIQ*']
found_devices = []

for pattern in uart_patterns:
    devices = glob.glob(pattern)
    found_devices.extend(devices)

if found_devices:
    print("\n✓ Found UART devices:")
    for dev in sorted(found_devices):
        # Check if readable
        readable = os.access(dev, os.R_OK | os.W_OK)
        print(f"  {dev} {'(accessible)' if readable else '(need sudo)'}")
else:
    print("\n❌ No UART devices found")
    print("\nUARTs may need to be enabled in device tree overlay")

print("\n" + "=" * 60)
print("Orange Pi 5 has these UARTs (from pinout):")
print("  - UART1 (TX_M1, RX_M1)")
print("  - UART3 (TX_M0, RX_M0)")
print("  - UART4 (TX_M0, RX_M0)")
print("  - UART10 (TX_M2, RX_M2)")
print("\nThese may map to /dev/ttyS1, /dev/ttyS3, /dev/ttyS4, /dev/ttyS10")
print("=" * 60)

# Check device tree overlays
print("\nChecking device tree configuration...")
overlay_files = [
    '/boot/orangepiEnv.txt',
    '/boot/armbianEnv.txt',
    '/boot/config.txt'
]

for f in overlay_files:
    if os.path.exists(f):
        print(f"\nFound {f}:")
        try:
            with open(f, 'r') as file:
                for line in file:
                    if 'uart' in line.lower() or 'overlay' in line.lower():
                        print(f"  {line.strip()}")
        except:
            print("  (cannot read - need sudo)")

print("\n" + "=" * 60)
print("To enable UARTs, you may need to:")
print("1. Edit /boot/orangepiEnv.txt or /boot/armbianEnv.txt")
print("2. Add: overlays=uart3 uart4")
print("3. Reboot")
print("=" * 60)
