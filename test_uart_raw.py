#!/usr/bin/env python3
"""
Raw UART test - Check if any data is coming from sensors
"""

import serial
import time

def test_uart(port, name):
    """Test a UART port for any incoming data"""
    print(f"\n{'='*60}")
    print(f"Testing {name}: {port}")
    print(f"{'='*60}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2.0
        )
        
        print(f"✓ Port opened successfully")
        print(f"Listening for 10 seconds...")
        print(f"(Sensor should output data ~10 times per second)")
        
        ser.reset_input_buffer()
        
        start_time = time.time()
        byte_count = 0
        line_count = 0
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                byte_count += len(data)
                
                # Try to decode and display
                try:
                    text = data.decode('ascii', errors='replace')
                    print(f"  Received: {repr(text)} ({len(data)} bytes)")
                    line_count += text.count('\r')
                except:
                    print(f"  Received: {data.hex()} ({len(data)} bytes)")
            
            time.sleep(0.1)
        
        ser.close()
        
        print(f"\nResults:")
        print(f"  Total bytes received: {byte_count}")
        print(f"  Total lines received: {line_count}")
        print(f"  Expected: ~100 bytes (10 readings)")
        
        if byte_count == 0:
            print(f"\n⚠ NO DATA RECEIVED!")
            print(f"  Possible causes:")
            print(f"  1. Sensor Pin 1 (BW) not connected HIGH - must be 3.3V or 5V")
            print(f"  2. Sensor Pin 5 (TX) not connected to Orange Pi")
            print(f"  3. Sensor not powered (Pin 6 to 5V, Pin 7 to GND)")
            print(f"  4. Wrong UART port mapping")
        elif byte_count < 50:
            print(f"\n⚠ LOW DATA RATE - possible connection issue")
        else:
            print(f"\n✓ Sensor appears to be working!")
            
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    print("="*60)
    print("MaxBotix MB1300AE UART Raw Data Test")
    print("="*60)
    print("\nThis test listens for raw serial data from sensors")
    print("Each sensor should output ~10 readings per second")
    print("Format: 'Rxxx\\r' where xxx is distance in cm\n")
    
    test_uart("/dev/ttyS4", "Sensor 1 (Pin 16 - UART4)")
    test_uart("/dev/ttyS3", "Sensor 2 (Pin 21 - UART3)")
    
    print("\n" + "="*60)
    print("IMPORTANT: Sensor Pin 1 (BW) MUST be connected to 3.3V or 5V")
    print("           Pin 1 HIGH = ASCII serial output on Pin 5")
    print("           Pin 1 LOW/floating = Binary analog output (not ASCII)")
    print("="*60)

if __name__ == "__main__":
    main()
