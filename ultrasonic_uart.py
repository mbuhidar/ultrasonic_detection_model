#!/usr/bin/env python3
"""
MaxBotix MB1300AE Ultrasonic Sensor Data Capture - Hardware UART Version
Using Orange Pi 5 hardware serial ports (UART3 and UART4)

WIRING REQUIREMENTS:
- Sensor Pin 1 (BW) MUST be connected to 3.3V for ASCII serial output
- Sensor Pin 5 (TX) connects to Orange Pi UART RX pins
- If Pin 1 is floating or LOW, sensor outputs binary data instead of ASCII
"""

import serial
import time
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class SensorReading:
    """Data structure for a sensor reading"""
    sensor_id: int
    timestamp: float
    distance_cm: int
    reading_number: int

class MB1300Sensor:
    """Handler for MB1300AE sensor via hardware UART"""
    
    def __init__(self, sensor_id: int, uart_port: str):
        """
        Initialize sensor
        
        Args:
            sensor_id: Sensor identifier (1 or 2)
            uart_port: UART device path (e.g., '/dev/ttyS3')
        """
        self.sensor_id = sensor_id
        self.uart_port = uart_port
        self.serial_port = None
        
    def open(self):
        """Open the serial port"""
        try:
            self.serial_port = serial.Serial(
                port=self.uart_port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            print(f"Sensor {self.sensor_id}: Opened {self.uart_port}")
            # Clear any buffered data
            self.serial_port.reset_input_buffer()
            return True
        except Exception as e:
            print(f"Sensor {self.sensor_id}: Failed to open {self.uart_port}: {e}")
            return False
    
    def close(self):
        """Close the serial port"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print(f"Sensor {self.sensor_id}: Closed {self.uart_port}")
    
    def read_distance(self, reading_number: int) -> Optional[SensorReading]:
        """
        Read one distance measurement from serial output
        
        Args:
            reading_number: Sequential reading number
            
        Returns:
            SensorReading object or None if read failed
        """
        if not self.serial_port or not self.serial_port.is_open:
            return None
        
        try:
            # Read until we get a complete line (ending with \r)
            line = self.serial_port.read_until(b'\r')
            
            if not line:
                return None
            
            # Parse the line: format is "Rxxx\r" where xxx is distance in cm
            line_str = line.decode('ascii', errors='ignore').strip()
            
            if line_str.startswith('R') and len(line_str) > 1:
                distance_str = line_str[1:]
                distance_cm = int(distance_str)
                
                return SensorReading(
                    sensor_id=self.sensor_id,
                    timestamp=time.time(),
                    distance_cm=distance_cm,
                    reading_number=reading_number
                )
        except (ValueError, UnicodeDecodeError) as e:
            print(f"Sensor {self.sensor_id}: Parse error: {e}")
        except Exception as e:
            print(f"Sensor {self.sensor_id}: Read error: {e}")
        
        return None

class DualSensorController:
    """Controller for managing two MB1300AE sensors"""
    
    def __init__(self, uart1: str = "/dev/ttyS4", uart2: str = "/dev/ttyS3"):
        """
        Initialize controller with two sensors
        
        Args:
            uart1: UART device for Sensor 1 (default: /dev/ttyS4 for UART4)
            uart2: UART device for Sensor 2 (default: /dev/ttyS3 for UART3)
        """
        self.sensor1 = MB1300Sensor(1, uart1)
        self.sensor2 = MB1300Sensor(2, uart2)
        self.data_dir = "data"
        
    def setup(self) -> bool:
        """Initialize sensors"""
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Open serial ports
        success1 = self.sensor1.open()
        success2 = self.sensor2.open()
        
        if not success1 or not success2:
            print("Failed to open one or more serial ports")
            self.cleanup()
            return False
        
        print("\n" + "="*60)
        print("Hardware UART Configuration:")
        print(f"  Sensor 1: {self.sensor1.uart_port} (Pin 16 - UART4_RX_M0)")
        print(f"  Sensor 2: {self.sensor2.uart_port} (Pin 21 - UART3_RX_M0)")
        print("\nIMPORTANT: Sensor Pin 1 (BW) must be connected to 3.3V!")
        print("  - Pin 1 HIGH = ASCII serial output (Rxxx\\r format)")
        print("  - Pin 1 LOW/floating = Binary analog data (not usable)")
        print("="*60 + "\n")
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.sensor1.close()
        self.sensor2.close()
    
    def capture_alternating(self, readings_per_sensor: int = 10):
        """
        Capture readings from both sensors continuously
        
        Args:
            readings_per_sensor: Number of readings to capture per cycle
        """
        try:
            cycle = 0
            all_readings: List[SensorReading] = []
            
            print("Starting continuous data capture...")
            print("Press Ctrl+C to stop\n")
            
            while True:
                cycle += 1
                print(f"\n{'='*60}")
                print(f"Cycle {cycle}")
                print(f"{'='*60}\n")
                
                # Capture from Sensor 1
                print(f"Capturing {readings_per_sensor} readings from Sensor 1...")
                for i in range(readings_per_sensor):
                    reading = self.sensor1.read_distance(i + 1)
                    if reading:
                        all_readings.append(reading)
                        print(f"  Sensor 1 Reading {i+1}: {reading.distance_cm} cm")
                    else:
                        print(f"  Sensor 1 Reading {i+1}: FAILED")
                    time.sleep(0.1)  # MB1300 ranges ~10Hz
                
                # Capture from Sensor 2
                print(f"\nCapturing {readings_per_sensor} readings from Sensor 2...")
                for i in range(readings_per_sensor):
                    reading = self.sensor2.read_distance(i + 1)
                    if reading:
                        all_readings.append(reading)
                        print(f"  Sensor 2 Reading {i+1}: {reading.distance_cm} cm")
                    else:
                        print(f"  Sensor 2 Reading {i+1}: FAILED")
                    time.sleep(0.1)
                
                # Save data after each cycle
                self._save_readings(all_readings)
                print(f"\nCycle {cycle} complete. Total readings collected: {len(all_readings)}")
                
        except KeyboardInterrupt:
            print("\n\nStopping capture...")
            self._save_readings(all_readings)
            print(f"Total readings collected: {len(all_readings)}")
    
    def _save_readings(self, readings: List[SensorReading]):
        """Save readings to CSV file"""
        if not readings:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"sensor_data_{timestamp}.csv")
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Sensor_ID', 'Timestamp', 'Distance_cm', 'Reading_Number'])
            
            for reading in readings:
                writer.writerow([
                    reading.sensor_id,
                    f"{reading.timestamp:.6f}",
                    reading.distance_cm,
                    reading.reading_number
                ])
        
        print(f"Data saved to: {filename}")

def main():
    """Main execution function"""
    controller = DualSensorController()
    
    print("="*60)
    print("MaxBotix MB1300AE Dual Sensor Data Capture")
    print("Hardware UART Version (Orange Pi 5)")
    print("="*60)
    
    try:
        if not controller.setup():
            print("Setup failed!")
            return 1
        
        # Run continuous capture with 10 readings per sensor per cycle
        controller.capture_alternating(readings_per_sensor=10)
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.cleanup()
        print("Cleanup complete")
    
    return 0

if __name__ == "__main__":
    exit(main())
