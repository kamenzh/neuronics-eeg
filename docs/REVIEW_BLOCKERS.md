# Remaining hardware work — A0.2

| ID | Current state | Remaining evidence |
| --- | --- | --- |
| HW-01 | P1 36619 / 8R003661901F selected; derived footprint added | Actual Sino-k plug/sample mating, hole fit, enclosure retention |
| HW-02 | Bounded DC clamp/injection calculation documented | ESD/transient behavior, leakage/noise and powered/unpowered rail injection |
| HW-03 | Body-current protection unresolved | Rail-to-contact and aggregate current, short/open failures, USB/power paths; 20k alone is insufficient evidence |
| HW-04 | Bias loop candidate | Cable/electrode simulator, settling/stability and recovery measurements |
| HW-05 | TPS7A24 power revision and DC margin review complete | Effective capacitance, startup/noise/temperature, reverse current and battery harness |
| HW-06 | Owned Nano and GPIO map selected | Protected controller branch, radio-burst droop, EMI, power sequencing/interlock |
| HW-07 | Analog/digital placement refined | Detailed independent layout review and measured noise/return behavior |
| HW-08 | Copper routing added | Current completeness and DRC evidence in validation/STATUS.md; fabricator stack-up still to be selected |
| HW-09 | Automated checks executed | Fresh saved-board reports; they do not establish physical safety/performance |
| HW-10 | Exact candidate PCB BOM | Verify source/stock/footprints, off-board parts, bare-board delivered quote |
| HW-11 | No physical tests performed | Bench log tied to PCB/firmware revisions |
| HW-12 | Body-use review not passed | Qualified review of final assembled hardware and all external connections |

Sockets replace the old bench pin headers. A touchproof connector does not make
the circuit safe for body connection. USB/shared grounds are not isolated.
