# PV style classes

| Class path | Use |
|---|---|
| `PV/Card` | PV template card: white, 6 px corners, 1 px #B3B3B3 border with darker bottom edge, soft shadow (v1.2) |
| `PV/Shell` | Transparent outer margin so the card shadow is not clipped by the embedding container |
| `PV/Body` | PV template inner padding (A1) |
| `PV/BodyBar` | PV range-bar template inner padding (B2) |
| `PV/HeaderRow` | Tag + letter row (fixed 12 px high, 3 px gap) |
| `PV/Tag` | Tag name in the 100 x 50 card: 11 px bold |
| `PV/Value` | Live value, A1 (18 px semibold, tabular) |
| `PV/ValueSmall` | Live value, B2 (16 px semibold, tabular) |
| `PV/Units` | Engineering units, 10 px muted |
| `PV/ChipRow` | Letter-indicator row (2 px gap) |
| `PV/Strip/Normal` | A1 edge strip, no alarm |
| `PV/Strip/Fault` | A1 edge strip, HW fault |
| `PV/Strip/Critical` | A1 edge strip, Critical alarm |
| `PV/Chip/Critical` | Letter indicator, Critical priority |
| `Bar/Band/Critical` | Range-bar band overlay, Critical priority |
| `PV/Strip/High` | A1 edge strip, High alarm |
| `PV/Chip/High` | Letter indicator, High priority |
| `Bar/Band/High` | Range-bar band overlay, High priority |
| `PV/Strip/Medium` | A1 edge strip, Medium alarm |
| `PV/Chip/Medium` | Letter indicator, Medium priority |
| `Bar/Band/Medium` | Range-bar band overlay, Medium priority |
| `PV/Strip/Low` | A1 edge strip, Low alarm |
| `PV/Chip/Low` | Letter indicator, Low priority |
| `Bar/Band/Low` | Range-bar band overlay, Low priority |
| `PV/Strip/Diagnostic` | A1 edge strip, Diagnostic alarm |
| `PV/Chip/Diagnostic` | Letter indicator, Diagnostic priority |
| `Bar/Band/Diagnostic` | Range-bar band overlay, Diagnostic priority |
| `PV/Chip/Fault` | Letter indicator FLT (HW fault): dark gray, white text |
| `PV/Chip/Inhibit` | Letter indicator INH (a limit is inhibited) |
| `PV/Chip/More` | +N overflow letter (more than 2 letters active); tooltip lists the hidden ones |
| `Alarm/Mod/Blink` | Modifier: blink while unacknowledged (uses efc-blink keyframes in the EFC_Styles stylesheet) |
| `Alarm/Mod/ClearedUnacked` | Modifier: cleared but unacknowledged = steady blink-OFF look (opacity 0.25) |
| `Bar/Band/Normal` | Range-bar normal band (L to H) |
| `Bar/Band/Alarm` | Range-bar alarm band (LL-L, H-HH) |
| `Bar/Band/Extreme` | Range-bar extreme band (below LL, above HH) |
| `Bar/Frame` | Range-bar outline (drawn over the bands) |
