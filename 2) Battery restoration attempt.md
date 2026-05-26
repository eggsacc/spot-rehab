****
**Date:** <font style="color:tomato; font-family:Consolas;">20-05-2026</font>
**Duration:** 5hr

**Objective:** 
>Attempt to open battery and test lithium cells

**Resources:** NIL 

****
## Work done
****
#### Disassemble battery module
- Battery module is held together with some adhesives along the perimeter, could be pried with some force.
- Battery module comprises of 56 Li-ion cells, in the 14s4p configuration.
- The BMS has 28 pads exposed for battery connection. The pads along the long edges of the PCB are the positive terminals, and the corresponding pad along the center of the PCB is the negative terminal.
#### Lithium ion cell diagnosis
- Initial voltage measurement of lithium cells shows an average voltage of only ~90mV, far below the minimum safe voltage of 2.5V.
- An attempt was made to slowly recharge the cells in groups to bring it back up to voltage.
- Initially, a 2.0V, 1.5A source was applied to each cell group across the pads. The power supply shows a steady increase in voltage until about 1.9V, drawing the full 1.5A of current.
- 3 sets of pads are inaccessible due to being completely covered by a plastic insulation piece below the power wires.
- After most of the cells have been recharged to about 2.0V, the voltage and current limit was increased to 16V/5A and applied to up to 5 cell groups together. The voltage gradually rose to about 14.5V where the power was disconnected after.
- A quick voltage test across pad P1 and GND shows a effective combined cell voltage of 13.3V.
- The battery was plugged into the spot charger for verification. This time, the status LED on the BMS started blinking indicating a successful handshake between the charger and battery over CAN. While the charging indicator light did blink green, it quickly became static indicating a full charge.
- However, another voltage test across P1 and GND reveals no increase in cell voltage, still hovering ~13.0V.
- According to the Spot user manual, a reported full charge when the cells are clearly discharged indicates that the cell voltages are highly imbalanced. The manual suggests leaving the battery plugged in to the charger to automatically rebalanced the voltages, but that did not seem to have an effect in this case as the voltage did not increase.
- After unplugging the charger and leaving the battery idle for some time, the lithium cells felt warm to the touch, and the individual cell pack voltages also dropped significantly from ~1.6V to ~0.6V. This suggests a resistive discharge of cells across other dead lithium cells which are just behaving as short circuits.

## Roadblocks
****
- Li-ion cells can't be charged; fully degraded.
- Imbalanced cell change causes Spot charger to fail.
## Next steps
****
- [x] Send Wonje replacement battery qty, SKU. It is a standard 14s4p configuration and should be replaceable by spot welding onto the original BMS pads.

## Media
****
![[IMG_20260520_141656244.jpg]]
![[IMG_20260520_131029783.jpg]]
![[IMG_20260520_141623391.jpg]]
![[IMG_20260520_141701045.jpg]]