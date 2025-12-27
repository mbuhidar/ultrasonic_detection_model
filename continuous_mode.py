#!/usr/bin/env python3
"""
MB1300AE Continuous Serial Mode - Read distance continuously
MB1300AE outputs serial data continuously when RX is HIGH or floating
"""
import time
import OPi.GPIO as GPIO
import csv
import os
from dataclasses import dataclass
from collections import deque

@dataclass
class Measurement:
    sensor: str
    distance_inches: float
    timestamp: float

class SoftwareSerial:
    """9600 baud software serial reader"""
    BIT_DURATION = 1.0 / 9600
    
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN)
    
    def read_byte(self, timeout=0.1):
        start = time.time()
        # Wait for start bit (HIGH->LOW)
        while GPIO.input(self.pin) == GPIO.HIGH:
            if time.time() - start > timeout:
                return None
        
        time.sleep(self.BIT_DURATION / 2)  # Middle of start bit
        if GPIO.input(self.pin) != GPIO.LOW:
            return None
        
        # Read 8 bits
        byte = 0
        for i in range(8):
            time.sleep(self.BIT_DURATION)
            if GPIO.input(self.pin):
                byte |= (1 << i)
        
        time.sleep(self.BIT_DURATION)  # Stop bit
        return byte
    
    def read_line(self, timeout=0.3):
        line = []
        start = time.time()
        while time.time() - start < timeout:
            b = self.read_byte(timeout=0.05)
            if b is None:
                continue
            if b == 0x0D:  # CR
                break
            if 32 <= b <= 126:
                line.append(chr(b))
        return ''.join(line) if line else None

class MB1300Continuous:
    """MB1300AE in continuous output mode"""
    
    def __init__(self, name, tx_pin):
        self.name = name
        self.serial = SoftwareSerial(tx_pin)
        self.measurements = deque(maxlen=1000)
    
    def read_distance(self):
        """Read one serial line: Rxxx where xxx is centimeters (convert to inches)"""
        line = self.serial.read_line()
        if line and line.startswith('R') and len(line) > 1:
            try:
                cm = float(line[1:])
                inches = cm / 2.54  # Convert cm to inches
                return inches
            except:
                return None
        return None

def main():
    print("MB1300AE Continuous Serial Reader")
    print("Sensors will output continuously (no triggering needed)")
    print("=" * 60)
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # Setup sensors
    sensor1 = MB1300Continuous("Sensor_1", tx_pin=12)
    sensor2 = MB1300Continuous("Sensor_2", tx_pin=18)
    
    # IMPORTANT: Pin 1 (BW) must be HIGH or floating to enable serial output
    # If you have Pin 1 connected, set it HIGH here
    # For now, we'll enable continuous ranging mode with RX HIGH
    
    GPIO.setup(16, GPIO.OUT)  # RX for sensor 1
    GPIO.setup(22, GPIO.OUT)  # RX for sensor 2
    GPIO.output(16, GPIO.HIGH)  # Enable continuous mode
    GPIO.output(22, GPIO.HIGH)
    
    print("NOTE: Sensor Pin 1 (BW) must be HIGH or open for serial output!")
    print("If sensors don't respond, connect Pin 1 to +5V or leave it floating")
    
    print("\nSensors enabled in continuous mode")
    print("Reading serial data... Press Ctrl+C to stop\n")
    
    all_measurements = []
    count = 0
    
    try:
        while True:
            # Read from sensor 1
            dist1 = sensor1.read_distance()
            if dist1:
                m = Measurement("Sensor_1", dist1, time.time())
                sensor1.measurements.append(m)
                all_measurements.append(m)
                print(f"[Sensor_1] {dist1:6.2f} inches")
                count += 1
            
            # Read from sensor 2
            dist2 = sensor2.read_distance()
            if dist2:
                m = Measurement("Sensor_2", dist2, time.time())
                sensor2.measurements.append(m)
                all_measurements.append(m)
                print(f"[Sensor_2] {dist2:6.2f} inches")
                count += 1
            
            if count % 20 == 0 and count > 0:
                print(f"\n>>> Total measurements: {count}\n")
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    finally:
        # Save data
        os.makedirs('data', exist_ok=True)
        filename = f'data/ultrasonic_{int(time.time())}.csv'
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Sensor', 'Distance_Inches', 'Timestamp'])
            for m in all_measurements:
                writer.writerow([m.sensor, f"{m.distance_inches:.2f}", f"{m.timestamp:.6f}"])
        
        print(f"\nSaved {len(all_measurements)} measurements to {filename}")
        
        # Statistics
        if sensor1.measurements:
            d = [m.distance_inches for m in sensor1.measurements]
            print(f"\nSensor 1: {len(d)} readings, avg={sum(d)/len(d):.2f}in, min={min(d):.2f}in, max={max(d):.2f}in")
        
        if sensor2.measurements:
            d = [m.distance_inches for m in sensor2.measurements]
            print(f"Sensor 2: {len(d)} readings, avg={sum(d)/len(d):.2f}in, min={min(d):.2f}in, max={max(d):.2f}in")
        
        GPIO.cleanup()
        print("\nDone!")

if __name__ == "__main__":
    main()
