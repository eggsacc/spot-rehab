****
**Date:** <font style="color:tomato; font-family:Consolas;">25-05-2026</font>
**Duration:** 4hrs
**Present:** _(add)_
**Subsystem:** 🔋 Power & Battery
**Outcome:** 🔧 WIP

**Objective:**
>Research & understand safety precautions when working with DIY lithium battery packs.

**Resources:**
>[Beginner's guide to building safe 18650 batteries](https://www.youtube.com/watch?v=tKg-jIrr_JE)
>[How to Build an eBike Battery](https://www.youtube.com/watch?v=ZxhIs_xxVY0)
>[Battery Thermal Management | LHS Materials](https://www.lhsmaterials.com/)
>[Phase Change Materials for EV Battery Thermal Management](https://www.emobility-engineering.com/phase-change-materials-ev-battery-thermal-management/)

****
## TL;DR
****
Desk-research session on safe DIY lithium-pack construction (fish-paper terminal insulation, PCM latent-heat filler for thermal management) plus rebuild sizing. Estimated Spot's draw at ~267 W average (~5–7 A), so cell-level links can use 5 mm nickel strip and each 4s pack lead a 0.15×8 mm pure-nickel strip.

## Work done
****
_Desk research + design calculations — no hardware work this session._

#### Research DIY pack safety & thermal management
- Reviewed guides on building safe 18650 packs and on battery thermal management (PCM).

#### Estimate power draw & size nickel strips
- Calculated Spot's average power draw and per-cell current to choose nickel-strip widths.

## Findings & data
****
- **Fish paper:** an insulating layer cut to shape and applied across the cell terminals to prevent accidental shorts.
- **PCM (phase-change material) latent-heat filler:** fills the gaps between cells; absorbs heat as it transitions solid→liquid, keeping cells at a uniform temperature. In thermal runaway, the surge of heat is absorbed by the material's latent heat of fusion, mitigating damage.
- **Spot power estimate:** battery rated ~500 Wh; datasheet ~1.5 h runtime. Assuming 1.5 h down to 20%, average power ≈ 0.8 × 500 / 1.5 ≈ **267 W**. Manual specifies a 38–52 V supply ⇒ current ≈ **5.13–7.03 A**.
- **Nickel strip ratings:** the original BD pack uses 12 mm nickel strips; a 0.15×12 mm pure-nickel strip is rated 17 A optimal / 25.5 A acceptable.
- At an estimated 400 W continuous (50% margin) ⇒ ~10.5 A max pack current; per-cell ≈ 2.63 A.

## Decisions
****
- **Decision:** Use 5 mm nickel strip for individual cell connections, and a 0.15×8 mm pure-nickel strip (11.33 A optimal, 17 A max) for each 4s pack lead.
  **Why:** Per-cell current is only ~2.63 A and pack max ~10.5 A, so these widths carry the load with margin.
  **Alternatives considered:** Matching the original 12 mm strips — overkill for the actual current.
- **Decision (design intent):** Include fish-paper terminal insulation and PCM latent-heat filler in the rebuilt pack.
  **Why:** Safety — prevent accidental shorts and manage thermal runaway.

## Roadblocks
****
- —

## Next steps
****
- —

## Media
****
- _(none)_
