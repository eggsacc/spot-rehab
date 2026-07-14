# FX23 encoder breakout — design review, final design & test plan

**Date:** <font style="color:tomato; font-family:Consolas;">04-07-2026</font>

**Duration:** _fill in actual session time_

**People:** Ming

**Subsystem:** 🦿 Actuators & Legs

**Outcome:** 🔧 WIP — board designed and reviewed, **not yet fab-ready** (1 blocking issue)

**Objective:**
>Design and validate a breakout PCB that mates directly with the hind hip-X secondary encoder assembly's FX23 connector, so its serial output (iC-Haus MU → RS-485 line driver, presumed LTC2863) can be read on the bench, independent of Spot's leg motherboard. Supports the BD support-ticket evidence and doubles as an acceptance test for any replacement encoder.

**Resources:**
>[HIROSE FX23/FX23L Series datasheet](../assets/HIROSE-FX23-datasheet.pdf)

****
## TL;DR

Breakout PCB fully designed: FX23-20P-0.5SV15 header (J1, bottom layer) broken out to 24 individual TestPoint pads (top layer) via 24 vias, with the connector's 4 retention tabs grounded. Design review found the pad/net accounting is exactly correct, but the PCB editor reports **3 of 25 nets still unrouted** — this blocks fabrication until fixed. Two more pre-fab checks (fab clearance/drill capability, a second mounting hole) are recommended. Once resolved, the board is ready to order; the 5-phase bench bring-up plan below is unchanged and ready to run once parts are in hand.

## Work done

#### Schematic revision (from the original 1:1 passthrough design)
- Reviewed the Hirose FX23-20P-0.5SV15 datasheet against the original schematic and found a pin-count mismatch: the schematic's J1/J2 only accounted for 24 pins, but the real footprint has 28 pads (20 signal + 4 Power Contacts + 4 Retention Tabs — the last group brass/tin-plated per the datasheet's Materials table, mechanical-only).
- Confirmed connector gender: the encoder-side connector is a **Receptacle**, so the breakout correctly uses the **Header** variant (FX23-20P-0.5SV15) to mate with it.
- Extended the J1 symbol from 24 → 28 pins; tied the 4 retention tabs (25–28) to a single shared GND net.
- Replaced the original pin-header J2 concept with **24 individual `Connector:TestPoint` symbols** (TP1–TP24), one per electrical net — the FX23's native 0.5mm pitch isn't hand-probeable, and TestPoint footprints keep soldermask off the pad for reliable multimeter/probe contact, plus let each net get renamed individually as its identity is discovered on the bench.

#### PCB layout
- J1 (FX23-20P-0.5SV15) placed on the **bottom** layer; 24 TestPoints on the **top** layer, connected via 24 vias.
- Uniform 0.15mm (6 mil) trace width and 0.2mm drill / 0.4mm pad vias applied across all 24 electrical nets, including the 4 power-contact nets.
- A scoped DRC clearance exception applied to J1's own pads/nets (~0.17mm actual pad-to-pad spacing vs. the 0.2mm board-wide default).
- Board: 40mm × 27.5mm, one mounting hole.

#### Design review (this session)
- Cross-checked the schematic, PCB layout, and 3D renders against the datasheet and the design plan.

## Findings & data

#### Pad/net accounting — confirmed correct
- **Pads: 52** = 24 TestPoint pads + 28 on J1 (20 signal + 4 power + 4 tabs). Matches design intent exactly.
- **Vias: 24** = one per TestPoint net (tabs don't need a via — grounded locally on the bottom layer near J1).
- **Nets: 25** = 24 TP nets + 1 shared GND net (the 4 tied tabs). Matches.

#### 🔴 Blocking: 3 of 25 nets are unrouted
The PCB editor's status bar reads `Pads 52 | Vias 24 | Track Segments 146 | Nets 25 | Unrouted 3`. Three connections are missing copper and must be completed before this can be fabricated. **Prime suspect: the 4-pad GND-tab net (25–28)** — it's the one net in this design tied to more than one pad (4 pads = exactly 3 connections), and multi-pad nets are the easiest to leave partially stitched. A net *label* reading "GND" confirms the netlist assignment, not the physical copper.

#### Trace/via sizing — sound given stated intent, one residual risk
Uniform 0.15mm trace + 0.2mm drill/0.4mm pad via across all 24 nets (power contacts included) is a reasonable call: the pinout is still unknown, the power contacts aren't intended for functional use, and selectively widening traces now would risk reintroducing clearance violations at the tight connector pitch. Note regardless: **the physical copper on TP21–24 (the Power Contact test pads) can't safely carry anything beyond passive-probe current** — a 0.15mm trace is nowhere near the connector pin's 3A rating.

#### J1 footprint clearance exception — correctly diagnosed
The ~0.17mm actual pad clearance inside the FX23 footprint (vs. the 0.2mm global default) is inherent to a 0.5mm-pitch part, not a bad footprint — confirmed by comparing pad geometry against the connector's real mechanical dimensions. A scoped rule exception limited to J1's pads/nets (rather than loosening the board-wide default) is the right fix.

#### Via size — reasonable, but check fab capability
0.2mm drill / 0.4mm pad is a standard "small via" size, but it's on the low end of what some fabs' standard (non-HDI) service supports as a capability floor. Confirm against the specific fab's capability table before ordering.

#### Only one mounting hole
Hirose's own datasheet explicitly warns against relying on the connector alone to secure the board ("using only the connectors to support the board may result in a load to the connector that results in damage or contact failure"). A single hole doesn't resist the twisting/rotational load the board will see across repeated mate/unmate cycles during bench bring-up (the datasheet caps the connector at 100 such cycles). Recommend a second, diagonally-placed mounting hole before fab.

## Decisions

>**Decision:** Keep uniform trace/via sizing across all 24 nets rather than pre-emptively widening the (currently unidentified) power-contact traces.

**Why:** Pinout is still unknown and the power pins aren't intended for functional use — widening now would be guessing, and risks reintroducing clearance violations at the tight connector pitch.

**Alternatives considered:** Size traces selectively once the pin-map is known — deferred; plan is to reinforce a specific trace after mapping (wider section or jumper wire) only if it turns out to carry real current.

>**Decision:** Replace the pin-header J2 with 24 individual TestPoint symbols/footprints.

**Why:** The FX23's native 0.5mm pitch isn't hand-probeable; dedicated TestPoint footprints keep soldermask off the pad for reliable contact, and each net can be renamed individually as its identity comes in from bench probing.

**Alternatives considered:** A single custom bare-pad-array footprint under one connector symbol — simpler schematic, but less flexible and doesn't self-document as the pin-map fills in. Not used.

## Roadblocks

- 3 unrouted nets block fabrication — must resolve first (see Findings).
- Fab capability for 0.15mm clearance / 0.2mm drill not yet confirmed.
- Full pinout of the 20 signal + 4 power contacts remains unknown until Phase 1 bench continuity mapping, post-fab.

## Next steps

**Before fab:**
- [x] Route the remaining 3 unrouted nets; re-run DRC/ratsnest and confirm 0 unrouted, 0 unresolved errors. *(done 06-07 — GND tab net routed; "3 unrouted" in review screenshots was just the GND net hidden for track visibility)*
- [x] Confirm fab capability: min clearance ≥0.15mm, min drill ≤0.2mm. *(confirmed 06-07 — fab supports both)*
- [x] Add a second mounting hole. *(done 06-07 — four 2mm corner holes added)*
- [x] Order the board. *(ordered 06-07 — see the [06-07 log](2026-07-06-fx23-breakout-finalized-ordered.md))*

**Bench bring-up, once boards arrive:**
- [ ] **Phase 0** — bare-board validation: visual inspection under magnification (signal row + tab pads for solder bridges), continuity J1↔TP for all 24 nets, confirm no shorts between adjacent J1 pads, confirm tabs read continuous to GND.
- [ ] **Phase 1** — mate to the encoder PCB, unpowered. Continuity-trace each TP to known reference points on the encoder PCB (iC-MU VDD/GND, the RS-485 driver's VCC/GND/A/B) and build a pin-map table (TP# → identified net → method → notes).
- [ ] **Phase 2** — current-limited bench-PSU power-up (~100mA limit) on the identified VCC/GND pair before trusting any other source; confirm current settles low/stable and the encoder wakes (≥4.5V, per the 02-07 EEPROM-probe finding).
- [ ] **Phase 3** — RS-485 capture via a USB-RS485 adapter or transceiver (not a direct GPIO wire — the differential pair needs a receiver, and the driver's logic side may swing near its own 5V rail). Sweep common baud rates; chase down the iC-Haus MU datasheet for protocol/framing specifics if it turns up rather than guessing blind.
- [ ] **Phase 4** — repeat Phases 1–3 on the known-good eR unit as a baseline; a side-by-side eR/eL capture is the strongest evidence for the BD support ticket.
- [ ] **Phase 5** — cut over from bench PSU to RPi 5V/GND, re-verify current draw and the serial capture still work identically.

## Media

Schematic — J1 (28-pin) + 24 TestPoint symbols + tab GND tie:

<img src="assets/fx23-breakout-schematic.png" width="700"/>

2-layer routed layout — FX23 on bottom, TestPoints on top:

<img src="assets/fx23-breakout-layout.png" width="700"/>

3D render, top side, TP1–TP24 labeled:

<img src="assets/fx23-breakout-3d-top.png" width="700"/>

3D render with the FX23 connector model mounted:

<img src="assets/fx23-breakout-3d-connector.png" width="700"/>
