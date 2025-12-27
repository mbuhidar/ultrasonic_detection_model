#!/usr/bin/env python3
"""
Diagnostic: Check if MB1300AE sensors are transmitting data
"""
import time
import OPi.GPIO as GPIO

TX_PIN_1 = 12
TX_PIN_2 = 18
RX_PIN_1 = 16
RX_PIN_2 = 22

print("MB1300AE Sensor Diagnostic")
print("=" * 60)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Setup pins
GPIO.setup(TX_PIN_1, GPIO.IN)
GPIO.setup(TX_PIN_2, GPIO.IN)
GPIO.setup(RX_PIN_1, GPIO.OUT)
GPIO.setup(RX_PIN_2, GPIO.OUT)

# Set RX pins LOW (stop continuous ranging)
GPIO.output(RX_PIN_1, GPIO.LOW)
GPIO.output(RX_PIN_2, GPIO.LOW)

time.sleep(0.5)

print("\n1. Checking TX pin states (with RX LOW - stopped)...")
print(f"   Sensor 1 TX (Pin 12): {GPIO.input(TX_PIN_1)} ({'HIGH' if GPIO.input(TX_PIN_1) else 'LOW'})")
print(f"   Sensor 2 TX (Pin 18): {GPIO.input(TX_PIN_2)} ({'HIGH' if GPIO.input(TX_PIN_2) else 'LOW'})")

print("\n2. Watching for activity on TX pins (5 seconds)...")
print("   Looking for any state changes...")

start = time.time()
changes_1 = 0
changes_2 = 0
last_1 = GPIO.input(TX_PIN_1)
last_2 = GPIO.input(TX_PIN_2)

while time.time() - start < 5:
    curr_1 = GPIO.input(TX_PIN_1)
    curr_2 = GPIO.input(TX_PIN_2)
    
    if curr_1 != last_1:
        changes_1 += 1
        if changes_1 <= 3:
            print(f"   Sensor 1: Change {changes_1} detected")
        last_1 = curr_1
        
    if curr_2 != last_2:
        changes_2 += 1
        if changes_2 <= 3:
            print(f"   Sensor 2: Change {changes_2} detected")
        last_2 = curr_2
    
    time.sleep(0.0001)

print(f"\n   Sensor 1 changes: {changes_1}")
print(f"   Sensor 2 changes: {changes_2}")

if changes_1 == 0 and changes_2 == 0:
    print("\n❌ NO ACTIVITY on either TX pin!")
    print("\nPossible issues:")
    print("  1. Sensor Pin 5 (TX) NOT connected to Orange Pi Pin 12/18")
    print("  2. Sensors not powered (check 5V on sensor Pin 6)")
    print("  3. Wrong sensor model (need MB1300AE with serial TX)")
    print("\nVerify wiring:")
    print("  - Sensor 1 Pin 5 (TX) → Orange Pi Pin 12")
    print("  - Sensor 2 Pin 5 (TX) → Orange Pi Pin 18")
else:
    print("\n✓ Activity detected!")

print("\n3. Testing trigger response...")
print("   Setting RX HIGH to trigger Sensor 1...")
GPIO.output(RX_PIN_1, GPIO.HIGH)
time.sleep(0.00003)  # 30us
GPIO.output(RX_PIN_1, GPIO.LOW)

print("   Watching TX pin for 500ms...")
start = time.time()
trigger_changes = 0
last_state = GPIO.input(TX_PIN_1)

while time.time() - start < 0.5:
    curr_state = GPIO.input(TX_PIN_1)
    if curr_state != last_state:
        trigger_changes += 1
        if trigger_changes <= 5:
            elapsed = (time.time() - start) * 1000
            print(f"   {elapsed:.1f}ms: State change {trigger_changes}")
        last_state = curr_state
    time.sleep(0.0001)

print(f"\n   Total changes after trigger: {trigger_changes}")

if trigger_changes > 0:
    print("   ✓ Sensor responding to trigger!")
else:
    print("   ❌ No response to trigger")
    print("\nCheck:")
    print("  - Is sensor Pin 4 (RX) connected to Orange Pi Pin 16?")
    print("  - Try manually connecting sensor Pin 4 to GND")

GPIO.cleanup()
print("\n" + "=" * 60)
