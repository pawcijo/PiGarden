Soil Moisture Sensor Calibration
=========================================

Calibrating the SEN0193 soil moisture sensor ensures accurate readings by mapping the sensor's raw output to real-world moisture levels. Follow these steps:

1. Setup:
   - Connect the sensor to the ADS7830 ADC and interface it with your microcontroller (e.g., Raspberry Pi).

2. Dry Soil Reading:
   - Place the sensor in dry soil, wait for the value to stabilize, and record the ADC output (Vdry).

3. Wet Soil Reading:
   - Insert the sensor into moist soil, allow it to stabilize, and record the ADC output (Vwet).

4. (Optional) Water Reading:
   - Submerge the sensor in water to determine the 100% moisture value (Vwater).

#### Formula:
Map the ADC values to a percentage:

$\text{Moisture (\%)} = \left( \frac{V_{\text{dry}} - V_{\text{current}}}{V_{\text{dry}} - V_{\text{wet}}} \right) \times 100$

Clamp the result between 0% and 100%.

#### Example Output:
```
- Dry Soil: 193
- Wet Soil: 100
- Water: 100
```
Use these values to fine-tune your soil monitoring system.
Check the calibration script for implementation!