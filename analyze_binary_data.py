#!/usr/bin/env python3
"""
Analyze the binary data pattern from MB1300AE sensors
Helps understand what mode the sensor is in
"""

import struct

# Sample binary data patterns from the test output
sample_data = [
    b'+\x00\x06fdy\x00',  # 7 bytes - most common pattern
    b'+\x00\x06Y2y\x00',  # 7 bytes - variant
    b'+\x00\x06\xef\x1e\x00',  # 7 bytes - variant
]

print("="*60)
print("MB1300AE Binary Data Pattern Analysis")
print("="*60)

for i, data in enumerate(sample_data, 1):
    print(f"\nPattern {i}: {data.hex()} ({len(data)} bytes)")
    print(f"  ASCII view: {repr(data)}")
    print(f"  Byte values: {[f'0x{b:02x}' for b in data]}")
    
    # Try to decode as if it contains distance info
    if len(data) >= 7:
        print(f"  Byte 0: 0x{data[0]:02x} ({data[0]}) = '+' or 0x2B")
        print(f"  Byte 1: 0x{data[1]:02x} ({data[1]})")
        print(f"  Byte 2: 0x{data[2]:02x} ({data[2]})")
        print(f"  Byte 3: 0x{data[3]:02x} ({data[3]}) = '{chr(data[3]) if 32 <= data[3] < 127 else '?'}'")
        print(f"  Byte 4: 0x{data[4]:02x} ({data[4]}) = '{chr(data[4]) if 32 <= data[4] < 127 else '?'}'")
        print(f"  Byte 5: 0x{data[5]:02x} ({data[5]}) = '{chr(data[5]) if 32 <= data[5] < 127 else '?'}'")
        print(f"  Byte 6: 0x{data[6]:02x} ({data[6]})")

print("\n" + "="*60)
print("ANALYSIS:")
print("="*60)
print("""
The data pattern shows:
- 7-8 byte packets (not ASCII 'Rxxx\\r' format)
- Starts with 0x2B ('+' character)
- Contains non-ASCII bytes
- No carriage return (\\r = 0x0D) terminators

This is NOT the ASCII serial format!

CONCLUSION: Pin 1 (BW) is NOT connected HIGH

Pin 1 (BW) Modes:
-----------------
1. BW = LOW (GND)      → No serial output at all
2. BW = FLOATING       → Binary analog waveform data ← YOU ARE HERE
3. BW = HIGH (3.3V/5V) → ASCII serial 'Rxxx\\r' format ← TARGET

ACTION REQUIRED:
Connect Pin 1 (BW) to 3.3V (Orange Pi Pin 1 or Pin 17)
on BOTH sensors to get ASCII output.

If you believe Pin 1 is already connected to 3.3V:
1. Check the physical connection - ensure good contact
2. Measure voltage at sensor Pin 1 with multimeter (should be ~3.3V)
3. Try connecting to 5V instead (Pin 2 or Pin 4)
4. Check for reversed pin numbering on your sensor header
""")

print("\n" + "="*60)
print("What ASCII output should look like:")
print("="*60)
print("  Received: 'R123\\r' (5 bytes)  ← 123 cm")
print("  Received: 'R045\\r' (5 bytes)  ← 45 cm")
print("  Received: 'R234\\r' (5 bytes)  ← 234 cm")
print("="*60)
