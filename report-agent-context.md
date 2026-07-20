# Report Agent — Session Context & Handoff

**Purpose:** everything needed to modify Yizhang's UROP report in a future chat without
re-deriving context. Read this file first, then edit `report/urop-report.md` and rebuild.

- **Report deliverable:** `report/urop-report.docx` (built) · **source:** `report/urop-report.md` · **build script:** `report/build-docx.py`
- **Authoritative spec:** `yizhang-report-agent-brief.md` (root) — the build brief; this file operationalises it.
- **Status:** full draft written & built. Two title-page facts pending (`[TBC]`): author full name + matriculation number. 11 `[Ming, SS-TBD]` seam placeholders await the sync step.
- **Repo root:** `C:\Users\yizha\OneDrive\Desktop\spot-rehab` · Windows 11 · PowerShell primary, Bash (git-bash) available · Python 3.13.

---

## 1. The task in one paragraph

Yizhang + Ming repaired a Boston Dynamics **Spot** quadruped (NUS UROP, CDE2605). Yizhang's
report covers **(1) the power/battery rebuild (full)** and **(2) the hardware layer of the
faulty `left_hind_x` hip actuator** — teardown, mechanical/encoder swaps, and encoder-board
electrical reverse-engineering — stopping at *"the fault is a physical hardware difference"*.
Everything on the **signal/diagnostic layer** and the **encoder repair** is **Ming's** and is
cited, never written, via `[Ming, SS-TBD]` placeholders (resolved later at a "sync" step).
Repo-only sourcing; invent nothing; sample reports are for **structure only** (isolated content).

**Thesis (every section serves it):** *Rebuilding Spot's power system and physically/electrically
reverse-engineering its faulty hip actuator to characterise the hardware and localise the fault
to a physical part.*

---

## 2. Decisions already made (from user)

| Decision | Choice |
|---|---|
| Output format | **Word `.docx`** (drafted in Markdown, converted with pandoc) |
| Battery scope | **Both packs, as completed** (pack #1 full arc + pack #2 V2). NB: goes beyond `battery-repair.md`, which framed pack #2 as future work; matches README + 16–18 Jun logs. |
| AY / term (title page) | **AY2025/2026 Special Term** |
| Register/structure | Fuller **numbered Sample-1 style**: List of Figures/Tables, 3 methodology chapters, appendices. (User delegated format: "decide what to keep yourself".) |
| Figures | **Embed real repo images** (owned-only), manual "**Figure N —**" captions. |

**Still pending / likely feedback areas:** insert name + matric (`[TBC]`); resolve 11
`[Ming, SS-TBD]`; possibly move **DB25 bypass** from Methodology 3 → Methodology 1 (brief maps
it to M1; I placed it in M3 as connector RE); tune figure density / section depth; overlap audit
vs Ming's report.

---

## 3. Build toolchain & how to rebuild

**Deps (already installed this machine):** `pypandoc-binary` (pandoc 3.9), `Pillow` 12, `pypdf` 6.14.
If missing: `pip install pypandoc-binary Pillow pypdf`. **System pandoc is NOT on PATH — use pypandoc.**

**Rebuild after editing the md:**
```bash
cd "C:/Users/yizha/OneDrive/Desktop/spot-rehab/report"
python build-docx.py       # -> urop-report.docx (~11 MB)
```

**What `build-docx.py` does (know before editing):**
- Downscales every referenced image to max 1500 px into a temp `.build-assets/` (photos→JPEG q82;
  diagram PNGs kept as PNG — see `DIAGRAM_PNGS` set in the script). Source images are untouched.
  Without this the docx is ~50 MB.
- **Page breaks:** the md uses `<!-- PB -->` marker lines; the script converts each to an openxml
  `<w:br w:type="page"/>`. **⚠ Do NOT write `\newpage`** — the leading `\n` gets mangled to a
  newline when writing via tools; always use `<!-- PB -->`.
- Contents = pandoc `--toc` → a **Word field**; in Word press **F9 / right-click → Update Field**
  to populate page numbers (empty until then; expected).
- Uses `-f markdown-implicit_figures` so manual `**Figure N —**` captions aren't double-numbered.

**Verify a build (structure sanity):**
```python
import zipfile; d=zipfile.ZipFile("urop-report.docx").read("word/document.xml").decode("utf-8","ignore")
# expect: 37 media, 3 page breaks (w:type="page"), 10 tables, "TOC" present
```
Last good build: **37 media · 3 page breaks · 10 tables · TOC field · 11.2 MB**.
**Seams = 11** in the md (`grep -oE '\[Ming, SS-TBD\]' urop-report.md`). The *docx* substring
`count("SS-TBD")` reports **13** — an artifact of pandoc splitting Word text runs, not extra
seams. Trust the md count.

**Render docx→text for QA** (write to utf-8 file; console cp1252 chokes on `−` U+2212):
`pypandoc.convert_file("urop-report.docx","plain",extra_args=["--wrap=none"])`.

---

## 4. Report structure → source map

Body headings are numbered by user's reading; front/back matter is `{.unnumbered}`. Section
numbers below are *logical* (Word will auto-number from the H1s).

| # | Section | Primary sources | Seam citation |
|---|---|---|---|
| — | Title page (YAML block) | brief §4.1; author `[TBC]` | — |
| — | List of Figures / Tables | manual lists (33 figs, 8 tables) | — |
| 1 | Introduction | `README.md` | scope-note seam |
| 2 | Background | `battery-repair.md`, `docs/battery/2026-05-13…`, `README.md`, `data/electrical/ic-mu-electrical-connection.md`, `docs/motor/2026-06-25-motor-disassembly.md` | **A**: encoder role |
| 3 | Methodology 1 — Power-system rebuild | **all** `docs/battery/*.md` + `battery-repair.md` | — |
| 4 | Methodology 2 — Actuator mechanical | 6 in-scope `docs/motor/*` (see §5) | **B**: each swap (Table 5 + articulation + offset Table 7) |
| 5 | Methodology 3 — Encoder electrical RE | `data/electrical/*.md` (+assets); DB25 bypass here | **C**: byte-identical read |
| 6 | Evaluation, Limitations & Improvements | swap logs, RE pages, `battery-repair.md` | cited |
| 7 | Conclusion | — (simulation = **planned**, not done) | repair (E) |
| — | References [1]–[8] IEEE | repo-cited URLs | — |
| — | Appendices A–E | A Gantt · B full EEPROM map · C pinout · D DB25 shorts · E battery CAD | — |

---

## 5. Source-log inventory (repo-only)

**IN SCOPE — battery** (`docs/battery/`, all 13):
`2026-05-13-battery-controller-inspection`, `05-20-battery-restoration-attempt`,
`05-21-battery-disassembly-sourcing`, `05-25-battery-pack-design`, `05-25-cad-battery-spacer`,
`05-28-battery-assembly`, `05-29-battery-assembly-2`, `06-02-battery-assembly-3`,
`06-04-battery-assembly-4`, `06-05-sw-update-and-test`, `06-11-battery-assembly-5`,
`06-16-battery-design-v2`, `06-17-battery-2-assembly`. Consolidated: `docs/subsystems/battery/battery-repair.md`.
(SoC-cable repair detail is inside `docs/motor/2026-06-18-driver-disgnostic.md`.)

**IN SCOPE — actuator mechanical** (`docs/motor/`, exactly these 6):
`2026-06-15-robot-teardown`, `2026-06-18-driver-disgnostic`, `2026-06-19-leg-component-swap`,
`2026-06-25-motor-disassembly`, `2026-06-30-output-encoder-swap`, `2026-07-16-encoder-read-attempt`.

**IN SCOPE — electrical RE** (`data/electrical/`): `ic-mu-electrical-connection.md`,
`ic-mu-eeprom-config-map.md`, `db25-cover-connection.md` (+ `assets/*.png`).

**OUT OF SCOPE — Ming's; do NOT use/cite as own** (`docs/motor/`): `06-12-joint-diagnosis`,
`07-01-spotcheck-diagnosis`, `07-02-encoder-eeprom-probe` (Ming did the *read*; my *decode* uses
the data page), `07-04`/`07-06`-fx23-breakout, `07-14-encoder-chip-swap`,
`07-15-encoder-board-swap-spotcheck3`, `07-17-encoder-airgap-fix-camera-repair`.
**Never use** `data/software/*` or `docs/software/*`.

**Log fixes applied silently (keep applying):** `2026-06-25-motor-disassembly.md` has an internal
date typo "25-04-2026" → use **25 Jun**; its subsystem tag "Power & Battery" is wrong → **actuator**.
Battery topology stated as **14s4p = two 7s4p sub-packs** (reconciles brief's "7s4p" vs consolidated "14s4p").

---

## 6. Scope seam — mine (write) vs Ming's (cite `[Ming, SS-TBD]`)

| I WRITE (hardware/acts/facts) | I CITE, never write (Ming's) |
|---|---|
| physical swap procedures; what moved, seating/offset | what SpotCheck/visualiser showed & meant |
| encoder-board decode, pinout, EEPROM register map | the "config identical → fault physical" **comparative read** (I own decode; read act is his) |
| teardown, disassembly, mechanical behaviour | encoder **repair** (chip rework, air-gap change) |
| DB25 bypass electrical logic | field/walking-test behaviour & diagnosis |

**Rule of thumb:** acts + hardware facts = mine; readings, interpretations, the fix = cited.
**Forbidden terms** (only appear guarded/cited): SpotCheck, `/joint_states`, Encoder Health, `[E]`,
`hl.hx`/`hr.hx`, seeding, FX23/breakout board (Ming's design — don't claim), cameras, ROS 2, SDK,
Autowalk, GraphNav, chip rework, air-gap. The 11 seams live at: Intro scope-note; Background
(encoder role); M2 (Table 5, "responded to articulation", Table 7 offset); M3 (byte-identical read);
Evaluation; Conclusion (repair). **Sync step:** replace every `[Ming, SS-TBD]` with real section #s.

---

## 7. Figures & tables

- **33 figures / 37 image files** (Figs 14,16,17,19 pair two images). All owned. Manual captions.
- **8 tables.** Full figure→file mapping is inline in `urop-report.md` (grep `!\[`).
- **Owned image sources:** `docs/assets/*.jpg|png` (battery, teardown, driver, swap, testpad) and
  `data/electrical/assets/*.png` (offset-enc-pcb-components, pinout-connections, testpads-connection, db25-cover-shorts).
- **Do NOT add these (Ming's / readings):** `spotcheck-*`, `hip-joint-angles.png`, `out-of-bounds*`,
  `hr-hx-out-of-bounds-boot`, `visualiser*`, `sensor-misread-*`, `eeprom-hexdump-left/right`,
  `fx23-breakout-*`, `walking*`, `stair-climb-*`, `camera-*`, `graph-*`, `data-*`, `motor-lockout`.
- Videos (`.MOV/.mp4`) can't embed in docx — not used.
- `docs/assets/` **is populated** on disk (git-tracked). Glob brace `**/*.{jpg,png}` mysteriously
  returns nothing here — use single-ext globs or `git ls-files | grep`.

---

## 8. Distilled data digest (verify edits without re-reading logs)

**Battery:** 56× **Samsung INR18650-30Q** (3000 mAh, 15 A cont/30 A peak) · **14s4p = 2×7s4p** ·
~500 Wh, ~1.5 h · BMS: single PCB, STM32, **CAN** · 28 pads (pos long edges, neg centre) ·
5 NTC thermistors per sub-pack. Dead cells ~**90 mV** (min safe 2.5 V); warm + collapse =
internal-short self-discharge → unrecoverable. Power est: ~**267 W** avg (~5.1–7.0 A @ 38–52 V),
50 % margin → ~**10.5 A** pack peak, ~**2.63 A/cell**. Nickel: **0.1×8 mm** cell links,
**0.15×12 mm** pack leads (OEM uses 12 mm throughout). Spacer **PC-CF** (V1, maybe PETG),
**ABS-GF** (V2). Welder **Error 22** = cracked cap solder joint. Pack #1: groups **1/2/8** bad
positive welds; group **1 = −0.5 V phantom** (broken *negative* weld, disconnected group) →
**reweld all** → first full balanced charge. Balance index: **0.213** bad (>0.1 needs balancing;
auto-balance needs fw **>V45**, pack was **V33**) → **pack #2 = 0.02** healthy. Firmware
**V3.x→V4.1.1→V5.1.6** (don't skip majors); Spot fw 3.3.1, controller 3.3.2. Pack #2 avg cell
**3.446 V ±0.002**; built 1 person/1 afternoon vs pack #1 2 people/3 days (laser-cut slotted strips).

**Actuator:** **hip-X** = abduction/adduction; **`left_hind_x`** faulty. **Primary encoder** =
motor-side **iC-MHM 14-bit absolute Hall** (rotor angle, robust 4-Hall). **Secondary output
encoder** = **iC-Haus iC-MU** Hall-IC at **harmonic-drive output** (post-reduction joint angle).
**Harmonic drive 50:1**. Hip motor **20 poles / 18 slots** (q=0.9), phase R ≈ **0.5 Ω**.
Swaps & physical outcome: driver boards (identical → fault stayed **left socket**); cables
(identical → stayed left); **full rotor+encoder+load-cell** assembly (fault moved to right **but
load-cell hard fault** — load cells calibrated per joint); **output-encoder PCB only** (fault
**cleared**, residual **offset**). Offsets from centre: **left ~0.53 rad (≈30°)**,
**right ~0.12 rad (≈6.8°)**; travel range consistent across joints; housing re-clock resolution
**45°** (8 screws). Controller board has epoxy coating (can't probe test points).

**Encoder board:** iC-MU + external config **EEPROM** + **LTC2863 RS-485/422** transceiver;
**ExtSSI slave, MODEA=7**. Wiring: **PA0→GND** (BiSS fallback), **PA1←RO** (MA clk),
**PA2→GND** (SLI), **PA3→DI** (SLO). Key EEPROM regs: `0x05` ENAC=1 (amplitude ctrl),
`0x0B` MODEA=7 ExtSSI / MODEB=0 ABZ, `0x0E` FILT4 (39 dB,14-bit), `0x0F` MPC=5 (≤19-bit),
`0x13–14` RESABZ=**16 384 edges**, `0x21–22` **CRC16=0x52A8 valid**, `0x3E–3F` MFG_ID=0x6943="iC".
Offset/preset block erased (0xFF), CRC8 mismatch = unused (not a fault). **Routing:** encoder wired
**direct to driver STM32** (NOT to main connector); driver streams over its own CAN. **Bench read
failed:** need RS-485/422 transceiver hardware (had none); driver STM32 unpowered (3.3 V rail
0.4 V; **LT3029** LDO not enabled by 5 V; 5 V rail OK 4.994 V; 0.11 A draw); no edges on A/Y lines.
**DB25 bypass:** 4 sets of cover pins shorted → replicate on open port to clear "uncovered payload
port" motor-power lockout.

---

## 9. References list (IEEE, in the report)

[1] Spot Battery SDS (Boston Dynamics) · [2] Samsung 30Q (Falcon PEV) · [3] Spot teardown (Reddit
r/IndiaTech) · [4] LHS Materials thermal · [5] iC-MU datasheet (ave-nl mirror) · [6] LTC2863
(Analog Devices) · [7] LT3029 (Analog Devices) · [8] Spot Software Updates (Boston Dynamics).
All URLs already in repo logs — do not add new external data.

---

## 10. Gotchas / environment quirks (don't rediscover)

- **PDF reading:** the `Read` tool fails on PDFs (`pdftoppm`/poppler absent). Use `pypdf` to
  extract text. Sample reports: `Sample UROP Reports/Sample UROP Report 1.pdf` (34 pp, detailed
  numbered style) & `2.pdf` (18 pp, compact). **Structure only — content is isolated, never cite.**
- **Page breaks:** `<!-- PB -->` marker, never `\newpage`.
- **docx size:** always via `build-docx.py` (downscales); raw embed = 50 MB.
- **Glob brace quirk:** `{jpg,png}` returns nothing; use single patterns / `git ls-files`.
- **Console encoding:** write QA text to utf-8 files (cp1252 can't print `−`).
- Sample-PDF text extracts were saved to the session scratchpad (ephemeral — regenerate if needed).

---

## 11. Fast start for next session

1. Read this file + `report/urop-report.md`. (Re-read specific logs from §5 only if a claim is challenged.)
2. Make edits in `report/urop-report.md` (keep passive past tense, no first person; justify choices;
   narrate dead-ends; reference figures/tables by number; keep seams to one cited sentence).
3. `cd report && python build-docx.py`, then verify counts (§3).
4. Respect §6 scope: never add Ming's signal-layer content or images (§7).
