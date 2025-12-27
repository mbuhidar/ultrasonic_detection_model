# MB1300AE Pin 1 (BW) Configuration

According to MaxBotix documentation:

## Pin 1 (BW) - Bandwidth / Output Mode Select

**Pin 1 (BW) controls the output format:**

1. **BW = LOW (connected to GND)**
   - Disables serial output on Pin 5
   - Pin 2 outputs analog envelope (wideband)
   
2. **BW = OPEN/FLOATING**
   - Default mode
   - Pin 2 outputs analog envelope
   - Pin 5 MAY output serial (sensor-dependent)
   
3. **BW = HIGH (connected to VCC or 5V)**
   - Enables serial ASCII output on Pin 5
   - Format: "Rxxx\r" where xxx is centimeters
   - Pin 2 outputs standard analog voltage

## Solution for Serial Output

**To ensure Pin 5 outputs ASCII serial data:**
Connect Pin 1 (BW) to **5V** (or to a GPIO set HIGH)

## Current Issue

The binary data received suggests:
- Pin 1 might be floating (not definitively HIGH)
- Sensor may be outputting analog waveform data
- Need to explicitly pull Pin 1 HIGH

## Wiring Fix

**Sensor 1:**
- Pin 1 (BW) → Orange Pi Pin 1 (3.3V) or Pin 4 (5V)
- Pin 5 (TX) → Orange Pi Pin 16 (UART4_RX)

**Sensor 2:**
- Pin 1 (BW) → Orange Pi Pin 2 (5V) or Pin 17 (3.3V)
- Pin 5 (TX) → Orange Pi Pin 21 (UART3_RX)

**Note:** 3.3V should be sufficient to pull BW HIGH. MB1300 is 5V tolerant.
