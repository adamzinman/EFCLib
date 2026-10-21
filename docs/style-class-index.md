| Class path | Use |
|---|---|
| `Text/Title` | Screen title in header bar (24px) |
| `Text/Header` | Section / panel heading (20px) |
| `Text/Subheader` | Sub-section heading (16px) |
| `Text/Body` | Default body text (14px) |
| `Text/Label` | Field label next to a value (12px) |
| `Text/Caption` | Footnotes, timestamps, hints (11px) |
| `Text/Micro` | Smallest legible text, use sparingly (10px) |
| `Text/TagName` | Equipment / instrument tag (e.g. XV-101) |
| `Text/Value` | Live process value (14px, tabular digits) |
| `Text/ValueLarge` | Key process value / KPI (20px) |
| `Text/ValueHero` | Overview headline number (32px) |
| `Text/Units` | Engineering units after a value (11px) |
| `Text/Status` | Status word under equipment (OPEN, RUNNING) |
| `Text/MenuItem` | Left-menu navigation text |
| `Text/Link` | Clickable text link |
| `Text/Code` | Monospace text: addresses, script names |
| `Text/Size/XXS` | Font size 10px at 1080p (0.926vh) |
| `Text/Size/XS` | Font size 11px at 1080p (1.019vh) |
| `Text/Size/S` | Font size 12px at 1080p (1.111vh) |
| `Text/Size/M` | Font size 14px at 1080p (1.296vh) |
| `Text/Size/L` | Font size 16px at 1080p (1.481vh) |
| `Text/Size/XL` | Font size 20px at 1080p (1.852vh) |
| `Text/Size/XXL` | Font size 24px at 1080p (2.222vh) |
| `Text/Size/XXXL` | Font size 32px at 1080p (2.963vh) |
| `Text/Weight/Light` | Font weight 300 |
| `Text/Weight/Regular` | Font weight 400 |
| `Text/Weight/Semibold` | Font weight 600 |
| `Text/Weight/Bold` | Font weight 700 |
| `Text/Color/Default` | Normal dark text |
| `Text/Color/Muted` | Secondary text |
| `Text/Color/Faint` | Tertiary text |
| `Text/Color/Disabled` | Disabled / unavailable |
| `Text/Color/Inverse` | Text on dark backgrounds |
| `Text/Color/Editable` | Operator-adjustable value |
| `Text/Color/Fault` | Fault text (dark; always pair with the word FAULT) |
| `Text/Mod/Italic` | Italic |
| `Text/Mod/Underline` | Underline |
| `Text/Mod/Upper` | UPPERCASE |
| `Text/Mod/Left` | Align left |
| `Text/Mod/Center` | Align center |
| `Text/Mod/Right` | Align right (values) |
| `Text/Mod/Ellipsis` | Single line, cut with ... |
| `Text/Mod/Wrap` | Allow wrapping |
| `Text/Mod/NoWrap` | Never wrap |
| `Text/Mod/Tabular` | Fixed-width digits so values don't jitter |
| `Text/Mod/NoSelect` | Prevent text selection (touch screens) |
| `Container/Screen` | Page root / process area background |
| `Container/Header` | Top header bar |
| `Container/Menu` | Left navigation menu (120px) |
| `Container/TrendPanel` | Right trend / dynamic trend panel |
| `Container/AlarmBar` | Bottom alarm bar (140px) |
| `Container/ProcessArea` | Main process graphic area |
| `Container/Panel` | Grouped content panel |
| `Container/Card` | Raised card / tile |
| `Container/Inset` | Recessed area (lists, readouts) |
| `Container/GroupBox` | Outlined group (no fill) |
| `Container/Toolbar` | Row of buttons / filters |
| `Container/Popup` | Popup / faceplate body |
| `Container/PopupHeader` | Popup / faceplate title strip |
| `Container/Faceplate` | Equipment faceplate section |
| `Container/ValueBox` | Boxed live value readout |
| `Container/Divider/Horizontal` | 1px horizontal rule |
| `Container/Divider/Vertical` | 1px vertical rule |
| `Container/Scroll` | Scrollable region |
| `Button/Default` | Standard command button |
| `Button/Primary` | Main action on a screen / popup |
| `Button/Subtle` | Low-emphasis button (no fill until hover) |
| `Button/Danger` | Stop / trip / destructive action (neutral per ISA-101; heavy border) |
| `Button/Start` | Start / open command (white = running convention) |
| `Button/Stop` | Stop / close command (gray = stopped convention) |
| `Button/Small` | Compact button (12px) |
| `Button/Large` | Large touch button (16px) |
| `Button/Icon` | Icon-only square button |
| `Button/Momentary` | Small blank square push button (valve template) |
| `Button/Toggle/Off` | Toggle in OFF position |
| `Button/Toggle/On` | Toggle in ON position |
| `Button/Nav` | Left-menu nav item |
| `Button/NavActive` | Left-menu item for the current page |
| `Button/Tab` | Tab (inactive) |
| `Button/TabActive` | Tab (selected) |
| `Input/Field` | Text / numeric entry (editable = blue text) |
| `Input/Setpoint` | Setpoint entry, right-aligned |
| `Input/Dropdown` | Dropdown selector |
| `Input/ReadOnly` | Display-only field |
| `Input/Invalid` | Entry failed validation |
| `Input/Pending` | Written but not yet confirmed by PLC |
| `Input/Check` | Checkbox / radio label text |
| `Value/Normal` | Good-quality live value |
| `Value/Setpoint` | Setpoint (read-only display) |
| `Value/Output` | Controller output % |
| `Value/BadQuality` | Bad / uncertain quality or comms loss |
| `Value/Stale` | Value not updating |
| `Value/Forced` | Forced / overridden in PLC |
| `Value/Simulated` | Simulated value (testing) |
| `State/Running` | Running / open |
| `State/Stopped` | Stopped / closed |
| `State/Transition` | Opening / closing / starting |
| `State/Fault` | Fault / failed |
| `State/OutOfService` | Out of service / disabled |
| `State/Unknown` | State unknown (bad quality) |
| `Mode/Auto` | Automatic mode (normal) |
| `Mode/Cascade` | Cascade mode |
| `Mode/Manual` | Manual mode (abnormal = dark) |
| `Mode/Local` | Local / field control |
| `Mode/Simulated` | Simulation mode |
| `Indicator/LED/On` | Lamp on (white) |
| `Indicator/LED/Off` | Lamp off (gray) |
| `Indicator/LED/Fault` | Lamp faulted (dark gray) |
| `Indicator/LED/Unknown` | Lamp state unknown |
| `Indicator/Permissive` | Orange P (permissive missing) |
| `Indicator/Interlock` | Red I (interlock active) |
| `Indicator/Badge` | Small count badge (e.g. alarm count) |
| `Bar/Track` | Level/bar graph background |
| `Bar/Fill` | Level/bar graph fill (normal) |
| `Bar/FillAlarm` | Bar fill when in alarm |
| `Bar/Marker` | Setpoint / limit marker line |
| `Alarm/Critical/Fill` | Critical alarm: solid fill (active, acked) |
| `Alarm/Critical/Unacked` | Critical alarm: blinking fill (active, unacked) |
| `Alarm/Critical/Outline` | Critical alarm: 3px outline around a value/symbol |
| `Alarm/Critical/Text` | Critical alarm: priority-colored text on a dark chip |
| `Alarm/High/Fill` | High alarm: solid fill (active, acked) |
| `Alarm/High/Unacked` | High alarm: blinking fill (active, unacked) |
| `Alarm/High/Outline` | High alarm: 3px outline around a value/symbol |
| `Alarm/High/Text` | High alarm: priority-colored text on a dark chip |
| `Alarm/Medium/Fill` | Medium alarm: solid fill (active, acked) |
| `Alarm/Medium/Unacked` | Medium alarm: blinking fill (active, unacked) |
| `Alarm/Medium/Outline` | Medium alarm: 3px outline around a value/symbol |
| `Alarm/Medium/Text` | Medium alarm: priority-colored text on a dark chip |
| `Alarm/Low/Fill` | Low alarm: solid fill (active, acked) |
| `Alarm/Low/Unacked` | Low alarm: blinking fill (active, unacked) |
| `Alarm/Low/Outline` | Low alarm: 3px outline around a value/symbol |
| `Alarm/Low/Text` | Low alarm: priority-colored text on a dark chip |
| `Alarm/Diagnostic/Fill` | Diagnostic alarm: solid fill (active, acked) |
| `Alarm/Diagnostic/Unacked` | Diagnostic alarm: blinking fill (active, unacked) |
| `Alarm/Diagnostic/Outline` | Diagnostic alarm: 3px outline around a value/symbol |
| `Alarm/Diagnostic/Text` | Diagnostic alarm: priority-colored text on a dark chip |
| `Alarm/Status/ClearedUnacked` | Returned to normal, not yet acked (steady + faded; flashing = active unacked only) |
| `Alarm/Status/Shelved` | Shelved alarm |
| `Alarm/Status/Suppressed` | Suppressed / disabled alarm |
| `Alarm/Banner` | Single-line most-recent-alarm banner |
| `Table/Header` | Table header cells |
| `Table/Row` | Table body row |
| `Table/RowAlt` | Alternate (striped) row |
| `Table/Cell` | Table cell padding |
| `Table/CellNumeric` | Right-aligned numeric cell |
| `Table/Selected` | Selected row |
| `Util/Pad/S` | Padding 4px |
| `Util/Pad/M` | Padding 8px |
| `Util/Pad/L` | Padding 12px |
| `Util/Pad/None` | No padding |
| `Util/Border` | 1px border |
| `Util/BorderDashed` | 1px dashed border |
| `Util/Rounded` | Rounded corners |
| `Util/Shadow` | Soft shadow (popups only per ISA-101) |
| `Util/Pointer` | Hand cursor (clickable) |
| `Util/Disabled` | Faded + not clickable |
| `Util/Transparent` | No background |
| `Util/Highlight` | Highlight / search hit (non-alarm blue-gray) |
| `Util/Collapsed` | Removed from layout (takes no space, keeps neighbours centered) |
| `Util/Clip` | Hide overflow |
| `Indicator/PermissiveBadge` | P badge: permissive missing (NFPA 79 amber, black text) |
| `Indicator/InterlockBadge` | I badge: interlock active (red, white text) |
| `Mode/ManualSplit` | Manual mode 'M' segment left of the status chip (useButton = false). Same height, font and border as the State/* chip |
| `Mode/ManualJoined` | Add to a State/* chip when Mode/ManualSplit sits on its left (squares the joined corners) |
| `Mode/ManualSplitStatus` | Status segment paired with Mode/ManualSplit (plain-text statuses) |
| `Button/Command` | Manual command button on P&ID templates: blank square, raised, sinks when pressed |
