# Process Value display templates (EFC_ProcessValues)

PV design **1.3.0**. Generator: `generator/build_pv.py`. Ships inside `projects/EFC_Library/` (`Templates/ProcessValues/`). Demo tags: `tags/PV_Demo_Tags.json`. Class list: [`pv-style-index.md`](pv-style-index.md).

**History:**
- v1.0 was imported on the gateway.
- v1.1 fixed the alarm bindings.
- v1.2 restyled the card.
- v1.3 resized it to 100×50.

**Status:** v1.1–v1.3 have not been re-tested on the gateway yet.

## Requirements and decisions
- Ignition Perspective 8.1, ready for the 8.3 upgrade. Uses EFC_Styles. Templates live in **Views/Templates/ProcessValues**. The only parameter is `tagPath`, a `DDT_Process_Value` instance.
- **Two templates**, both 100×50 white rounded cards with a shadow:
  - **A1 `PV_StatusStrip`** (primary).
  - **B2 `PV_RangeBar`**, styled like A1.
  - The views are 104×54 so the `PV/Shell` margin keeps the shadow from being clipped.
- **Letters** appear in a fixed order: FLT · HH · H · L · LL · OVR · UNR · INH. At most 2 are visible; the rest collapse into **+N**, which has an "Also: …" tooltip and blinks if a hidden letter is unacked. Letter colors come from the configured alarm priority.
- **Blinking:** a letter blinks while unacked and goes solid once acked. Cleared-but-unacked shows faded (opacity 0.25).
- **HW_Fault** gets a new alarm, priority **High** (a UDT change). It displays dark gray.

## Implementation
- **Tag reads:** indirect tag bindings read PV, Name, Description, Units, HW_Fault and the Inhibit bits. B2 also reads Eng_Min, Eng_Max and the four SPs.
- **Alarm state (v1.1):** `custom.alm` is an expression on `{view.custom.tick}` (`now(1000)`) with a script transform. The transform calls `system.alarm.queryStatus(source=["prov:<prov>:/tag:<path>/*"])` and returns a code per FLT/HH/H/L/LL/OVR/UNR: -1 for none, otherwise state·10 + priority. Errors are logged to `EFC_PV`. This replaced `isAlarmActiveFiltered`, which Perspective doesn't re-run when alarms change.
- **A1 strip:** fault first, then the highest active priority (blinking if any item is unacked), then the faded cleared color, otherwise Normal.
- **B2 track:** a percent-mode coordinate container holding the base bands, the priority overlays, a frame and the SVG pointer. The range is in the Track tooltip.
- **Scaling:** all sizes are in vh.

## Open items
- Raise the faded level (cleared-unacked and the blink OFF phase) from 0.25 to about 0.4 on white?
- Fold the PV classes (`PV/*`, `Alarm/Mod/*`, `Bar/Band/*`, `Bar/Frame`) into EFC_Styles.
- `PV/Chip/Diagnostic` and `PV/Strip/Diagnostic` still use `#7A7A7A`. EFC_Styles moved Diagnostic to `#6E6E6E` in the ISA-101 audit.
- Add the `HW_Fault` alarm (High) to the real `DDT_Process_Value` UDT.
- **Tight spots:** the A1 tag truncates with 3+ letters; large values with 4-letter units only just fit; text at 1080p is 9–11 px.
- **To verify on a gateway:** the queryStatus state strings and the nested source wildcard.
