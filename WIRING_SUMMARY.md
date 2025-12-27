# MB1300AE Wiring Configuration Summary

## CRITICAL: Pin 1 (BW) Must Be Connected HIGH

The MB1300AE Pin 1 (BW - Bandwidth) controls the output mode:

- **Pin 1 = HIGH (3.3V or 5V)**: ASCII serial output on Pin 5 → `"Rxxx\r"` format ✓
- **Pin 1 = LOW (GND)**: Serial output disabled ✗
- **Pin 1 = FLOATING**: Binary analog data (not ASCII) ✗

## Correct Wiring Configuration

### Sensor 1 (MB1300AE #1)
```
MB1300 Pin 1 (BW)  → Orange Pi Pin 1 (3.3V) or Pin 17 (3.3V)  [REQUIRED FOR ASCII]
MB1300 Pin 5 (TX)  → Orange Pi Pin 16 (UART4_RX_M0)
MB1300 Pin 6 (+5V) → Orange Pi Pin 4 (5V Power)
MB1300 Pin 7 (GND) → Orange Pi Pin 6 (Ground)
```

### Sensor 2 (MB1300AE #2)
```
MB1300 Pin 1 (BW)  → Orange Pi Pin 1 (3.3V) or Pin 17 (3.3V)  [REQUIRED FOR ASCII]
MB1300 Pin 5 (TX)  → Orange Pi Pin 21 (UART3_RX_M0)
MB1300 Pin 6 (+5V) → Orange Pi Pin 2 (5V Power)
MB1300 Pin 7 (GND) → Orange Pi Pin 9 (Ground)
```

**Note:** Both sensors' Pin 1 can share the same 3.3V pin (Pin 1 or Pin 17).

## Visual Diagram

```
Orange Pi 5                          MaxBotix MB1300AE
26-Pin Header                        Sensor Pinout
=============                        ==============

Pin 1  (3.3V) ----┬----------------> Pin 1 (BW - Mode Select)  ← BOTH SENSORS
Pin 17 (3.3V) ----┘                  

Pin 4  (5V)   ------------------->   Pin 6 (+5V)               ← Sensor 1
Pin 6  (GND)  ------------------->   Pin 7 (GND)               ← Sensor 1
Pin 16 (UART4_RX) <---------------   Pin 5 (TX Serial Out)     ← Sensor 1

Pin 2  (5V)   ------------------->   Pin 6 (+5V)               ← Sensor 2
Pin 9  (GND)  ------------------->   Pin 7 (GND)               ← Sensor 2
Pin 21 (UART3_RX) <---------------   Pin 5 (TX Serial Out)     ← Sensor 2
```

## What You Should See

### With Pin 1 Connected to 3.3V (CORRECT)
```
Received: 'R123\r' (5 bytes)    ← ASCII format
Received: 'R124\r' (5 bytes)
Received: 'R125\r' (5 bytes)
```

### With Pin 1 Floating or Disconnected (WRONG)
```
Received: '+\x00\x06YY\x1e\x00' (7 bytes)    ← Binary data
Received: '+\x00\x06��\x1e\x00' (7 bytes)
```

## Testing Steps

1. **Connect Pin 1 (BW) to 3.3V** on both sensors
2. **Reboot** to ensure UART overlays are loaded
3. **Run test**: `python3 test_uart_raw.py`
4. **Verify ASCII output**: Should see `"Rxxx\r"` format, not binary

## Files Updated

- ✓ `PINOUT.md` - Updated wiring tables and diagrams
- ✓ `ultrasonic_uart.py` - Added Pin 1 requirement warnings
- ✓ `test_uart_raw.py` - Updated diagnostic messages
- ✓ `BW_PIN_CONFIG.md` - Detailed Pin 1 behavior explanation
- ✓ `WIRING_SUMMARY.md` - This file

## Next Steps

1. **Hardware**: Connect both sensors' Pin 1 (BW) to Orange Pi Pin 1 (3.3V)
2. **Test**: Run `python3 test_uart_raw.py` to verify ASCII output
3. **Capture**: Run `python3 ultrasonic_uart.py` for data collection

If you still see binary data after connecting Pin 1 to 3.3V, try 5V instead (MB1300 is 5V tolerant).
