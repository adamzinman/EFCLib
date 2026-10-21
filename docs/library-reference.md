# Library reference: PID_Symbols + EFC_Styles (v5.1, Ignition Perspective 8.1)

A library of templates for actively controlled devices, in a modern ISA-inspired style. It is built from the design notes in [`design-notes.md`](design-notes.md). Shapes come from the reference library; colors and text come from EFC_Styles, revised to match ISA-101, ISA-18.2, NFPA 79 and ANSI Z535.

## Contents
Since v7.0 everything ships as one project, **EFC_Library** (`dist/EFC_Library_PROJECT.zip`, built with `python3 build.py --dist`; unzipped in the repo at `projects/EFC_Library/`). The rows below describe the parts that are merged into it.

| Item | What it is |
|---|---|
| PID_Symbols part | 16 templates (one per controlled-device symbol) + `Templates/_Demo`, inside EFC_Library |
| EFC_Styles part | Style library (166 classes, ISA-101 audit fixes applied), inside EFC_Library |
| `tags/` (repo root) | UDTs `PID_Motor`, `PID_ControlValve`, the demo stand-in `Valve_Discrete_Demo` (same members as the plant discrete-valve UDT) and 13 demo instances (`PID_Demo` folder) |
| `symbols/` (repo root) | 214 plain SVGs to import as needed: all 198 static symbols from v2, recolored to the standards palette, plus the 16 active symbols in `symbols/Active/` |
| `docs/previews/` | Rendered previews of the demo templates (`python3 build.py --preview`) |
| `generator/` | `active.py` (geometry + palette), `build_pid.py` (templates), `pid_common.py` (shared helpers, static SVG export), `build_styles.py` (EFC_Styles), `preview.py` / `preview_pid.py`, `check_81.py` (8.1 import check), `make_project_zip.py`, `v2/` (static symbol source). Run everything from the repo root with `python3 build.py`. |

## Templates (one per symbol, only parameter = `tagPath`)
The project imports straight into **Views → Templates** (`Templates/<Category>/<Symbol>`, demo at `Templates/_Demo`), with no `PID` folder.
Every template takes **`tagPath`** (the UDT instance). Valve and running-equipment templates also take **`useButton`** (default `true`; see v4.4). Everything else comes from the UDT:
- the tag text comes from `Name`, with `Description` as its tooltip
- feedback mode comes from `Feedback_Enabled`
- the mode letter and P/I badges come from the mode, permissive and interlock members
- the alarm outline is the **highest active alarm priority on any member of the instance** (`isAlarmActiveFiltered` on `tagPath/*`, priorities 1–4; shelved alarms ignored)

The symbol is **embedded in the template as a Perspective Drawing** (`ia.shapes.svg`): every SVG shape lives in the view JSON, and each shape's fill, outline color and outline weight is bound to the state, command and alarm properties, so the fills change in place as the state changes. There's no image link or data URI. There are no nested symbol views. Clicking the symbol does nothing yet (faceplates to follow).

| Template | Size @1080p | UDT | Button |
|---|---|---|---|
| `Templates/Valves/Valve_OnOff_Pneumatic` · `Valve_Solenoid` · `Valve_MOV` | 120×100 | Plant discrete-valve UDT | Writes `HMI_CMD = NOT CMD`, Manual only |
| `Templates/Valves/Valve_Control` | 120×100 | `PID_ControlValve` | none (operated by output %) |
| `Templates/Rotating/` `Pump_Centrifugal` · `Pump_Vacuum` · `Pump_PD_Rotary` · `Pump_Diaphragm` · `Pump_Reciprocating` · `Compressor_Centrifugal` · `Compressor_Diaphragm` · `Blower` · `Agitator` · `Motor` | 120×116 | `PID_Motor` | Momentary start/stop (PB) |
| `Templates/HeatTransfer/` `HX_AirCooled` · `Heater_Electric` | 120×116 | `PID_Motor` | Momentary start/stop (PB) |

To use one, drag the template for the right symbol onto a screen and set `tagPath`. `PID_Motor` and `PID_ControlValve` gained `Name`, `Description` and `Feedback_Enabled` members, and `PID_Motor.Fault` now carries a demo High alarm.

### Layout (the same on every template)
- **Tag name:** above the symbol, centered on the symbol's centerline. Uses `Text/TagName`.
- **Status:** below the symbol, centered on the same centerline. It stays centered whether or not the button is there.
- **P badge** (`Indicator/PermissiveBadge`): on the left. Shown when `PermOK` = 0.
- **I badge** (`Indicator/InterlockBadge`): on the right. Shown when `Intlk` = 1.
- **Badges and the process line:** the badges are never on the process line.
  - Valves: they sit at actuator height.
  - Pumps and compressors: they sit above the y = 50 ports.
  - Centrifugal pump and blower: I drops to lower right, clear of the top-right discharge (set automatically from `symbol`).
- **Momentary button** (`Button/Momentary`, blank square): bottom left, **visible only in Manual** (valves: `Manual` = 1; motors: `Mode` = 1). It's hidden in Auto, Off and Locked Out.
  - Open/close on valves, start/stop on running equipment.
  - **Motor:** writes PB 1 on press and 0 on release. Disabled only when stopped **and** P or I is showing.
  - **AutoValve:** one click writes `HMI_CMD = NOT CMD`, in Manual only (see the AutoValve section).
  - Stopping or closing is always allowed. Tooltip reads Open/Close or Start/Stop.
- **No mode letters** (note 27). Manual is shown by the button, which only appears in Manual.
  - Other options (white M, orange M, inverted tag, chip) are documented in the notes. To switch, change `MANUAL_M` in `build_styles.py`.

### Status logic
| Template | Status values | State derivation |
|---|---|---|
| AutoValve | CLOSED · OPEN · OPENING / CLOSING · FAULT | ZSO → open, ZSC → closed, neither → travel, both → fault. With Feedback_Enabled = 0 the symbol follows CMD. |
| ControlValve | `NN %` (Pos, or Out without feedback) · FAULT | Body = position (> 1 % = open); actuator head = command (Out > 1 %) |
| Motor | STOPPED · RUNNING · STARTING / STOPPING · FAULT | Run and Cmd agree → that state; they disagree → transition; Fault → fault. Without feedback the symbol follows Cmd. |

### AutoValve: mapped to the plant discrete-valve UDT
Point `tagPath` at an instance of the existing discrete-valve UDT (OPC tags `{OPC Server}/{OPC Prefix}{Tag}.{TagName}`).

| Member | Used for |
|---|---|
| `CMD` | Actuator head color; direction of travel (OPENING / CLOSING); the button writes its inverse |
| `ZSO` / `ZSC` | Body state: open / closed / travelling. Both made = FAULT (the UDT has no fault bit). |
| `Feedback_Enabled` | 0 → the symbol follows CMD (no limit switches) |
| `Permissive` | **1 = permissive missing** → orange P badge; opening blocked |
| `Interlock` | 1 = interlock active → red I badge; opening blocked |
| `InterlockList` | Shown in the I badge tooltip (as text) |
| `Manual` / `Off` / `LockedOut` | Mode letter left of the status: **M** manual, **D** off (disabled), **L** locked out. Auto shows nothing. Priority: L > D > M. All three letters are yellow (`Mode/ManualSplit`). |
| `Name` | Tag text above the symbol (the `label` param overrides it; the tagPath's last segment is the fallback) |
| `Description` | Tooltip on the tag text |
| `HMI_CMD` | **Written by the button: one click writes `NOT CMD`** (maintained bit, no pulse) |
| not used | Auto, Auto_Perm, Man_Perm, HMI_Auto, HMI_Manual, HMI_Off, HMI_Lockout, REQ, Cycle_Count, Reset_Count (faceplate/popup candidates) |

**Button rules:**
- **Enabled:** only when Manual = 1 and the valve is not Off or Locked Out.
- **Open vs close:** opening is blocked while P or I is showing; closing is always allowed.
- **Tooltip:** reads Open, Close, "Manual mode required" or "Locked out".
- **PLC side:** the PLC must still enforce all of this.

### UDTs for the other templates (memory tags in the export; point them at the M580 addresses)
| UDT | Members |
|---|---|
| `PID_Motor` | Cmd, Run, PB, PermOK, Intlk, Fault, Mode |
| `PID_ControlValve` | Out (%), Pos (%), PermOK, Intlk, Fault, Mode |

**PLC side (Motor template):**
- Toggle Cmd on the **rising edge** of PB, and ignore open/start requests when not permitted.
- The PLC must enforce permissives and interlocks itself; the HMI badges are information only.
- A very fast click can produce a short pulse. If your scan could miss it, have the PLC reset PB and delete the release events on the button.

## Symbols & colors
| State | Fill | Notes |
|---|---|---|
| 0 stopped / closed | gray `#9E9E9E` | |
| 1 running / open | white `#FFFFFF` | |
| 2 transition | light gray `#C4C4C4` | Darker than the `#D9D9D9` screen so it stays visible |
| 3 fault | dark gray `#3A3A3A` | Inner details flip to light gray so they stay readable. Red is reserved for Critical alarms. |

- **Alarm outline:** 3 px in the priority color. Low `#00A3E0`, Medium `#FFD200`, High `#FF7A00`, Critical `#D50000`.
- **Actuator head:** shows the command; the valve body shows position feedback.
- **On/off valve:** rectangular actuator, the stem runs to the body center, and there's no ball circle in the body.
- **Diaphragm compressor:** geometry taken from the user's base image (converging lines, bold curved diaphragm). Its geometry is in the notes doc.

## EFC_Styles changes in this release
**v5 (ISA-101 audit, see `claude/isa101-audit.md`):**
- **`Button/Danger`:** hover and pressed are now neutral (`#F5F5F5` / `#BFBFBF`); the last red is gone.
- **`State/OutOfService`:** text darkened to `#5E5E5E` (5.5:1), border `#7F7F7F`.
- **`Indicator/Permissive`** (text form): `#8F4500` (4.9:1).
- **`Alarm/Diagnostic`:** fill `#6E6E6E` (5.1:1 with white text); the text form on dark is `#9A9A9A`.
- **`Alarm/Status/ClearedUnacked`:** steady and faded (opacity 0.45) instead of blinking. Flashing now means an active, unacknowledged alarm only.
- **`Text/Micro` and `Text/Size/XXS`:** 9 px → 10 px.
- **New class `Util/Collapsed`:** takes an element out of the layout with zero width.

**Earlier (v3/v4):**
- **Fault color:** `#D50000` → `#3A3A3A`. This affects `State/Fault`, `Text/Color/Fault` and `Indicator/LED/Fault`.
- **Diagnostic alarm:** purple → gray (`#7A7A7A`, now `#6E6E6E`).
- **Simulated / forced:** purple → teal.
- **`Button/Danger`:** now neutral with a heavy border.
- **`Util/Highlight`:** now blue-gray.
- **`Util/Blink`:** removed. Flashing now means an unacknowledged alarm only.
- **New classes:** `Indicator/PermissiveBadge`, `Indicator/InterlockBadge`, `Mode/ManualSplit`, `Mode/ManualSplitStatus`.

## Ignition 8.1 compatibility
Both projects target **Ignition 8.1** and pass `generator/check_81.py`, a static import check:
- **Project zips:** `project.json` sits at the zip root (title, parent, enabled, inheritable). Every resource uses the 8.1 layout: `com.inductiveautomation.perspective/<type>/<path>/` plus `resource.json` (scope `G`, version 1).
- **Style classes:** in the 8.1 `style.json` form (`base.style` plus `variants` with `pseudo`).
- **Coordinate containers:** percent mode, with every child position a 0–1 fraction (the 8.1 format).
- **Expression functions:** only 8.1 functions are used: `case`, `if`, `indexOf`, `lastIndexOf`, `len`, `numberFormat`, `substring`, `coalesce`, `toStr`, `try`, `forceQuality`, `isAlarmActiveFiltered`. The earlier `endsWith()` call doesn't exist in 8.1 and was replaced with `indexOf()`.
- **Symbol rendering (v5.1):** each template contains one **Drawing** component (`ia.shapes.svg`, `preserveAspectRatio` = `xMidYMid`, a valid 8.1 enum value). Its `elements` hold the symbol's paths, rects and circles. The bindings `props.elements[n].fill.paint`, `.stroke.paint` and `.stroke.width` point at the custom props `fill`, `head`, `line`, `con` and `lw` (plain `#RRGGBB`). The control-valve position bar is a Drawing too: its fill rect's `y`/`height` are bound to Pos and its pointer path `d` to Out. Nothing lives in Image Management, and there are no external files or data URIs.
- **Alarm lookup:** `isAlarmActiveFiltered(tagPath + "/*", "*", "*", p, p, 0, 1, 0)`, an 8.1 alarming expression function. Each call is wrapped as `forceQuality(coalesce(try(…, false), false))`. The function returns Bad_NotFound quality when no member of the instance has an alarm configured (seen on DDT_Valve). The wrapper turns that into 0, so the bad quality can't spread to the outline bindings (`line`, `lw`).
- **Bindings and events:** indirect tag bindings on `{view.params.tagPath}`. Gateway-scoped DOM event scripts call `system.tag.writeBlocking` and `system.perspective.openPopup`.
- **Tags:** 8.1 tag JSON (`UdtType` / `UdtInstance`) with data types `Boolean`, `Int2`, `Float4`.
- **Version-dependent:** the EFC_Styles **Advanced Stylesheet** (`stylesheet/stylesheet.css`, holding only the unacknowledged-alarm blink keyframes) needs **8.1.22 or later**. On older 8.1 builds, everything else works and `Alarm/*/Unacked` shows solid instead of blinking.
- **Not testable offline:** the import itself and live rendering. Open `Templates/_Demo` after import.

## Single-file import (EFC_PID_Library_PROJECT.zip)
`EFC_PID_Library_PROJECT.zip` holds everything in one project, with no parent required:
- all EFC_Styles classes and the stylesheet
- the 16 templates
- `Templates/_Demo` and `Styles/_Catalog`

Import it on its own, or set it as your HMI project's parent. The two separate zips (`EFC_Styles_PROJECT.zip` then `PID_Symbols_PROJECT.zip`) are still included if you prefer the inheritance chain. Don't import both the single file and the separate pair into the same inheritance chain.

## Import order
1. Gateway: import `EFC_Styles_PROJECT.zip` (overwrite the existing project).
2. Tag Browser → Data Types → import `PID_Motor_UDT.json`, `PID_ControlValve_UDT.json`, and `Valve_Discrete_Demo_UDT.json` (demo only; real valves use your existing discrete-valve UDT).
3. Tags root → import `PID_Demo_Instances.json` (optional demo).
4. Gateway: import `PID_Symbols_PROJECT.zip` (overwrite the earlier version). Check that its parent is `EFC_Styles` and your HMI project's parent is `PID_Symbols`.
5. Open `Templates/_Demo`.
