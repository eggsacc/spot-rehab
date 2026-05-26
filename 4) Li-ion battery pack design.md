****
**Date:** <font style="color:tomato; font-family:Consolas;">25-05-2026</font> 
**Duration:** 4hrs 

**Objective:** 
>Research & understand safety precautions when working with DIY lithium battery packs.

**Resources:** 
>[Beginner’s guide to building safe 18650 batteries](https://www.youtube.com/watch?v=tKg-jIrr_JE)
>[How to Build an eBike Battery](https://www.youtube.com/watch?v=ZxhIs_xxVY0)
>[Battery Thermal Management | LHS Materials](https://www.lhsmaterials.com/)
>[Phase Change Materials for EV Battery Thermal Management](https://www.emobility-engineering.com/phase-change-materials-ev-battery-thermal-management/)

****
## Work done
****
#### Fish paper
- A layer of fish paper is to be cut to shape and pasted across the terminals of the batteries to insulate the terminals to prevent accidental shorts.
#### Latent heat filler
- A phase-change material (PCM) is used to fill the gaps between the lithium cells.
- Heat energy from the batteries are absorbed by the material as it transitions from a solid to a liquid. The phase change of the PCM ensures the batteries stay at a constant, uniform temperature.
- In the even of thermal runaway, the sudden surge of heat can be safely absorbed to overcome the latent heat of fusion in the material instead, mitigating damage.
#### Spot power consumption estimate
- Spot battery rated ~500Wh, and the official datasheet suggests approximately 1.5hr of runtime on full charge.
- Assuming 1.5hrs to 20% battery, average power consumption by Spot is ~$0.8\times \frac{500}{1.5}\approx 267W$.
- User manual suggests a voltage supply of 38-52V. Hence, the current draw is in the range of $[5.13A, 7.03A]$.
#### Nickel strip sizing
- The original Boston Dynamics battery pack uses 12mm wide nickel strips. 
- The current rating for a 0.15 * 12mm pure nickel strip is 17A optimal and 25.5A acceptable.
- If we estimate the continuous power consumption of Spot to be 400W (50% margin), estimated current draw is $\approx 10.5A$ max. Per-cell current draw is only $\approx 2.63A$. 
- Hence, individual cell connection can use a 5mm nickel strip, and each 4s pack lead can use a 0.15 * 8mm pure nickel strip (11.33A optimal, 17A max).

## Roadblocks
****

## Next steps
****
- [ ] 

## Media
****
