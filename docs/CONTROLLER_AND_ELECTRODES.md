# Owned hardware and interface — A0.3

**Use the Waveshare ESP32-S3-Nano already owned by Kamen. No new controller is needed.**
This is an external controller connected by short wires to J11, not a module
soldered into the EEG PCB. Keep its antenna and switching regulator away from
input/reference circuitry. None of these MCU choices establishes EEG noise performance.

| Owned board | Assessment for this prototype |
| --- | --- |
| Waveshare ESP32-S3-Nano | Selected: accessible headers, spare GPIO, 16 MB flash and 8 MB PSRAM; ample room for buffering and later firmware |
| ESP32 DevKitC-style / ESP-WROOM-32 | Adequate for acquisition; exact clone/power circuit would need identification; older board is a useful spare |
| Waveshare ESP32-S3-Zero | Also adequate; compact packaging is less important than accessible wiring for the first prototype |
| Seeed XIAO ESP32S3 | Also capable and attractive for a smaller wearable revision; fewer exposed pins leave less expansion margin |

At 250 samples/s/channel the ADS1299 returns 27 bytes per frame, or 6,750 bytes/s
before packet metadata. Large PSRAM is convenient, not a requirement. Acquire
into bounded internal-memory buffers; do not assume PSRAM is suitable for every
DMA allocation. Send packets from a separate task and record overruns. The MCU
receives digital samples over SPI; its built-in ADC is not used for EEG.

## Wiring contract

The source of truth is `hardware/interface.json`. Board labels are not raw GPIO
numbers. ESP-IDF uses the GPIO column. If using Arduino's Nano ESP32 board profile,
select native GPIO numbering or translate deliberately; do not mix the two schemes.

**A0.3 cable change: pin 11 = Nano 3V3, pin 12 = GPIO6 enable (formerly GND).**

| J11 pin | Net | Nano label | Native GPIO |
| --- | --- | --- | --- |
| 1 | GND | GND | — |
| 2 | GND | GND | — |
| 3 | HOST_SPI_SCLK | D2 | 5 |
| 4 | HOST_SPI_MOSI | D11 | 38 |
| 5 | HOST_SPI_MISO | D12 | 47 |
| 6 | HOST_ADS_CS_N | D10 | 21 |
| 7 | HOST_ADS_DRDY_N | D9 | 18 |
| 8 | HOST_ADS_RESET_N | D8 | 17 |
| 9 | HOST_ADS_START | D7 | 10 |
| 10 | HOST_ADS_PWDN_N | D6 | 9 |
| 11 | HOST_3V3 | 3V3 | — |
| 12 | IF_EN | D3 | 6 |

SCLK is deliberately remapped to D2/GPIO5 using the GPIO matrix, rather than the
board's usual D13/GPIO48, which also drives the onboard SCK LED. Explicitly set
all SPI pins in firmware. This map avoids native USB GPIO19/20, strapping pins,
flash/PSRAM, RGB LED pins and UART0. Keep the LED idle during acquisition.

Use SPI mode 1 and initially 1 MHz. One ideal frame takes 216 us of the 4 ms
sample period; command timing, scheduling and radio interference still need testing.
Initial target gain is 12, eight enabled channels, 250 SPS. The schematic connects
REF_FILTERED directly to all eight INxN pins: MISC1=0x00 and CHnSET.SRB2=0.
Start with internal test/shorted-input modes, bias and lead-off disabled.
Verify register readback and TI startup timing before enabling conversions.
U4/U5 provide power-off tolerant buffering with separate supply ports; keep IF_EN LOW
until supplies and GPIO states are established. Analog injection and brownout still
need physical tests. These buffers are not galvanic isolation.

## Power concept

A six-AA alkaline pack is the current candidate, with **7.2–10.2 V assumed at
its terminals under operating conditions** for calculations. This is not a
measured battery lifetime or automatic low-voltage cutoff. The pack feeds two
branches: the AFE through J12/F1/D10/SW1 and the Nano through its own protected,
switched branch to **VIN**. Do not connect this pack to Nano 3V3 or VBUS.

Waveshare documents 6–21 V at VIN and an onboard MP2322 buck regulator; the
candidate battery range is compatible in principle, so a separate 5 V buck is
not assumed necessary. The [A0.3 harness candidate](POWER_HARNESS_A0_3.md) now defines the branch fuses,
master switch, polarity diode and power-order test plan. Actual holder/switch
selection, inrush, voltage drop and radio-burst behavior remain to be verified. F1's 100 mA hold
rating is for the AFE branch only and must not carry the Nano radio load.
The AFE 5 V and 3.3 V LDOs supply the ADC and the AFE-side buffer ports only. All returns are common;
this is **not galvanic isolation**.

USB is for programming/bench testing with every electrode disconnected from a
person. The future recording arrangement is battery-only and wireless with USB,
chargers and mains-connected instruments disconnected, after the final body-use
review. The current schematic is not approved for body connection.

## Electrode set

The user supplied the Sino-k product link with variant **42757052924081**.
The page lists **SGE117DN**, ten gold-plated cup electrode leadwires. Allocate
8 to CH1–CH8, 1 to REF and 1 to BIAS. These ten physical contacts require only
eight measurement channels and one ADS1299. BIAS is an output, not protective
earth; REF is the shared measurement reference, not the PCB ground connection.

The user identifies the plugs as probably 1.5 mm touchproof DIN 42802. A0.3
uses P1 Technologies 36619 / 8R003661901F right-angle PCB jacks at J1-J10.
The old pin headers are gone. Confirm actual plug mating, the candidate drill
pattern and enclosure access with a sample before fabrication; see the
[A0.3 socket worksheet](REVIEW_FIXES_A0_3.md). Lead colors do not define
scalp positions: label and verify each lead-to-channel assignment.

The linked description says “cable diameter:1.9m”; that is ambiguous and is not
used as a verified length, diameter or cable-capacitance value in calculations.

## Primary sources checked 2026-11-15

- [Waveshare Nano documentation and pinout](https://docs.waveshare.com/ESP32-S3-Nano)
- [Waveshare board schematic](https://files.waveshare.com/wiki/ESP32-S3-Nano/ESP32-S3-Nano-Schematic.pdf)
- [Espressif SPI master / GPIO matrix](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/spi_master.html)
- [Sino-k supplied product](https://www.sinokmed.com/collections/ecg-cables/products/eeg-cable-10-leadwires-golden-plated-cup-electrodes?variant=42757052924081)
- [TI ADS1299 datasheet](https://www.ti.com/lit/ds/symlink/ads1299.pdf)

Board comparison is an engineering judgment using the user's owned-board list
and verified selected-board documentation; it is not a measured noise ranking.
