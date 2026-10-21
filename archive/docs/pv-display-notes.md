# Process Value display templates: design notes

**Status 2026-10-06: v1.3 built.** Deliverables: `EFC_ProcessValues.zip`, an Ignition 8.1 project export, and `EFC_ProcessValues_Package.zip`, which adds demo tags, a README and the generator. The generator is saved as `claude/pv-template-generator.py`.
- v1.0 was imported by the user.
- v1.1 fixed the alarm bindings.
- v1.2 restyled the card.
- v1.3 resized it to 100×50.
- v1.1–v1.3 are not yet re-tested on the gateway.

## v1.3: 100 × 50 blocks (2026-10-06)
- **User request:** size the block to 100w × 50h. Preview PV_Display_100x50.png; the user said "generate", accepting option 1 (the tag truncates when the letters need room).
- **Cards:** both are 100×50 @1080p. Views are **104×54** (`PV/Shell` shadow margin). Existing instances need resizing.
- **New classes:**
  - `PV/Tag`: 11 px bold, min-width 0, ellipsis.
  - `PV/Value`: 18 px (A1).
  - `PV/ValueSmall`: 16 px (B2).
  - `PV/Units`: 10 px.
  - `PV/Chip/More`: +N, #595959 with white text.
- **Changed classes:**
  - Letter boxes 9 px text, 12 px tall, 12 px min width, 2 px padding.
  - HeaderRow 12 px tall with a 3 px gap.
  - Body padding 5/5/6/5; BodyBar 4/5/5/5.
  - Strip 4 px.
- **Removed:** `Bar/RangeLabel`. 36 classes in the project.
- **Letter limit:** at most **2 letters**; the rest collapse into a **+N** box.
  - A letter shows when it is present and fewer than 2 present letters come before it in the order FLT · HH · H · L · LL · OVR · UNR · INH.
  - +N shows when the total is above 2. Its tooltip is "Also: …", and it blinks if a hidden non-INH letter is active-unacked.
- **B2:** the track is 12 px tall (5 px caret plus a 6 px band). The 8×12 SVG pointer has width 8/88 of the track.
  - The range-end labels were removed; the range is in the Track tooltip ("Range min to max units").
- **Known tight spots:**
  - With 3+ letters, the A1 tag truncates ("PIT-…").
  - A large value with 4-letter units (1,234.5 SCFH) only just fits.
  - 9–11 px text at 1080p.

## v1.2 card restyle
- **Card (A1-2 / B2-2):** white #FFFFFF, 1 px #B3B3B3 border with a #8C8C8C bottom edge, 6 px radius, `boxShadow 0 1px 3px rgba(0,0,0,.22)`. The shadow is a deliberate ISA-101 exception.
- **Open (not answered):** raise the faded level (cleared-unacked and the blink OFF phase) from 0.25 to about 0.4 for the white background. Still 0.25.

## v1.1 alarm-state fix
- **Cause:** `isAlarmActiveFiltered` in Perspective. It runs in gateway scope, where the provider must be in the path; it never re-runs; and its bindings showed as errors in the user's Designer.
- **Fix:** `custom.alm`, an expression on `{view.custom.tick}` (`now(1000)`) with a script transform.
  - The transform calls `system.alarm.queryStatus(source=["prov:<prov>:/tag:<path>/*"])` and returns `{FLT, HH, H, L, LL, OVR, UNR}` codes (-1, or state·10 + priority; ActiveUnacked 10+p, ActiveAcked p, ClearUnacked 20+p).
  - Errors are logged to `EFC_PV`.
  - **To verify:** the `str(ev.getState())` values and the nested source wildcard.

## Package
- **Project:** `EFC_ProcessValues` (parent `EFC_Styles`, inheritable). Views are under **Views/Templates/ProcessValues**: `PV_StatusStrip` (A1), `PV_RangeBar` (B2) and `_Demo`.
- **Style classes (36):** they ship inside the project, because the project-doc EFC_Styles generator is older than PID v4.4. **TODO:** fold them into EFC_Styles.
- **Demo tags:** `PV_Demo_Tags.json`, imported at the `[default]` root. UDT `DDT_Process_Value_Demo`, instances `PV_Demo/PT001`–`PT005`.
- **Import:** gateway project import, then either Designer **File → Import** into the HMI/PID project, or the chain `EFC_Styles → EFC_ProcessValues → PID_Symbols → HMI`.

## Implementation
- **Only parameter:** `tagPath`. Indirect tag bindings read PV, Name (fallback: last tagPath segment), Description (tag tooltip), Units, HW_Fault, the `*/Inhibit` bits, and, for B2, Eng_Min, Eng_Max and the `*/SP`.
- **Derived values:** `activePri`, `clearedPri`, `fltActive`, `anyUnacked`, `inh` and `badValue`.
- **A1 strip:** fault first, then the highest active priority (blinks if any item is unacked), then the faded cleared color, otherwise Normal.
- **B2 track:** a percent-mode coordinate container with base bands from the SP fractions, priority overlays, a Bar/Frame and the SVG pointer.
- **Scaling:** all sizes are in vh. The templates scale on 16:9 screens if the embedding container scales too.
- **PID_Symbols:** those templates also use `isAlarmActiveFiltered`, so they likely need the same fix.

## Requirements and decisions
- Ignition Perspective 8.1; 8.3 upgrade within about 6 months. Uses EFC_Styles. The only parameter is `tagPath`.
- A1 status strip (primary) and B2 range bar (A1-styled), both **100×50** white rounded cards with a shadow.
- Letters in the fixed order FLT · HH · H · L · LL · OVR · UNR · INH, max 2 visible plus +N. Colors come from the configured priority.
- Blink while unacked, solid once acked; cleared-unacked shown faded.
- HW_Fault gets a new alarm, priority **High** (UDT change). It displays dark gray.

## Design history
- **Rounds 1–7:** A1 + B2, blink and faded behaviour, B2 matched to A1.
- **v1.0:** built.
- **v1.1:** queryStatus alarm state.
- **v1.2:** white card with shadow.
- **v1.3:** 100×50 cards with the +N overflow.
