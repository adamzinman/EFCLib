# P&ID Active Template Library: design notes

Notes collected 2026-10-05. **Compiled into PID_Symbols v3 on 2026-10-05** (see `claude/pid-symbol-suite.md`). Templates widened to 120 px so the manual M chip clears the button. **Current release: v5.1 (2026-10-07).**

**Workflow rule (2026-10-06):** for every change, generate the preview image only. Do not rebuild or repackage the library (project zips, bundle, SVGs) until the user approves the preview.

1. **Purpose:** a library of templates for devices that are actively controlled, in a somewhat modern take on ISA-inspired SCADA symbols.
2. **Static symbols:** keep every static symbol from v2. Export them as plain SVGs in a separate `symbols/` folder (category subfolders), not as Perspective views.
3. **Valve baseline:** the original AutoValve rules.
   - UDT `PID_AutoValve`: Cmd, ZSO, ZSC, PB, PermOK, Intlk, Fault.
   - Momentary PB: writes 1 on press, 0 on release. The PLC toggles Cmd on the rising edge.
   - The button is disabled only when the valve is commanded closed and P or I is showing.
   - Status text: CLOSED / OPEN / OPENING / CLOSING / FAULT.
4. **Styling:** all text sizes, colors and attributes come from EFC_Styles classes. No inline styling. New needs become new EFC_Styles classes.
5. **Valve geometry:** rectangular actuator on top; the stem connects to the center of the body (y = 70).
6. **Reference shapes:** use the linked library https://claude.ai/artifact/3BqrQ3x6MxzorkGYA2aoZz for the active symbols. Conventions to carry over:
   - Closed bowtie triangles with vertical ends.
   - Contrast details that flip light on dark fills.
   - Narrow level slot inside vessels.
   - Port notes on each symbol.
7. **Colors:** EFC_Styles colors win over the linked library's.
8. **Diaphragm compressor:** add it as an active symbol, with the linked library's state logic and EFC colors.
9. **P and I badges:** every controlled device gets P (permissive) on the LEFT and I (interlock) on the RIGHT, never on the process-line path. They use the new classes `Indicator/PermissiveBadge` and `Indicator/InterlockBadge`.
10. **ISA-101 color audit:** applied.
11. **Other North American standards** (ISA-5.5, NFPA 79, ANSI Z535 / OSHA 1910.144, ASME A13.1, CGA): checked and applied.
    - Fault fill becomes dark gray `#3A3A3A`; the alarm outline carries the priority color.
    - Diagnostic alarm becomes gray (`#7A7A7A`, later `#6E6E6E` per note 40).
    - Simulated / forced becomes teal `#00897B`.
    - Bad quality stays magenta `#B000B0`.
    - Highlight becomes `#DCE3EC`.
    - `Button/Danger` is neutral on the HMI.
    - `Util/Blink` is removed (flashing = unacknowledged alarm only).
    - P badge is orange `#F08000` with black text; I badge is red `#C00000` with white text.
    - No fluid-colored lines or cylinders.
12. **Apply the recommendations** from 10–11.
13. **Automated valve:** no circle in the center of the body.
14. **Diaphragm compressor geometry:** taken from the user's base image (2026-10-05). See the geometry below.
15. **Text:** tag name ABOVE the symbol, status BELOW, both centered on the symbol's centerline. Values and units go under the status.
16. **Running equipment** (motors, pumps, compressors, blowers, fans, agitators, conveyors):
    - One momentary start/stop button at the BOTTOM LEFT. It toggles the run state, with the same rules as the valve PB. Tooltip reads Start/Stop.
    - The button is disabled only when the device is stopped and P or I is showing.
    - New UDT: Cmd, Run, PB, PermOK, Intlk, Fault, Mode.
17. **Manual mode indicator: Option C2 (chosen 2026-10-05).** In manual, the status becomes a split chip: a dark left segment (`#3A3A3A`) holding a **yellow M** (`#FFD200`), then the normal status text (`M | RUNNING`, `M | OPEN`). Auto shows no marker; only abnormal modes are flagged. The other options are kept below in case this changes.
18. **Discrete valves use the plant UDT** (2026-10-05). AutoValve reads `CMD`, `ZSO`, `ZSC`, `Feedback_Enabled`, `Permissive` (**1 = missing**), `Interlock`, `InterlockList` (I tooltip), `Manual`, `Off`, `LockedOut`, `Name`, `Description`.
    - **Button:** one click writes `HMI_CMD = NOT CMD`. It's enabled in Manual only, never when Off or Locked Out. Opening is blocked by P or I; closing is always allowed.
    - **Mode letter** left of the status: **M** manual, **D** off (disabled), **L** locked out. Priority L > D > M. All yellow.
    - **Fault:** both limit switches made (the UDT has no fault bit).
    - **Not used yet:** Auto, Auto_Perm, Man_Perm, HMI_Auto, HMI_Manual, HMI_Off, HMI_Lockout, REQ, Cycle_Count, Reset_Count.
19. **Symbols render as embedded images** (2026-10-05). **Superseded by note 42 (v5.1):** the symbol is now a Drawing, not an Image with a data URI.
20. **Every template follows the design rules** (tag, status, actuation button, P/I, mode letter). **Its only parameter is `tagPath`** to the UDT instance (amended by note 37: valves and running equipment also take `useButton`).
21. **The symbol is an embedded SVG inside each template**, with all the other agreed elements kept. That means one template per symbol (`PID/Templates/<Category>/<Symbol>`) and no nested symbol views.
22. **Defaults applied with v4 (2026-10-05):**
    - The alarm outline is the highest active alarm priority on the UDT instance (`isAlarmActiveFiltered` on `tagPath/*`).
    - Clicking the symbol does nothing yet; faceplates are to follow.
    - The control valve has no actuation button.
23. **Views land in `Views/Templates`** (`Templates/<Category>/<Symbol>`, demo at `Templates/_Demo`), with no `PID` folder.
24. **The actuation button is hidden unless the device is in Manual** (valves: `Manual`; motors: `Mode` = 1). The existing enable rules still apply when it's visible.
25. **Control valve position indicator:** a vertical moving indicator showing commanded (`Out`) and actual (`Pos`) position. Planned as a narrow bar right of the actuator, above the process line: the fill is the actual position and a blue pointer is the command.
26. **Fault outline:** a faulted valve or device gets a red outline.
27. **Mode letters removed:** M / D / L / A are gone from devices and valves. Manual is signalled by the button, which only shows in Manual.
28. **Position/feedback as a border:** use a border around the device/valve state, with the background matching the state color. **Interpretation not yet confirmed:** A = a state-colored tile behind the symbol with a feedback border; B = the symbol keeps its state fill and its own outline shows feedback. **Applied as B in v4.1:** the fill stays the state color. The dashed travel outline was later removed; see note 32.
29. **Diaphragm compressor:** the center arc is removed. The lines are widened and symmetric: `M19,28 L87,40 M19,72 L87,60`.
30. **New Vacuum Pump symbol** (`Pump_Vacuum`): the compressor base plus a small circle (r = 7) at (33, 50), between the lines and just under halfway from the center to the left edge. The old static liquid-ring SVG is renamed `Pump_Vacuum_LiquidRing`.
31. **Fault across the library:** keep the dark-gray fault fill and make the outer border red (3 px). The red border takes precedence over the alarm-priority outline while faulted.
32. **Light gray is back on opening/closing/starting/stopping** (2026-10-06). It's a solid fill with no dashed outline. The transition gray is darkened to `#C4C4C4` (EFC_Styles and the symbols) so it shows against the `#D9D9D9` screen.
33. **All valve statuses (including the positioner %) use the bordered state chip** under the symbol, matching running equipment: Stopped (closed or 0 %), Running (open), Transition (opening or closing), Fault. Each chip is sized to its text and centered.
34. **Valve P and I sit beside the actuator** (approved 2026-10-06): a 3 px gap on each side, centered on the actuator height, computed per valve symbol.
35. **Control valve position bar** (approved 2026-10-06): left of the valve, just outside the P badge, at x = 18–31 and y = 9–46 px of the 120×100 template, so it's taller and closer to the stem. The pointer overhangs the bar so it stays visible at 0 % and 100 %.
36. **Manual command button** (approved 2026-10-06): `Button/Command` (EFC_Styles), a blank square the same height as the status chip, on the status row. It's a subtle raised key (toned down), sinks when pressed and fades when disabled.
37. **`useButton` parameter** on valve and running-equipment templates (default true; amends note 20). When it's false there's no button: in Manual you click the symbol to command it, with the same enable rules, and the cursor shows a hand only when a click would act.
38. **With `useButton` = false, a yellow M shows Manual.** It sits left of the status and matches the chip's height, font and border (`Mode/ManualSplit` + `Mode/ManualJoined`).
39. **Live-gateway fixes** (2026-10-06, `[EFC]RGTCR/Valves/AV001` on `DDT_Valve`): every read of a tag-bound property is wrapped in `coalesce()`, the alarm lookup is wrapped in `try()`, and the I tooltip parses the `InterlockList` document (`Status`, `Description[20]`, `InterlockName[20]`, `Used[20]`). `DDT_Valve` will gain a `Permissive` member (1 = missing).
40. **ISA-101 audit fixes** (approved 2026-10-06, shipped in v5; see `claude/isa101-audit.md`):
    - `Button/Danger` hover/press are neutral.
    - `State/OutOfService` text is `#5E5E5E`.
    - The `Indicator/Permissive` text form is `#8F4500`.
    - The `Alarm/Diagnostic` fill is `#6E6E6E`, and its text on dark is `#9A9A9A`.
    - `Alarm/Status/ClearedUnacked` is steady (opacity 0.45) instead of flashing.
    - The XXS / `Text/Micro` size is 10 px.
41. **Hidden M collapses to zero width** (shipped in v5). When the M isn't used (`useButton` = true, or in Auto), the M label has `meta.visible` false and the class `Util/Collapsed`, so the status chip centers alone on the symbol centerline. When the M is shown, the M and the status are centered as one unit, so the status text sits ~11 px right of the centerline.
42. **Symbols embedded as Drawing elements** (v5.1, 2026-10-07; verified on the gateway with `[EFC]RGTCR/Valves/AV002`).
    - Each template's symbol is an `ia.shapes.svg` with all SVG shapes in `props.elements`. Each shape's `fill.paint`, `stroke.paint` and `stroke.width` are bound to the custom props `fill`, `head`, `line`, `con` and `lw` (plain `#RRGGBB`). This replaced the Image/data-URI source, which showed as a broken link.
    - The control-valve position bar is also a Drawing: the fill rect's `y`/`height` are bound to Pos and the pointer `d` to Out.
    - `preserveAspectRatio` must be a bare 8.1 enum value (`xMidYMid`, not `xMidYMid meet`). `check_81.py` checks this.
    - The alarm lookup is quality-guarded: each call is `forceQuality(coalesce(try(isAlarmActiveFiltered(...), false), false))`. With no alarms configured on the instance it returns Bad_NotFound, and that bad quality had spread into `line` and `lw`.
    - `permMissing` shows Bad_NodeIdUnknown until the PLC has the `Permissive` variable. The template treats it as not missing until then.

## Open items
- **Alarm outline:** 3 px may swamp 36 px valves. 2 px on valves is suggested; not decided.
- **Valve status width:** OPENING / CLOSING is tight next to the button.
- **With the M shown:** should the status chip itself stay on the centerline (the M hangs off its left), rather than centering the M and status as a unit? Not decided.

## Compressor_Diaphragm geometry (viewBox 0 0 100 100, native 64 px @1080p)
Updated 2026-10-05 from the user's base image, which supersedes the earlier reconstruction.

| Element | Role | Geometry |
|---|---|---|
| nozzles | pipe (2 px) | `M6,50 L12,50 M88,50 L94,50` |
| casing | state fill + alarm outline (1.5 / 3 px) | `circle cx=50 cy=50 r=38` |
| compressor lines | contrast stroke (1 px), converging left to right, symmetric (note 29) | `M19,28 L87,40 M19,72 L87,60` |

Ports: suction is left at (6, 50) and discharge is right at (94, 50). P badge goes top left and I badge top right, both above the y = 50 line. Colors follow EFC_Styles: the base image's red fault and light-gray stopped map to dark gray `#3A3A3A` and `#9E9E9E`.

## Pump_Vacuum geometry (viewBox 0 0 100 100, native 64 px @1080p)
The same as Compressor_Diaphragm plus an inner circle `cx=33 cy=50 r=7` (contrast stroke, 1.5 px).

## Manual-mode indicator options (kept for future reference; letters removed in note 27)
All options leave auto with no marker (ISA-101: flag only abnormal modes). Previews: `Manual_Mode_Options.png`, `Manual_Mode_M_Colors.png`.

| Option | Description | Pros | Cons |
|---|---|---|---|
| A: Mode chip | Dark `Mode/Manual` chip "MAN" (or "M" on pumps) in the bottom-right corner, opposite the start/stop button | Explicit; existing class; extends to LOC/SIM | Extra element; crowded on pumps |
| B: Inverted tag | Tag name turns white-on-dark (`#3A3A3A`) in manual | No new element or layout change; scans well across a screen | Doesn't say which abnormal mode; learned convention |
| C: Split status chip | Dark left segment added to the status: `MAN \| RUNNING` | Mode and state read together; self-explanatory | Status widens in manual |
| C1: Split chip, white M | `M` in white on the dark segment | Most ISA-101-pure; no alarm color used | Least eye-catching |
| **C2: Split chip, yellow M (chosen)** | `M` in yellow `#FFD200` on the dark segment | Most visible on gray | Same yellow as Medium alarms (ANSI Z535 "caution"); could be read as a P3 alarm |
| C3: Split chip, orange M | `M` in orange `#FF7A00` on the dark segment | Strong attention cue | Competes with the orange P badge and High alarms |
| (suggested) Split chip, blue-gray M | Light blue-gray M | More pop than white without borrowing an alarm color | Not previewed |

Split-chip spec: 1 px `#262626` border, 2 px radius; M segment `#3A3A3A`, bold, ~10 px at 1080p, 5 px side padding; status segment white with `Text/Status` text. The M color is a single value, so it can be swapped in the style library (`Mode/ManualSplit` class) without touching the templates.
