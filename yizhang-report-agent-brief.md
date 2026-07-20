# Yizhang UROP Report - Agent Build Brief (repo-only)

Self-contained build spec for **Yizhang's** UROP report. Everything you need is in **this repository**. Do **not** read any external wiki, notebook, or the companion (Ming's) report - you never see Ming's draft; you cite it with placeholders that are resolved later. Write the report by synthesising the repo's dated logs and data pages into authored prose.

---

## 1. What you are writing

**Thesis (one sentence - every section must serve it):** *Rebuilding the Spot's power system and physically/electrically reverse-engineering its faulty hip actuator to characterise the hardware and localise the fault to a physical part.*

**Your subsystems:** (1) **Power & Battery** - full. (2) **Actuator & Legs - hardware layer** only: the physical teardown, mechanical swaps, and the encoder-board electrical reverse-engineering.

**Explicitly NOT yours** (these belong to the companion report - cite them, never write them): any diagnostic *interpretation* of control signals (SpotCheck / `/joint_states` readings, Encoder-Health, `[E]` flags), the encoder *repair* (chip rework, air-gap change), the cameras, the ROS 2 / SDK / autonomy work, and the FX23 breakout board (the `connector/` KiCad project is in this repo but the board is Ming's design - do not claim it).

## 2. Sources (repo-only)

Read only these. Paths are repo-relative.

- **Power/battery:** `docs/battery/*.md` (13 dated session logs) and the consolidated `docs/subsystems/battery/battery-repair.md`.
- **Actuator mechanical (hardware layer):** `docs/motor/2026-06-15-robot-teardown.md`, `docs/motor/2026-06-18-driver-disgnostic.md`, `docs/motor/2026-06-19-leg-component-swap.md`, `docs/motor/2026-06-25-motor-disassembly.md`, `docs/motor/2026-06-30-output-encoder-swap.md`, `docs/motor/2026-07-16-encoder-read-attempt.md`.
- **Encoder electrical RE:** `data/electrical/ic-mu-electrical-connection.md`, `data/electrical/ic-mu-eeprom-config-map.md`, `data/electrical/db25-cover-connection.md` (+ `data/electrical/assets/`).
- **Status / specs orientation:** repo `README.md` (dashboard: subsystem status, hip-motor specs, cell type).

Do not use `docs/motor/` logs for dates outside the list above (07-01/02/04/06/14/15/17 and 06-12 are Ming's diagnosis/repair - out of scope). Do not use `data/software/` or `docs/software/` at all.

## 3. Absolute rules

1. **Repo-only.** Every factual claim traces to a file in Section 2. Invent nothing - no numbers, dates, or results not in the logs.
2. **Synthesise, do not copy.** The logs are raw material; write authored prose, not pasted log text.
3. **Stay in the hardware layer.** Describe physical acts and hardware/electrical observations. Do **not** interpret control-signal readings or diagnose the fault beyond "the fault is a physical hardware difference."
4. **Cite Ming's layer as a single premise sentence** with a placeholder section number `[Ming, SS-TBD]` (resolved at the sync step, Section 8). Never re-describe his layer.
5. **Do not read or paraphrase Ming's report.** Draft only from the repo sources.
6. **Forward work is not a result.** If simulation is mentioned, label it as planned future work - no simulation exists in this repo.

## 4. Report structure + per-section source map

Follow this structure (standard UROP report skeleton). For each section: **Sources -> Write -> Own figures**.

1. **Title page** - CDE2605 UROP, correct AY/semester, descriptive title (working: "Power-System Rebuild and Hardware Reverse-Engineering of a Spot Hip Actuator"), author name + matriculation number.
2. **Contents; List of figures; List of tables.**
3. **Introduction** - *Sources:* `README.md` (subsystem status). *Write:* Spot arrived with dead battery packs and a mechanically-unknown faulty hip actuator; objectives - rebuild the power system, and physically/electrically characterise the actuator/encoder hardware to localise the fault to a physical part; brief note on working approach (bench teardown/reassembly). Forward-point to the methodology.
4. **Background** - *Sources:* `docs/battery/2026-05-13-battery-controller-inspection.md`, `README.md` (Notes: 7s4p, CAN BMS, INR18650-30Q, hip specs), `data/electrical/ic-mu-electrical-connection.md`. *Write:* battery pack/BMS architecture; the hip-X actuator mechanical/electrical architecture (50:1 harmonic drive, the stacked secondary-encoder + load-cell PCBs) **from the hardware angle**. *Seam A:* the functional/signal role of the encoders is Ming's - one cited sentence only.
5. **Methodology 1 - Power-system rebuild** - *Sources:* all `docs/battery/*.md` + `docs/subsystems/battery/battery-repair.md`. *Write:* inspection, restoration attempt, cell sourcing, pack design + CAD spacer, V2 redesign, assembly, BMS + SoC-cable repair, DB25 cover-detection bypass. *Own figures:* pack photos, CAD (spacer/V2 brackets), BMS/SoC repair photos.
6. **Methodology 2 - Actuator mechanical investigation** *(full chapter)* - *Sources:* the six `docs/motor/` files in Section 2. *Write:* teardown, motor disassembly, driver diagnostics, and the leg/encoder swap **procedures + physical observations** (seating, offsets, mechanical behaviour). *Own figures:* teardown/disassembly photos, encoder/magnet swap photos. *Seam B:* each swap's *diagnostic reading* is Ming's - state the physical act and observation, then cite `[Ming, SS-TBD]` for the interpretation.
7. **Methodology 3 - Encoder electrical reverse-engineering** - *Sources:* `data/electrical/*.md`. *Write:* EEPROM register/config-map decode + datasheet-normality; encoder-board routing + pinout (iC-MU + transceiver); DB25 detection logic; bench-readout limits. *Own figures:* pinout diagram, EEPROM register-map table, DB25 pin-short diagram. *Seam C:* the EEPROM was physically *read* by Ming - you own the *decode/analysis*; cite `[Ming, SS-TBD]` for the comparative read that established both encoders identical.
8. **Evaluation, Limitations & Improvements** - *Sources:* `docs/subsystems/battery/battery-repair.md`, the swap logs, the RE pages. *Write:* pack balance/charge results; what the mechanical swaps physically ruled in/out; what the electrical RE established (fault is physical) vs bench-readout constraints. Pair each limitation with an improvement.
9. **Conclusion** - objectives met; skills gained (battery systems, PCB reverse-engineering, encoder hardware); future work (simulation, framed as planned, not done).
10. **References** (IEEE, numbered, cited inline `[n]`) and **Appendices** (Gantt chart; EEPROM register map; pinout diagrams; battery CAD iterations).

## 5. The actuator seam - what is yours vs cited

You and the companion report meet only at the actuator. Keep to the **hardware layer**:

| You WRITE (hardware) | You CITE, never write (Ming's) |
|---|---|
| the physical swap procedure (what was moved, how, seating/offset) | what SpotCheck / the visualiser showed, and what it meant |
| the encoder-board electrical decode, pinout, EEPROM register map | the "config identical -> fault is physical" *comparative read* (you own the decode; the read act is his) |
| teardown, disassembly, mechanical behaviour | the encoder repair (chip rework, air-gap change) |
| the DB25 bypass electrical logic | the field/walking-test behaviour and diagnosis |

Rule of thumb: **acts and hardware facts are yours; readings, interpretations, and the fix are cited.**

## 6. Seam handoff sentences (your side)

Use these forms; keep the placeholder until the sync step:

- **A (architecture):** "...the secondary output-encoder PCB (its control-signal role is described in Ming, SS-TBD)."
- **B (swaps):** "The secondary encoders were interchanged between the hind hip-X sockets with the magnets held fixed; both joints then responded to articulation (the diagnostic interpretation is reported in Ming, SS-TBD)."
- **C (EEPROM):** "The configuration EEPROM decodes to `MODEA=7` ExtSSI...; the comparative bench read establishing both encoders byte-identical is reported in Ming, SS-TBD."
- **Repair (E):** "...localising the fault to a physical part; the subsequent repair is reported in Ming, SS-TBD."

## 7. Figures you own

battery pack photos + CAD (spacer, V2 brackets); BMS / SoC-cable repair photos; teardown + motor-disassembly photos; encoder/magnet **swap** photos; encoder-board pinout diagram; EEPROM register-map table; DB25 pin-short diagram. Do **not** use SpotCheck tables, `/joint_states` plots, field-test stills, camera screenshots, or FX23 board figures - those are Ming's.

## 8. Writing sequence

1. **Draft** each section from its mapped sources (Section 4), in the register of Section 9, using the glossary of Section 10. Own only the hardware layer; drop in the Section-6 premise sentences with `SS-TBD` placeholders.
2. **Number** your sections and record the numbers.
3. **Sync** (with the person coordinating both reports): exchange section numbers and replace every `[Ming, SS-TBD]` with the real section reference; confirm each seam is exactly one cited sentence on your side.
4. **Overlap audit:** the two finished reports are compared - no shared sentence except the cited premises, no shared figure. Fix any drift by compressing to a citation.
5. **Finalise:** IEEE references, Gantt appendix, figure/table numbering + lists, contents, title page.

## 9. Writing register

Match this across the whole report: agentless **passive, past tense, no first person** ("the packs were rebuilt", not "we rebuilt"). Paragraph shape: goal -> complication -> method -> result. **Justify every choice** in a clause. **Narrate dead ends** (e.g. the failed restoration attempt, the bench-readout that hit its limit) as findings. **State assumptions** before a claim. **Quantify and hedge** (give numbers with honest error context). **Reference every figure/table by number** ("as shown in Figure 4"). Define a term on first use, then use the canonical form (Section 10) only.

## 10. Glossary (canonical terms - use verbatim)

| Term | Refers to |
|---|---|
| **Spot** | the Boston Dynamics quadruped under repair |
| **hip-X (abduction) joint** | the abduction/adduction actuator of a leg; define once, then "hip-X" |
| **`left_hind_x`** | the specific faulty joint (left hind hip-X) |
| **primary encoder** | the motor-side IC-MHM 14-bit absolute Hall encoder |
| **secondary output encoder** | the iC-Haus iC-MU Hall-IC at the harmonic-drive output |
| **eL / eR** | the left / right secondary-encoder **PCBs** (never the magnets) |
| **mL / mR** | the left / right **magnets** (diametric rotor magnets) |
| **harmonic drive (50:1 reducer)** | the strain-wave gearbox on the hip-X motor |
| **air gap** | the chip-to-magnet spacing at the secondary encoder |
| **EEPROM config** | the 24C02 external config store on the encoder board |
| **BMS** | the CAN-based battery management system |
| **7s4p / INR18650-30Q** | pack topology / Samsung cell used |
| **DB25 cover bypass** | shorting payload-port cover-detect pins to clear the motor-power lockout |

Signal-layer terms (**SpotCheck**, **Encoder Health**, **`[E]`**, **`hl.hx`/`hr.hx`**, **seeding**) belong to Ming's report - if you must name one, cite him; do not build analysis on them.
