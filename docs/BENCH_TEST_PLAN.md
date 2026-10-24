# Bench test plan

**No person connected for any test in this document.** Internal self-test,
external signal generators, USB and oscilloscopes are bench tools here, not
equipment to attach while wearing electrodes. Record actual data; an unchecked
box is not a passed test.

## Before power

- Verify the manufactured revision against the schematic/BOM and inspect the
  ADS1299 orientation, solder bridges, polarity and regulator markings.
- Check battery polarity and resistance between each rail and GND. Capacitor
  charging can affect a resistance reading; do not interpret a momentary low
  value alone as a short.
- Confirm no electrode or person is connected. Start with a current-limited
  bench supply for electronics-only work. Set limits from the reviewed power
  budget, allowing capacitor inrush, rather than guessing a high current.

## Power and startup

- Apply the intended battery voltage and measure the 5 V and 3.3 V rails at U1.
  ADS1299 recommended AVDD-AVSS is 4.75-5.25 V and DVDD-DGND is 1.8-3.6 V;
  target the selected regulators' tighter specified ranges in this design.
- Check rail ripple and unexpected heating; vary supply voltage over the
  selected pack's actual range. Record controller/radio activity conditions.
- Keep digital control inputs low while supplies settle. Wait for the datasheet
  power-on interval AND VCAP1 >1.1 V before reset/configuration. Review exact
  PWDN/RESET timing against the datasheet rather than relying on a generic delay.
- Confirm the internal reference is near its expected 4.5 V value after enabling
  it and allowing it to settle. Verify VCAP nodes without loading them heavily.

## SPI and on-chip tests

- Select 3.3 V SPI mode 1, MSB first, initially at a conservative clock such as
  1 MHz. Verify setup/hold and command decode timing against the datasheet.
- Issue SDATAC before register writes/reads. Read ID; for the eight-channel
  ADS1299 the expected ID is 0x3E, subject to the datasheet's field definition.
  Read back every register written and log it.
- Configure all eight channels for the internal test source with bias and
  lead-off excitation disabled. Use the datasheet's test waveform amplitude,
  frequency and reference/gain equation to predict digital codes.
- Confirm 27 bytes per 8-channel frame: 24 status bits + 8 signed 24-bit values.
  Check the status header (1100), two's-complement sign extension, ordering and
  volts-per-code conversion.
- Check DRDY at the selected sample rate. The internal oscillator has tolerance;
  record the actual measured rate rather than assuming exact wall-clock 250 Hz.

## Noise, input behavior and RF interference

- Use the internal input-short mode, then a suitable external dummy-electrode
  fixture held at the valid common-mode voltage. Grounding inputs of a unipolar
  5 V design is not automatically a valid low-noise test condition.
- Record raw samples for at least 60 s per condition, report clipping, RMS noise,
  PSD and the exact bandwidth/filter used. Compare like-for-like against the
  datasheet's noise conditions. A 24-bit word is not 24 noise-free bits.
- Feed known differential signals, initially 10 Hz and 20/50/100 uV amplitude,
  superimposed on a valid common-mode voltage. Use a characterized attenuator
  or suitable isolated calibrator; an ordinary generator cannot necessarily
  produce accurate microvolt signals directly.
- Check gain/scale, phase consistency between channels, crosstalk and DC offset
  headroom. Test larger offsets and overload recovery within allowed limits.
- Repeat noise and test-signal captures with the ESP32 radio off and streaming.
  Check burst-correlated artifacts. Do not increase gain just to enlarge plots.
- A simulation must model sources it claims to test. `simulate_input.py` only
  checks one ideal RC path; it does not model the ADC or bias-loop stability.

## Timing and wireless integrity

- Assign an incrementing counter at acquisition, not on packet arrival. Record
  DRDY/acquisition timestamps and receiver arrival times separately.
- Stream for at least ten minutes. Report acquired, transmitted and received
  frame counts, losses, duplicates, reorder events and buffer overruns.
- If batching samples into a wireless packet, retain individual frame counters
  and timing. Never silently interpolate gaps in the raw recording.

## Before even considering scalp recordings

Close the body-use blockers with an experienced reviewer. Bench pass does not
prove body safety. Final recording must use an approved self-contained battery
arrangement and wireless communication, with chargers, programming cables and
mains-connected instruments disconnected. Battery operation alone is not the
review. A first biological validation would be a repeatable eyes-open/closed
alpha experiment before classifier or control claims.

## Measurement record template

For each test save: PCB revision and serial, firmware commit, instrument models,
supply and current limit, sample rate, gain, register dump, input fixture,
raw-data path, processing settings, expected result, observed result, pass/fail
reason and reviewer/date. Store recordings privately by default.
