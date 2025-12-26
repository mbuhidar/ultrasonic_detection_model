#!/usr/bin/env python3
"""
GPIO Diagnostic Tool for Orange Pi 5
Tests GPIO pins to verify they're working correctly
"""

import time
import sys

try:
    import OPi.GPIO as GPIO
except ImportError:
    print("Error: OPi.GPIO not installed")
    sys.exit(1)

def test_gpio_basic():
    """Test basic GPIO functionality"""
    print("=" * 60)
    print("Orange Pi 5 GPIO Diagnostic Test")
    print("=" * 60)
    
    # Pins we're using for sensors
    test_pins = {
        12: "Sensor_1_PW",
        16: "Sensor_1_Trigger",
        18: "Sensor_2_PW",
        22: "Sensor_2_Trigger"
    }
    
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        print("\n1. Testing OUTPUT pins (Trigger pins)...")
        print("-" * 60)
        
        for pin in [16, 22]:
            try:
                GPIO.setup(pin, GPIO.OUT)
                print(f"   Pin {pin} ({test_pins[pin]}): Setup OK")
                
                # Test toggling
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(pin, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(pin, GPIO.HIGH)
                print(f"   Pin {pin}: Toggle test PASSED")
                
            except Exception as e:
                print(f"   Pin {pin}: FAILED - {e}")
        
        print("\n2. Testing INPUT pins (Pulse Width pins)...")
        print("-" * 60)
        
        for pin in [12, 18]:
            try:
                GPIO.setup(pin, GPIO.IN)
                state = GPIO.input(pin)
                print(f"   Pin {pin} ({test_pins[pin]}): Setup OK")
                print(f"   Pin {pin}: Current state = {state} ({'HIGH' if state else 'LOW'})")
                
            except Exception as e:
                print(f"   Pin {pin}: FAILED - {e}")
        
        print("\n3. Testing Sensor Trigger Sequence...")
        print("-" * 60)
        
        # Setup trigger pins
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(16, GPIO.HIGH)
        GPIO.output(22, GPIO.HIGH)
        
        # Setup input pins
        GPIO.setup(12, GPIO.IN)
        GPIO.setup(18, GPIO.IN)
        
        # Test Sensor 1
        print("\n   Testing Sensor 1 (Pin 16 trigger, Pin 12 input):")
        print("   - Setting trigger HIGH (idle)")
        GPIO.output(16, GPIO.HIGH)
        time.sleep(0.1)
        
        print("   - Reading PW pin before trigger:", GPIO.input(12))
        
        print("   - Sending trigger pulse (LOW for 25us)...")
        GPIO.output(16, GPIO.LOW)
        time.sleep(0.000025)
        GPIO.output(16, GPIO.HIGH)
        
        print("   - Waiting for pulse response...")
        start_time = time.time()
        timeout = 0.1  # 100ms timeout
        
        # Wait for any change on PW pin
        initial_state = GPIO.input(12)
        response_detected = False
        
        while time.time() - start_time < timeout:
            if GPIO.input(12) != initial_state:
                response_detected = True
                print("   ✓ Sensor 1 RESPONDED!")
                break
            time.sleep(0.0001)
        
        if not response_detected:
            print("   ✗ Sensor 1 NO RESPONSE")
            print(f"     Initial state: {initial_state}")
            print(f"     Final state: {GPIO.input(12)}")
        
        time.sleep(0.1)
        
        # Test Sensor 2
        print("\n   Testing Sensor 2 (Pin 22 trigger, Pin 18 input):")
        print("   - Setting trigger HIGH (idle)")
        GPIO.output(22, GPIO.HIGH)
        time.sleep(0.1)
        
        print("   - Reading PW pin before trigger:", GPIO.input(18))
        
        print("   - Sending trigger pulse (LOW for 25us)...")
        GPIO.output(22, GPIO.LOW)
        time.sleep(0.000025)
        GPIO.output(22, GPIO.HIGH)
        
        print("   - Waiting for pulse response...")
        start_time = time.time()
        
        initial_state = GPIO.input(18)
        response_detected = False
        
        while time.time() - start_time < timeout:
            if GPIO.input(18) != initial_state:
                response_detected = True
                print("   ✓ Sensor 2 RESPONDED!")
                break
            time.sleep(0.0001)
        
        if not response_detected:
            print("   ✗ Sensor 2 NO RESPONSE")
            print(f"     Initial state: {initial_state}")
            print(f"     Final state: {GPIO.input(18)}")
        
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING TIPS:")
        print("=" * 60)
        print("If sensors don't respond:")
        print("1. Check 5V power connection to both sensors")
        print("2. Check ground connections")
        print("3. Verify sensor Pin 4 (RX) is connected to trigger pins")
        print("4. Verify sensor Pin 2 (PW) is connected to input pins")
        print("5. Check if sensors have objects in range (2-300 inches)")
        print("6. Make sure sensors are powered on (may have LED indicator)")
        print("7. Use a multimeter to verify 5V on sensor power pins")
        print("8. Try connecting Pin 4 (RX) to GND briefly to trigger")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        GPIO.cleanup()
        print("\nGPIO cleanup complete")

if __name__ == "__main__":
    test_gpio_basic()
