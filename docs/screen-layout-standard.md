# Perspective screen design standard

This is the layout standard every EFC Perspective screen and template follows. It is also an appendix to the EFC Controls Standard; `Perspective_Screen_Design_Standard.pdf` is the published copy.

## Frame (16:9)
Screens scale at 16:9 from **1920×1080 to 3840×2160**. Text inside templates must stay usable across that whole range, which is why every EFC_Styles size is in vh: 1080p is 1×, 1440p is 1.33× and 2160p is 2×.

| Region | Size at 3840×2160 (largest) | Notes |
|---|---|---|
| Header | top | Title, navigation, status |
| Alarm bar | bottom, 140 px tall | Most-recent alarms |
| Left menu | 120 px wide | Screen navigation |
| Trends / dynamic window | right, 800 px wide | Trends; faceplates open here (e.g. the Haskel pump faceplate) |
| Process area | remainder | P&ID templates (PID_Symbols, PV, loops) |

All regions scale down proportionally on smaller displays.

## Graphics conventions
- **ISA-101 high-performance grayscale:**
  - Background `#D9D9D9`.
  - Color only for abnormal states.
  - Color always backed by text or shape.
  - Flashing only for unacknowledged alarms.
- **Equipment state:** running/open is white, stopped/closed is gray, transition is `#C4C4C4`, and fault is dark gray `#3A3A3A` with a red border.
- **Automated valves:** the actuator head shows the command; the body shows actual feedback when separate feedback exists.
- **Device templates:**
  - Tag above, status below, both centered on the symbol's centerline.
  - Orange P when a permissive blocks the device; red I when an interlock blocks it.
  - A small blank-square command button appears in Manual.
  - The only parameter is `tagPath`, plus `useButton`.
- **Static symbols:** plain SVGs in `symbols/`, imported as needed.
- **Styles:** use EFC_Styles classes (`props.style.classes`), never inline styles. See [`style-library.md`](style-library.md).
