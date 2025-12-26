#!/usr/bin/env python3
"""
Test both trigger methods for MB1300
"""
import time
import OPi.GPIO as GPIO

PW_PIN = 12
TRIGGER_PIN = 16

print("MB1300 Trigger Method Test")
print("=" * 50)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(PW_PIN, GPIO.IN)

def watch_changes(duration=0.2):
    """Watch for pin changes"""
    start = time.time()
    changes = 0
    last = GPIO.input(PW_PIN)
    while (time.time() - start) < duration:
        current = GPIO.input(PW_PIN)
        if current != last:
            changes += 1
            last = current
    return changes

# Test 1: HIGH to LOW pulse (RX pin trigger)
print("\n1. Testing RX trigger (HIGH->LOW->HIGH)...")
GPIO.output(TRIGGER_PIN, GPIO.HIGH)
time.sleep(0.1)
print(f"   Before: PW={GPIO.input(PW_PIN)}")
GPIO.output(TRIGGER_PIN, GPIO.LOW)
time.sleep(0.00002)  # 20us LOW
GPIO.output(TRIGGER_PIN, GPIO.HIGH)
changes1 = watch_changes(0.2)
print(f"   Changes: {changes1}")

time.sleep(0.5)

# Test 2: LOW to HIGH pulse
print("\n2. Testing inverted trigger (LOW->HIGH->LOW)...")
GPIO.output(TRIGGER_PIN, GPIO.LOW)
time.sleep(0.1)
print(f"   Before: PW={GPIO.input(PW_PIN)}")
GPIO.output(TRIGGER_PIN, GPIO.HIGH)
time.sleep(0.00002)  # 20us HIGH
GPIO.output(TRIGGER_PIN, GPIO.LOW)
changes2 = watch_changes(0.2)
print(f"   Changes: {changes2}")

time.sleep(0.5)

# Test 3: Longer LOW pulse
print("\n3. Testing longer LOW pulse (100us)...")
GPIO.output(TRIGGER_PIN, GPIO.HIGH)
time.sleep(0.1)
print(f"   Before: PW={GPIO.input(PW_PIN)}")
GPIO.output(TRIGGER_PIN, GPIO.LOW)
time.sleep(0.0001)  # 100us LOW
GPIO.output(TRIGGER_PIN, GPIO.HIGH)
changes3 = watch_changes(0.2)
print(f"   Changes: {changes3}")

time.sleep(0.5)

# Test 4: Check if sensor is in continuous mode
print("\n4. Testing if sensor is in continuous mode...")
print("   (just watching with no trigger)")
changes4 = watch_changes(0.5)
print(f"   Changes: {changes4}")

print("\n" + "=" * 50)
print("RESULTS:")
print(f"  Method 1 (RX LOW pulse): {changes1} changes")
print(f"  Method 2 (inverted): {changes2} changes")
print(f"  Method 3 (long pulse): {changes3} changes")
print(f"  Method 4 (no trigger): {changes4} changes")

if changes4 > 0:
    print("\n⚠️  Sensor running in CONTINUOUS mode")
    print("   Pin 5 (TX) might be grounded or connected")
elif max(changes1, changes2, changes3) > 0:
    winner = max([(changes1, 1), (changes2, 2), (changes3, 3)])[1]
    print(f"\n✅ Method {winner} WORKS!")
else:
    print("\n❌ NO METHODS WORK")
    print("\nCheck:")
    print("  - Is sensor Pin 4 (RX) connected to Orange Pi Pin 16?")
    print("  - Try manually connecting sensor Pin 4 to GND")
    print("  - Is sensor Pin 5 (TX) floating (not connected)?")

GPIO.cleanup()
