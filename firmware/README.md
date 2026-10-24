# ESP32 acquisition firmware

Implementation pending. Select the actual ESP32 development board before
choosing GPIOs; J11 on the acquisition PCB is a generic interface.

Required behavior: correct power-up/reset sequencing, SPI mode 1, register
readback, all eight signed 24-bit samples per DRDY event, an acquisition-side
counter/timestamp, bounded buffering and explicit overrun/loss reporting.
Do not run wireless transmission inside a long acquisition interrupt handler.

Start with internal test and shorted-input modes, bias/lead-off disabled.
Keep gain, rate, channel order, reference and raw scale in metadata. An ESP32
needs its own suitable supply; do not take its radio current from J11 pin 11.
