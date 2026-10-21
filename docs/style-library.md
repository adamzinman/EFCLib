# EFC_Styles: using the style library

EFC_Styles is the ISA-101 light-gray style class library that every view, template and symbol uses. **166 classes**, a project stylesheet (the `efc-blink` keyframes) and the `Styles/_Catalog` view. Generator: `generator/build_styles.py`. Full list: [`style-class-index.md`](style-class-index.md). Audit: [`isa101-audit.md`](isa101-audit.md).

## Applying
- Put one or more class paths in a component's `props.style.classes`, separated by spaces, e.g. `Text/Value Text/Mod/Right`.
- Bind that property to switch classes by state, e.g. `if({[.]Fault}, "State/Fault", if({[.]Run}, "State/Running", "State/Stopped"))`.
- Never style inline. If something is missing, add a class to the generator.
- **Projects:** use `EFC_Styles` as the parent of `PID_Symbols` / `EFC_ProcessValues`, and chain your HMI project below them. Or use the merged `EFC_PID_Library` project as the parent. Ignition allows one parent per project, so chain them.
- Open `Styles/_Catalog` to see every class on live components.

## Scaling
All sizes, padding and borders are in **vh** (1080p px / 10.8): 1080p is 1×, 1440p is 1.33× and 2160p is 2×.

| Type scale | px @1080p | Used by |
|---|---|---|
| `Text/Size/XXS` | 10 (9 before v5) | `Text/Micro` |
| `Text/Size/XS` | 11 | `Text/Caption`, `Text/Units`, `Text/Status` |
| `Text/Size/S` | 12 | `Text/Label`, `Text/TagName`, `Text/MenuItem` |
| `Text/Size/M` | 14 | `Text/Body`, `Text/Value` |
| `Text/Size/L` | 16 | `Text/Subheader` |
| `Text/Size/XL` | 20 | `Text/Header`, `Text/ValueLarge` |
| `Text/Size/XXL` | 24 | `Text/Title` |
| `Text/Size/XXXL` | 32 | `Text/ValueHero` |

## Colors (ISA-101 / ISA-18.2 / NFPA 79 / ANSI Z535)
- **Screen and states:**
  - Screen `#D9D9D9`.
  - Running/open white, stopped/closed `#9E9E9E`, transition `#C4C4C4`.
  - Fault `#3A3A3A` with a red border on symbols.
- **Alarm priorities:** Critical `#D50000`, High `#FF7A00`, Medium `#FFD200`, Low `#00A3E0`, Diagnostic gray `#6E6E6E`. Never use alarm colors for anything else; the documented exceptions are in the audit.
- **Badges:** P badge orange `#F08000` with black text; I badge red `#C00000` with white text.
- **Other:**
  - Simulated is teal (purple is reserved, per ANSI Z535).
  - Bad quality is magenta `#B000B0`.
  - Editable values and commands are blue `#1F4E99`.
- **Blinking:** only `Alarm/*/Unacked` blinks (`efc-blink`, which needs the Advanced Stylesheet on 8.1.22+). `Alarm/Status/ClearedUnacked` is steady and faded.

## Folders
- **Text/:** roles, Size, Weight, Color and Mod.
- **Container/:** Screen, Header, Menu, TrendPanel, AlarmBar, ProcessArea, Panel, Card, Popup, Faceplate and more.
- **Button/:** Default, Primary, Subtle, Danger (neutral), Start, Stop, Command, Momentary, Toggle, Nav, Tab and more.
- **Input/** and **Value/**.
- **State/** and **Mode/**, including `Mode/ManualSplit` / `ManualJoined`.
- **Indicator/:** LEDs, Permissive/Interlock and their badges.
- **Bar/**.
- **Alarm/:** priority × Fill / Unacked / Outline / Text, plus Status.
- **Table/**.
- **Util/:** Pad, Border, Shadow, Pointer, Disabled, Highlight, Clip, Collapsed.
