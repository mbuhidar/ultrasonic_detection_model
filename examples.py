#!/usr/bin/env python3
"""
Example usage script demonstrating different ways to use the ultrasonic sensor controller.
"""

import time
import csv
from ultrasonic_capture import DualSensorController, SensorConfig, PulseWidthMeasurement


def example_single_measurement():
    """Example 1: Take a single measurement cycle."""
    print("=== Example 1: Single Measurement Cycle ===\n")
    
    sensor1_config = SensorConfig(name="Sensor_1", pw_pin=12, trigger_pin=16)
    sensor2_config = SensorConfig(name="Sensor_2", pw_pin=18, trigger_pin=22)
    
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    try:
        controller.setup()
        
        # Take one measurement cycle (10 pulses each)
        measurements1, measurements2 = controller.single_cycle(pulses_per_trigger=10)
        
        print(f"\nSensor 1 captured {len(measurements1)} measurements")
        print(f"Sensor 2 captured {len(measurements2)} measurements")
        
        # Display some results
        if measurements1:
            avg_dist = sum(m.distance_inches for m in measurements1) / len(measurements1)
            print(f"Sensor 1 average distance: {avg_dist:.2f} inches")
            
        if measurements2:
            avg_dist = sum(m.distance_inches for m in measurements2) / len(measurements2)
            print(f"Sensor 2 average distance: {avg_dist:.2f} inches")
            
    finally:
        controller.cleanup()


def example_continuous_with_callback():
    """Example 2: Continuous capture with real-time callback."""
    print("\n=== Example 2: Continuous Capture with Callback ===\n")
    
    sensor1_config = SensorConfig(name="Sensor_1", pw_pin=12, trigger_pin=16)
    sensor2_config = SensorConfig(name="Sensor_2", pw_pin=18, trigger_pin=22)
    
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    # Define custom callback for real-time processing
    def my_callback(measurement: PulseWidthMeasurement):
        # Only print every 5th measurement to reduce output
        if measurement.pulse_number % 5 == 0:
            print(f"[{measurement.sensor_name}] Pulse {measurement.pulse_number}: "
                  f"{measurement.distance_inches:.2f} inches")
    
    try:
        controller.setup()
        controller.set_callbacks(my_callback)
        
        # Start continuous capture
        controller.start_continuous_capture(cycle_delay=0.3, pulses_per_trigger=10)
        
        # Run continuously until interrupted
        print("Capturing continuously...")
        while controller.is_running:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
    finally:
        controller.stop_continuous_capture()
        controller.cleanup()


def example_save_to_csv():
    """Example 3: Continuous capture and save to CSV file."""
    print("\n=== Example 3: Save Measurements to CSV ===\n")
    
    sensor1_config = SensorConfig(name="Sensor_1", pw_pin=12, trigger_pin=16)
    sensor2_config = SensorConfig(name="Sensor_2", pw_pin=18, trigger_pin=22)
    
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    try:
        controller.setup()
        
        # Capture data continuously
        controller.start_continuous_capture(cycle_delay=0.2, pulses_per_trigger=10)
        print("Capturing continuously... Press Ctrl+C to stop and save data")
        
        # Run until interrupted
        while controller.is_running:
            time.sleep(1)
            if controller.cycle_count % 10 == 0 and controller.cycle_count > 0:
                print(f"\rCycles: {controller.cycle_count}", end='', flush=True)
        
        controller.stop_continuous_capture()
        print("\n\nSaving data...")
        
        # Save to CSV
        csv_filename = f"ultrasonic_data_{int(time.time())}.csv"
        all_measurements = controller.get_all_measurements()
        
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Sensor', 'Cycle', 'Pulse_Number', 'Distance_Inches', 
                           'Pulse_Width_us', 'Timestamp'])
            
            cycle = 0
            for sensor_name, measurements in all_measurements.items():
                for i, m in enumerate(measurements):
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
        
        print(f"\nData saved to {csv_filename}")
        
        # Print summary
        total_measurements = sum(len(m) for m in all_measurements.values())
        print(f"Total measurements saved: {total_measurements}")
        controller.print_statistics()
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        controller.stop_continuous_capture()
        controller.cleanup()


def example_interactive_mode():
    """Example 4: Interactive mode - start/stop with user input."""
    print("\n=== Example 4: Interactive Mode ===\n")
    
    sensor1_config = SensorConfig(name="Sensor_1", pw_pin=12, trigger_pin=16)
    sensor2_config = SensorConfig(name="Sensor_2", pw_pin=18, trigger_pin=22)
    
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    try:
        controller.setup()
        
        print("Commands:")
        print("  's' - Start continuous capture")
        print("  'x' - Stop continuous capture")
        print("  'o' - Take one measurement cycle")
        print("  'r' - Show statistics")
        print("  'q' - Quit")
        print()
        
        while True:
            cmd = input("Enter command: ").strip().lower()
            
            if cmd == 's':
                controller.start_continuous_capture(cycle_delay=0.3, pulses_per_trigger=10)
                print("Capture started")
                
            elif cmd == 'x':
                controller.stop_continuous_capture()
                print("Capture stopped")
                
            elif cmd == 'o':
                print("Taking single measurement...")
                m1, m2 = controller.single_cycle(pulses_per_trigger=10)
                print(f"Captured {len(m1)} from Sensor 1, {len(m2)} from Sensor 2")
                
            elif cmd == 'r':
                controller.print_statistics()
                
            elif cmd == 'q':
                break
                
            else:
                print("Invalid command")
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        controller.stop_continuous_capture()
        controller.cleanup()


def example_custom_pulse_count():
    """Example 5: Capture different number of pulses per trigger."""
    print("\n=== Example 5: Custom Pulse Count ===\n")
    
    sensor1_config = SensorConfig(name="Sensor_1", pw_pin=12, trigger_pin=16)
    sensor2_config = SensorConfig(name="Sensor_2", pw_pin=18, trigger_pin=22)
    
    controller = DualSensorController(sensor1_config, sensor2_config)
    
    try:
        controller.setup()
        
        # Capture only first 5 pulses instead of all 10
        print("Capturing first 5 pulses per trigger...")
        measurements1, measurements2 = controller.single_cycle(pulses_per_trigger=5)
        
        print(f"\nSensor 1: {len(measurements1)} measurements")
        for m in measurements1:
            print(f"  Pulse {m.pulse_number}: {m.distance_inches:.2f} inches")
            
        print(f"\nSensor 2: {len(measurements2)} measurements")
        for m in measurements2:
            print(f"  Pulse {m.pulse_number}: {m.distance_inches:.2f} inches")
            
    finally:
        controller.cleanup()


if __name__ == "__main__":
    print("MaxBotix MB1300 Dual Sensor Examples")
    print("=" * 50)
    
    # Uncomment the example you want to run:
    
    example_single_measurement()
    # example_continuous_with_callback()
    # example_save_to_csv()
    # example_interactive_mode()
    # example_custom_pulse_count()
