# ESP32 acquisition firmware — implementation contract for A0.3

**Current A0.5 hardware.** J11 pin 1 is ground. Pad 2 is isolated and must be keyed with no wire. See the [A0.5 electrical review](../docs/A0_5_PROTECTION.md) for current values, fault cases, cable assembly and remaining tests.

**Implementation and hardware testing remain pending.** The selected board is
Kamen's Waveshare ESP32-S3-Nano. This directory is a specification, not runnable
firmware. See [the wiring/power sequence](../docs/POWER_HARNESS_A0_3.md).

Use native GPIO numbers: SCLK 5, MOSI 38, MISO 47, CS 21, DRDY 18, RESET 17,
START 10, PWDN 9, **IF_EN 6**. J11.11 takes Nano 3V3; J11.12 takes GPIO6.
Do not apply the old A0.2 cable or confuse Arduino Nano D labels with GPIO numbers.

## First implementation milestone

1. Boot with IF_EN LOW and all six host outputs LOW. Provide an explicit bench
   wake/configure command; conversions must not start automatically on reset.
2. After supply checks, enable buffers, release PWDN and verify the power-on
   interval and VCAP1 >1.1 V. Firmware cannot measure VCAP1 on this hardware.
   Use the bench procedure; a fixed delay is not proof of a valid startup.
3. Reset, issue SDATAC before register access, dump ID and registers, write the
   intended configuration and read it back. Allow reference settling. Check ID
   with `(id & 0x1f) == 0x1e`; revision bits are not a fixed 0x3E contract.
4. Acquire using SPI mode 1, MSB first, initially 1 MHz: 27 bytes per frame
   (3 status + 8 × 3 channel bytes). Validate the status prefix, sign-extend
   24-bit samples, and preserve unmodified frames/channel order.
5. Timestamp and count DRDY events at acquisition. Keep ISR work short, use a
   bounded queue, and count missed events, reads crossing a new DRDY and full
   queues. Report timing gaps as well: an ISR count cannot prove all physical
   edges were serviced. Move Wi-Fi/transmission to a separate task.
6. Add a Python recorder preserving raw codes, gain/reference metadata, device
   timestamps, arrival timestamps and loss/duplicate/reorder/session counts.
   Record raw data before any filtering; never silently interpolate it.
7. Build the pinned toolchain, test protocol corruption/sign boundaries/counter
   wrap, then measure acquisition with radio off/on. No build or physical test
   is claimed by A0.3.

## Initial register intent

These are design targets to implement and verify against TI's current tables,
not an already-running configuration. All channels use gain 12, SRB2 off;
MISC1.SRB1 stays off because the PCB directly joins the negative inputs.

| Register / mode | Target |
| --- | --- |
| CONFIG1 | 0x96: 250 SPS nominal |
| CONFIG2, internal test | 0xD0 |
| CONFIG2, short/external bench | 0xC0 |
| CONFIG3 | 0xE8: reference on, internal bias-reference selected, bias amplifier off |
| CH1SET–CH8SET, internal test | 0x55 |
| CH1SET–CH8SET, internal input short | 0x51 |
| CH1SET–CH8SET, external bench source | 0x50 |
| BIAS_SENSP/N, LOFF_SENSP/N, LOFF_FLIP | 0x00 |
| GPIO | 0x0F, inputs |
| MISC1, MISC2, CONFIG4 | 0x00 |

**Gain 12 is field 101, not 110 (gain 24).** Verify reserved/read-only bits with
appropriate masks during readback, and satisfy multi-byte command decode timing.
Bias and lead-off remain disabled for the first milestone. External test inputs
need a valid common-mode voltage; neither a person nor an input grounded outside
the PGA's common-mode range is the initial test source.

Primary reference: [TI ADS1299 datasheet](https://www.ti.com/lit/ds/symlink/ads1299.pdf),
register map, serial timing and startup sequence. The firmware will also need
pinned Espressif/Waveshare board settings and tested packet-format documentation.
