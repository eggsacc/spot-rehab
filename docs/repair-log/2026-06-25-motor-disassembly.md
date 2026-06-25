# Leg motor assembly teardown

**Date:** <font style="color:tomato; font-family:Consolas;">25-04-2026</font>

**Duration:** 4hrs

**People:** Ming, Yizhang

**Subsystem:** 🔋 Power & Battery

**Outcome:** ✅ Complete

**Objective:**
>Disassemble leg motors to further troubleshoot static angle feedback issue.

**Resources:**
NIL

****
## TL;DR

Disassembled hip (X) motor and identified a second hall effect sensor within supposedly to measure the actual joint position after harmonic drive reduction.

## Work done

#### Spot amputation
- Spot was once again opened and had both hind legs amputated for inspection.

#### Disassembly of hip (X) motor
- To isolate the hip abduction (X) motor, the hip flexion (Y) motor can be removed from the rotor housing by unscrewing 4 _very tight_ torx screws (thank god it wasn't hex).
- A flange acting as both the cover and mechanical limits to the X-motor can be removed by unscrewing 8 _very tight_ M3 hex screws.
- The X-motor assembly can be pulled apart with some force; without the flange, the assembly is held together by a snug fit between the rotor bearing and housing.

## Findings & data
- 50:1 harmonic reducer used in X-motor
- Secondary IC-Haus hall effect sensor founs beside the harmonic drive input.
- All the screws used inside the motor assembly (e.g those underneath the flange, output shaft and those holding the stator down) are labelled numerically. Perhaps this is the tightening pattern to ensure the rotor is properly centered?

## Decisions
>**Decision:** Investigate the secondary encoder in detail next session and compare to other leg.

**Why:** Motor driver and cable swaps already eliminated the possibility of faulty drivers and communication failures. The secondary encoder which was not exposed before is now the primary suspect for the static/unresponsive joint angle feedback; this is the sensor theorized to feedback the actual joint angles post reduction.

**Alternatives considered:** Investigate the encoder diametric magnet for the axial absolute encoder. However inspection and comparison with the working leg reveals no binding/misplacement of magnet. This is also an unlikely failure mode as the IC-MHM encoder used has 4 hall sensors and is extremely robust; small deviations in magnet placement should had negligible effects and not cause frozen joint readings.

## Roadblocks
NIL

## Next steps
- [ ] Disassemble right leg hip (X) motor
- [ ] In-depth diagnostics of secondary hall effect sensor

## Media
![alt text](../assets/secondary-hall-sensor.jpg)
![alt text](../assets/harmonic-reducer.jpg)

