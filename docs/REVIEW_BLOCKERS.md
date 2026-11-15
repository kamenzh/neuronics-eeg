# Remaining hardware work — A0.3

| ID | Current state | Remaining evidence |
| --- | --- | --- |
| HW-01 | P1 36619 selected; slot/hole tolerance model revised | Real Sino-k plug/socket mating, coupon solder fit, fabricator acceptance, enclosure support |
| HW-02 | Bounded DC clamp calculation | ESD/transients, leakage, powered/unpowered analog rail injection |
| HW-03 | Body-current protection unresolved | Rail-to-contact/aggregate current, faults, USB/power paths; 20k alone is insufficient |
| HW-04 | Bias-loop candidate, disabled for initial tests | Electrode/cable model, stability and recovery measurements |
| HW-05 | Local supplies/reference rerouted; extra reference capacitor | Effective capacitance, cold/aged startup, noise, stability and temperature |
| HW-06 | Power-off tolerant GPIO buffers + harness candidate | Brownout/power orders, final holder/switch, inrush/fuse/drop tests and radio interference |
| HW-07 | Independent changed-layout review complete | Physical noise/returns, CMRR, buffer-series-resistor edge behavior |
| HW-08 | Complete copper, fresh clean full DRC | Named fabricator stack-up and exported manufacturing-file inspection |
| HW-09 | Stronger workflow guards and evidence hashes | Checks remain limited to their documented scope |
| HW-10 | 107 candidate PCB components | Exact stock/source review, offboard parts and delivered bare-board quote |
| HW-11 | No board or firmware acquisition test yet | Built firmware/receiver and measured bench log tied to revisions |
| HW-12 | No body-use approval | Qualified assembled-system review including enclosure and external connections |

See [implemented changes](REVIEW_FIXES_A0_3.md), [independent criticism](INDEPENDENT_REVIEW_A0_3.md)
and [the next-step roadmap](NEXT_STEPS.md). A touchproof jack and battery power do
not qualify the complete device for a person. Do not attach the current prototype.
