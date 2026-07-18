# Battery pack #2 design optimization

**Date:** <font style="color:tomato; font-family:Consolas;">16-06-2026</font>

**Duration:** 4hrs

**People:** Yizhang

**Subsystem:** 🔋 Power & Battery

**Outcome:** ✅ Complete

**Objective:**
>Optimize battery pack design to make pack #2 structurally mode rigid and align better with the original pack design.

**Resources:**
NIL

****
## TL;DR

Optimized battery pack V2 design to incorporate another set of braces and structural members used in the original pack for rigidity. Optimized dimensions after V1 to more accurately fit the casing/PCB.

## Work done

#### Additional battery braces design
- Another set of battery braces were designed with slightly tighter tolerances to hold the battery lattice tightly together. Design V1 only relied on the terminal brackets to align the batteries and there were some play when the pack was flexed.
- The additional braces are designed to be printed in ABS for higher temperature resiliance.

#### Incorporating original structural components
- The original pack used injection molded spacers secured to the terminal brackets with plastic expansion rivets for rigidity.
- The width of terminal brackets were adjusted and additional holes were cut out to accomodate these spacers in positions similar to the original pack design.

#### Terminal bracket dimension adjustment
- After assembly of pack V1, some geometrical adjustments were noted and implemented in V2 to better fit the PCB and casing cutouts.
- The new brackets are 3D printed with glass filled ABS (ABS-GF) for maximum dimensional stability under high temperatures.

#### BMS PCB mounting nuts
- Design V1 incoporates circular cut-outs aligned with the BMS PCB mounting holes similar to the original design.
- The original design uses slightly larger plastic expanding rivets to secure the PCB to the brackets. However, due to the 3D printing orientation of the brackets, the force exerted by the expanding rivets caused the layer lines to split.
- Hence, in V2, this was addressed by the use of captured M3 nuts under 1.2mm of plastic. The BMS is secured using M3x6mm screws instead.

## Findings & data
NIL

## Decisions
NIL

## Roadblocks
NIL

## Next steps
- [x] Assembled pack #2

## Media
![alt text](../assets/battery-v2-cad.png)
