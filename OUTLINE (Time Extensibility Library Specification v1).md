# Repository Outline — Time Extensibility Library Specification v1

> **Repository:** `Ambience-Suites/Time-Extensibility-Library-Specification-v1`
> **Clone:** `gh repo clone Ambience-Suites/Time-Extensibility-Library-Specification-v1`

---

## Overview

The **Time Extensibility Library Specification v1** is a Billfold Technologies smart-contract-based module used with the Business Particle Library for maintenance of time and loop functions of technical analysis strategies, trade indicators, and libraries. It provides standards-compliant time management covering CBOE session intervals, XBRL reporting blocks, and SMPTE time code conventions.

---

## Folder Structure

```
Time-Extensibility-Library-Specification-v1/
│
├── specs/                          # Core library and engine specifications
│   ├── Time Extensibility Library Specification v1.md
│   ├── Billfold International Order Book Specification v1.md
│   └── Stattice_Engine_Compiler_Specification_v1.md
│
├── intrasession/                   # Intrasession Standard Time documents & data
│   ├── Intrasession Standard Time v1.md
│   ├── Intrasession Standard Time v1 (1).csv
│   ├── Intrasession.md
│   ├── Billfold Technologies Intrasession Report v1.md
│   └── Billfold Technologies Intrasession Report.pdf
│
├── dateabank/                      # Dateabank Business Almanac
│   ├── Dateabank.md
│   └── Dateabank Business Almanac v1
│
├── src/                            # Source code (C#, Solidity)
│   ├── TIMREDEX.cs
│   ├── Time Based Liquidity.cs
│   └── beamology-dossier-v4.sol.txt
│
├── docs/                           # General documentation and reference
│   ├── Business Machine Package Hierarchy Document.md
│   ├── Time Based Liquidity.md
│   └── Buspar 1.csv
│
├── calendar/                       # Scheduling and calendar files
│   └── Repository Runtime Exchange--2025-06-28--14-13-55.ics
│
├── .github/
│   └── workflows/
│       └── update-changelog.yml    # Auto-updates CHANGELOG.md on every push
│
├── OUTLINE.md                      # This file — repository map and outline
├── CHANGELOG.md                    # Auto-updated log of all changes
├── README.md                       # Project overview and quick-start guide
└── LICENSE
```

---

## Section Summaries

### specs/
Contains the primary specification documents that define the Time Extensibility Library and related Billfold Technologies engines.

| File | Description |
|------|-------------|
| `Time Extensibility Library Specification v1.md` | Encyclopedic instruction set for TradingView time extensibility; covers TimeBase, SessionManager, RealTimeEngine, StrategyTester, ActionScheduler, and AssetBibliographics modules. |
| `Billfold International Order Book Specification v1.md` | Specification for the international order book module integrated with Billfold Technologies. |
| `Stattice_Engine_Compiler_Specification_v1.md` | Specification for the Stattice Engine compiler used in strategy and indicator compilation. |

### intrasession/
Documents and data for the Intrasession Standard Time (IST) subsystem — the granular, session-aware time layer.

| File | Description |
|------|-------------|
| `Intrasession Standard Time v1.md` | Outline and reference for IST document structure, identifier patterns, and C# API. |
| `Intrasession Standard Time v1 (1).csv` | Master IST data file — time slots mapped to Occucode identifiers. |
| `Intrasession.md` | IST-to-Occucode conversion tables, API interfaces, and CBOE/XBRL compliance notes. |
| `Billfold Technologies Intrasession Report v1.md` | Formatted intrasession report using Billfold Technologies conventions. |
| `Billfold Technologies Intrasession Report.pdf` | PDF export of the intrasession report. |

### dateabank/
The Dateabank Business Almanac integrates the Business Particle Library for scheduling, event management, and Beamology Dossier smart-contract filtering.

| File | Description |
|------|-------------|
| `Dateabank.md` | Business Almanac specification: particle registry, Beamology Dossier filter, composite event calendar. |
| `Dateabank Business Almanac v1` | Base almanac data file. |

### src/
Source-code assets for the library, including C# implementation files and a Solidity smart contract.

| File | Description |
|------|-------------|
| `TIMREDEX.cs` | TIMREDEX C# implementation — time index and exchange data structures. |
| `Time Based Liquidity.cs` | Time-based liquidity C# module for technical analysis strategies. |
| `beamology-dossier-v4.sol.txt` | Beamology Dossier v4 Solidity smart contract for particle registry filtering. |

### docs/
General documentation and support reference materials.

| File | Description |
|------|-------------|
| `Business Machine Package Hierarchy Document.md` | Component and package specification for business machines in the Beamology Trade Engine. |
| `Time Based Liquidity.md` | Narrative documentation for the time-based liquidity module. |
| `Buspar 1.csv` | Support data file for business particle references. |

### calendar/
ICS calendar files for operational scheduling and event tracking.

| File | Description |
|------|-------------|
| `Repository Runtime Exchange--2025-06-28--14-13-55.ics` | Composite runtime exchange calendar capturing sessions, audits, and bibliographic events. |

---

## Key Concepts

- **TimeBase** — Abstract base for all time models (intra/inter-session, UTC/local, SMPTE).
- **SessionManager** — Manages session definitions (open/close, holiday schedules) per CBOE/CME calendars.
- **RealTimeEngine** — Real-time event hooks for indicators and strategies.
- **ActionScheduler** — Schedules timed trade actions, alerts, and recalculations.
- **Occucode** — Unique second-slot identifier format `[SS] summit-conference-semester` for granular event tracing.
- **TIMREDEX** — Time index exchange data structure powering the library's session registry.
- **Beamology Dossier** — Solidity smart contract that filters unregistered business particles.

---

## Standards & References

- [CBOE Trading Hours](https://www.cboe.com/about/hours/)
- [CBOE Symbol Reference Data](https://www.cboe.com/us/equities/market_statistics/symbol_reference/)
- [XBRL Specifications](https://www.xbrl.org/specifications/)
- [SMPTE Time Code Standards](https://www.smpte.org/standards)
- [Numbermaiden CIA Service Registry](https://github.com/Numbermaiden/Numbermaiden-CIA-Service-Registry)
- [Business Particle Accelerator](https://github.com/Business-Particle-Accelerator)

---

## Ambience Suites GUI Library

This specification operates within the broader **Ambience Suites GUI Library** ecosystem. Rendering and animation data produced by the Cycles component is serialized using **Content Data Serial Boxes** for distribution across GUI contexts.

See [Content_Data_Serial_Boxes.md](Content_Data_Serial_Boxes.md) for:
- Box format schema (Content, State, Config types)
- Integration mappings for the Cycles repository
- Generation, validation, and lifecycle process
