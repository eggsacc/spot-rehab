****
**Date:** <font style="color:tomato; font-family:Consolas;">20-05-2026</font>
**Duration:** 5hr
**Present:** _(add)_
**Subsystem:** 🔋 Power & Battery
**Outcome:** 🔧 WIP

**Objective:**
>Open the battery and test the lithium cells.

**Resources:** NIL

****
## TL;DR
****
Opened the battery module and found the cells deeply over-discharged (~90 mV vs. a 2.5 V safe minimum). Bench-charging brought the pack up to ~13 V, but it wouldn't hold — the cells warmed and self-discharged, and the Spot charger falsely reported "full". Conclusion: the cells are degraded beyond recovery and must be replaced.

## Work done
****
#### Disassemble battery module
- Pried apart the perimeter adhesive holding the module together (takes some force).
- Mapped the BMS pad layout for cell access.

#### Cell diagnosis & recovery attempt
- Measured initial cell-group voltages.
- Applied 2.0 V / 1.5 A to each accessible cell group to slowly recharge.
- Once groups reached ~2.0 V, raised limits to 16 V / 5 A across up to 5 groups at a time.
- Plugged the pack into the Spot charger to verify the result.
- Left the pack idle, then re-measured.

## Findings & data
****
- Battery is 56 cells in a 14s4p configuration. The BMS exposes 28 pads: positives along the long edges of the PCB, negative down the center.
- Initial cell voltage averaged only ~90 mV — far below the 2.5 V minimum safe voltage.
- During slow recharge, voltage rose steadily to ~1.9 V while drawing the full 1.5 A.
- 3 sets of pads are inaccessible — covered by a plastic insulation piece beneath the power wires.
- After staged recharge, the pack reached ~14.5 V on the supply; P1–GND measured 13.3 V combined.
- On the Spot charger: the BMS status LED blinked (successful CAN handshake); the charge indicator blinked green then went static (reported full charge).
- Post-charge P1–GND retest showed no increase (~13.0 V).
- After idling, the cells were warm to the touch and pack voltages dropped from ~1.6 V to ~0.6 V.
  - → Per the Spot manual, a "full" report on clearly-discharged cells indicates highly imbalanced cells; the suggested fix (leave plugged in to auto-rebalance) had no effect here.
  - → The warmth + voltage drop indicates resistive self-discharge through dead cells now behaving as short circuits — i.e. the cells are fully degraded.

## Decisions
****
- **Decision:** Replace the cells rather than attempt further recovery.
  **Why:** Cells are over-discharged to ~90 mV and won't hold charge (warm + self-discharging through shorted dead cells); the charger only reports false "full" due to imbalance.
  **Alternatives considered:** Rebalancing via the charger per the manual — attempted, no effect.
- **Decision:** Rebuild using the standard 14s4p configuration, spot-welded onto the original BMS pads.
  **Why:** Keeps the original BMS and form factor; the config is standard and replaceable.
  **Alternatives considered:** —

## Roadblocks
****
- Li-ion cells can't be charged — fully degraded.
- Imbalanced cell charge causes the Spot charger to fail (false "full").

## Next steps
****
- [x] Send Wonje the replacement battery quantity & SKU (standard 14s4p, replaceable by spot-welding onto the original BMS pads).

## Media
****
> 🖼️ *Images to be added (copy originals over later):*
- `IMG_20260520_141656244.jpg`
- `IMG_20260520_131029783.jpg`
- `IMG_20260520_141623391.jpg`
- `IMG_20260520_141701045.jpg`
