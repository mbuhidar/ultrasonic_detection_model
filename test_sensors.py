#!/usr/bin/env python3
"""
Simple test to verify MaxBotix MB1300 sensor response
Tests one sensor at a time with detailed output
"""

import time
import sys

try:
    import OPi.GPIO as GPIO
except ImportError:
    print("Error: OPi.GPIO not installed")
    sys.exit(1)

# Pin configuration (using BOARD numbering)
SENSOR1_PW = 12      # GPIO4_A4 (132)
SENSOR1_TRIGGER = 16 # GPIO4_B0 (136)
SENSOR2_PW = 18      # GPIO4_B1 (137)
SENSOR2_TRIGGER = 22 # GPIO4_B2 (138)

def test_single_sensor(pw_pin, trigger_pin, sensor_name):
    """Test a single sensor"""
    print(f"\n{'='*60}")
    print(f"Testing {sensor_name}")
    print(f"PW Pin: {pw_pin}, Trigger Pin: {trigger_pin}")
    print(f"{'='*60}")
    
    try:
        # Setup
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(pw_pin, GPIO.IN)
        
        # Set trigger to idle (HIGH)
        GPIO.output(trigger_pin, GPIO.HIGH)
        time.sleep(0.1)
        
        # Check initial state
        initial_state = GPIO.input(pw_pin)
        print(f"Initial PW pin state: {'HIGH' if initial_state else 'LOW'}")
        
        if initial_state == 0:
            print("⚠️  WARNING: PW pin is LOW (should be HIGH when idle)")
            print("   Check: Is sensor powered? (5V on sensor Pin 6)")
            print("   Check: Is PW connected? (sensor Pin 2 to Orange Pi)")
            return False
        
        print("\nSending trigger pulse...")
        GPIO.output(trigger_pin, GPIO.LOW)
        time.sleep(0.000025)  # 25 microseconds
        GPIO.output(trigger_pin, GPIO.HIGH)
        
        print("Trigger sent, monitoring PW pin for 100ms...")
        
        # Monitor for state changes
        start_time = time.time()
        state_changes = []
        last_state = GPIO.input(pw_pin)
        change_count = 0
        
        while time.time() - start_time < 0.1:  # 100ms
            current_state = GPIO.input(pw_pin)
            if current_state != last_state:
                change_count += 1
                timestamp = (time.time() - start_time) * 1000  # ms
                state_changes.append((timestamp, 'HIGH' if current_state else 'LOW'))
                last_state = current_state
                if change_count <= 5:  # Don't spam output
                    print(f"  {timestamp:.2f}ms: Pin changed to {'HIGH' if current_state else 'LOW'}")
            time.sleep(0.0001)  # 0.1ms polling
        
        print(f"\nTotal state changes detected: {change_count}")
        
        if change_count == 0:
            print("❌ NO RESPONSE from sensor")
            print("\nTroubleshooting:")
            print("  1. Check trigger connection (sensor Pin 4 to Orange Pi)")
            print("  2. Verify 5V power to sensor")
            print("  3. Check ground connection")
            print("  4. Ensure sensor has clear line of sight (2-300 inches)")
            print("  5. Try holding sensor Pin 4 (RX) to GND manually")
            return False
        elif change_count < 10:
            print(f"⚠️  WARNING: Only {change_count} changes detected (expected ~20 for 10 pulses)")
            print("   Sensor may be responding but signal quality is poor")
            return False
        else:
            print(f"✅ SUCCESS! Sensor responding with {change_count} state changes")
            print("   (Expected ~20 changes for 10 pulses)")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        GPIO.cleanup()

def main():
    print("MaxBotix MB1300 Simple Sensor Test")
    print("This will test each sensor individually")
    print("\nPress Ctrl+C to stop\n")
    
    time.sleep(1)
    
    # Test Sensor 1
    result1 = test_single_sensor(SENSOR1_PW, SENSOR1_TRIGGER, "Sensor 1")
    
    time.sleep(1)
    
    # Test Sensor 2
    result2 = test_single_sensor(SENSOR2_PW, SENSOR2_TRIGGER, "Sensor 2")
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Sensor 1: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Sensor 2: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"{'='*60}\n")
    
    if result1 and result2:
        print("Both sensors working! You can now run ultrasonic_capture.py")
    else:
        print("Fix the failing sensor(s) before running the main program")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        GPIO.cleanup()
