#!/usr/bin/env python3
"""
Orange Pi 5 MaxBotix MB1300 Ultrasonic Sensor Controller
Captures 10 pulse width measurements from two sensors in alternating pattern.
"""

import time
import threading
import csv
import os
import serial
from dataclasses import dataclass
from typing import List, Callable, Optional
from collections import deque

try:
    import OPi.GPIO as GPIO
except ImportError:
    print("Warning: OPi.GPIO not installed. Install with: pip install OPi.GPIO")
    import sys
    sys.exit(1)


@dataclass
class SensorConfig:
    """Configuration for a single MB1300 sensor."""
    name: str
    tx_pin: int  # Serial TX output pin (connects to sensor Pin 5)
    trigger_pin: int  # Trigger output pin (connects to sensor Pin 4 RX)
    

@dataclass
class PulseWidthMeasurement:
    """Single pulse width measurement."""
    sensor_name: str
    pulse_number: int  # 1-10 for each trigger
    pulse_width_us: float  # Microseconds
    distance_inches: float  # Calculated distance
    timestamp: float  # Unix timestamp


class MB1300Sensor:
    """Controller for MaxBotix MB1300AE ultrasonic sensor using serial output."""
    
    TRIGGER_DURATION_US = 25  # Microseconds to hold trigger high
    SENSOR_WARMUP_MS = 250  # Sensor needs 250ms after power-on
    BAUD_RATE = 9600  # Serial baud rate for MB1300
    SERIAL_TIMEOUT = 0.1  # Serial read timeout in seconds
    
    def __init__(self, config: SensorConfig):
        self.config = config
        self.measurements: deque = deque(maxlen=1000)
        self.is_capturing = False
        self.pulse_count = 0
        self.callback: Optional[Callable] = None
        self._lock = threading.Lock()
        self.serial_port = None
        
    def setup_gpio(self):
        """Initialize GPIO pins for this sensor."""
        # Trigger pin as output (RX on sensor)
        GPIO.setup(self.config.trigger_pin, GPIO.OUT)
        GPIO.output(self.config.trigger_pin, GPIO.LOW)  # Hold LOW to stop ranging
        
        # TX pin will be used for serial communication (not GPIO)
        
    def trigger(self):
        """Send trigger pulse to start ranging."""
        # RX is normally held LOW (stopped)
        # Pulse HIGH for 20+ microseconds to trigger ranging
        GPIO.output(self.config.trigger_pin, GPIO.HIGH)
        time.sleep(self.TRIGGER_DURATION_US / 1_000_000)
        GPIO.output(self.config.trigger_pin, GPIO.LOW)
        
        # Small delay after trigger for sensor to start responding
        time.sleep(0.001)  # 1ms delay
        
    def setup_serial(self, uart_device: str):
        """Setup serial connection for reading sensor data.
        
        Args:
            uart_device: UART device path (e.g., '/dev/ttyS3' for UART3)
        """
        try:
            self.serial_port = serial.Serial(
                port=uart_device,
                baudrate=self.BAUD_RATE,
                timeout=self.SERIAL_TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            return True
        except Exception as e:
            print(f"Error opening serial port {uart_device}: {e}")
            return False
    
    def read_serial_measurement(self) -> Optional[float]:
        """
        Read one distance measurement from serial output.
        MB1300 outputs format: Rxxx\r where xxx is distance in mm.
        Returns distance in inches, or None if error.
        """
        if not self.serial_port or not self.serial_port.is_open:
            return None
            
        try:
            # Read until we get 'R' start character
            line = self.serial_port.read_until(b'\r')
            
            if len(line) > 0 and line[0] == ord('R'):
                # Parse distance in mm
                distance_str = line[1:-1].decode('ascii').strip()
                distance_mm = int(distance_str)
                distance_inches = distance_mm / 25.4  # Convert mm to inches
                return distance_inches
            return None
            
        except Exception as e:
            return None
    
    def capture_pulse_series(self, num_pulses: int = 10) -> List[PulseWidthMeasurement]:
        """
        Capture a series of measurements after trigger.
        MB1300 outputs readings continuously after trigger.
        """
        measurements = []
        
        for pulse_num in range(1, num_pulses + 1):
            distance_inches = self.read_serial_measurement()
            
            if distance_inches is not None:
                # For MB1300AE serial, we don't have pulse width
                # Store distance_mm * 58 as pseudo pulse width for compatibility
                pseudo_pulse_width = distance_inches * 25.4 * 58  # mm * 58us/cm
                
                measurement = PulseWidthMeasurement(
                    sensor_name=self.config.name,
                    pulse_number=pulse_num,
                    pulse_width_us=pseudo_pulse_width,
                    distance_inches=distance_inches,
                    timestamp=time.time()
                )
                
                measurements.append(measurement)
                
                with self._lock:
                    self.measurements.append(measurement)
                
                # Call callback if registered
                if self.callback:
                    self.callback(measurement)
            else:
                print(f"Warning: {self.config.name} pulse {pulse_num} timeout or invalid")
                
            # Small delay between pulse measurements
            time.sleep(0.001)
            
        return measurements
    
    def get_recent_measurements(self, count: int = 10) -> List[PulseWidthMeasurement]:
        """Get the most recent N measurements."""
        with self._lock:
            return list(self.measurements)[-count:]


class DualSensorController:
    """Controller for two MB1300 sensors with alternating triggering."""
    
    def __init__(self, sensor1_config: SensorConfig, sensor2_config: SensorConfig):
        self.sensor1 = MB1300Sensor(sensor1_config)
        self.sensor2 = MB1300Sensor(sensor2_config)
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.cycle_count = 0
        
    def setup(self, uart1_device: str = '/dev/ttyS3', uart2_device: str = '/dev/ttyS4'):
        """Initialize GPIO mode and setup both sensors.
        
        Args:
            uart1_device: UART device for sensor 1 (default /dev/ttyS3)
            uart2_device: UART device for sensor 2 (default /dev/ttyS4)
        """
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setwarnings(False)
        
        self.sensor1.setup_gpio()
        self.sensor2.setup_gpio()
        
        print(f"GPIO initialized for {self.sensor1.config.name} and {self.sensor2.config.name}")
        
        # Setup serial ports
        print(f"Setting up serial ports...")
        if not self.sensor1.setup_serial(uart1_device):
            print(f"Warning: Could not open {uart1_device} for {self.sensor1.config.name}")
        if not self.sensor2.setup_serial(uart2_device):
            print(f"Warning: Could not open {uart2_device} for {self.sensor2.config.name}")
        
        # Wait for sensors to warm up (MB1300 needs 250ms after power-on)
        print("Waiting for sensors to warm up (250ms)...")
        time.sleep(0.25)
        
        print("Ready to capture data!")
        
    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup()
        print("GPIO cleaned up")
        
    def single_cycle(self, pulses_per_trigger: int = 10):
        """
        Execute one cycle: trigger sensor1, capture, trigger sensor2, capture.
        """
        self.cycle_count += 1
        
        # Trigger and capture from Sensor 1
        print(f"\n[Cycle {self.cycle_count}] Triggering {self.sensor1.config.name}...")
        self.sensor1.trigger()
        measurements1 = self.sensor1.capture_pulse_series(pulses_per_trigger)
        print(f"  Captured {len(measurements1)} pulses from {self.sensor1.config.name}")
        
        # Small delay between sensors
        time.sleep(0.01)
        
        # Trigger and capture from Sensor 2
        print(f"[Cycle {self.cycle_count}] Triggering {self.sensor2.config.name}...")
        self.sensor2.trigger()
        measurements2 = self.sensor2.capture_pulse_series(pulses_per_trigger)
        print(f"  Captured {len(measurements2)} pulses from {self.sensor2.config.name}")
        
        return measurements1, measurements2
    
    def start_continuous_capture(self, cycle_delay: float = 0.1, pulses_per_trigger: int = 10):
        """
        Start continuous alternating capture in background thread.
        
        Args:
            cycle_delay: Delay between complete cycles (seconds)
            pulses_per_trigger: Number of pulses to capture per trigger (default 10)
        """
        if self.is_running:
            print("Capture already running")
            return
            
        self.is_running = True
        self.cycle_count = 0
        
        def capture_loop():
            print("Starting continuous capture...")
            while self.is_running:
                try:
                    self.single_cycle(pulses_per_trigger)
                    time.sleep(cycle_delay)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error in capture loop: {e}")
                    
            print("Capture loop stopped")
            
        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        
    def stop_continuous_capture(self):
        """Stop continuous capture."""
        if not self.is_running:
            print("Capture not running")
            return
            
        print("Stopping continuous capture...")
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
            
    def set_callbacks(self, callback: Callable[[PulseWidthMeasurement], None]):
        """Set callback function to be called for each measurement."""
        self.sensor1.callback = callback
        self.sensor2.callback = callback
        
    def get_all_measurements(self) -> dict:
        """Get all measurements from both sensors."""
        return {
            self.sensor1.config.name: list(self.sensor1.measurements),
            self.sensor2.config.name: list(self.sensor2.measurements)
        }
    
    def print_statistics(self):
        """Print summary statistics for both sensors."""
        for sensor in [self.sensor1, self.sensor2]:
            measurements = list(sensor.measurements)
            if measurements:
                distances = [m.distance_inches for m in measurements]
                print(f"\n{sensor.config.name} Statistics:")
                print(f"  Total measurements: {len(measurements)}")
                print(f"  Min distance: {min(distances):.2f} inches")
                print(f"  Max distance: {max(distances):.2f} inches")
                print(f"  Avg distance: {sum(distances)/len(distances):.2f} inches")
            else:
                print(f"\n{sensor.config.name}: No measurements")
    
    def save_to_csv(self, filename: str = None) -> str:
        """Save all measurements to CSV file.
        
        Args:
            filename: Optional filename. If None, auto-generates with timestamp.
            
        Returns:
            Path to saved CSV file
        """
        if filename is None:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = int(time.time())
            filename = os.path.join(data_dir, f'ultrasonic_data_{timestamp}.csv')
        
        all_measurements = self.get_all_measurements()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Sensor', 'Cycle', 'Pulse_Number', 'Distance_Inches', 
                           'Pulse_Width_us', 'Timestamp'])
            
            cycle = 0
            for sensor_name, measurements in all_measurements.items():
                for m in measurements:
                    if m.pulse_number == 1:
                        cycle += 1
                    writer.writerow([
                        m.sensor_name,
                        cycle,
                        m.pulse_number,
                        f"{m.distance_inches:.3f}",
                        f"{m.pulse_width_us:.1f}",
                        f"{m.timestamp:.6f}"
                    ])
        
        return filename


def main():
    """Example usage of the dual sensor controller."""
    
    # Define sensor configurations based on pinout
    # MB1300AE uses serial output (Pin 5 TX)
    sensor1_config = SensorConfig(
        name="Sensor_1",
        tx_pin=8,       # Physical pin 8 (UART0_TX) - connects to sensor Pin 5
        trigger_pin=16  # Physical pin 16 (GPIO136) - connects to sensor Pin 4
    )
    
    sensor2_config = SensorConfig(
        name="Sensor_2",
        tx_pin=10,      # Physical pin 10 (UART0_RX) - connects to sensor Pin 5
        trigger_pin=22  # Physical pin 22 (GPIO138) - connects to sensor Pin 4
    )
    
    # Create controller
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    # Set up callback for real-time processing
    def measurement_callback(measurement: PulseWidthMeasurement):
        # Show detailed output for each pulse
        print(f"  [{measurement.sensor_name}] Pulse {measurement.pulse_number:2d}: "
              f"{measurement.distance_inches:6.2f} in ({measurement.pulse_width_us:7.0f} μs)")
    
    controller.set_callbacks(measurement_callback)
    
    try:
        # Initialize GPIO
        controller.setup()
        
        # Start continuous capture (10 pulses per trigger, 0.2s between cycles)
        controller.start_continuous_capture(cycle_delay=0.2, pulses_per_trigger=10)
        
        # Run continuously until interrupted
        print("\nCapturing continuously... Press Ctrl+C to stop")
        print("="*60)
        
        while controller.is_running:
            time.sleep(1)
            # Print periodic status update
            if controller.cycle_count % 5 == 0 and controller.cycle_count > 0:
                print(f"\rCycles completed: {controller.cycle_count}", end='', flush=True)
        
    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nShutting down...")
        controller.stop_continuous_capture()
        
        # Save data to CSV
        print("\nSaving data to CSV...")
        csv_file = controller.save_to_csv()
        total_measurements = sum(len(m) for m in controller.get_all_measurements().values())
        print(f"Saved {total_measurements} measurements to: {csv_file}")
        
        # Print final statistics
        print("\n" + "="*60)
        print("FINAL STATISTICS")
        print("="*60)
        controller.print_statistics()
        
        controller.cleanup()
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
