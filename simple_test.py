#!/usr/bin/env python3
"""
Ultra-simple sensor test - just checks if sensor responds
"""
import time
import OPi.GPIO as GPIO

# Pin numbers
PW_PIN = 12
TRIGGER_PIN = 16

print("Simple Sensor 1 Test")
print("=" * 40)

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(PW_PIN, GPIO.IN)

# Set trigger HIGH (idle)
GPIO.output(TRIGGER_PIN, GPIO.HIGH)
time.sleep(0.5)

# Check if sensor is powered
print(f"PW pin initial state: {GPIO.input(PW_PIN)} (should be 1)")

# Send trigger
print("Sending trigger...")
GPIO.output(TRIGGER_PIN, GPIO.LOW)
time.sleep(0.00003)  # 30 microseconds
GPIO.output(TRIGGER_PIN, GPIO.HIGH)

# Watch for any changes
print("Watching for 200ms...")
start = time.time()
changes = 0
last = GPIO.input(PW_PIN)

while (time.time() - start) < 0.2:
    current = GPIO.input(PW_PIN)
    if current != last:
        changes += 1
        print(f"  Change {changes}: pin = {current}")
        last = current

print(f"\nTotal changes: {changes}")

if changes > 0:
    print("✅ SENSOR RESPONDING!")
else:
    print("❌ NO RESPONSE - check wiring")

GPIO.cleanup()
