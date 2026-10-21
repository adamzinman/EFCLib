"""
EFC Perspective Style Library generator (Ignition 8.1, ISA-101 light gray).

Edit PALETTE / TYPE_SCALE below, then run:  python3 build_styles.py
Outputs (in ./dist):
  EFC_Styles.zip      Perspective project: style classes, stylesheet.css, Styles/_Catalog view
  style_preview.html  Browser preview of every class (vh converted to px at 1080p)
  style_index.md      Table of every class path + what it is for
"""
import json, os, re, zipfile, datetime, html

PROJECT = "EFC_Styles"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "styles")   # gitignored build output

# ---------------------------------------------------------------- palette
PALETTE = {
    # neutrals (ISA-101 grayscale)
    "screen":      "#D9D9D9",   # process area / page background
    "header":      "#C4C4C4",   # header bar
    "menu":        "#CCCCCC",   # left menu
    "trend":       "#E0E0E0",   # right trend panel
    "alarmBar":    "#BDBDBD",   # bottom alarm bar
    "panel":       "#E6E6E6",
    "card":        "#F0F0F0",
    "inset":       "#CFCFCF",
    "field":       "#FFFFFF",   # editable entry background
    "readonly":    "#EDEDED",
    "border":      "#A6A6A6",
    "borderDark":  "#7F7F7F",
    "borderXDark": "#595959",
    "text":        "#1F1F1F",
    "textMuted":   "#4D4D4D",
    "textFaint":   "#5A5A5A",
    "textDisabled":"#9A9A9A",
    "textInverse": "#FFFFFF",
    "accent":      "#4D4D4D",   # primary button / active nav
    "editable":    "#1F4E99",   # setpoints & operator-entry values
    "link":        "#1F4E99",
    "hover":       "#F5F5F5",
    "pressed":     "#BFBFBF",
    # equipment state (matches P&ID symbol suite convention)
    "running":     "#FFFFFF",
    "stopped":     "#9E9E9E",
    "transition":  "#C4C4C4",   # visible against the #D9D9D9 screen
    "fault":       "#3A3A3A",   # ISA-101: dark gray, red is reserved for Critical alarms
    # abnormal / mode
    "manual":      "#595959",
    "simulated":   "#D7EEEB", "simulatedText": "#00695C",   # teal (purple = radiation per ANSI Z535)
    "badQuality":  "#B000B0",
    "permissive":  "#8F4500",   # orange P text form (4.9:1 on gray; ISA-101 audit)
    "interlock":   "#C00000",   # red I
    # alarm priorities (Ignition: Diagnostic, Low, Medium, High, Critical)
    "alarmCritical": "#D50000",
    "alarmHigh":     "#FF7A00",
    "alarmMedium":   "#FFD200",
    "alarmLow":      "#00A3E0",
    "alarmDiag":     "#6E6E6E",   # neutral gray (5.1:1 with white text; ISA-101 audit)
}
P = PALETTE

# ------------------------------------------------------------ type scale
# px at 1920x1080 -> vh (1vh = 10.8px at 1080p, 21.6px at 2160p)
def vh(px):
    return f"{round(px / 10.8, 3)}vh"

TYPE_SCALE = {"XXS": 10, "XS": 11, "S": 12, "M": 14, "L": 16, "XL": 20, "XXL": 24, "XXXL": 32}
FS = {k: vh(v) for k, v in TYPE_SCALE.items()}
LINE = vh(1)        # 1 px line at 1080p (2 px at 4K)
LINE2 = vh(2)
LINE3 = vh(3)       # alarm outline weight (matches symbols)
RAD = vh(3)
PAD_S, PAD_M, PAD_L = vh(4), vh(8), vh(12)
FONT = "'Noto Sans', 'Segoe UI', Arial, sans-serif"
MONO = "'Noto Sans Mono', Consolas, 'Courier New', monospace"

# ---------------------------------------------------------- class builder
CLASSES = {}   # path -> (dict(base, variants), description)

def sc(path, desc, base, hover=None, active=None, focus=None, disabled=None):
    variants = []
    for pseudo, st in (("hover", hover), ("active", active), ("focus", focus), ("disabled", disabled)):
        if st:
            variants.append({"pseudo": pseudo, "style": st})
    CLASSES[path] = ({"base": {"style": base}, "variants": variants}, desc)

def text(size, weight="400", color=None, **extra):
    s = {"fontSize": FS[size], "fontWeight": weight, "color": color or P["text"], "fontFamily": FONT}
    s.update(extra)
    return s

# ---------------- Text: semantic roles
sc("Text/Title",     "Screen title in header bar (24px)",           text("XXL", "700"))
sc("Text/Header",    "Section / panel heading (20px)",              text("XL", "600"))
sc("Text/Subheader", "Sub-section heading (16px)",                  text("L", "600"))
sc("Text/Body",      "Default body text (14px)",                    text("M"))
sc("Text/Label",     "Field label next to a value (12px)",          text("S", "400", P["textMuted"]))
sc("Text/Caption",   "Footnotes, timestamps, hints (11px)",         text("XS", "400", P["textFaint"]))
sc("Text/Micro",     "Smallest legible text, use sparingly (10px)",  text("XXS", "400", P["textFaint"]))
sc("Text/TagName",   "Equipment / instrument tag (e.g. XV-101)",    text("S", "700", letterSpacing="0.02em"))
sc("Text/Value",     "Live process value (14px, tabular digits)",   text("M", "600", fontVariantNumeric="tabular-nums"))
sc("Text/ValueLarge","Key process value / KPI (20px)",              text("XL", "600", fontVariantNumeric="tabular-nums"))
sc("Text/ValueHero", "Overview headline number (32px)",             text("XXXL", "700", fontVariantNumeric="tabular-nums"))
sc("Text/Units",     "Engineering units after a value (11px)",      text("XS", "400", P["textMuted"], marginLeft=vh(3)))
sc("Text/Status",    "Status word under equipment (OPEN, RUNNING)", text("XS", "700", letterSpacing="0.04em", textTransform="uppercase"))
sc("Text/MenuItem",  "Left-menu navigation text",                   text("S", "600"))
sc("Text/Link",      "Clickable text link",
   text("M", "400", P["link"], textDecoration="underline", cursor="pointer"),
   hover={"color": "#0F2E66"})
sc("Text/Code",      "Monospace text: addresses, script names",     {"fontSize": FS["S"], "fontFamily": MONO, "color": P["text"]})

# ---------------- Text: size scale (combine with any other class)
for k, px in TYPE_SCALE.items():
    sc(f"Text/Size/{k}", f"Font size {px}px at 1080p ({FS[k]})", {"fontSize": FS[k]})

# ---------------- Text: weight
for name, w in (("Light", "300"), ("Regular", "400"), ("Semibold", "600"), ("Bold", "700")):
    sc(f"Text/Weight/{name}", f"Font weight {w}", {"fontWeight": w})

# ---------------- Text: color
for name, c, d in (("Default", P["text"], "Normal dark text"),
                   ("Muted", P["textMuted"], "Secondary text"),
                   ("Faint", P["textFaint"], "Tertiary text"),
                   ("Disabled", P["textDisabled"], "Disabled / unavailable"),
                   ("Inverse", P["textInverse"], "Text on dark backgrounds"),
                   ("Editable", P["editable"], "Operator-adjustable value"),
                   ("Fault", P["fault"], "Fault text (dark; always pair with the word FAULT)")):
    sc(f"Text/Color/{name}", d, {"color": c})

# ---------------- Text: modifiers
sc("Text/Mod/Italic",    "Italic",               {"fontStyle": "italic"})
sc("Text/Mod/Underline", "Underline",            {"textDecoration": "underline"})
sc("Text/Mod/Upper",     "UPPERCASE",            {"textTransform": "uppercase", "letterSpacing": "0.03em"})
sc("Text/Mod/Left",      "Align left",           {"textAlign": "left", "justifyContent": "flex-start"})
sc("Text/Mod/Center",    "Align center",         {"textAlign": "center", "justifyContent": "center"})
sc("Text/Mod/Right",     "Align right (values)", {"textAlign": "right", "justifyContent": "flex-end"})
sc("Text/Mod/Ellipsis",  "Single line, cut with ...", {"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"})
sc("Text/Mod/Wrap",      "Allow wrapping",       {"whiteSpace": "normal", "overflowWrap": "anywhere"})
sc("Text/Mod/NoWrap",    "Never wrap",           {"whiteSpace": "nowrap"})
sc("Text/Mod/Tabular",   "Fixed-width digits so values don't jitter", {"fontVariantNumeric": "tabular-nums"})
sc("Text/Mod/NoSelect",  "Prevent text selection (touch screens)", {"userSelect": "none"})

# ---------------- Containers / layout regions
def box(bg, border=None, **extra):
    s = {"backgroundColor": bg}
    if border:
        s["border"] = f"{LINE} solid {border}"
    s.update(extra)
    return s

sc("Container/Screen",      "Page root / process area background", box(P["screen"], fontFamily=FONT, color=P["text"]))
sc("Container/Header",      "Top header bar",          box(P["header"], borderBottom=f"{LINE} solid {P['borderDark']}", padding=f"0 {PAD_M}"))
sc("Container/Menu",        "Left navigation menu (120px)", box(P["menu"], borderRight=f"{LINE} solid {P['borderDark']}"))
sc("Container/TrendPanel",  "Right trend / dynamic trend panel", box(P["trend"], borderLeft=f"{LINE} solid {P['borderDark']}"))
sc("Container/AlarmBar",    "Bottom alarm bar (140px)", box(P["alarmBar"], borderTop=f"{LINE} solid {P['borderDark']}"))
sc("Container/ProcessArea", "Main process graphic area", box(P["screen"]))
sc("Container/Panel",       "Grouped content panel",   box(P["panel"], P["border"], borderRadius=RAD, padding=PAD_M))
sc("Container/Card",        "Raised card / tile",      box(P["card"], P["border"], borderRadius=RAD, padding=PAD_M))
sc("Container/Inset",       "Recessed area (lists, readouts)", box(P["inset"], borderTop=f"{LINE} solid {P['borderDark']}", borderLeft=f"{LINE} solid {P['borderDark']}", borderRight=f"{LINE} solid {P['card']}", borderBottom=f"{LINE} solid {P['card']}", padding=PAD_S))
sc("Container/GroupBox",    "Outlined group (no fill)", {"border": f"{LINE} solid {P['borderDark']}", "borderRadius": RAD, "padding": PAD_M})
sc("Container/Toolbar",     "Row of buttons / filters", box(P["panel"], borderBottom=f"{LINE} solid {P['border']}", padding=PAD_S))
sc("Container/Popup",       "Popup / faceplate body",  box(P["panel"], P["borderXDark"], boxShadow="0 0.4vh 1.2vh rgba(0,0,0,0.35)"))
sc("Container/PopupHeader", "Popup / faceplate title strip", box(P["borderXDark"], color=P["textInverse"], fontSize=FS["L"], fontWeight="600", padding=f"{PAD_S} {PAD_M}"))
sc("Container/Faceplate",   "Equipment faceplate section", box(P["card"], P["border"], padding=PAD_M))
sc("Container/ValueBox",    "Boxed live value readout", box(P["field"], P["border"], padding=f"{vh(2)} {PAD_S}", justifyContent="flex-end"))
sc("Container/Divider/Horizontal", "1px horizontal rule", {"borderTop": f"{LINE} solid {P['borderDark']}", "height": "0px", "alignSelf": "stretch"})
sc("Container/Divider/Vertical",   "1px vertical rule",   {"borderLeft": f"{LINE} solid {P['borderDark']}", "width": "0px", "alignSelf": "stretch"})
sc("Container/Scroll",      "Scrollable region",       {"overflowY": "auto", "overflowX": "hidden"})

# ---------------- Buttons
BTN = {"backgroundColor": P["panel"], "color": P["text"], "border": f"{LINE} solid {P['borderDark']}",
       "borderRadius": RAD, "fontSize": FS["M"], "fontWeight": "600", "fontFamily": FONT,
       "padding": f"{PAD_S} {PAD_M}", "cursor": "pointer", "boxShadow": "none", "userSelect": "none"}
DIS = {"backgroundColor": P["readonly"], "color": P["textDisabled"], "borderColor": P["border"], "cursor": "not-allowed"}

def btn(path, desc, over=None, hover=None, active=None):
    base = dict(BTN); base.update(over or {})
    sc(path, desc, base,
       hover=hover or {"backgroundColor": P["hover"]},
       active=active or {"backgroundColor": P["pressed"]},
       focus={"outline": f"{LINE2} solid {P['editable']}", "outlineOffset": vh(1)},
       disabled=DIS)

btn("Button/Default",   "Standard command button")
btn("Button/Primary",   "Main action on a screen / popup",
    {"backgroundColor": P["accent"], "color": P["textInverse"], "borderColor": P["borderXDark"]},
    hover={"backgroundColor": "#666666"}, active={"backgroundColor": "#333333"})
btn("Button/Subtle",    "Low-emphasis button (no fill until hover)",
    {"backgroundColor": "transparent", "borderColor": "transparent"},
    hover={"backgroundColor": P["hover"], "borderColor": P["border"]})
btn("Button/Danger",    "Stop / trip / destructive action (neutral per ISA-101; heavy border)",
    {"backgroundColor": P["panel"], "color": P["text"], "borderColor": P["text"], "borderWidth": LINE2, "fontWeight": "800"},
    hover={"backgroundColor": "#F5F5F5"}, active={"backgroundColor": P["pressed"]})   # ISA-101 audit: no red on hover/press
btn("Button/Start",     "Start / open command (white = running convention)",
    {"backgroundColor": P["running"]})
btn("Button/Stop",      "Stop / close command (gray = stopped convention)",
    {"backgroundColor": P["stopped"]}, hover={"backgroundColor": "#B0B0B0"})
btn("Button/Small",     "Compact button (12px)", {"fontSize": FS["S"], "padding": f"{vh(2)} {PAD_S}"})
btn("Button/Large",     "Large touch button (16px)", {"fontSize": FS["L"], "padding": f"{PAD_M} {PAD_L}"})
btn("Button/Icon",      "Icon-only square button",
    {"backgroundColor": "transparent", "borderColor": "transparent", "padding": vh(2)},
    hover={"backgroundColor": P["hover"], "borderColor": P["border"]})
btn("Button/Momentary", "Small blank square push button (valve template)",
    {"backgroundColor": P["field"], "padding": "0px", "borderRadius": vh(2), "minWidth": "0px", "minHeight": "0px"})
btn("Button/Toggle/Off", "Toggle in OFF position",
    {"backgroundColor": P["stopped"]})
btn("Button/Toggle/On",  "Toggle in ON position",
    {"backgroundColor": P["running"], "borderColor": P["borderXDark"], "borderWidth": LINE2})
btn("Button/Nav",        "Left-menu nav item",
    {"backgroundColor": "transparent", "border": "none", "borderRadius": "0px", "borderLeft": f"{vh(4)} solid transparent",
     "fontSize": FS["S"], "justifyContent": "flex-start", "textAlign": "left"},
    hover={"backgroundColor": P["hover"]})
btn("Button/NavActive",  "Left-menu item for the current page",
    {"backgroundColor": P["field"], "border": "none", "borderRadius": "0px", "borderLeft": f"{vh(4)} solid {P['accent']}",
     "fontSize": FS["S"], "justifyContent": "flex-start", "textAlign": "left"},
    hover={"backgroundColor": P["field"]})
btn("Button/Tab",        "Tab (inactive)",
    {"backgroundColor": P["inset"], "borderRadius": f"{RAD} {RAD} 0 0", "borderBottom": "none", "fontSize": FS["S"]})
btn("Button/TabActive",  "Tab (selected)",
    {"backgroundColor": P["panel"], "borderRadius": f"{RAD} {RAD} 0 0", "borderBottom": f"{LINE} solid {P['panel']}", "fontSize": FS["S"]},
    hover={"backgroundColor": P["panel"]})

# ---------------- Inputs
FIELD = {"backgroundColor": P["field"], "color": P["editable"], "border": f"{LINE} solid {P['borderDark']}",
         "borderRadius": vh(2), "fontSize": FS["M"], "fontFamily": FONT, "fontWeight": "600",
         "padding": f"{vh(2)} {PAD_S}", "fontVariantNumeric": "tabular-nums"}
def fld(path, desc, over=None, **kw):
    s = dict(FIELD); s.update(over or {})
    sc(path, desc, s,
       hover=kw.get("hover", {"borderColor": P["borderXDark"]}),
       focus={"borderColor": P["editable"], "outline": f"{LINE} solid {P['editable']}"},
       disabled={"backgroundColor": P["readonly"], "color": P["textDisabled"], "borderColor": P["border"]})
fld("Input/Field",     "Text / numeric entry (editable = blue text)")
fld("Input/Setpoint",  "Setpoint entry, right-aligned", {"textAlign": "right"})
fld("Input/Dropdown",  "Dropdown selector", {"color": P["text"], "fontWeight": "400"})
fld("Input/ReadOnly",  "Display-only field", {"backgroundColor": P["readonly"], "color": P["text"], "borderColor": P["border"]}, hover={})
fld("Input/Invalid",   "Entry failed validation", {"borderColor": P["fault"], "borderWidth": LINE2, "backgroundColor": "#FFF3F3"})
fld("Input/Pending",   "Written but not yet confirmed by PLC", {"borderStyle": "dashed", "borderColor": P["editable"], "fontStyle": "italic"})
sc("Input/Check",      "Checkbox / radio label text", text("M"))

# ---------------- Process value quality
sc("Value/Normal",     "Good-quality live value", text("M", "600", fontVariantNumeric="tabular-nums"))
sc("Value/Setpoint",   "Setpoint (read-only display)", text("M", "600", P["editable"], fontVariantNumeric="tabular-nums"))
sc("Value/Output",     "Controller output %", text("M", "600", P["textMuted"], fontVariantNumeric="tabular-nums"))
sc("Value/BadQuality", "Bad / uncertain quality or comms loss",
   {"color": P["textFaint"], "fontStyle": "italic", "outline": f"{LINE} dashed {P['badQuality']}", "outlineOffset": f"-{LINE}", "backgroundColor": P["readonly"]})
sc("Value/Stale",      "Value not updating", {"color": P["textFaint"], "fontStyle": "italic"})
sc("Value/Forced",     "Forced / overridden in PLC", {"backgroundColor": P["simulated"], "color": P["simulatedText"], "border": f"{LINE} solid {P['simulatedText']}"})
sc("Value/Simulated",  "Simulated value (testing)", {"backgroundColor": P["simulated"], "color": P["simulatedText"], "fontStyle": "italic"})

# ---------------- Equipment state chips
CHIP = {"fontSize": FS["XS"], "fontWeight": "700", "letterSpacing": "0.04em", "textTransform": "uppercase",
        "borderRadius": vh(2), "padding": f"{vh(1)} {PAD_S}", "border": f"{LINE} solid {P['borderDark']}",
        "textAlign": "center", "justifyContent": "center", "fontFamily": FONT}
def chip(path, desc, bg, fg, **extra):
    s = dict(CHIP); s.update({"backgroundColor": bg, "color": fg}); s.update(extra)
    sc(path, desc, s)
chip("State/Running",    "Running / open",              P["running"], P["text"])
chip("State/Stopped",    "Stopped / closed",            P["stopped"], P["text"])
chip("State/Transition", "Opening / closing / starting",P["transition"], P["text"], borderStyle="dashed")
chip("State/Fault",      "Fault / failed",              P["fault"], P["textInverse"], borderColor="#000000")
chip("State/OutOfService","Out of service / disabled",  P["readonly"], "#5E5E5E", borderStyle="dashed", borderColor="#7F7F7F")   # 5.5:1 (ISA-101 audit)
chip("State/Unknown",    "State unknown (bad quality)", P["readonly"], P["badQuality"], borderStyle="dashed", borderColor=P["badQuality"])
chip("Mode/Auto",        "Automatic mode (normal)",     P["panel"], P["text"])
chip("Mode/Cascade",     "Cascade mode",                P["panel"], P["text"])
chip("Mode/Manual",      "Manual mode (abnormal = dark)", P["manual"], P["textInverse"], borderColor=P["text"])
chip("Mode/Local",       "Local / field control",       P["manual"], P["textInverse"], borderColor=P["text"], fontStyle="italic")
chip("Mode/Simulated",   "Simulation mode",             P["simulated"], P["simulatedText"], borderColor=P["simulatedText"])

# ---------------- Indicators
LED = {"borderRadius": "50%", "border": f"{LINE} solid {P['borderXDark']}", "minWidth": vh(10), "minHeight": vh(10)}
for name, bg, d in (("On", P["running"], "Lamp on (white)"), ("Off", P["stopped"], "Lamp off (gray)"),
                    ("Fault", P["fault"], "Lamp faulted (dark gray)")):
    s = dict(LED); s["backgroundColor"] = bg
    sc(f"Indicator/LED/{name}", d, s)
s = dict(LED); s.update({"backgroundColor": P["readonly"], "border": f"{LINE} dashed {P['badQuality']}"})
sc("Indicator/LED/Unknown", "Lamp state unknown", s)
sc("Indicator/Permissive", "Orange P (permissive missing)", text("S", "800", P["permissive"]))
sc("Indicator/Interlock",  "Red I (interlock active)",      text("S", "800", P["interlock"]))
sc("Indicator/Badge",      "Small count badge (e.g. alarm count)",
   {"backgroundColor": P["borderXDark"], "color": P["textInverse"], "fontSize": FS["XS"], "fontWeight": "700",
    "borderRadius": vh(8), "padding": f"0 {vh(5)}", "justifyContent": "center", "textAlign": "center"})
sc("Bar/Track",     "Level/bar graph background", {"backgroundColor": P["field"], "border": f"{LINE} solid {P['borderDark']}"})
sc("Bar/Fill",      "Level/bar graph fill (normal)", {"backgroundColor": "#8C8C8C"})
sc("Bar/FillAlarm", "Bar fill when in alarm",   {"backgroundColor": P["alarmHigh"]})
sc("Bar/Marker",    "Setpoint / limit marker line", {"backgroundColor": P["editable"], "minHeight": LINE2})

# ---------------- Alarms
ALARMS = (("Critical", P["alarmCritical"], P["textInverse"]),
          ("High",     P["alarmHigh"],     P["text"]),
          ("Medium",   P["alarmMedium"],   P["text"]),
          ("Low",      P["alarmLow"],      P["text"]),
          ("Diagnostic", P["alarmDiag"],   P["textInverse"]))
for name, c, fg in ALARMS:
    sc(f"Alarm/{name}/Fill",    f"{name} alarm: solid fill (active, acked)",
       {"backgroundColor": c, "color": fg, "fontWeight": "700", "padding": f"0 {vh(3)}", "borderRadius": vh(2)})
    sc(f"Alarm/{name}/Unacked", f"{name} alarm: blinking fill (active, unacked)",
       {"backgroundColor": c, "color": fg, "fontWeight": "700", "padding": f"0 {vh(3)}", "borderRadius": vh(2), "animation": "efc-blink 1s steps(1, end) infinite"})
    sc(f"Alarm/{name}/Outline", f"{name} alarm: 3px outline around a value/symbol",
       {"outline": f"{LINE3} solid {c}", "outlineOffset": f"{LINE}"})
    sc(f"Alarm/{name}/Text",    f"{name} alarm: priority-colored text on a dark chip",
       {"color": "#FF4D4D" if name == "Critical" else ("#9A9A9A" if name == "Diagnostic" else c), "backgroundColor": P["text"], "fontWeight": "700", "padding": f"0 {vh(3)}", "borderRadius": vh(2)})
sc("Alarm/Status/ClearedUnacked", "Returned to normal, not yet acked (steady + faded; flashing = active unacked only)",
   {"backgroundColor": P["field"], "color": P["text"], "border": f"{LINE2} solid {P['borderXDark']}", "opacity": "0.45"})
sc("Alarm/Status/Shelved",    "Shelved alarm", {"backgroundColor": P["readonly"], "color": P["textFaint"], "border": f"{LINE} dashed {P['borderDark']}", "fontStyle": "italic"})
sc("Alarm/Status/Suppressed", "Suppressed / disabled alarm", {"color": P["textDisabled"], "textDecoration": "line-through"})
sc("Alarm/Banner",  "Single-line most-recent-alarm banner", text("M", "600", backgroundColor=P["card"], border=f"{LINE} solid {P['borderDark']}", padding=f"{vh(2)} {PAD_M}"))

# ---------------- Table
sc("Table/Header",  "Table header cells", text("S", "700", P["text"], backgroundColor=P["inset"], borderBottom=f"{LINE} solid {P['borderDark']}", padding=f"{vh(3)} {PAD_S}"))
sc("Table/Row",     "Table body row",     text("S", "400", backgroundColor=P["card"], borderBottom=f"{LINE} solid {P['border']}"), hover={"backgroundColor": P["hover"]})
sc("Table/RowAlt",  "Alternate (striped) row", {"backgroundColor": P["panel"]})
sc("Table/Cell",    "Table cell padding", {"padding": f"{vh(3)} {PAD_S}", "fontSize": FS["S"]})
sc("Table/CellNumeric", "Right-aligned numeric cell", {"padding": f"{vh(3)} {PAD_S}", "fontSize": FS["S"], "textAlign": "right", "fontVariantNumeric": "tabular-nums"})
sc("Table/Selected","Selected row", {"backgroundColor": "#C9D6EA", "color": P["text"]})

# ---------------- Utility
sc("Util/Pad/S", "Padding 4px",  {"padding": PAD_S})
sc("Util/Pad/M", "Padding 8px",  {"padding": PAD_M})
sc("Util/Pad/L", "Padding 12px", {"padding": PAD_L})
sc("Util/Pad/None", "No padding", {"padding": "0px"})
sc("Util/Border",  "1px border", {"border": f"{LINE} solid {P['borderDark']}"})
sc("Util/BorderDashed", "1px dashed border", {"border": f"{LINE} dashed {P['borderDark']}"})
sc("Util/Rounded", "Rounded corners", {"borderRadius": RAD})
sc("Util/Shadow",  "Soft shadow (popups only per ISA-101)", {"boxShadow": "0 0.2vh 0.6vh rgba(0,0,0,0.3)"})
sc("Util/Pointer", "Hand cursor (clickable)", {"cursor": "pointer"})
sc("Util/Disabled","Faded + not clickable", {"opacity": "0.45", "pointerEvents": "none", "cursor": "not-allowed"})
sc("Util/Transparent", "No background", {"backgroundColor": "transparent"})
sc("Util/Highlight", "Highlight / search hit (non-alarm blue-gray)", {"backgroundColor": "#DCE3EC"})
sc("Util/Collapsed", "Removed from layout (takes no space, keeps neighbours centered)",
   {"display": "none", "width": "0px", "minWidth": "0px", "maxWidth": "0px", "flexBasis": "0px", "padding": "0px", "margin": "0px",
    "borderWidth": "0px", "overflow": "hidden", "fontSize": "0px", "visibility": "hidden"})   # zero width even if a component rule keeps display
sc("Util/Clip",    "Hide overflow", {"overflow": "hidden"})


# ---------------- P&ID template badges + manual-mode split chip (v3 notes 9, 17)
BADGE = {"fontSize": FS["S"], "fontWeight": "800", "fontFamily": FONT, "border": f"{LINE} solid {P['text']}",
         "borderRadius": vh(2), "textAlign": "center", "justifyContent": "center", "alignItems": "center", "lineHeight": "1"}
sc("Indicator/PermissiveBadge", "P badge: permissive missing (NFPA 79 amber, black text)", {**BADGE, "backgroundColor": "#F08000", "color": "#000000"})
sc("Indicator/InterlockBadge",  "I badge: interlock active (red, white text)",            {**BADGE, "backgroundColor": "#C00000", "color": "#FFFFFF"})
MANUAL_M = "#FFD200"   # chosen option C2 (yellow M). Alternatives: C1 white #FFFFFF, C3 orange #FF7A00, blue-gray #B8C7D9
sc("Mode/ManualSplit",       "Manual mode 'M' segment left of the status chip (useButton = false). Same height, font and border as the State/* chip",
   {"backgroundColor": P["fault"], "color": MANUAL_M, "fontSize": FS["XS"], "fontWeight": "700", "letterSpacing": "0.04em", "fontFamily": FONT,
    "border": f"{LINE} solid {P['text']}", "borderRight": "none", "borderRadius": f"{vh(2)} 0 0 {vh(2)}",
    "padding": f"{vh(1)} {vh(5)}", "textAlign": "center", "justifyContent": "center", "alignItems": "center"})
sc("Mode/ManualJoined",      "Add to a State/* chip when Mode/ManualSplit sits on its left (squares the joined corners)",
   {"borderRadius": f"0 {vh(2)} {vh(2)} 0"})
sc("Mode/ManualSplitStatus", "Status segment paired with Mode/ManualSplit (plain-text statuses)",
   {"backgroundColor": P["field"], "border": f"{LINE} solid {P['text']}", "borderRadius": f"0 {vh(2)} {vh(2)} 0",
    "padding": f"0 {vh(5)}", "justifyContent": "center", "alignItems": "center"})

# ---------------- template manual-command button: square, status-chip height, subtle raised key (approved 2026-10-06)
sc("Button/Command", "Manual command button on P&ID templates: blank square, raised, sinks when pressed",
   {"backgroundImage": "linear-gradient(#F4F4F4, #E4E4E4)", "backgroundColor": "#ECECEC", "border": f"{LINE} solid #7A7A7A",
    "borderRadius": RAD, "boxShadow": "inset 0 -0.093vh 0 #C8C8C8, 0 0.093vh 0.093vh rgba(0,0,0,0.22)", "cursor": "pointer",
    "padding": "0px", "minWidth": "0px", "minHeight": "0px"},
   hover={"backgroundImage": "linear-gradient(#FAFAFA, #EAEAEA)", "borderColor": "#595959"},
   active={"backgroundImage": "none", "backgroundColor": "#D6D6D6", "boxShadow": "inset 0 0.093vh 0.185vh rgba(0,0,0,0.35)"},
   disabled={"backgroundImage": "none", "backgroundColor": "#E3E3E3", "opacity": "0.45", "boxShadow": "none", "cursor": "not-allowed"})

# ---------------------------------------------------------- stylesheet.css
STYLESHEET = """/* EFC Perspective stylesheet - generated by build_styles.py
   Holds the keyframes used by Alarm/<Priority>/Unacked (flashing = unacknowledged alarm only, ISA-18.2). */
@keyframes efc-blink {
  0%   { opacity: 1; }
  50%  { opacity: 0.25; }
}
@media (prefers-reduced-motion: reduce) {
  [class*="psc-Alarm/"], [class*="psc-Alarm\\/"] { animation-duration: 2s !important; }
}
"""

# ---------------------------------------------------------- catalog view
_name_counts = {}
def uname(base):
    base = re.sub(r"[^A-Za-z0-9_]", "_", base)
    n = _name_counts.get(base, 0); _name_counts[base] = n + 1
    return base if n == 0 else f"{base}_{n}"

def label(txt, classes, extra_style=None, basis="auto"):
    st = {"classes": classes}; st.update(extra_style or {})
    return {"type": "ia.display.label", "version": 0, "meta": {"name": uname("Lbl_" + txt)},
            "position": {"basis": basis, "shrink": 0}, "props": {"text": txt, "style": st}}

def button(txt, classes):
    return {"type": "ia.input.button", "version": 0, "meta": {"name": uname("Btn_" + txt)},
            "position": {"basis": "auto", "shrink": 0}, "props": {"text": txt, "style": {"classes": classes}}}

def field(txt, classes):
    return {"type": "ia.input.text-field", "version": 0, "meta": {"name": uname("Fld_" + txt)},
            "position": {"basis": vh(150) if False else "150px", "shrink": 0}, "props": {"text": txt, "style": {"classes": classes}}}

def flex(name, children, direction="row", classes="", wrap=True, gap=vh(8)):
    style = {"gap": gap}
    if classes: style["classes"] = classes
    p = {"direction": direction, "style": style}
    if wrap: p["wrap"] = "wrap"
    if direction == "row": p["alignItems"] = "center"
    return {"type": "ia.container.flex", "version": 0, "meta": {"name": uname(name)},
            "position": {"basis": "auto", "shrink": 0}, "props": p, "children": children}

SECTIONS = [
    ("Text", "Text/"), ("Containers", "Container/"), ("Buttons", "Button/"), ("Inputs", "Input/"),
    ("Values", "Value/"), ("States & Modes", ("State/", "Mode/")), ("Indicators & Bars", ("Indicator/", "Bar/")),
    ("Alarms", "Alarm/"), ("Table", "Table/"), ("Utility", "Util/"),
]
SAMPLE = {"Value/": "123.4", "Indicator/LED": "", "Bar/": ""}

def sample_for(path):
    short = path.split("/", 1)[1]
    if path.startswith("Button/"):
        return button(short, path)
    if path.startswith("Input/") and path != "Input/Check":
        return field("42.0" if "Setpoint" in path or path == "Input/Field" else short, path)
    if path.startswith("Indicator/LED"):
        return flex("LED_" + short, [label("", path, {"width": vh(14), "height": vh(14)}), label(short, "Text/Caption")], gap=vh(4))
    if path.startswith("Bar/"):
        return label(short, path + " Text/Caption", {"minWidth": "120px", "minHeight": vh(14), "padding": "0 4px"})
    if path.startswith("Container/"):
        return label(short, path + " Text/Body", {"minWidth": "140px", "minHeight": "48px", "padding": "6px"})
    if path.startswith("Util/"):
        return label(short, path + " Text/Body Container/Card")
    return label(short, path)

def build_view():
    kids = [label("EFC Style Library", "Text/Title Container/Header", {"padding": "10px 16px"}),
            label("Every style class in the library. Select a component to see its class in props.style.classes.",
                  "Text/Caption Util/Pad/M")]
    for title, prefix in SECTIONS:
        prefixes = prefix if isinstance(prefix, tuple) else (prefix,)
        paths = [p for p in CLASSES if p.startswith(prefixes)]
        groups = {}
        for p in paths:
            g = "/".join(p.split("/")[:2]) if p.count("/") >= 2 else p.split("/")[0]
            groups.setdefault(g, []).append(p)
        rows = [label(title, "Text/Header")]
        for g, ps in groups.items():
            rows.append(flex("Row_" + g, [label(g, "Text/Label", {"width": "160px"}, basis="160px")] + [sample_for(p) for p in ps]))
        kids.append(flex("Sec_" + title, rows, direction="column", classes="Container/Panel", wrap=False))
    root = {"type": "ia.container.flex", "version": 0, "meta": {"name": "root"},
            "props": {"direction": "column", "style": {"classes": "Container/Screen", "gap": "12px", "padding": "12px", "overflowY": "auto"}},
            "children": kids}
    return {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 1920, "height": 1080}}, "root": root}

# ---------------------------------------------------------- writers
def resource_json(files):
    ts = os.environ.get("EFC_BUILD_TIMESTAMP", "2026-10-07T00:00:00Z")   # fixed (from VERSION via build.py) so rebuilds diff cleanly in git
    return json.dumps({"scope": "G", "version": 1, "restricted": False, "overridable": True,
                       "files": files, "attributes": {"lastModification": {"actor": "efc-ignition-library", "timestamp": ts}}}, indent=2)

def build_zip():
    os.makedirs(OUT, exist_ok=True)
    zpath = os.path.join(OUT, f"{PROJECT}.zip")
    base = "com.inductiveautomation.perspective"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps({"title": PROJECT, "description": "EFC ISA-101 style class library (generated)",
                                               "parent": "", "enabled": True, "inheritable": True}, indent=2))
        for path, (body, _) in CLASSES.items():
            d = f"{base}/style-classes/{path}"
            z.writestr(f"{d}/style.json", json.dumps(body, indent=2))
            z.writestr(f"{d}/resource.json", resource_json(["style.json"]))
        z.writestr(f"{base}/stylesheet/stylesheet.css", STYLESHEET)
        z.writestr(f"{base}/stylesheet/resource.json", resource_json(["stylesheet.css"]))
        z.writestr(f"{base}/views/Styles/_Catalog/view.json", json.dumps(build_view(), indent=2))
        z.writestr(f"{base}/views/Styles/_Catalog/resource.json", resource_json(["view.json"]))
    return zpath

def css_of(style, px=True):
    out = []
    for k, v in style.items():
        if px and isinstance(v, str):
            v = re.sub(r"(-?[\d.]+)vh", lambda m: f"{round(float(m.group(1)) * 10.8, 2)}px", v)
        out.append(re.sub(r"[A-Z]", lambda m: "-" + m.group(0).lower(), k) + ":" + str(v))
    return ";".join(out)

def build_preview():
    css = [STYLESHEET, "body{margin:0;background:#D9D9D9;font-family:" + FONT + "}",
           ".sec{background:#E6E6E6;border:1px solid #A6A6A6;margin:12px;padding:10px;border-radius:3px}",
           ".row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:6px 0}",
           ".g{width:160px;font-size:12px;color:#4D4D4D}", ".s{display:flex;align-items:center}"]
    for path, (body, _) in CLASSES.items():
        cls = "psc-" + path.replace("/", "_")
        css.append(f".{cls}{{{css_of(body['base']['style'])}}}")
        for v in body["variants"]:
            css.append(f".{cls}:{v['pseudo']}{{{css_of(v['style'])}}}")
    rows = []
    for title, prefix in SECTIONS:
        prefixes = prefix if isinstance(prefix, tuple) else (prefix,)
        groups = {}
        for p in CLASSES:
            if p.startswith(prefixes):
                g = "/".join(p.split("/")[:2]) if p.count("/") >= 2 else p.split("/")[0]
                groups.setdefault(g, []).append(p)
        rows.append(f"<div class='sec'><div class='psc-Text_Header'>{title}</div>")
        for g, ps in groups.items():
            items = []
            for p in ps:
                c = "psc-" + p.replace("/", "_"); short = html.escape(p.split("/", 1)[1])
                if p.startswith("Button/"):
                    items.append(f"<button class='{c}' title='{p}'>{short}</button>")
                elif p.startswith("Input/") and p != "Input/Check":
                    items.append(f"<input class='{c}' value='{short}' title='{p}' style='width:140px'>")
                elif p.startswith("Indicator/LED"):
                    items.append(f"<span class='s' title='{p}'><span class='{c}' style='display:inline-block;width:15px;height:15px'></span>&nbsp;<span class='psc-Text_Caption'>{short}</span></span>")
                elif p.startswith(("Bar/", "Container/", "Util/")):
                    extra = "psc-Text_Body" + (" psc-Container_Card" if p.startswith("Util/") else "")
                    items.append(f"<div class='s {c} {extra}' title='{p}' style='min-width:120px;min-height:{'15px' if p.startswith('Bar/') else '40px'};padding:4px'>{short}</div>")
                else:
                    items.append(f"<span class='s {c}' title='{p}'>{short}</span>")
            rows.append(f"<div class='row'><div class='g'>{g}</div>{''.join(items)}</div>")
        rows.append("</div>")
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><title>EFC Style Library</title><style>{''.join(css)}</style></head>"
           f"<body><div class='psc-Container_Header psc-Text_Title' style='padding:10px 16px'>EFC Style Library — preview at 1920×1080</div>{''.join(rows)}</body></html>")
    p = os.path.join(OUT, "style_preview.html")
    open(p, "w").write(doc)
    return p

def build_index():
    lines = ["| Class path | Use |", "|---|---|"]
    lines += [f"| `{p}` | {d} |" for p, (_, d) in CLASSES.items()]
    p = os.path.join(OUT, "style_index.md")
    open(p, "w").write("\n".join(lines) + "\n")
    return p

if __name__ == "__main__":
    print(build_zip()); print(build_preview()); print(build_index())
    print(f"{len(CLASSES)} style classes")
