# What "encoder health < 20%" Actually Meant

**Subject:** Boston Dynamics Spot Enterprise — hind-hip output encoder (iC-Haus iC-MU, 1.28 mm pole width, radial/nonius ring)
**Status:** Resolved. Root cause identified and fixed by mechanical means.
**Date:** July 2026

---

## 1. Conclusion

**"Encoder health %" is a signal-amplitude / AGC-gain-headroom metric, not a diagnostic of the encoder IC, its configuration, or its data link.**

The iC-MU runs automatic gain control on both the master and nonius Hall tracks (`ENAC=1`, EEPROM `0x05 = 0x88`, confirmed by dump). The AGC servos the sensed sine/cosine track amplitudes to a fixed target (~2 Vpp internally) by adjusting a coarse/fine gain pair (`ACGAIN_x` / `AFGAIN_x`, readable at SER `0x2B` / `0x2F`). The applied gain is therefore a direct, continuously-varying inverse proxy for received field strength.

BD's exposed number is almost certainly a normalisation of the remaining gain reserve:

```
health% ≈ (1 − applied_gain / max_gain) × 100      (form unconfirmed)
```

`< 20%` = the AGC is near its rail = the sensor is scraping the bottom of its usable field. It is a **margin** number, not a pass/fail on the die.

**The physical cause of the low margin was excessive radial airgap between the sensor face and the nonius ring OD**, introduced by the reassembly stack-up (`LIN=1` in the EEPROM confirms radial scan, so the critical dimension is radial standoff, not axial).

---

## 2. The decisive evidence

### 2.1 The filing experiment (single-variable, controlled)

The spacer between the encoder PCB and the housing was filed down, reducing the sensor-to-ring gap by **0.15 mm**. Nothing else changed — no chip, no EEPROM write, no firmware, no calibration parameter, no wiring.

Result on the treated side:
- `encoder health < 20%` — **gone**
- intermittent `sensor misread` — **gone**

This is the strongest single datum in the entire investigation. A metric that moves monotonically and exclusively with airgap, when airgap is the only variable touched, is an airgap-dependent metric. For the iC-MU there is exactly one such quantity: track signal amplitude, expressed through AGC gain.

### 2.2 Why 0.15 mm is a large change (and not a marginal tweak)

For a periodic magnetic scale, field amplitude at standoff `z` falls approximately as:

```
A(z) ∝ exp(−2π·z / λ)
```

With iC-MU pole width 1.28 mm → spatial period **λ = 2.56 mm** → decay constant **λ/2π = 0.407 mm**.

```
gain from −0.15 mm  =  exp(0.15 / 0.407)  =  ×1.45   (+45%,  +3.2 dB)
```

A 45% amplitude increase is more than enough to lift a marginally-railed AGC back into regulation. **This validates the earlier scale argument: at a 1.28 mm pole width, 50–150 µm of tolerance stack-up is not a rounding error — it is a large fraction of the working budget.** "Very little play" at the assembly is not a defence.

### 2.3 The eliminations that preceded it

Each of these independently rules out a competing explanation:

| Test performed | Result | What it kills |
|---|---|---|
| iC-MU chip desoldered, replaced with new OEM part | `<20%` health **persisted** | The die. A brand-new manufacturer part reading the same value cannot be a degraded chip. |
| Both magnet rings swapped L↔R across housings | Fault did not follow the ring | Ring magnetisation / demagnetised ring. |
| Both stator housings swapped | Fault did not follow the stator | Stator-side mechanics. |
| Driver PCB swapped L↔R | Fault did not follow the board | STM32, power stage, rotor-side iC-MHM, driver firmware. |
| Mainboard→driver harness swapped L↔R | Fault did not move | Harness, mainboard channel. |
| Full EEPROM dump + byte-level decode vs. Table 8 | CRC16 `0x52A8` **matches**; `DEV_ID="MU"`, `MFG_ID="iC"`, `MPC=0x5` matches physically-counted 32/31 ring geometry | Config corruption, boot-read failure, wrong mode. |

By elimination, the only surviving variable was the **magnetic coupling geometry** — and the filing experiment then confirmed it positively rather than by exclusion.

### 2.4 The "both hind hips" clue

After reassembly, **both** hind hips reported `<20%` — including the never-swapped right side. Both had been opened. The front hips (untouched) were the obvious controls and were never read. The filing experiment made that control read unnecessary: it demonstrated causality directly rather than by comparison.

Interpretation: reassembly systematically restored the encoder PCB at a slightly greater radial standoff than factory — consistent with a spacer/seating-face stack-up (backplate seating, flex-to-backplate bondline, spacer thickness, screw torque, possible burr or debris).

---

## 3. The `sensor misread` fault has the same root cause

This is a significant retroactive correction.

The misread warning **cleared at the same instant as the health metric, from the same 0.15 mm mechanical change.** Two symptoms that remit together under a single physical intervention share a cause.

Mechanism:
- EEPROM `0x0C` → `CFGEW = 0x00` → **all error/warning sources are enabled and visible on the frame's nERR/nWARN bits.**
- Per the iC-MU error map, the amplitude limit conditions (`Ax_MIN` / `Ax_MAX`) are asserted on **both** the error and warning bits when `CFGEW = 0`.
- With the AGC railed, amplitude intermittently dips below `Ax_MIN` → nERR asserts on that frame → the motor-driver STM32 logs it as `enc.hl.hx misread`.
- Non-blocking, because position data is still nominally valid — exactly the observed behaviour.

### Hypotheses now dead — do not revive

| Hypothesis | Why it's dead |
|---|---|
| **CRC8 blank-offset-block path** (`0x2F` stored `0xFF` vs. calculated `0x67`, cyclic check with `NCHK_CRC=0` raising `CRC_ERR`) | The CRC8 mismatch is real and unchanged, yet the misread disappeared after filing. A static config byte cannot explain a symptom that a mechanical adjustment removed. **The proposed fix — writing `0x67` to `0x2F` — is unnecessary.** The blank offset block is simply BD never programming a path (`OFF_ABZ`/`OFF_UVW`/`PRES_POS`) it does not use, since `MODE_ST=2` outputs raw master/nonius. |
| **BiSS fallback on EEPROM boot-read failure** (PA0 grounded → 32-bit frame vs. expected 38-bit → CRC window misalignment) | Same argument. Filing does not affect an I²C boot read. Also never explained the frozen angle. |
| **"Frozen and misread are two separate faults"** | Partially superseded. The *frozen angle* was genuinely separate and was fixed by the chip replacement. The *misread* and the *health metric* are one fault. |
| **ExtSSI → BiSS EEPROM switch** (`0x0B`: `0x07` → `0x02`) to read `ACGAIN`/`AFGAIN`/`STATUS0/1` | No longer needed diagnostically. Only worth doing now if a quantitative gain readback is wanted for the report. |

---

## 4. Open item: the airgap magnitude claim

The recollection from the first teardown that the airgap is **"definitely larger than 2 mm"** is almost certainly a mismeasurement — probably taken to the PCB or backplate face rather than to the die's sensing surface, or including package and ring-glue thickness.

Reason: at `z = 2 mm`,

```
A(2.0) / A(0.3)  =  exp(−(2.0 − 0.3)/0.407)  =  exp(−4.18)  ≈  0.015
```

i.e. **~1.5% of the signal at a normal 0.3 mm gap, ~36 dB down.** No AGC has that range; the encoder would not have produced a valid absolute angle at all, let alone one that calibrates and walks. The iC-MU family at 1.28 mm pole width works at standoffs of order **0.1–0.5 mm**. Whatever was measured, it was not the magnetic gap.

**Caveat against over-claiming the fix:** because the decay is exponential, a 0.15 mm reduction yields ×1.45 *regardless of the absolute starting gap*. So the fact that the fix worked does **not** independently pin down the absolute airgap. It proves the system was sitting in the amplitude-limited regime; it does not measure where.

Worth doing for the report: measure the true standoff with feeler gauges or a depth mic to the die face, before and after.

---

## 5. Remaining work

- **Right hind hip still reports occasional misreads.** The fix is proven: file its spacer by 0.15 mm. Expect the health metric and the misreads to clear together — and that co-remission, reproduced on a second joint, would be a clean replication of the whole conclusion.
- Optional quantification (nice-to-have for the report, not required): passive scope capture of the ExtSSI frame → decode 14-bit raw master + 14-bit raw nonius (`MODE_ST=2`) → compute nonius sync margin `TOLSPON = raw_M − raw_N × 32/31` against the ±4.92° limit for `MPC=0x5`, mapped per angle, filed vs. unfiled joint. This would turn a qualitative "health went away" into a measured amplitude/alignment curve.

---

## 6. Summary statement for the report

> Spot's `encoder health < 20%` warning on the hind hips was not an encoder failure. The iC-MU output encoder runs automatic gain control on its Hall tracks; BD's health percentage reports the remaining AGC gain reserve, which is an inverse proxy for received magnetic field strength. Reassembly of the actuator left the sensor at an excessive radial standoff from the nonius ring, driving the AGC toward its rail and intermittently below the internal minimum-amplitude limit — which the motor driver logged as a `sensor misread`. Reducing the standoff by 0.15 mm, by filing the PCB-to-housing spacer, increased track amplitude by roughly 45% (field decays with a 0.407 mm constant at this 1.28 mm pole width) and cleared both symptoms simultaneously. Chip replacement, magnet-ring swaps, driver/harness swaps and a full EEPROM decode had all previously exonerated the electronics and configuration; the fault was purely mechanical tolerance stack-up in the magnetic gap.

---

## Appendix: relevant EEPROM fields

| Addr | Value | Field | Relevance |
|---|---|---|---|
| `0x05` | `88` | `ENAC=1`, `CIBM=8` | AGC active → gain is a live, gap-dependent quantity. **This is the field the health metric derives from.** |
| `0x0C` | `00` | `CFGEW=0` | All errors/warnings enabled → amplitude limits (`Ax_MIN`/`Ax_MAX`) surface on the frame nERR/nWARN bits → driver logs them as misreads. |
| `0x0E` | `14` | `LIN=1`, `FILT=4` | **Radial/linear scan** → critical gap is radial (sensor face to ring OD), not axial. |
| `0x0F` | `05` | `MPC=5` | 32 master / 31 nonius periods, 19-bit max. Sets ring circumference ≈ 32 × 2.56 mm ≈ 82 mm (Ø ≈ 26 mm). |
| `0x12` | `20` | `MODE_ST=2` | Raw master/nonius output → the offset/preset block is unused, which is why `0x23–0x2E` is blank and its CRC8 is stale. Not a fault. |
| `0x21–22` | `52 A8` | `CRC16` | **Matches.** Config integrity confirmed; boot-read failure ruled out. |
| `0x2F` | `FF` | `CRC8` | Stale vs. calculated `0x67`, over a never-programmed block. **Benign — do not "fix".** |
