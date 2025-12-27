#!/usr/bin/env python3
"""
Orange Pi 5 MaxBotix MB1300AE Ultrasonic Sensor Controller
Uses software serial to read TX output from sensors (9600 baud)
"""

import time
import sys
import csv
import os
from dataclasses import dataclass
from typing import List, Optional
from collections import deque

try:
    import OPi.GPIO as GPIO
except ImportError:
    print("Error: OPi.GPIO not installed. Install with: pip install OPi.GPIO")
    sys.exit(1)


@dataclass
class SensorConfig:
    """Configuration for a single MB1300AE sensor"""
    name: str
    tx_pin: int      # Pin 5 (TX) - Serial output
    rx_pin: int      # Pin 4 (RX) - Trigger control


@dataclass
class RangeMeasurement:
    """Single range measurement from sensor"""
    distance_inches: float
    raw_value: int
    timestamp: float
    cycle: int
    pulse_number: int


class SoftwareSerial:
    """Software serial reader for 9600 baud (104 microseconds per bit)"""
    
    BAUD_RATE = 9600
    BIT_DURATION = 1.0 / BAUD_RATE  # ~104 microseconds
    
    def __init__(self, rx_pin: int):
        self.rx_pin = rx_pin
        GPIO.setup(rx_pin, GPIO.IN)
        
    def read_byte(self, timeout_ms: float = 100) -> Optional[int]:
        """Read one byte using software serial (8N1 format)"""
        start_time = time.time()
        timeout_sec = timeout_ms / 1000.0
        
        # Wait for start bit (HIGH to LOW transition)
        while GPIO.input(self.rx_pin) == GPIO.HIGH:
            if time.time() - start_time > timeout_sec:
                return None
                
        # Wait half a bit period to sample in middle of start bit
        time.sleep(self.BIT_DURATION / 2)
        
        if GPIO.input(self.rx_pin) != GPIO.LOW:
            return None  # False start bit
            
        # Read 8 data bits (LSB first)
        byte_value = 0
        for bit_num in range(8):
            time.sleep(self.BIT_DURATION)
            if GPIO.input(self.rx_pin) == GPIO.HIGH:
                byte_value |= (1 << bit_num)
                
        # Wait for stop bit
        time.sleep(self.BIT_DURATION)
        
        return byte_value
        
    def read_line(self, timeout_ms: float = 200) -> Optional[str]:
        """Read a line of text ending with \\r"""
        line = []
        start_time = time.time()
        timeout_sec = timeout_ms / 1000.0
        
        while True:
            if time.time() - start_time > timeout_sec:
                return None
                
            byte = self.read_byte(timeout_ms=50)
            if byte is None:
                continue
                
            if byte == 0x0D:  # Carriage return
                break
                
            if 32 <= byte <= 126:  # Printable ASCII
                line.append(chr(byte))
                
        return ''.join(line) if line else None


class MB1300Sensor:
    """Controller for MaxBotix MB1300AE ultrasonic sensor using serial output."""
    
    TRIGGER_DURATION_US = 25  # Microseconds to hold RX high
    SENSOR_WARMUP_MS = 250    # Sensor needs 250ms after power-on
    MAX_MEASUREMENTS = 1000   # Maximum measurements to store
    
    def __init__(self, config: SensorConfig):
        self.config = config
        self.measurements = deque(maxlen=self.MAX_MEASUREMENTS)
        self.serial = None
        
    def setup_gpio(self):
        """Initialize GPIO pins"""
        # RX pin (trigger) - Start LOW to stop continuous ranging
        GPIO.setup(self.config.rx_pin, GPIO.OUT, initial=GPIO.LOW)
        
        # TX pin for software serial reading
        self.serial = SoftwareSerial(self.config.tx_pin)
        
        print(f"GPIO initialized for {self.config.name}")
        
    def trigger(self):
        """Trigger sensor by pulsing RX pin HIGH"""
        # Pulse RX HIGH for at least 20μs to trigger ranging
        GPIO.output(self.config.rx_pin, GPIO.HIGH)
        time.sleep(self.TRIGGER_DURATION_US / 1_000_000)
        GPIO.output(self.config.rx_pin, GPIO.LOW)
        
    def read_serial_measurement(self) -> Optional[float]:
        """Read one range measurement from serial output"""
        if not self.serial:
            return None
            
        # MB1300 outputs: Rxxx\\r where xxx is range in inches
        line = self.serial.read_line(timeout_ms=200)
        
        if not line:
            return None
            
        # Parse "Rxxx" format
        if line.startswith('R') and len(line) >= 2:
            try:
                range_inches = int(line[1:])
                return float(range_inches)
            except ValueError:
                return None
                
        return None
    
    def capture_pulse_series(self, num_pulses: int = 10, cycle: int = 0) -> List[RangeMeasurement]:
        """Capture multiple measurements from sensor after trigger"""
        measurements = []
        
        # Trigger the sensor
        self.trigger()
        
        # Small delay for sensor to start responding
        time.sleep(0.005)
        
        # Capture the specified number of readings
        for pulse_num in range(1, num_pulses + 1):
            distance = self.read_serial_measurement()
            
            if distance is not None:
                measurement = RangeMeasurement(
                    distance_inches=distance,
                    raw_value=int(distance),
                    timestamp=time.time(),
                    cycle=cycle,
                    pulse_number=pulse_num
                )
                measurements.append(measurement)
                self.measurements.append(measurement)
                
                print(f"  [{self.config.name}] Pulse {pulse_num:2d}: {distance:6.2f} in")
            else:
                print(f"  Warning: {self.config.name} pulse {pulse_num} timeout or invalid")
                
        return measurements
    
    def get_recent_measurements(self, count: int = 10) -> List[RangeMeasurement]:
        """Get the most recent measurements"""
        return list(self.measurements)[-count:]


class DualSensorController:
    """Controller for two MB1300AE sensors with alternating triggering."""
    
    def __init__(self, sensor1_config: SensorConfig, sensor2_config: SensorConfig):
        self.sensor1 = MB1300Sensor(sensor1_config)
        self.sensor2 = MB1300Sensor(sensor2_config)
        self.cycle_count = 0
        self.running = False
        
    def setup(self):
        """Initialize both sensors"""
        print("Initializing GPIO...")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        self.sensor1.setup_gpio()
        self.sensor2.setup_gpio()
        
        # Warmup period
        print(f"Waiting for sensors to warm up ({MB1300Sensor.SENSOR_WARMUP_MS}ms)...")
        time.sleep(MB1300Sensor.SENSOR_WARMUP_MS / 1000.0)
        
        print("Ready to capture data!")
        
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()
        print("GPIO cleanup complete")
        
    def single_cycle(self, pulses_per_trigger: int = 10):
        """Execute one cycle: trigger sensor1, then sensor2"""
        self.cycle_count += 1
        
        # Trigger and capture from Sensor 1
        print(f"\n[Cycle {self.cycle_count}] Triggering {self.sensor1.config.name}...")
        measurements1 = self.sensor1.capture_pulse_series(pulses_per_trigger, self.cycle_count)
        print(f"  Captured {len(measurements1)} from {self.sensor1.config.name}")
        
        # Small delay between sensors
        time.sleep(0.02)
        
        # Trigger and capture from Sensor 2
        print(f"[Cycle {self.cycle_count}] Triggering {self.sensor2.config.name}...")
        measurements2 = self.sensor2.capture_pulse_series(pulses_per_trigger, self.cycle_count)
        print(f"  Captured {len(measurements2)} from {self.sensor2.config.name}")
        
    def continuous_capture(self, pulses_per_trigger: int = 10, delay_between_cycles: float = 0.1):
        """Continuously capture data until stopped"""
        self.running = True
        
        print("\nStarting continuous capture...")
        print("\nCapturing continuously... Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while self.running:
                self.single_cycle(pulses_per_trigger)
                
                # Show progress every 5 cycles
                if self.cycle_count % 5 == 0:
                    print(f"\n>>> Cycles completed: {self.cycle_count}")
                
                time.sleep(delay_between_cycles)
                
        except KeyboardInterrupt:
            print("\n\nStopped by user (Ctrl+C)")
            self.running = False
            
    def stop_capture(self):
        """Stop continuous capture"""
        self.running = False
        print("Stopping continuous capture...")
        time.sleep(0.1)
        print("Capture loop stopped")
        
    def get_all_measurements(self) -> List[tuple]:
        """Get all measurements from both sensors"""
        all_measurements = []
        
        for m in self.sensor1.measurements:
            all_measurements.append(('Sensor_1', m))
            
        for m in self.sensor2.measurements:
            all_measurements.append(('Sensor_2', m))
        
        # Sort by timestamp
        all_measurements.sort(key=lambda x: x[1].timestamp)
        
        return all_measurements
        
    def save_to_csv(self, filename: str = None):
        """Save all measurements to CSV file"""
        if filename is None:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            timestamp = int(time.time())
            filename = f'data/ultrasonic_data_{timestamp}.csv'
            
        measurements = self.get_all_measurements()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Sensor', 'Cycle', 'Pulse_Number', 'Distance_Inches', 'Raw_Value', 'Timestamp'])
            
            for sensor_name, m in measurements:
                writer.writerow([
                    sensor_name,
                    m.cycle,
                    m.pulse_number,
                    f"{m.distance_inches:.2f}",
                    m.raw_value,
                    f"{m.timestamp:.6f}"
                ])
                
        print(f"Saved {len(measurements)} measurements to: {os.path.abspath(filename)}")
        
    def print_statistics(self):
        """Print statistics for both sensors"""
        print("\n" + "=" * 60)
        print("FINAL STATISTICS")
        print("=" * 60)
        
        for sensor in [self.sensor1, self.sensor2]:
            if len(sensor.measurements) == 0:
                print(f"\n{sensor.config.name}: No measurements captured")
                continue
                
            distances = [m.distance_inches for m in sensor.measurements]
            
            print(f"\n{sensor.config.name}:")
            print(f"  Total measurements: {len(distances)}")
            print(f"  Min distance: {min(distances):.2f} inches")
            print(f"  Max distance: {max(distances):.2f} inches")
            print(f"  Average distance: {sum(distances)/len(distances):.2f} inches")


def main():
    """Main function - runs continuous capture loop"""
    
    # Configure sensors with Orange Pi 5 pins
    sensor1_config = SensorConfig(
        name="Sensor_1",
        tx_pin=12,  # Pin 12 - GPIO4_A4 - Read serial data (from sensor Pin 5)
        rx_pin=16   # Pin 16 - GPIO4_B0 - Trigger control (to sensor Pin 4)
    )
    
    sensor2_config = SensorConfig(
        name="Sensor_2", 
        tx_pin=18,  # Pin 18 - GPIO4_B1 - Read serial data (from sensor Pin 5)
        rx_pin=22   # Pin 22 - GPIO4_B2 - Trigger control (to sensor Pin 4)
    )
    
    # Create controller
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    try:
        # Setup GPIO
        controller.setup()
        
        # Run continuous capture (runs until Ctrl+C)
        controller.continuous_capture(
            pulses_per_trigger=10,
            delay_between_cycles=0.1
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        
    finally:
        # Stop capture
        controller.stop_capture()
        
        # Save data to CSV
        print("\nSaving data to CSV...")
        controller.save_to_csv()
        
        # Print statistics
        controller.print_statistics()
        
        # Cleanup
        controller.cleanup()
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
