****
**Date:** <font style="color:tomato; font-family:Consolas;">21-05-2026</font>
**Duration:** 7hrs

**Objective:** 
>Disassemble lithium cells from BMS, source new cells

**Resources:**
>[Spot Battery Safety Data Sheets (SDS)](https://support.bostondynamics.com/s/article/Spot-Battery-Safety-Data-Sheets-SDS-49922)
>[18650 SAMSUNG 30Q 3000MAH Battery Cell](https://www.falconpev.com.sg/products/18650-samsung-30q-3000mah?_pos=3&_sid=ede1ee71e&_ss=r)

****
## Work done
****
#### Disassembly of power & CAN cables
- To remove the lithium cell packs from the BMS PCB, the power wires and CAN cable must be removed, followed by the plastic insulator that blocks access to 3 of the battery pads.
- The power cables are glued in place by a blob of very tough glue. The glue is removed by slowly cutting it into smaller chunks and prying off bit by bit.
- Once the power cables are unscrewed and the CAN cable unplugged, the plastic insulator piece can be pried off.

#### Separation of lithium cell packs from PCB
- The lithium cell packs are held to the PCB with some white plastic rivets that secures the plastic frame, as well as the nickle strips from the battery.
- The rivets are easily removed by prying with a flat head screwdriver.
- An attempt was made to cut the nickle strips, but the plastic frame behind it blocked the cutter.
- The spot-welded nickle strips could be pried apart from the PCB with some force, leaving little bumps of welded nickle behind on the PCB pads which could be post-processed.
- 2 flexible PCBs are unplugged from the PCB before removing the cell packs.

#### Seperation of A/B cell packs
- The 56 cells are arranged in 2x 7s4p packs, labelled A and B.
- To seperate the packs, there are 2 types of plastic connectors to be removed.
- The long, plastic snap-connector clips the 2 packs together and can be removed by prying either ends loose and twisting slightly to disengage the center clips.
- A shorter plastic connector is joined with black rivets to hold the end caps for each pack. The black rivets can be easily removed by pushing on the center axle from the bottom.

#### Removal of thermistor strip
- Each cell pack has a long, flexible PCB kapton taped to it, which connects to the BMS PCB.
- Each PCB strip has 5 SMD NTC thermistors used to monitor the temperature across the pack.
- There seem to be some kind of thermal adhesive used underneath each thermistor to improve heat transfer with the cell pack surface.
- The thermistors are labelled A and B to identify which side they belonged to originally. This probably dosn't matter since the PCBs are identical but just in case.

#### Identifying lithium cell specs
- INR18650-30Q from Samsung, listed in their [battery safety data sheets](https://support.bostondynamics.com/s/article/Spot-Battery-Safety-Data-Sheets-SDS-49922). 
- 3000$mAh$
- 15A discharge, 30A peak

#### Sourcing replacement cells
- Sim lim square/tower visit, all 3 stores don't have the cell type. Only INR18650-35E which is a higher capacity, higher amp version (and quite abit more expensive).
- Asked 5 shops on shopee that retails lithium ion cells, either not enough stock or does not support bulk purchases.
- Possible replacement cell is the LG HG2, with identical capacity and slightly higher current capability (20A). Found on shopee someone selling 56 pieces for $663.
- [Falcon PEV](https://www.falconpev.com.sg/products/18650-samsung-30q-3000mah?_pos=3&_sid=ede1ee71e&_ss=r) also sells the original Samsung cells, for way cheaper; waiting for reply or quote.

## Roadblocks
****
- Lack of suppliers for replacement cells
## Next steps
****
- [ ] Wait for response from Falcon PEV
- [ ] Wait for response from global 18650 battery shop
- [ ] Alternatively, find a closely matched, modern lithium cell as replacement

## Media
****
![[IMG_20260521_121830345.jpg]]
![[IMG_20260521_124027876.jpg]]
![[IMG_20260521_124113245.jpg]]
![[IMG_20260521_134440796.jpg]]
![[IMG_20260521_135625072.jpg]]
![[IMG_20260521_135124446.jpg]]
![[IMG_20260521_135810683.jpg]]
![[IMG_20260521_140552170.jpg]]
![[IMG_20260521_105100286 1.jpg]]
![[IMG_20260521_110136668.jpg]]
![[IMG_20260521_105122540.jpg]]
![[IMG_20260521_141908595.jpg]]
