# Design inventory

Every design in the EFC Ignition library and where it lives. Status as of **v7.0 (2026-10-19)**.

Since v7.0 all designs ship as **one Perspective project, `EFC_Library`** (no parent), unzipped at `projects/EFC_Library/` and zipped by `build.py --dist` as `EFC_Library_PROJECT.zip`. The parts below are its sources. One image per view: `docs/previews/templates/<Category>/<Name>.png` (`python3 build.py --preview`); review notes in [template-review](template-review.md).

## Parts merged into EFC_Library
| Design | Version | Views in EFC_Library | Source | Docs |
|---|---|---|---|---|
| EFC_Styles: ISA-101 style classes | 166 classes (v5.1) | style classes, stylesheet, `Styles/_Catalog` | `generator/build_styles.py` | [style-library](style-library.md), [style-class-index](style-class-index.md), [isa101-audit](isa101-audit.md) |
| PID_Symbols: controlled-device templates | v5.1 (gateway-verified on a DDT_Valve instance) | `Templates/Valves/` (4), `Templates/Rotating/` (10), `Templates/HeatTransfer/` (2), `Templates/_Demo` | `generator/build_pid.py`, `pid_common.py`, `active.py` | [library-reference](library-reference.md), [design-notes](design-notes.md) |
| EFC_ProcessValues: PV_StatusStrip / PV_RangeBar | PV 1.3.0 (not re-tested on a gateway) | `Templates/ProcessValues/` | `generator/build_pv.py`, `common.py` | [pv-display](pv-display.md), [pv-style-index](pv-style-index.md) |
| PID_Loops: loop cards B1–B4 + LoopConfig popup | built 2026-10-05; not gateway-tested | `Templates/Loops/` (was `PID/Templates/`), `Templates/Loops/Popups/LoopConfig` (was `PID/Popups/`), `Templates/Loops/_Demo` | `generator/pid_loops/generate_loops.py` | [pid-loop-templates](pid-loop-templates.md) |
| EFC_StationFaceplates: DDT_Station sidebar / fill / tile | export of 2026-10-06 (imported) | `Templates/Station/` | `imported/EFC_StationFaceplates/` (edit in Designer) | [station-faceplates](station-faceplates.md) |
| EFC_IOFaceplates: Modicon x80 I/O card faceplates | export of 2026-10-07 (imported) | `Templates/IO/` (was `IO/`): 8 card faceplates, `Parts/`, `RackOverview`, `_Demo` | `imported/EFC_IOFaceplates/` (edit in Designer) | [design-briefs](design-briefs.md) |

## Outside the project
| Design | Version | Files | Source |
|---|---|---|---|
| Static P&ID symbols | v5.1 | `symbols/<Category>/` (198) + `symbols/Active/` (16) | `generator/v2/`, `pid_common.py` |
| PID tags (UDTs + demo) | v5.1 | `tags/PID_*_UDT.json`, `Valve_Discrete_Demo_UDT.json`, `PID_Demo_Instances.json` | `build_pid.py` |
| Nav connectors: off-page connector options A–D | options only; none chosen | `symbols/NavConnectors/`, `mockups/nav-connectors.html` | `generator/nav_connectors/` |
| Screen design standard | — | [screen-layout-standard](screen-layout-standard.md) | — |

## Not in the repo yet
| Design | Status |
|---|---|
| Diaphragm compressor screen | in progress ([design-briefs](design-briefs.md)) |
| Haskel pump faceplate | in progress, not built ([design-briefs](design-briefs.md)) |

## Archived
See [`archive/ARCHIVED.md`](../archive/ARCHIVED.md). The separate v6.3 projects (EFC_Styles, PID_Symbols, EFC_PID_Library, EFC_ProcessValues, PID_Loops, EFC_IOFaceplates, EFC_StationFaceplates) live on at git tag `v6.3`.

## Cross-cutting to-dos
- **EFC_IOFaceplates:** BMXAMO0802 lists 8 channels; the card has 2 (see [template-review](template-review.md)).
- **PID_Loops:** column containers need `alignItems: stretch`; move to EFC_Styles classes; decide whether to relabel OUT as CV.
- **PID_Symbols:** move the alarm outline from `isAlarmActiveFiltered` to the `queryStatus` pattern used by EFC_ProcessValues. Preview first, per the workflow rule.
- **EFC_Styles:** fold in the PV classes and the Station classes (`Station/Step/*`, `Bar/Band/Deadband`); align PV Diagnostic `#7A7A7A` with `#6E6E6E`.
- **PID layout open items:** valve alarm outline 2 px vs 3 px; OPENING/CLOSING width; centering when the M is shown.
