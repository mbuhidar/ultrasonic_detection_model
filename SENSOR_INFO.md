# MaxBotix MB1300 vs MB1200 Clarification

## IMPORTANT: Sensor Model Identification

The MaxBotix XL-MaxSonar series has different variants:

### MB1200 Series (EZ - Easy)
- **Pin 2 (PW)**: Digital Pulse Width output
- Can be read directly with GPIO
- Scale: 58μs per cm (147μs per inch)

### MB1300 Series (AE - Acoustic Envelope)  
- **Pin 2 (AN)**: Analog voltage waveform output
- **Cannot be read with digital GPIO!**
- Requires ADC (Analog-to-Digital Converter)
- **Pin 5 (TX)**: Serial output (digital, can use this instead)

## Your Sensor: MB1300

According to your description, you have **MB1300** sensors.

### Available Options:

1. **Use Serial Output (Recommended for MB1300)**
   - Connect Pin 5 (TX) instead of Pin 2 (PW/AN)
   - Read serial data at 9600 baud
   - Get "Rxxx\r" format (R + distance in mm)

2. **Add ADC Hardware**
   - Use ADS1115 or MCP3008 ADC module
   - Connect MB1300 Pin 2 (AN) to ADC
   - Process analog waveform (complex)

3. **Switch to MB1200 Series**
   - MB1200 has digital pulse width on Pin 2
   - Direct GPIO compatible
   - Easier to use

## Recommended Solution: Serial Output

The easiest solution for MB1300 is to use the serial output on Pin 5 (TX).

Would you like me to:
1. Rewrite the code to use serial output (Pin 5 TX)?
2. Or verify if you actually have MB1200 (EZ) sensors instead?
