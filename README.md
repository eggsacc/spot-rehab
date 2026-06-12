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
> **❌ Non-operational** — battery pack #1 rebuilt & charging; robot still down pending hind-leg actuator diagnosis.

| | |
|---|---|
| 📅 **Last session** | 11-06-2026 — Battery fault diagnosis & re-weld (full charge achieved) |
| 🎯 **Current focus** | 🦿 Actuators & Legs (hind-leg motor) · 🔋 2nd battery pack |
| 🚧 **Blocking issue** | Left hind leg fails self-right; 2nd battery pack pending improved brackets |

---

## 📊 Subsystem Status

| Subsystem | Flag | Active | Notes |
|-----------|:----:|:------:|-------|
| 🔋 **Power & Battery** | 🔧 `WIP` |  | Pack #1 rebuilt & verified (full charge) — see [battery repair report](docs/subsystems/battery/battery-repair.md); 2nd pack pending |
| 🦿 **Actuators & Legs** | 🔧 `WIP` | 👈 | Left hind leg fails self-right; actuators move but motion stuck — under investigation |
| 🧠 **Compute & Mainboard** | ⬜ `N/A` |  | Not yet assessed |
| 📷 **Sensors & Cameras** | ⬜ `N/A` |  | Not yet assessed |
| 📡 **Comms & Networking** | ⬜ `N/A` |  | Not yet assessed |
| 🦴 **Chassis & Mechanical** | ⬜ `N/A` |  | Not yet assessed |

<sub>**Flags** — ✅ `PASS` functional & verified · ❌ `FAIL` confirmed fault, needs repair · 🔧 `WIP` currently being worked on · ⬜ `N/A` not yet assessed</sub>

---

## 🗒️ Repair Log

Newest first — full logs in [`docs/repair-log/`](docs/repair-log/).

> [!TIP]
> 📄 **Consolidated subsystem report:** [Battery pack repair](docs/subsystems/battery/battery-repair.md)

| Date | Session | Outcome |
|------|---------|:------:|
| 11-06-2026 | [Battery fault diagnosis & re-weld](docs/repair-log/2026-06-11-battery-assembly-5.md) | 🔧 |
| 05-06-2026 | [Battery diagnostics & Spot update](docs/repair-log/2026-06-05-sw-update-and-test.md) | 🔧 |
| 04-06-2026 | [Battery assembly — BMS & charge test](docs/repair-log/2026-06-04-battery-assembly-4.md) | ✅ |
| 02-06-2026 | [Replacement battery assembly (3)](docs/repair-log/2026-06-02-battery-assembly-3.md) | 🔧 |
| 29-05-2026 | [Replacement battery assembly (2)](docs/repair-log/2026-05-29-battery-assembly-2.md) | 🔧 |
| 28-05-2026 | [Replacement battery assembly (1)](docs/repair-log/2026-05-28-battery-assembly.md) | 🔧 |
| 25-05-2026 | [CAD design of battery spacer](docs/repair-log/2026-05-25-cad-battery-spacer.md) | ✅ |
| 25-05-2026 | [DIY Li-ion pack design & safety](docs/repair-log/2026-05-25-battery-pack-design.md) | ✅ |
| 21-05-2026 | [Battery disassembly & sourcing replacement](docs/repair-log/2026-05-21-battery-disassembly-sourcing.md) | ✅ |
| 20-05-2026 | [Battery restoration attempt](docs/repair-log/2026-05-20-battery-restoration-attempt.md) | ✅ |
| 13-05-2026 | [Battery & controller inspection](docs/repair-log/2026-05-13-battery-controller-inspection.md) | ✅ |

---

## 🗂️ Repository Layout

```
Spot/
├── README.md                  ← Project overview & status board (this file)
├── templates/
│   └── dev-log-template.md     ← Copy this to start a new session log
└── docs/
    ├── assets/                 ← Shared images & media, referenced by all docs
    ├── repair-log/             ← Dated session logs (one file per session)
    ├── software-log/           ← Software / setup session logs
    └── subsystems/             ← Consolidated per-subsystem reports
        ├── battery/battery-repair.md
        └── software/jazzysetup.md
```

> [!TIP]
> Session logs live in `docs/repair-log/`, named `YYYY-MM-DD-short-objective.md` so they sort chronologically.

---

## 📝 Logging a Session

1. **Copy** [`templates/dev-log-template.md`](templates/dev-log-template.md) into `docs/repair-log/`, named `YYYY-MM-DD-short-objective.md`.
2. **Header** — fill in Date, Duration, Present, Subsystem, and the Outcome flag.
3. **Body** — split your notes by kind so nothing gets buried:
   - **Work done** → the steps you took.
   - **Findings & data** → specs, measurements, part numbers (the stuff you'll cite in the report).
   - **Decisions** → what you chose, *why*, and what you ruled out.
4. **Roadblocks** + **Next steps** — use checkboxes for follow-ups.
5. **Update** the [Subsystem Status](#-subsystem-status) board and the [Repair Log](#-repair-log) index above.

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

<div align="center"><sub>Last updated: 2026-06-12</sub></div>
