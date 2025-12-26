# Ultrasonic Detection Model - MaxBotix MB1300

Orange Pi 5 project for capturing ultrasonic sensor data from two MaxBotix XL-MaxSonar-EZ MB1300 sensors with alternating triggering patterns.

## Hardware Requirements

- Orange Pi 5 single-board computer
- 2x MaxBotix XL-MaxSonar-EZ MB1300 ultrasonic sensors
- 5V power supply (adequate current for both sensors)
- Jumper wires for GPIO connections

## Pinout

See [PINOUT.md](PINOUT.md) for detailed connection diagram between Orange Pi 5 and the sensors.

**Quick Reference:**
- Sensor 1: PW→Pin12, RX→Pin16, 5V→Pin4, GND→Pin6
- Sensor 2: PW→Pin18, RX→Pin22, 5V→Pin2, GND→Pin9

## Software Requirements

```bash
# Install OPi.GPIO library for Orange Pi
pip install OPi.GPIO

# Or if using sudo
sudo pip install OPi.GPIO
```

## Project Files

- `ultrasonic_capture.py` - Main library with sensor control classes
- `examples.py` - Example usage scripts demonstrating various features
- `PINOUT.md` - Hardware connection documentation
- `data/` - Directory where CSV data files are automatically saved

## Quick Start

### Basic Usage

```python
from ultrasonic_capture import DualSensorController, SensorConfig

# Configure sensors
sensor1 = SensorConfig(name="Sensor_1", pw_pin=12, trigger_pin=16)
sensor2 = SensorConfig(name="Sensor_2", pw_pin=18, trigger_pin=22)

# Create controller
controller = DualSensorController(sensor1, sensor2)

try:
    controller.setup()
    
    # Take single measurement (10 pulses from each sensor)
    m1, m2 = controller.single_cycle(pulses_per_trigger=10)
    
    print(f"Sensor 1: {len(m1)} measurements")
    print(f"Sensor 2: {len(m2)} measurements")
    
finally:
    controller.cleanup()
```

### Continuous Capture (Runs Until Ctrl+C)

```python
# Start continuous alternating capture
controller.start_continuous_capture(
    cycle_delay=0.2,        # Delay between cycles
    pulses_per_trigger=10   # Capture 10 pulses per trigger
)

# Run continuously until interrupted
print("Press Ctrl+C to stop...")
try:
    while controller.is_running:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
    controller.stop_continuous_capture()
    controller.print_statistics()
```

## Running Examples

The `examples.py` file contains 5 different usage examples:

```bash
# Make executable
chmod +x examples.py

# Run examples (edit file to uncomment desired example)
python3 examples.py
```

### Available Examples:

1. **Single Measurement** - Take one measurement cycle
2. **Continuous with Callback** - Real-time data processing
3. **Save to CSV** - Record measurements to file
4. **Interactive Mode** - Manual start/stop control
5. **Custom Pulse Count** - Capture fewer than 10 pulses

## Features

- **Alternating Pattern**: Sensors trigger each other in sequence
- **10 Pulse Capture**: Each trigger captures 10 consecutive measurements
- **Pulse Width Measurement**: 147 μs per inch scaling
- **Thread-Safe**: Safe concurrent access to measurement data
- **Callbacks**: Real-time measurement processing
- **Statistics**: Built-in min/max/average calculations
- **CSV Export**: Save measurements for analysis

## How It Works

1. Controller triggers Sensor 1 by pulling RX pin LOW
2. Sensor 1 outputs 10 pulses on PW pin
3. Controller measures pulse widths and calculates distances
4. After delay, Controller triggers Sensor 2
5. Sensor 2 outputs 10 pulses on PW pin
6. **Process repeats continuously in an infinite loop until stopped (Ctrl+C)**

Each pulse width represents a distance measurement:
- **Pulse Width (μs) ÷ 147 = Distance (inches)**

## Measurement Range

- Minimum: ~2 inches (294 μs pulse width)
- Maximum: ~300 inches / 7.65m (44,100 μs pulse width)
- Resolution: 1 inch
- Update Rate: ~20 Hz typical

## Notes

- Ensure sensors are powered from stable 5V source
- Keep sensors at least 6 inches apart to avoid cross-talk
- GPIO pins must be run with appropriate permissions (may need sudo)
- Point sensors in slightly different directions if measuring same area

## Troubleshooting

**"OPi.GPIO not installed"**
```bash
pip install OPi.GPIO
```

**Permission denied errors**
```bash
sudo python3 ultrasonic_capture.py
```

**No measurements captured**
- Check wiring connections
- Verify 5V power is supplied to sensors
- Ensure nothing is blocking sensor detection range
- Check that sensors are spaced apart

**Inconsistent readings**
- Objects should be within 2-300 inch range
- Avoid highly absorbent materials (foam, fabric)
- Ensure stable mounting (vibration affects readings)

## License

MIT License - Feel free to use and modify for your projects.
