# ESP32 acquisition firmware

**Selected board: the user's Waveshare ESP32-S3-Nano. Firmware implementation is
pending.** Wiring and initial settings live in `hardware/interface.json`; see
[controller/electrode guide](../docs/CONTROLLER_AND_ELECTRODES.md).

Use native ESP32 GPIO numbers deliberately: SCLK 5 (Nano D2, remapped to avoid
SCK LED), MOSI 38, MISO 47, CS 21, DRDY 18, RESET 17, START 10, PWDN 9.
J11 pin 11 stays unwired. Do not use Arduino Nano D-pin numbers as raw GPIOs.

Required behavior: power-up/reset sequencing from the TI datasheet, SPI mode 1
(initially 1MHz), register readback, eight signed 24-bit samples per DRDY event,
an acquisition-side counter/timestamp, bounded buffering and explicit overruns.
Initial target 250SPS, gain 12; MISC1=0x00, SRB2 off (direct shared negative inputs).

Start with internal-test and shorted-input modes, bias/lead-off disabled.
Keep channel order, gain, rate, reference and scale in recorded metadata.
Radio transmission belongs in a separate task, not a long interrupt handler.
Test short/unplugged and unpowered cases; signal GPIOs can backfeed the AFE.
Use only electrode-disconnected bench tests until the final body-use review.
