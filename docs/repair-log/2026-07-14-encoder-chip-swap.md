# Encoder chip swap, breakout dead-end & double encoder-health fault

**Date:** <font style="color:tomato; font-family:Consolas;">14-07-2026</font>

**Duration:** 6h

**People:** Ming, Yizhang

**Subsystem:** 🦿 Actuators & Legs

**Outcome:** 🔧 WIP — robot walks and survives cold boots, but BOTH hind hip-X joints now report Encoder Health <20%

**Objective:**
>Bring up the fabricated FX23 breakout board for bench readout of the secondary encoder, and repair the left hind hip-X by replacing the defective eL encoder chip; verify with SpotCheck.

**Resources:**
>[04-07 breakout design & test plan](2026-07-04-fx23-breakout-design-test-plan.md)
>[01-07 SpotCheck diagnosis](2026-07-01-spotcheck-diagnosis.md)
>[02-07 encoder EEPROM probe](2026-07-02-encoder-eeprom-probe.md)

****
## TL;DR

The assembled FX23 breakout turned out to probe the wrong interface, as the encoder's RS-485 transceiver never reaches the FX23 connector (it routes through a separate connector into the driver board; only GND is common), so the bench-readout plan is retired. We instead repaired eL directly: the iC-MU Y2HC chip reworked onto the original eL PCB, everything reassembled to native config. The robot boots (after the usual jog-into-bounds trick), runs SpotCheck, walks, and (for the first time since the fault appeared) **survives a cold power cycle**. But SpotCheck now flags **BOTH hind hip-X encoders at <20% health**, the hind legs walk visibly bent inward, and both joints throw transient "Sensor misread" faults mid-walk. Neither flag is expected: the left has a brand-new chip, and the right (eR) had tested healthy on 01-07 (only ever in the *left* socket). The next steps are to inspect the rework quality, re-seat both boards, and run a third SpotCheck to see if the right joint's health clears and whether the left's gait straightens.

## Work done

#### FX23 breakout bring-up → architecture dead-end
- Assembled the breakout and ran Phase 0/1 continuity mapping against the encoder assembly.
- **Discovery: the RS-485 transceiver does not connect to the FX23.** The transceiver routes through a *different* connector into the **driver board**, and it is the driver board's output that leaves through the FX23. Continuity transceiver ↔ FX23 exists **only on GND**.
- Consequence: the breakout can only observe the driver-board interface, not the raw encoder serial. Decided against designing a second breakout for the transceiver-side connector (lead time) and went for the direct repair instead.

#### eL repair — chip-level rework
- **third-party iC-Haus iC-MU chip, "Y2HC" marking** — the installed chip reads `MU Y2H C 12T 223504` vs the original's `MU Y2HC_44 19702`; the trailing number also differs between our own original left and right units → lot/date code, not a variant marker (photo below).
- Reworked the new chip onto the **original eL PCB** — the board's own 24C02 EEPROM (config verified byte-identical to the healthy eR's in the [02-07 probe](2026-07-02-encoder-eeprom-probe.md)) and the original left magnet stay.
- Reinstalled the reworked board in the **left** hind hip-X; returned eR home to the **right** (it had sat in the left leg since the 01-07 diagnostics). Robot now in native config for the first time since 30-06.

#### Boot, SpotCheck ×2, walking
- Boot faulted `spot.hr.hx.pos.fault — Value out of bounds (too low)` (DTC `SP-N0N01-HRHX`) — note: on the **right** hip this time. Cleared with the established manual-jog-into-bounds trick, then ran SpotCheck (run 1). Robot walked normally afterwards.
- **Cold power cycle** → booted, ran SpotCheck again (run 2) → walked again. First cold-boot survival on record for this fault.
- Extended walking/driving session to observe behaviour (video below).

## Findings & data

#### SpotCheck joint offset cal — changes from previous stored offsets, mRad
`*` = significant change in stored calibration; `[E]` = Encoder Health <20%. Health Stats ✅ and Load Cell Cal ✅ both runs; Camera Check ❗ (known rear-camera fault).

**Run 1** (first SpotCheck after the rebuild):

| Joint | Front Left | Front Right | Hind Left | Hind Right |
|---|---|---|---|---|
| Hip X | 0.89 | 0.48 | **114.68 \* [E]** | **-5.54 \* [E]** |
| Hip Y | 0.02 | -1.05 | 0.28 | -0.66 |
| Knee | -0.31 | 1.66 | 2.53 | 0.37 |

**Run 2** (after cold power cycle):

| Joint | Front Left | Front Right | Hind Left | Hind Right |
|---|---|---|---|---|
| Hip X | -0.48 | 0.32 | **-2.05 [E]** | **111.23 \* [E]** |
| Hip Y | -0.85 | -0.20 | -0.31 | -0.95 |
| Knee | 0.35 | 0.46 | -1.74 | -0.70 |

#### What the full SpotCheck record now establishes

| SpotCheck | Left socket | Right socket |
|---|---|---|
| 01-07 | eR + mR → **healthy** (-533.59 mRad) | eL + mL → **[E]** |
| 14-07 ×2 | NEW chip + mL → **[E]** | eR + mR → **[E]** |

- The **only healthy reading ever obtained is eR + mR in the LEFT socket**. Two previously assumed "facts" fall: 
(1) *"the left magnet is fine" was never health-verified*: on 01-07 the magnets had been swapped too, so the healthy left-socket reading used both right-leg parts; mL has flagged `[E]` under every encoder ever tested on it. 
(2) *eR was never health-tested in its own right socket before now*: pre-teardown, no SpotCheck ever ran; "the right leg never froze" only proves boot seeding, not >20% health.
- The ~113 mRad `*` offsets are symmetric and arrive one run apart (hl +114.68 in run 1, hr +111.23 in run 2) — consistent with each socket's stored cal absorbing the eL↔eR encoder-zero difference from the crossed-config era, possibly committing one run late for `[E]`-flagged joints. The bad alternative — eR's absolute angle genuinely jumping ~6.4° between boots — isn't excluded yet; a third SpotCheck discriminates (small hr change → catch-up; another ~100 mRad jump → genuine instability).

#### Walking behaviour
- **Gait: hind legs visibly adducted: feet pulled inward under the body midline ("knock-kneed")** vs reference footage of a stock Spot, whose feet track vertically under the hips. Front legs near-normal. Consistent with mis-seeded hip-X (abduction axis) absolute angles: seed off by δ → every commanded pose lands δ inward; the ~6.4° cal shifts match the visible lean. The SpotCheck offsets themselves were computed *from* `[E]`-flagged encoders, so the stored cal has likely baked the lean in.
- **Transient `pos.fault — Sensor misread`** (DTC `SP-N0N06-HRHX` / `SP-N0N06-HLHX`) on **both** hind hip-X joints while driving; 13 historic faults accumulated in one session. Mechanism: runtime cross-check of secondary vs primary encoder tripping on weak-signal misreads.
- **Fast backward walking reliably triggers a recovery routine**: the robot stops, looks upward, splays the legs outward, then resumes: a fault-triggered re-seed/re-validation stance, i.e. the escalation of the misread faults, not a separate bug.

#### Interpretation
Everything observed (inward gait, misreads, recovery stances) is downstream of **unreliable absolute hip-X sensing on both hind sockets**. Candidate causes, ranked:
1. **Same-session seating/air-gap error on both hips** (one systematic reassembly mistake explains both flags: these Hall-IC boards read their magnetic pole disc across a precise air gap; small errors collapse signal amplitude → AGC maxes → <20%).
2. **Left socket: chip-rework quality** as the iC-MU's on-die Hall array must sit over the disc's master/nonius tracks to sub-mm precision; a hand-reworked chip a few tenths of a mm off-centre or rotated reads a degraded signal. (EEPROM/config is ruled out: the config chip never moved and its image is verified good.) Alternatively, **the original fault may never have been the chip**: if it was board-level (trace/supply) or magnet/gap, a new chip on the same board reproduces the symptom.
3. **Right socket: eR degraded by handling** (5+ unbolt/rebolt cycles since 30-06): or it was never >20% in that socket to begin with (never measured).

## Decisions

>**Decision:** Abandon the FX23-breakout bench-readout path; repair by direct chip replacement instead.

**Why:** The breakout physically cannot see the encoder's serial lines (wrong interface point as only GND is common with the transceiver), and a second breakout for the transceiver-side connector costs another design + fab cycle we didn't have time for.

**Alternatives considered:** Second breakout PCB for the transceiver-side connector deferred indefinitely, probing the driver-board side of the FX23 is possible with the existing board but reads the processed bus, not the raw encoder output.

>**Decision:** Replace the iC-MU chip only, keeping the original eL PCB, EEPROM and magnet.

**Why:** The 02-07 EEPROM probe proved the config intact and byte-identical to the healthy unit's, pointing at the Hall front-end silicon; a chip swap is the minimal intervention that tests that theory. Buying a bare chip is also the only sourcing we have (no BD part supply).

**Alternatives considered:** Whole replacement board from BD is not possible.

## Roadblocks

- **Both hind hip-X joints <20% encoder health** — every cold boot risks a seed failure on either hind hip; the robot is usable for flat-floor diagnostics only (no stairs/payload) until sensing is trustworthy.
- Raw encoder serial remains unobservable on the bench (no transceiver-side breakout).

## Next steps

- [ ] Inspect the reworked iC-MU's **placement alignment** (centering/rotation vs the original footprint witness marks) and solder quality under magnification.
- [ ] **Re-seat both hind hip-X encoder boards**; inspect and clean both magnet discs; verify air gap.
- [ ] **Third SpotCheck** — discriminates the `hr 111.23*` reading (cal catch-up vs genuine boot-to-boot jump) and checks whether `[E]` clears after re-seating; a healthy cal should visibly straighten the gait.
- [ ] If gait stays bent after a healthy cal: consider `REVERT_CAL` so offsets are recomputed from healthy reads.

## Media

#### Repair process

New iC-MU chip reworked onto the original eL board (`MU Y2H C 12T 223504`; RS-485 transceiver below it; flux residue from the rework still visible):

<img src="assets/encoder-board-new-icmu-chip.jpg" width="400"/>

Chip rework at the Hakko FR-810B hot-air station over a preheater plate:

<img src="assets/icmu-chip-rework-station.jpg" width="400"/>

FX23 connector reflowed onto the breakout board (EDIC HP15 hotplate, 230°C):

<img src="assets/fx23-breakout-connector-reflow.jpg" width="400"/>

#### Faults & SpotCheck

Boot fault — `hr.hx` value out of bounds (too low), pre-SpotCheck:

<img src="assets/hr-hx-out-of-bounds-boot.jpg" width="400"/>

SpotCheck run 1 (post-rebuild) and run 2 (post cold power cycle) — both hind hip-X `[E]`:

<img src="assets/spotcheck-run1-offset-table.jpg" width="400"/>
<img src="assets/spotcheck-run2-offset-table.jpg" width="400"/>

Mid-walk "Sensor misread" faults — active and historic views (both hind hip-X):

<img src="assets/sensor-misread-active.jpg" width="400"/>
<img src="assets/sensor-misread-historic.jpg" width="400"/>

Walking gait — note the hind legs angling inward under the body:

<div align="left">
  <video width="360" height="640" controls>
    <source src="assets/walking-gait-inward.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>
