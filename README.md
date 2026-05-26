<div align="center">

# 🐾 Spot Repair Log

**Diagnosing & repairing a Boston Dynamics _Spot_ quadruped robot**
NUS · Undergraduate Research Opportunities Programme (UROP)

</div>

---

## 📖 About

This repository is the shared engineering logbook for our UROP project: bringing a faulty Boston Dynamics **Spot** robot back to life. Every working session is recorded as a dated **dev log**, and this README is the dashboard — it tracks the health of each subsystem and what we're working on right now.

> [!NOTE]
> Starting a session? Copy [`templates/dev-log-template.md`](templates/dev-log-template.md), fill it in, and update the **[Subsystem Status](#-subsystem-status)** board below before you finish.

---

## 🤖 Robot Status

> [!WARNING]
> **❌ Non-operational** — battery pack disassembled for lithium-cell replacement.

| | |
|---|---|
| 📅 **Last session** | 21-05-2026 — battery cell teardown & cell sourcing |
| 🎯 **Current focus** | 🔋 Power & Battery |
| 🚧 **Blocking issue** | Sourcing replacement 18650 cells (Samsung INR18650-30Q) |

---

## 📊 Subsystem Status

| Subsystem | Flag | Active | Notes |
|-----------|:----:|:------:|-------|
| 🔋 **Power & Battery** | 🔧 `WIP` | 👈 | Replacing lithium cells; sourcing a cell supplier |
| 🦿 **Actuators & Legs** | ⬜ `N/A` |  | Not yet assessed |
| 🧠 **Compute & Mainboard** | ⬜ `N/A` |  | Not yet assessed |
| 📷 **Sensors & Cameras** | ⬜ `N/A` |  | Not yet assessed |
| 📡 **Comms & Networking** | ⬜ `N/A` |  | Not yet assessed |
| 🦴 **Chassis & Mechanical** | ⬜ `N/A` |  | Not yet assessed |

<sub>**Flags** — ✅ `PASS` functional & verified · ❌ `FAIL` confirmed fault, needs repair · 🔧 `WIP` currently being worked on · ⬜ `N/A` not yet assessed</sub>

---

## 🗂️ Repository Layout

```
Spot/
├── README.md                 ← Project overview & status board (this file)
├── example-dev-log.md.md     ← Reference: a completed dev log (battery teardown)
└── templates/
    └── dev-log-template.md   ← Copy this to start a new session log
```

> [!TIP]
> Keep session logs together in a `logs/` folder, named by date — e.g. `logs/2026-05-21-battery-teardown.md`.

---

## 📝 Logging a Session

1. **Copy** [`templates/dev-log-template.md`](templates/dev-log-template.md) and name it by date.
2. **Header** — fill in Date, Duration, Present, Subsystem, and the Outcome flag.
3. **Body** — split your notes by kind so nothing gets buried:
   - **Work done** → the steps you took.
   - **Findings & data** → specs, measurements, part numbers (the stuff you'll cite in the report).
   - **Decisions** → what you chose, *why*, and what you ruled out.
4. **Roadblocks** + **Next steps** — use checkboxes for follow-ups.
5. **Update the [Subsystem Status](#-subsystem-status) board** above if a subsystem's flag changed.

---

## 🔗 References

- [Spot Battery Safety Data Sheets (SDS)](https://support.bostondynamics.com/s/article/Spot-Battery-Safety-Data-Sheets-SDS-49922)

---

## 👥 Team

| Name | Role |
|------|------|
| _(your name)_ | UROP Researcher |
| _(partner name)_ | UROP Researcher |
| _(supervisor)_ | Faculty Supervisor |

---

<div align="center"><sub>Last updated: 2026-05-27</sub></div>
