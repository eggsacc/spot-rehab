<div align="center">

# 🐾 Spot Rehabilitation

**Diagnosing & repairing a Boston Dynamics _Spot_ quadruped robot**
NUS · Undergraduate Research Opportunities Programme (UROP)

</div>

---

## 📖 About

The Spot robot dog in NUS has not been a very good boi lately. This repository documents the abuse of Spot and hopefully a full recovery 🦴.

---

## 🤖 Robot Status

> [!WARNING] AMPUTATED
> **❌🦵🦵 Severely crippled:**  Currently a double amputee 😢😢

![alt text](spot-state.jpg)

| | |
|---|---|
| 📅 **Last session** | 18-06-2026 — Battery repair complete and motor diagnostics |
| 🎯 **Current focus** | 🦿 Actuators & Legs (hind-leg motor) |
| 🚧 **Blocking issue** | Left hind leg fails self-right |

---

## 📊 Subsystem Status

| Subsystem | Flag | Active | Notes |
|-----------|:----:|:------:|-------|
| 🔋 **Power & Battery** | ✅ Complete |  | Pack #1, #2 rebuilt & verified (full charge, firmware updated) |
| 🦿 **Actuators & Legs** | 🔧 `WIP` | 👈 | Left hind leg fails self-right; actuators move but motion stuck — under investigation |
| 🧠 **Compute & Mainboard** | ⬜ `N/A` |  | Not yet assessed |
| 📷 **Sensors & Cameras** | ❌ `FAIL` |  | Rear depth camera server fails to start |
| 📡 **Comms & Networking** | ⬜ `N/A` |  | Not yet assessed |
| 🦴 **Chassis & Mechanical** | ⬜ `N/A` |  | Not yet assessed |

<sub>**Flags** — ✅ `Complete` functional & verified · ❌ `FAIL` confirmed fault, needs repair · 🔧 `WIP` currently being worked on · ⬜ `N/A` not yet assessed</sub>

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

## 🔗 References

- [Spot Battery Safety Data Sheets (SDS)](https://support.bostondynamics.com/s/article/Spot-Battery-Safety-Data-Sheets-SDS-49922)

---

## 👥 Team

| Name | Role |
|------|------|
| @eggsacc | UROP Researcher |
| @Kmyming | UROP Researcher |
| @NickInSynchronicity | Project Supervisor |

---

<div align="center"><sub>Last updated: 2026-06-12</sub></div>
