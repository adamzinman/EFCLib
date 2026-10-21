# ISA-101 audit: EFC_Styles + PID_Symbols

Audited 2026-10-06 against v4. Scope: the 165 EFC_Styles classes, all PID_Symbols templates, the 16 active symbols and the 214 static SVGs.

**Status:** the fixes were approved on 2026-10-06 and shipped in v5 (2026-10-07). The style library is now 166 classes. All three projects pass `generator/check_81.py`.

## Passes
- The screen background is gray (`#D9D9D9`), and equipment is neutral gray. Running is white, stopped is gray, with no red/green run states.
- Color is used only for abnormal states, and it's always backed by something else: status text, P/I letters, outline weight.
- Alarm colors follow the ISA-18.2 priority order: Critical `#D50000`, High `#FF7A00`, Medium `#FFD200`, Low `#00A3E0`, Diagnostic gray.
- Flashing appears only in the Alarm Unacked classes. `Util/Blink` was removed earlier.
- Faults show as text (FAULT) as well as by the dark fill and the red border.
- There are no fluid colors on lines or vessels. The static SVGs use only the muted level fill `#7F8FA6`.
- The templates have no inline styles; everything comes from EFC_Styles classes.
- Gradients and shadows are limited to `Button/Command` (the bevel shows a control can be pressed), `Container/Popup` and `Util/Shadow`.

## Fixes (shipped in v5)
| # | Class | Issue | Fix |
|---|---|---|---|
| 1 | `Button/Danger` hover/active | Still red (`#E53935` / `#A00000`) | Neutral `#F5F5F5` / `#BFBFBF`, 2 px dark border |
| 2 | `State/OutOfService` | Text `#9A9A9A` on `#EDEDED` is 2.4:1 | Text `#5E5E5E` (5.5:1), border `#7F7F7F` |
| 3 | `Indicator/Permissive` (text form) | `#B85A00` is 3.3:1 | `#8F4500` (4.9:1) |
| 4 | `Alarm/Diagnostic` | `#7A7A7A` fill with white text is 4.3:1; the text form on dark is 3.8:1 | Fill `#6E6E6E` (5.1:1); text on dark `#9A9A9A` (5.9:1) |
| 5 | `Alarm/Status/ClearedUnacked` | Blinks | Steady, opacity 0.45. Flashing is for active unacked alarms only |
| 6 | `Text/Micro`, `Text/Size/XXS` | 9 px at 1080p | 10 px |

v5 also adds `Util/Collapsed`, which takes an element out of the layout with zero width. The hidden manual M uses it so the status stays centered (design note 41).

## Documented deviations (kept by user decision)
- **Manual M:** yellow `#FFD200`, the same as Medium alarms. It sits on a dark split-chip segment, which sets it apart from alarm chips (note 17).
- **Fault border:** Critical red, 3 px. It's always shown with the FAULT text and the dark fill (note 31).
- **P/I badges:** orange and red, following NFPA 79 (note 11).
- **Command/editable blue `#1F4E99` vs Low alarm `#00A3E0`:** both are blues, but they differ in hue and lightness. Don't introduce any other blues.
- **`Alarm/Critical/Text`:** `#FF4D4D` on dark backgrounds, for contrast.
- **`Text/Color/Inverse` and disabled text:** low contrast by design.

## Out of scope
The PV display, IO card and station faceplates (separate work).
