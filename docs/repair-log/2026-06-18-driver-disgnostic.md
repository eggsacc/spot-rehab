# Battery #2 SoC cable repair and driver diagnostics

**Date:** <font style="color:tomato; font-family:Consolas;">18-06-2026</font>

**Duration:** 7hr

**People:** Ming, Yizhang

**Subsystem:** 🦿 Actuators & Legs, 🔋 Power & Battery

**Outcome:** ✅ Complete

**Objective:**
>Repair broken flat flex cable for SoC on battery pack #2, concluding battery repair. Further diagnose left hip motor issue.

**Resources:**
NIL

****
## TL;DR

Battery pack #2 complete, SoC flex cable repaired and is able to achieve full charge. Left hip motor experiences same issues after swapping driver PCB. It can be deduced that the drivers themselves are not the problem, but rather the encoder feedback.

## Work done
#### Battery pack #2 flex cable repair
- After assembling battery pack #2, the SoC button was unresponsive. Inspecting the connectors uncovers that the SoC flat flex cable was sheared near the bottom.
- The ends of the broken cable were soldered together after scraping off the plastic insulation layer on both ends to expose the copper traces.
- More kapton tape was used to secure the cable down and prevent tension/stresses on the solder joints.
- Flex cable connector fastener was also missing!!
- A piece of cardboard did the trick to hold it in temporarily.
- Pressing the SoC again successfully reveals the charge level.

#### Battery pack #2 charge test & update
- Pack #2 was left to charge for about 1hr until the charger status LED turned a static green, indicating a full charge.
- Pressing the SoC indeed shows a full charge
- Pack #2 is inserted into Spot and powered on. The controller prompted for a firmware update for the battery which successfully completed.
- Under battery info, the balance value of pack #2 is 0.02, which is extremely healthy.
- Battery repair concludes!

#### Comparison of left, right rear hip motor drivers
- It was hypothesized that the encoder on the left hip motor driver was defective, hence the stale angle updates and lack of motion.
- Both legs were dismantled from Spot turning it into a double amputee.
- Both drivers were retrieved from the hip motors and compared.
- Both drivers were identical and showed no signs of component degradation.
- Rotating both hip motors manually shows the diametric magnet is firmly seated and rotates in the opposite direction.
- The protrusion height of both the hip motor magnets were identical.

#### Swapping of motor drivers
- To furthur diagnose the issue, the left and right hip motor drivers were exchanged and the legs reinstalled on Spot.
- After turning on Spot and enabling motor power, the controller reports no errors from the motors.
- When attempting self-right as prompted by the controller, Spot enters the previous stuttering motion again with the left-hind leg unable to reach the target position.
- In the 3D model view, the reflected position of the left hind leg is still inaccurate and completely tucked under the robot.
- The right leg, however, moves as expected and motion was observed from the hip motors.

## Findings & data
#### Battery pack #2 balance
- 0.02 as reported in battery statistics under Admin console.

#### Hip motor specs
- 20 poles
- 18 slots
- $q=18/20=0.9$
- Phase resistance: $0.5\omega$

## Decisions
>**Decision:**

**Why:**

**Alternatives considered:**

## Roadblocks
- _Anything that blocked progress or is still unresolved._

## Next steps
- [ ] _Action item for next session_

## Media
![[filename.jpg]]
