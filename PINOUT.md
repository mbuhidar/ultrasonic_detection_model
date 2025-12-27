# Orange Pi 5 GPIO Pinout Reference

## Orange Pi 5 Complete 26-Pin Header Pinout

**Board**: Orange Pi 5 (RK3588S SoC)  
**Header**: 26-pin 2.54mm pitch  
**GPIO Logic Level**: 3.3V  
**Power Pins**: 5V and 3.3V available

### Complete Pin Mapping Table

| Physical Pin | Function | GPIO Chip | GPIO# | Alt Functions | Direction |
|--------------|----------|-----------|-------|---------------|-----------|
| 1 | 3.3V Power | - | - | Power | - |
| 2 | 5V Power | - | - | Power | - |
| 3 | I2C3_SDA_M1 | GPIO1_A4 | 36 | I2C3 SDA | I/O |
| 4 | 5V Power | - | - | Power | - |
| 5 | I2C3_SCL_M1 | GPIO1_A3 | 35 | I2C3 SCL | I/O |
| 6 | Ground | - | - | Ground | - |
| 7 | PWM1_M1 | GPIO1_B2 | 42 | PWM1 | Output |
| 8 | UART0_TX | GPIO0_B5 | 13 | UART0 TX | Output |
| 9 | Ground | - | - | Ground | - |
| 10 | UART0_RX | GPIO0_B6 | 14 | UART0 RX | Input |
| 11 | GPIO4_A3 | GPIO4_A3 | 131 | GPIO | I/O |
| 12 | GPIO4_A4 | GPIO4_A4 | 132 | GPIO, SPI4_CLK | I/O |
| 13 | GPIO4_B3 | GPIO4_B3 | 139 | GPIO | I/O |
| 14 | Ground | - | - | Ground | - |
| 15 | GPIO4_A5 | GPIO4_A5 | 133 | GPIO, SPI4_MOSI | I/O |
| 16 | UART4_RX_M0 | GPIO4_B0 | 136 | UART4 RX, GPIO, SPI4_CS0 | Input |
| 17 | 3.3V Power | - | - | Power | - |
| 18 | GPIO4_B1 | GPIO4_B1 | 137 | GPIO, SPI4_MISO | I/O |
| 19 | SPI0_MOSI | GPIO1_B3 | 43 | SPI0 MOSI | Output |
| 20 | Ground | - | - | Ground | - |
| 21 | UART3_RX_M0 | GPIO1_B4 | 44 | UART3 RX, SPI0 MISO | Input |
| 22 | GPIO4_B2 | GPIO4_B2 | 138 | GPIO, SPI4_CS1 | I/O |
| 23 | SPI0_CLK | GPIO1_B1 | 41 | SPI0 CLK | Output |
| 24 | SPI0_CS0 | GPIO1_B5 | 45 | SPI0 CS0 | Output |
| 25 | Ground | - | - | Ground | - |
| 26 | SPI0_CS1 | GPIO1_B6 | 46 | SPI0 CS1 | Output |

### Pin Summary

**Power Pins:**
- Pin 1, 17: 3.3V (max 500mA combined)
- Pin 2, 4: 5V (depends on power supply capacity)

**Ground Pins:**
- Pin 6, 9, 14, 20, 25

**Available GPIO Pins for General Use:**
- Pin 11: GPIO4_A3 (131)
- Pin 12: GPIO4_A4 (132)
- Pin 13: GPIO4_B3 (139)
- Pin 15: GPIO4_A5 (133)
- Pin 16: GPIO4_B0 (136)
- Pin 18: GPIO4_B1 (137)
- Pin 22: GPIO4_B2 (138)

**Communication Interfaces:**
- I2C3: Pin 3 (SDA), Pin 5 (SCL)
- UART0: Pin 8 (TX), Pin 10 (RX)
- UART3: Pin 21 (RX_M0) - **Used for Sensor 2**
- UART4: Pin 16 (RX_M0) - **Used for Sensor 1**
- SPI0: Pin 19 (MOSI), Pin 21 (MISO), Pin 23 (CLK), Pin 24 (CS0), Pin 26 (CS1)
- SPI4 (alternate): Pin 12 (CLK), Pin 15 (MOSI), Pin 16 (CS0), Pin 18 (MISO), Pin 22 (CS1)
- PWM1: Pin 7

### Visual Pin Layout (Top View)

```
Orange Pi 5 - 26 Pin Header (2x13)
=====================================

    3.3V  [1]  [2]  5V         ← Sensor 2 Power
I2C3_SDA  [3]  [4]  5V         ← Sensor 1 Power
I2C3_SCL  [5]  [6]  GND        ← Sensor 1 Ground
    PWM1  [7]  [8]  UART0_TX
     GND  [9]  [10] UART0_RX   ← Sensor 2 Ground
GPIO4_A3 [11]  [12] GPIO4_A4
GPIO4_B3 [13]  [14] GND
GPIO4_A5 [15]  [16] UART4_RX   ← Sensor 1 Serial Input
    3.3V [17]  [18] GPIO4_B1
SPI0_MOSI[19]  [20] GND
UART3_RX [21]  [22] GPIO4_B2   ← Sensor 2 Serial Input
 SPI0_CLK[23]  [24] SPI0_CS0
     GND [25]  [26] SPI0_CS1

Pin 1 is closest to the edge of the board
```

### GPIO Numbering Formula

For RK3588S GPIO chips:
- **GPIO0**: Base 0
- **GPIO1**: Base 32  
- **GPIO2**: Base 64
- **GPIO3**: Base 96
- **GPIO4**: Base 128

**Formula**: `GPIO_Number = Bank_Base + (Group × 8) + Pin`
- **Groups**: A=0, B=1, C=2, D=3
- **Pins**: 0-7 within each group

**Examples:**
- GPIO4_A4 = 128 + (0×8) + 4 = **132**
- GPIO4_B0 = 128 + (1×8) + 0 = **136**
- GPIO4_B1 = 128 + (1×8) + 1 = **137**
- GPIO4_B2 = 128 + (1×8) + 2 = **138**
- GPIO1_A3 = 32 + (0×8) + 3 = **35**

---

## MaxBotix MB1300 Sensor Connection Guide

### Sensor Overview
- **Model**: MaxBotix XL-MaxSonar-EZ MB1300
- **Voltage**: 5V DC
- **Range**: 0-7.65m (0-300 inches)
- **Beam Pattern**: 10 degrees

## Sensor Wiring Configuration

### Sensor 1 (MB1300AE #1)
| MB1300 Pin | Function | Orange Pi 5 Pin | UART/GPIO |
|------------|----------|-----------------|-----------||
| Pin 1 (BW) | Mode Select | Pin 1 or 17 | **3.3V (Required for ASCII serial)** |
| Pin 2 (AN) | Analog Envelope | - | Not Used (requires ADC) |
| Pin 3 (AN) | Analog Voltage | - | Not Used (requires ADC) |
| Pin 4 (RX) | Trigger Input | Pin 11 or 13 | GPIO (optional) |
| Pin 5 (TX) | Serial Output | Pin 16 | **UART4_RX_M0** |
| Pin 6 (+5V)| Power Supply | Pin 4 | 5V Power |
| Pin 7 (GND)| Ground | Pin 6 | Ground |

### Sensor 2 (MB1300AE #2)
| MB1300 Pin | Function | Orange Pi 5 Pin | UART/GPIO |
|------------|----------|-----------------|-----------||
| Pin 1 (BW) | Mode Select | Pin 1 or 17 | **3.3V (Required for ASCII serial)** |
| Pin 2 (AN) | Analog Envelope | - | Not Used (requires ADC) |
| Pin 3 (AN) | Analog Voltage | - | Not Used (requires ADC) |
| Pin 4 (RX) | Trigger Input | Pin 22 | GPIO (optional) |
| Pin 5 (TX) | Serial Output | Pin 21 | **UART3_RX_M0** |
| Pin 6 (+5V)| Power Supply | Pin 2 | 5V Power |
| Pin 7 (GND)| Ground | Pin 9 | Ground |

## Connection Diagram
```
Orange Pi 5                    MaxBotix MB1300AE Sensor 1
-----------                    --------------------------
Pin 1  (3.3V)     ---------->  Pin 1 (BW - Mode Select)
Pin 4  (5V)       ---------->  Pin 6 (+5V)
Pin 6  (GND)      ---------->  Pin 7 (GND)
Pin 16 (UART4_RX) <----------  Pin 5 (TX - Serial Out)

Orange Pi 5                    MaxBotix MB1300AE Sensor 2
-----------                    --------------------------
Pin 17 (3.3V)     ---------->  Pin 1 (BW - Mode Select)
Pin 2  (5V)       ---------->  Pin 6 (+5V)
Pin 9  (GND)      ---------->  Pin 7 (GND)
Pin 21 (UART3_RX) <----------  Pin 5 (TX - Serial Out)

Note: Both sensors' Pin 1 (BW) can share Orange Pi Pin 1 (3.3V) if needed.
      Sensor Pin 4 (RX) can be left floating for continuous ranging mode.
```

### Pins Used Summary

**Sensor 1:**
- 3.3V (BW Mode): Physical Pin 1 or 17
- 5V Power: Physical Pin 4
- Ground: Physical Pin 6
- Serial Input (UART4_RX_M0): Physical Pin 16
- Optional Trigger Output: Pin 11 or 13 (GPIO, if using triggered mode)

**Sensor 2:**
- 3.3V (BW Mode): Physical Pin 1 or 17 (can share with Sensor 1)
- 5V Power: Physical Pin 2
- Ground: Physical Pin 9
- Serial Input (UART3_RX_M0): Physical Pin 21
- Optional Trigger Output: Pin 22 (GPIO, if using triggered mode)

### Available Unused GPIO Pins

If you need to connect additional sensors or devices, these GPIO pins are available:

| Physical Pin | GPIO Chip | GPIO# | Notes |
|--------------|-----------|-------|-------|
| 11 | GPIO4_A3 | 131 | General purpose I/O |
| 13 | GPIO4_B3 | 139 | General purpose I/O |
| 15 | GPIO4_A5 | 133 | Can also be SPI4_MOSI |
| 7 | GPIO1_B2 | 42 | Can also be PWM1 |

**Additional Power Available:**
- Pin 2: 5V (used by Sensor 2)
- Pin 4: 5V (used by Sensor 1)
- Pin 1, 17: 3.3V (max 500mA combined)

**Additional Ground Pins:**
- Pin 14, 20, 25

## Serial Output Specifications
- **Baud Rate**: 9600, 8 data bits, no parity, 1 stop bit (8N1)
- **Format**: Rxxx\r where xxx is distance in centimeters
- **Example**: "R123\r" = 123cm = 48.4 inches
- **Update Rate**: ~10 Hz (10 readings per second)
- **Range Output**: 30cm to 765cm (12 in to 300 in)

## Triggering
- RX pin (Pin 4) is internally pulled HIGH
- Sensor ranges continuously when RX is HIGH or floating
- **Hold RX LOW to stop ranging**
- **Pulse RX HIGH for 20+ μs to trigger a single reading**
- After trigger, sensor outputs distance via serial on Pin 5 (TX)
- System runs in continuous loop until manually stopped (Ctrl+C)

## Notes
- **Orange Pi 5 has 26 pins** (not 40 like Raspberry Pi)
- **RK3588S SoC** (not RK3588 - the "S" variant is used in Orange Pi 5)
- Ensure sensors are powered from a stable 5V source
- Orange Pi 5 GPIO operates at **3.3V logic level**
- MB1300 is 5V tolerant on RX input (safe to connect to 3.3V GPIO)
- PW output from MB1300 is compatible with 3.3V logic input on Orange Pi 5
- Keep sensors at least 6 inches apart to avoid cross-talk
- Point sensors in slightly different directions if measuring same area

## Important: GPIO Pin Numbering Modes

The OPi.GPIO library supports two numbering modes:

### 1. BOARD Mode (Physical Pin Numbers) - **USED IN THIS PROJECT**
```python
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN)  # Uses physical pin number 12
```

### 2. BCM/SOC Mode (Chip GPIO Numbers)
```python
GPIO.setmode(GPIO.BCM)  # or GPIO.SOC
GPIO.setup(132, GPIO.IN)  # Uses GPIO chip number 132 (GPIO4_A4)
```

**This project uses BOARD mode**, so all pin references use the physical pin numbers (1-26) printed on the board.

## RK3588S GPIO Chip Mapping Reference

### GPIO Number Calculation
RK3588S has 5 GPIO banks (GPIO0 through GPIO4). Each bank has up to 4 groups (A, B, C, D), and each group has 8 pins (0-7).

**Formula**: `GPIO_Number = Bank_Base + (Group × 8) + Pin`

**Bank Base Numbers:**
- GPIO0: 0
- GPIO1: 32
- GPIO2: 64
- GPIO3: 96
- GPIO4: 128

**Group Numbers:**
- A = 0
- B = 1
- C = 2
- D = 3

**Examples:**
- GPIO4_A4 = 128 + (0 × 8) + 4 = **132**
- GPIO4_B0 = 128 + (1 × 8) + 0 = **136**
- GPIO4_B1 = 128 + (1 × 8) + 1 = **137**
- GPIO4_B2 = 128 + (1 × 8) + 2 = **138**
- GPIO1_A3 = 32 + (0 × 8) + 3 = **35**
- GPIO1_A4 = 32 + (0 × 8) + 4 = **36**

This is useful if you need to control GPIO pins using sysfs (/sys/class/gpio/) or other low-level interfaces.
