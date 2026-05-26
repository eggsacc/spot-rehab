****
**Date:** <font style="color:tomato; font-family:Consolas;">13-05-2026</font>
**Duration:** 3hr

**Objective:** 
>Attempt to charge battery and test controller

**Resources:** 
> - [Comprehensive Teardown Report of the Quadruped Robot Spot : r/IndiaTech](https://www.reddit.com/r/IndiaTech/comments/1nwsba2/comprehensive_teardown_report_of_the_quadruped/)
>- [LHS Materials](https://www.lhsmaterials.com/thermal-regulation)

****
## Work done
****
**Attempt to charge both Spot batteries using legacy charger**
- Battery charger seems functional; green AC indicator lights up as expected upon power on.
- However, connecting the battery to the charger causes the charging indicator light to briefly blink red before vanishing. The charging indicator should constantly blink green during normal charging according to the manual.

**Attempt to turn on controller**
- Controller turns on by long pressing top power button, with ~28% charge
- Successfully connects to wifi, joysticks/buttons responsive
- Spot app launches properly, and past mission cache visible
- Controller can be charged with micro-usb (slow!)
- Battery life is concerning; 10 minute of basically doing nothing depleted more than 10% of battery

**Find Spot hardware documentation**
- Full teardown report in Chinese: [Comprehensive Teardown Report of the Quadruped Robot Spot : r/IndiaTech](https://www.reddit.com/r/IndiaTech/comments/1nwsba2/comprehensive_teardown_report_of_the_quadruped/)

**Battery characteristics (P.g 167)**
- 56 * 18650 Li-ion batteries, split into 2 packs of 28
- Batteries are surrounded by [LHS Materials](https://www.lhsmaterials.com/thermal-regulation) which provides thermal homogeneity and heat absorbtion to protect batteries
- BMS communicates with robot via CAN bus

## Roadblocks
****
- Batteries do not charge
- Unable to open battery packs due to sealants around the parameter

## Next steps
****
- [x] Find royston to disassemble battery pack
- [x] Attempt to jump start/trickle charge cells

## Media
****
![[6064426941181268352.jpg]]
![[6064426941181268351.jpg]]
![[Pasted image 20260513170450.png]]
![[Pasted image 20260513170512.png]]



