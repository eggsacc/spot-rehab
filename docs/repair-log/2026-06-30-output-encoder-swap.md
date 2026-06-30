# Output encoder PCB swap

**Date:** <font style="color:tomato; font-family:Consolas;">30-06-2026</font>

**Duration:** 6hr

**People:** Ming, Yizhang

**Subsystem:** 🦿 Actuators & Legs

**Outcome:** ✅ Complete

**Objective:**
>Swap the output encoder modules for the hind hips and test to isolate root issue.

**Resources:**
>- [IC MU datasheet](https://ave-nl.com/wp-content/uploads/2021/12/MU_datasheet_F2en_AVE.pdf) 
>- [LTC2863 transceiver](https://www.analog.com/media/en/technical-documentation/data-sheets/2862345fc.pdf)

****
## TL;DR

First swapped hind hip's entire rotor assemblies, then only the output encoder PCB. The former relocated the frozen angle issue to the right hip, while the latter somehow resolved the issue and instead gave active, off-limit readings. Robot is unable to power up due to the angle out of range faults.

## Work done
#### Swap hind leg rotor assemblies
- The entire rotor assembly (main connector + encoder + force beedback module) was plucked out and swapped around.
- After reassembling Spot, powering it on reveals a loadcell error for the right hip.
- The live model viewer in the console reflects no angle updates for the right leg when manually jogged. The left hip works well.
- Robot is unable to power up due to loadcell error being categorized as a hard fault.

#### Swap hind hip output encoder + connector only
- Spot was amputated again. This time, only the main connector PCB including the encoder is removed and swapped.
- The rotors + loadcell assembly is placed back in their original stators. Apparently the load cells are calibrated per joint and swapping them likely resulted in the error above.
- The motor driver boards are also swapped back (they were swapped a long long time ago).
- After reassembly and powering up Spot, the loadcell error disappeared.
- Jogging the legs manually also reveals that the frozen angle issue is gone! Both hind hips reflect real time position changes in the console.
- However, the left hind hip seems to suffer from some offset issue. The controller also logs a angle off limits fault.
- The robot is unable to power on the motors due to the angle fault.
- The right hip, however, seems to reflect angles accurately.

#### Angle limits test
- Spot's 4 legs were manually jogged across the full range of motion and the 4 hip angle readings were recorded at the limits.
- The data shows that the sign of the hip joints are matched per-side: the angle limit when the legs are tucked beneath the robot is negative for the left-side hips and positive for the right.
- The data also shows a relatively centered range about the horizontal position.
- Comparing the left and right hips, the right hip had a consistant angle offset from the left. This infers a encoder calibration offset error.


## Findings & data
_Hard facts worth extracting: measurements, part numbers, specs, fault readings — the stuff you'll cite in the report later._
-

## Decisions
>**Decision:**

**Why:**

**Alternatives considered:**

## Roadblocks
- _Anything that blocked progress or is still unresolved._

## Next steps
- [ ] _Action item for next session_

## Media
![alt text](staged-assets/rotor-swap.jpg)
![alt text](staged-assets/encoder-closeup.jpg)
