# Next steps for Neuronic A0.4

A0.4 has routed hardware, an updated 109-component BOM and independently parsed [bare-board and assembly files](../hardware/fabrication/A0.4/). The objective is an eight-channel wireless EEG instrument using the Waveshare ESP32-S3-Nano. The board has not been assembled.

| When | Work | Completion evidence |
| --- | --- | --- |
| Before a final-design order | Resolve the exact Sino-k lead and P1 jack interface. The leads have not been ordered. | Obtain the lead maker's drawing or mating-part confirmation. Check the first available pair and enclosure clearance. |
| Before final design approval | Complete the electrode protection, power-fault and service-interface review with an engineer experienced in body-connected electronics. | Document credible fault paths, limits, protective measures, and any circuit or enclosure changes. The A0.4 discharge loads cover only a bounded subset of rail-injection cases. |
| Before submitting CAM | Get a shop to review four-layer construction, tolerances on plated slots and J12 holes, mask, finish and price. | Written acceptance of shop notes and CAM preview matched to the exact revision. Re-export any revised CAD. |
| In parallel | Implement the Nano acquisition firmware and PC recorder. | Reproducible build, eight-channel records with timestamps and loss accounting. |
| Following assembly | Use a dummy electrode fixture for rail sequencing, startup, injected signals, CMRR, noise, bias stability, radio and fault tests. | Archive conditions, instruments, limits and results. Check continuity, polarity and mechanical fit. |
| Before recording a person | Qualify the entire assembled battery, enclosure, leads and electronics against the system safety requirements. | Qualified review plus physical fault and leakage measurements. |

The [A0.4 engineering review](A0_4_DESIGN_REVIEW.md) records the circuit decisions and their limits. The [detailed verification plan](reviews/independent-577aad8-2026-11-17/VERIFICATION_PLAN.md) gives bench procedures.
