"""
EFC Process Value templates for Ignition Perspective 8.1
  Templates/ProcessValues/PV_StatusStrip   (A1, 160x52 @1080p)
  Templates/ProcessValues/PV_RangeBar      (B2, 160x84 @1080p)
  Templates/ProcessValues/_Demo

Outputs in ./dist:
  EFC_ProcessValues.zip     Perspective project (parent EFC_Styles): 3 views + the new style classes
  PV_Demo_Tags.json         Demo UDT DDT_Process_Value_Demo + 5 instances (import at the [default] provider root)
Only template parameter: tagPath (path to a DDT_Process_Value instance, e.g. [default]Area1/PT002).
"""
import json, os, re, zipfile, datetime
from urllib.parse import quote

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
PROJECT = "EFC_ProcessValues"
PARENT = "EFC_Styles"
BASE = "com.inductiveautomation.perspective"
FOLDER = "Templates/ProcessValues"

def vh(px): return f"{round(px / 10.8, 3)}vh"
FONT = "'Noto Sans', 'Segoe UI', Arial, sans-serif"

# ----------------------------------------------------------------- palette (EFC_Styles)
P = dict(card="#F0F0F0", border="#A6A6A6", borderDark="#7F7F7F", text="#1F1F1F", muted="#4D4D4D", faint="#5A5A5A",
         readonly="#EDEDED", field="#FFFFFF", fault="#3A3A3A", bandAlarm="#C9C9C9", bandExtreme="#A6A6A6")
PRI = {"Critical": ("#D50000", "#FFFFFF"), "High": ("#FF7A00", "#1F1F1F"), "Medium": ("#FFD200", "#1F1F1F"),
       "Low": ("#00A3E0", "#1F1F1F"), "Diagnostic": ("#7A7A7A", "#FFFFFF")}
PRI_BY_NUM = {4: "Critical", 3: "High", 2: "Medium", 1: "Low", 0: "Diagnostic"}

# ----------------------------------------------------------------- new style classes
CLASSES = {}
def sc(path, desc, style): CLASSES[path] = ({"base": {"style": style}, "variants": []}, desc)

sc("PV/Card", "PV template card: white, 6 px corners, 1 px #B3B3B3 border with darker bottom edge, soft shadow (v1.2)",
   {"backgroundColor": "#FFFFFF", "border": f"{vh(1)} solid #B3B3B3", "borderBottomColor": "#8C8C8C",
    "borderRadius": vh(6), "boxShadow": f"0 {vh(1)} {vh(3)} rgba(0,0,0,0.22)",
    "overflow": "hidden", "fontFamily": FONT, "boxSizing": "border-box"})
sc("PV/Shell", "Transparent outer margin so the card shadow is not clipped by the embedding container",
   {"padding": f"{vh(1)} {vh(2)} {vh(3)} {vh(2)}", "backgroundColor": "transparent", "overflow": "visible", "boxSizing": "border-box"})
sc("PV/Body", "PV template inner padding (A1)", {"padding": f"{vh(5)} {vh(5)} {vh(6)} {vh(5)}", "minWidth": "0px"})
sc("PV/BodyBar", "PV range-bar template inner padding (B2)", {"padding": f"{vh(4)} {vh(5)} {vh(5)} {vh(5)}"})
sc("PV/HeaderRow", "Tag + letter row (fixed 12 px high, 3 px gap)", {"gap": vh(3), "height": vh(12), "minHeight": vh(12), "minWidth": "0px"})
sc("PV/Tag", "Tag name in the 100 x 50 card: 11 px bold", {"fontSize": vh(11), "fontWeight": "700", "color": P["text"], "fontFamily": FONT,
                                                          "letterSpacing": "0.01em", "lineHeight": vh(12), "minWidth": "0px",
                                                          "overflow": "hidden", "whiteSpace": "nowrap", "textOverflow": "ellipsis"})
sc("PV/Value", "Live value, A1 (18 px semibold, tabular)", {"fontSize": vh(18), "fontWeight": "600", "color": P["text"], "fontFamily": FONT,
                                                           "fontVariantNumeric": "tabular-nums", "lineHeight": "1"})
sc("PV/ValueSmall", "Live value, B2 (16 px semibold, tabular)", {"fontSize": vh(16), "fontWeight": "600", "color": P["text"], "fontFamily": FONT,
                                                                "fontVariantNumeric": "tabular-nums", "lineHeight": "1"})
sc("PV/Units", "Engineering units, 10 px muted", {"fontSize": vh(10), "color": P["muted"], "fontFamily": FONT, "marginLeft": vh(3)})
sc("PV/ChipRow", "Letter-indicator row (2 px gap)", {"gap": vh(2)})
sc("PV/Strip/Normal", "A1 edge strip, no alarm", {"backgroundColor": P["border"]})
sc("PV/Strip/Fault", "A1 edge strip, HW fault", {"backgroundColor": P["fault"]})
CHIP = {"fontSize": vh(9), "fontWeight": "700", "fontFamily": FONT, "lineHeight": vh(12), "height": vh(12),
        "minWidth": vh(12), "padding": f"0 {vh(2)}", "borderRadius": vh(2), "letterSpacing": "0.01em",
        "textAlign": "center", "justifyContent": "center", "alignItems": "center", "boxSizing": "border-box",
        "whiteSpace": "nowrap"}
for name, (bg, fg) in PRI.items():
    sc(f"PV/Strip/{name}", f"A1 edge strip, {name} alarm", {"backgroundColor": bg})
    sc(f"PV/Chip/{name}", f"Letter indicator, {name} priority", {**CHIP, "backgroundColor": bg, "color": fg})
    sc(f"Bar/Band/{name}", f"Range-bar band overlay, {name} priority", {"backgroundColor": bg, "borderLeft": f"{vh(1)} solid {P['borderDark']}"})
sc("PV/Chip/Fault", "Letter indicator FLT (HW fault): dark gray, white text",
   {**CHIP, "backgroundColor": P["fault"], "color": "#FFFFFF", "border": f"{vh(1)} solid #000000"})
sc("PV/Chip/Inhibit", "Letter indicator INH (a limit is inhibited)",
   {**CHIP, "backgroundColor": P["readonly"], "color": P["faint"], "border": f"{vh(1)} dashed {P['borderDark']}",
    "fontStyle": "italic", "fontWeight": "600"})
sc("PV/Chip/More", "+N overflow letter (more than 2 letters active); tooltip lists the hidden ones",
   {**CHIP, "backgroundColor": "#595959", "color": "#FFFFFF"})
sc("Alarm/Mod/Blink", "Modifier: blink while unacknowledged (uses efc-blink keyframes in the EFC_Styles stylesheet)",
   {"animation": "efc-blink 1s steps(1, end) infinite"})
sc("Alarm/Mod/ClearedUnacked", "Modifier: cleared but unacknowledged = steady blink-OFF look (opacity 0.25)",
   {"opacity": "0.25"})
sc("Bar/Band/Normal", "Range-bar normal band (L to H)", {"backgroundColor": P["field"], "borderLeft": f"{vh(1)} solid {P['borderDark']}"})
sc("Bar/Band/Alarm", "Range-bar alarm band (LL-L, H-HH)", {"backgroundColor": P["bandAlarm"], "borderLeft": f"{vh(1)} solid {P['borderDark']}"})
sc("Bar/Band/Extreme", "Range-bar extreme band (below LL, above HH)", {"backgroundColor": P["bandExtreme"]})
sc("Bar/Frame", "Range-bar outline (drawn over the bands)", {"border": f"{vh(1)} solid {P['borderDark']}", "borderRadius": vh(2),
                                                              "backgroundColor": "transparent", "boxSizing": "border-box", "pointerEvents": "none"})

# ----------------------------------------------------------------- expression helpers
TP = "{view.params.tagPath}"
ALARMS = [  # key, path suffix of the alarm-bearing tag
    ("FLT", "/HW_Fault"), ("HH", "/HH/Alarm"), ("H", "/H/Alarm"), ("L", "/L/Alarm"),
    ("LL", "/LL/Alarm"), ("OVR", "/Overrange"), ("UNR", "/Underrange")]
C = lambda k: "{view.custom.a" + k + "}"

def iaf(path, pmin, pmax, cleared, acked):
    return f'isAlarmActiveFiltered({path}, "*", "*", {pmin}, {pmax}, {cleared}, {acked}, 0)'

def alarm_code(suffix):
    """-1 = none; else state*10 + priority.  state 0 = active acked, 1 = active unacked, 2 = cleared unacked.
    Re-evaluated every tick (isAlarmActiveFiltered does not push updates in Perspective)."""
    p = f'{TP} + "{suffix}"'
    state = f"if({iaf(p, 0, 4, 0, 0)}, 10, if({iaf(p, 0, 4, 0, 1)}, 0, 20))"
    pri = (f"case(true, {iaf(p, 4, 4, 1, 1)}, 4, {iaf(p, 3, 3, 1, 1)}, 3, "
           f"{iaf(p, 2, 2, 1, 1)}, 2, {iaf(p, 1, 1, 1, 1)}, 1, 0)")
    return (f"if(isNull({{view.custom.tick}}) || len({TP}) = 0, -1,\n"
            f"  if(!{iaf(p, 0, 4, 1, 1)}, -1,\n"
            f"    {state} + {pri}))")

PRI_NAME = lambda x: f'case({x}, 4, "Critical", 3, "High", 2, "Medium", 1, "Low", "Diagnostic")'

def mod(code):
    return f'if({code} >= 20, " Alarm/Mod/ClearedUnacked", if({code} >= 10, " Alarm/Mod/Blink", ""))'

def chip_classes(k):
    c = C(k)
    if k == "FLT":
        return f'if({c} < 0, "PV/Chip/Fault", "PV/Chip/Fault" + {mod(c)})'
    return f'if({c} < 0, "", "PV/Chip/" + {PRI_NAME(c + " % 10")} + {mod(c)})'

def b_tag(rel, fallback=None):
    return {"binding": {"type": "tag", "config": {"mode": "indirect", "tagPath": "{0}" + rel,
                                                  "references": {"0": TP}, "fallbackDelay": 2.5}}}

def b_expr(e, persistent=None):
    return {"binding": {"type": "expr", "config": {"expression": e}}}

ALM_SCRIPT = '\t# One alarm-status query per refresh for this UDT instance. Returns {key: code}:\n\t# -1 = none, else state*10 + priority (state 0 active-acked, 1 active-unacked, 2 cleared-unacked;\n\t# priority 0 Diagnostic .. 4 Critical). Replaces isAlarmActiveFiltered (gateway scope needs the\n\t# provider in the path and Perspective never re-runs it on alarm changes).\n\tout = {"FLT": -1, "HH": -1, "H": -1, "L": -1, "LL": -1, "OVR": -1, "UNR": -1}\n\ttp = self.view.params.tagPath\n\tif not tp:\n\t\treturn out\n\ttp = str(tp).strip()\n\tprov = "*"\n\tpath = tp\n\tif tp.startswith("[") and "]" in tp:\n\t\tprov = tp[1:tp.index("]")] or "*"\n\t\tpath = tp[tp.index("]") + 1:]\n\tpath = path.strip("/")\n\tkeys = {"hw_fault": "FLT", "hh/alarm": "HH", "h/alarm": "H", "l/alarm": "L",\n\t\t\t"ll/alarm": "LL", "overrange": "OVR", "underrange": "UNR"}\n\ttry:\n\t\tevents = system.alarm.queryStatus(source=["prov:%s:/tag:%s/*" % (prov, path)])\n\texcept Exception as e:\n\t\tsystem.util.getLogger("EFC_PV").warn("queryStatus failed for %s: %s" % (tp, e))\n\t\treturn out\n\tagg = {}\n\tfor ev in events:\n\t\tst = str(ev.getState())\n\t\tif st not in ("ActiveUnacked", "ActiveAcked", "ClearUnacked"):\n\t\t\tcontinue\n\t\tsrc = str(ev.getSource())\n\t\tif ":/tag:" not in src:\n\t\t\tcontinue\n\t\ttag = src.split(":/tag:", 1)[1].split(":/alm:", 1)[0].strip("/")\n\t\tif not tag.lower().startswith(path.lower() + "/"):\n\t\t\tcontinue\n\t\tkey = keys.get(tag[len(path) + 1:].lower())\n\t\tif key is None:\n\t\t\tcontinue\n\t\tpri = int(ev.getPriority().ordinal())\n\t\ta = agg.setdefault(key, {"act": -1, "unack": False, "clr": -1})\n\t\tif st == "ClearUnacked":\n\t\t\ta["clr"] = max(a["clr"], pri)\n\t\telse:\n\t\t\ta["act"] = max(a["act"], pri)\n\t\t\tif st == "ActiveUnacked":\n\t\t\t\ta["unack"] = True\n\tfor key, a in agg.items():\n\t\tif a["act"] >= 0:\n\t\t\tout[key] = (10 if a["unack"] else 0) + a["act"]\n\t\telif a["clr"] >= 0:\n\t\t\tout[key] = 20 + a["clr"]\n\treturn out'

def common_custom():
    pc = {
        "params.tagPath": {"paramDirection": "input", "persistent": True},
        "custom.tick": b_expr("now(1000)"),
        "custom.pv": b_tag("/PV"),
        "custom.name": b_tag("/Name"),
        "custom.desc": b_tag("/Description"),
        "custom.units": b_tag("/Units"),
        "custom.hwFault": b_tag("/HW_Fault"),
        "custom.inhHH": b_tag("/HH/Inhibit"), "custom.inhH": b_tag("/H/Inhibit"),
        "custom.inhL": b_tag("/L/Inhibit"), "custom.inhLL": b_tag("/LL/Inhibit"),
    }
    pc["custom.alm"] = {"binding": {"type": "expr", "config": {"expression": "{view.custom.tick}"},
                                    "transforms": [{"type": "script", "code": ALM_SCRIPT}]}}
    for k, suffix in ALARMS:
        if k == "FLT":   # alarm on HW_Fault; if none is configured yet, still show a steady FLT from the bit
            pc["custom.aFLTalm"] = b_expr("coalesce({view.custom.alm.FLT}, -1)")
            pc["custom.aFLT"] = b_expr("if({view.custom.aFLTalm} >= 0, {view.custom.aFLTalm},\n"
                                       "  if(toBoolean(coalesce({view.custom.hwFault}, false)), 3, -1))")
        else:
            pc[f"custom.a{k}"] = b_expr("coalesce({view.custom.alm.%s}, -1)" % k)
    codes = ", ".join(C(k) for k, _ in ALARMS if k != "FLT")
    act = ", ".join(f"if({C(k)} >= 0 && {C(k)} < 20, {C(k)} % 10, -1)" for k, _ in ALARMS if k != "FLT")
    clr = ", ".join(f"if({C(k)} >= 20, {C(k)} % 10, -1)" for k, _ in ALARMS if k != "FLT")
    pc["custom.fltActive"] = b_expr(f"{C('FLT')} >= 0 && {C('FLT')} < 20")
    pc["custom.anyUnacked"] = b_expr(" || ".join(f"({C(k)} >= 10 && {C(k)} < 20)" for k, _ in ALARMS))
    pc["custom.activePri"] = b_expr(f"max(-1, {act})")
    pc["custom.clearedPri"] = b_expr(f"max(-1, {clr})")
    pc["custom.inh"] = b_expr("toBoolean(coalesce({view.custom.inhHH}, false)) || toBoolean(coalesce({view.custom.inhH}, false)) || "
                              "toBoolean(coalesce({view.custom.inhL}, false)) || toBoolean(coalesce({view.custom.inhLL}, false))")
    pc["custom.badValue"] = b_expr("!isGood({view.custom.pv}) || {view.custom.fltActive}")
    return pc

def common_defaults():
    return {"tick": None, "pv": None, "name": "", "desc": "", "units": "", "hwFault": False,
            "inhHH": False, "inhH": False, "inhL": False, "inhLL": False,
            **{f"a{k}": -1 for k, _ in ALARMS}, "aFLTalm": -1,
            "alm": {"FLT": -1, "HH": -1, "H": -1, "L": -1, "LL": -1, "OVR": -1, "UNR": -1}, "fltActive": False, "anyUnacked": False, "activePri": -1, "clearedPri": -1, "inh": False, "badValue": False}

# ----------------------------------------------------------------- component builders
def comp(ctype, name, props=None, position=None, children=None, prop_config=None, meta_extra=None):
    c = {"type": ctype, "version": 0, "meta": {"name": name}, "position": position or {}, "props": props or {}}
    if meta_extra: c["meta"].update(meta_extra)
    if prop_config: c["propConfig"] = prop_config
    if children is not None: c["children"] = children
    return c

def label(name, classes="", text="", position=None, pc=None, meta_extra=None):
    return comp("ia.display.label", name, {"text": text, "style": {"classes": classes}}, position, prop_config=pc, meta_extra=meta_extra)

def flex(name, direction, children, classes="", position=None, justify="flex-start", align="stretch", pc=None):
    return comp("ia.container.flex", name, {"direction": direction, "justify": justify, "alignItems": align,
                                            "wrap": "nowrap", "style": {"classes": classes}}, position, children, pc)

FIX = lambda basis: {"basis": basis, "grow": 0, "shrink": 0}

def tag_label():
    name_expr = ('if(isNull({view.custom.name}) || len(toStr({view.custom.name})) = 0 || toStr({view.custom.name}) = "null",\n'
                 '  substring({view.params.tagPath}, max(lastIndexOf({view.params.tagPath}, "/"), lastIndexOf({view.params.tagPath}, "]")) + 1),\n'
                 '  toStr({view.custom.name}))')
    tip = ('if(isNull({view.custom.desc}) || toStr({view.custom.desc}) = "null", "", toStr({view.custom.desc}))')
    return label("Tag", "PV/Tag Text/Mod/Ellipsis", "PT002", {"basis": "auto", "grow": 1, "shrink": 1},
                 pc={"props.text": b_expr(name_expr), "meta.tooltip.text": b_expr(tip)},
                 meta_extra={"tooltip": {"enabled": True, "text": ""}})

LETTERS = ["FLT", "HH", "H", "L", "LL", "OVR", "UNR", "INH"]
MAX_LETTERS = 2

def present(k):
    return "{view.custom.inh}" if k == "INH" else f"{C(k)} >= 0"

def n_before(k):
    prev = LETTERS[:LETTERS.index(k)]
    return "(" + " + ".join(f"if({present(p)}, 1, 0)" for p in prev) + ")" if prev else "0"

def chip_row():
    kids = []
    tips = {"FLT": "Hardware / transmitter fault", "HH": "High-high alarm", "H": "High alarm", "L": "Low alarm",
            "LL": "Low-low alarm", "OVR": "Signal over range", "UNR": "Signal under range", "INH": "A limit alarm is inhibited"}
    for k in LETTERS:
        disp = b_expr(f"({present(k)}) && {n_before(k)} < {MAX_LETTERS}")
        if k == "INH":
            kids.append(label("Chip_INH", "PV/Chip/Inhibit", "INH", {**FIX("auto"), "display": False}, {"position.display": disp},
                              meta_extra={"tooltip": {"enabled": True, "text": tips[k]}}))
            continue
        pc = {"position.display": disp, "props.style.classes": b_expr(chip_classes(k))}
        kids.append(label(f"Chip_{k}", "", k, {**FIX("auto"), "display": False}, pc,
                          meta_extra={"tooltip": {"enabled": True, "text": tips[k]}}))
    # +N overflow letter
    hid = lambda k: f"(({present(k)}) && {n_before(k)} >= {MAX_LETTERS})"
    total = " + ".join(f"if({present(k)}, 1, 0)" for k in LETTERS)
    more_pc = {
        "position.display": b_expr(f"({total}) > {MAX_LETTERS}"),
        "props.text": b_expr(f'"+" + toStr(({total}) - {MAX_LETTERS})'),
        "props.style.classes": b_expr('"PV/Chip/More" + if(' + " || ".join(
            f"({hid(k)} && {C(k)} >= 10 && {C(k)} < 20)" for k in LETTERS if k != "INH") + ', " Alarm/Mod/Blink", "")'),
        "meta.tooltip.text": b_expr('"Also: " + ' + " + ".join(f'if({hid(k)}, "{k} ", "")' for k in LETTERS)),
    }
    kids.append(label("Chip_More", "PV/Chip/More", "+1", {**FIX("auto"), "display": False}, more_pc,
                      meta_extra={"tooltip": {"enabled": True, "text": ""}}))
    return flex("Chips", "row", kids, "PV/ChipRow", FIX("auto"), justify="flex-end", align="center")

def value_row(vcls_base="PV/Value"):
    vtext = 'if(isNull({view.custom.pv}), "---", numberFormat({view.custom.pv}, "#,##0.0"))'
    vcls = '"' + vcls_base + ' Text/Mod/NoWrap" + if({view.custom.badValue}, " Value/BadQuality", "")'
    units = 'if(isNull({view.custom.units}) || toStr({view.custom.units}) = "null", "", toStr({view.custom.units}))'
    return flex("ValueRow", "row", [
        label("Value", vcls_base, "28.2", {"basis": "auto", "grow": 1, "shrink": 1},
              {"props.text": b_expr(vtext), "props.style.classes": b_expr(vcls)}),
        label("Units", "PV/Units Text/Mod/NoWrap", "PSIG", FIX("auto"), {"props.text": b_expr(units)}),
    ], "", FIX("auto"), justify="space-between", align="baseline")

def header_row():
    return flex("HeaderRow", "row", [tag_label(), chip_row()], "PV/HeaderRow", FIX("auto"),
                justify="space-between", align="center")

def strip_classes():
    return ('if({view.custom.fltActive}, "PV/Strip/Fault" + if({view.custom.anyUnacked}, " Alarm/Mod/Blink", ""),\n'
            f' if({{view.custom.activePri}} >= 0, "PV/Strip/" + {PRI_NAME("{view.custom.activePri}")} + if({{view.custom.anyUnacked}}, " Alarm/Mod/Blink", ""),\n'
            f'  if({C("FLT")} >= 20, "PV/Strip/Fault Alarm/Mod/ClearedUnacked",\n'
            f'   if({{view.custom.clearedPri}} >= 0, "PV/Strip/" + {PRI_NAME("{view.custom.clearedPri}")} + " Alarm/Mod/ClearedUnacked",\n'
            '    "PV/Strip/Normal"))))')

def view(root, custom_defaults, prop_config, w, h):
    return {"custom": custom_defaults, "params": {"tagPath": ""}, "propConfig": prop_config,
            "props": {"defaultSize": {"width": w, "height": h}}, "root": root}

# ----------------------------------------------------------------- A1: PV_StatusStrip
def build_a1():
    strip = label("Strip", "PV/Strip/Normal", "", {"basis": vh(4), "grow": 0, "shrink": 0},
                  {"props.style.classes": b_expr(strip_classes())})
    body = flex("Body", "column", [header_row(), value_row()], "PV/Body", {"basis": "auto", "grow": 1, "shrink": 1},
                justify="space-between")
    card = flex("Card", "row", [strip, body], "PV/Card", {"basis": "auto", "grow": 1, "shrink": 1}, justify="flex-start", align="stretch")
    root = flex("root", "column", [card], "PV/Shell", justify="flex-start", align="stretch")
    return view(root, common_defaults(), common_custom(), 104, 54)

# ----------------------------------------------------------------- B2: PV_RangeBar
def svg_uri(svg): return "data:image/svg+xml;utf8," + quote(svg, safe="=:/;,'()<> ")
POINTER = svg_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 12' preserveAspectRatio='none'>"
                  "<polygon points='0,0 8,0 4,5' fill='#1F1F1F'/><rect x='2' y='5' width='4' height='7' fill='#FFFFFF'/>"
                  "<rect x='3' y='5' width='2' height='7' fill='#1F1F1F'/></svg>")
POINTER_BAD = svg_uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 12' preserveAspectRatio='none'>"
                      "<polygon points='0,0 8,0 4,5' fill='#B000B0'/></svg>")
TRACK_W = 88.0    # px @1080p (100 - 2 x 5 padding - 2 x 1 border)
TRACK_H = 12.0
PTR_W = 8.0 / TRACK_W
BAND_Y, BAND_H = 5 / TRACK_H, 6 / TRACK_H

def frac(x):
    return (f"if({{view.custom.engMax}} = {{view.custom.engMin}} || isNull({x}), 0, "
            f"max(0, min(1, ({x} - {{view.custom.engMin}}) / ({{view.custom.engMax}} - {{view.custom.engMin}}))))")

def build_b2():
    pc = common_custom()
    pc.update({
        "custom.engMin": b_tag("/Eng_Min"), "custom.engMax": b_tag("/Eng_Max"),
        "custom.spLL": b_tag("/LL/SP"), "custom.spL": b_tag("/L/SP"),
        "custom.spH": b_tag("/H/SP"), "custom.spHH": b_tag("/HH/SP"),
        "custom.fLL": b_expr(frac("{view.custom.spLL}")), "custom.fL": b_expr(frac("{view.custom.spL}")),
        "custom.fH": b_expr(frac("{view.custom.spH}")), "custom.fHH": b_expr(frac("{view.custom.spHH}")),
        "custom.fPV": b_expr(frac("{view.custom.pv}")),
    })
    defaults = common_defaults()
    defaults.update({"engMin": 0, "engMax": 100, "spLL": 10, "spL": 20, "spH": 80, "spHH": 90,
                     "fLL": 0.1, "fL": 0.2, "fH": 0.8, "fHH": 0.9, "fPV": 0.5})
    f = lambda k: "{view.custom." + k + "}"
    bands = [("Band_LL", "Bar/Band/Extreme", "0", f("fLL")),
             ("Band_L", "Bar/Band/Alarm", f("fLL"), f("fL")),
             ("Band_N", "Bar/Band/Normal", f("fL"), f("fH")),
             ("Band_H", "Bar/Band/Alarm", f("fH"), f("fHH")),
             ("Band_HH", "Bar/Band/Alarm", f("fHH"), "1")]
    bands[4] = ("Band_HH", "Bar/Band/Extreme", f("fHH"), "1")
    kids = []
    DEF = {"Band_LL": (0, .1), "Band_L": (.1, .2), "Band_N": (.2, .8), "Band_H": (.8, .9), "Band_HH": (.9, 1),
           "Alarm_LL": (0, .1), "Alarm_L": (.1, .2), "Alarm_H": (.8, .9), "Alarm_HH": (.9, 1)}
    for name, cls, x0, x1 in bands:
        bpc = {"position.x": b_expr(x0) if x0 != "0" else None, "position.width": b_expr(f"max(0, {x1} - {x0})")}
        bpc = {k: v for k, v in bpc.items() if v}
        a, b = DEF[name]
        kids.append(label(name, cls, "", {"x": a, "y": BAND_Y, "width": round(b - a, 4), "height": BAND_H}, bpc))
    # alarm overlays on the four limit bands (priority color, blink / faded)
    for k, x0, x1 in (("LL", "0", f("fLL")), ("L", f("fLL"), f("fL")), ("H", f("fH"), f("fHH")), ("HH", f("fHH"), "1")):
        c = C(k)
        opc = {"position.display": b_expr(f"{c} >= 0"),
               "position.width": b_expr(f"max(0, {x1} - {x0})"),
               "props.style.classes": b_expr(f'if({c} < 0, "", "Bar/Band/" + {PRI_NAME(c + " % 10")} + {mod(c)})')}
        if x0 != "0": opc["position.x"] = b_expr(x0)
        a, b = DEF[f"Alarm_{k}"]
        kids.append(label(f"Alarm_{k}", "", "", {"x": a, "y": BAND_Y, "width": round(b - a, 4), "height": BAND_H, "display": False}, opc))
    kids.append(label("Frame", "Bar/Frame", "", {"x": 0, "y": BAND_Y, "width": 1, "height": BAND_H}))
    ptr = comp("ia.display.image", "Pointer", {"source": POINTER, "fit": {"mode": "fill"}},
               {"x": 0.5 - PTR_W / 2, "y": 0, "width": PTR_W, "height": 1},
               prop_config={"position.x": b_expr(f"{f('fPV')} * (1 - {PTR_W:.5f})"),
                            "props.source": b_expr(f'if({{view.custom.badValue}}, "{POINTER_BAD}", "{POINTER}")')})
    kids.append(ptr)
    rng = ('"Range " + numberFormat({view.custom.engMin}, "#,##0.##") + " to " + numberFormat({view.custom.engMax}, "#,##0.##") + " " + '
           'if(isNull({view.custom.units}) || toStr({view.custom.units}) = "null", "", toStr({view.custom.units}))')
    track = comp("ia.container.coord", "Track", {"mode": "percent", "style": {"classes": ""}}, FIX(vh(TRACK_H)), kids,
                 prop_config={"meta.tooltip.text": b_expr(rng)}, meta_extra={"tooltip": {"enabled": True, "text": ""}})
    card = flex("Card", "column", [header_row(), value_row("PV/ValueSmall"), track], "PV/Card PV/BodyBar",
                {"basis": "auto", "grow": 1, "shrink": 1}, justify="space-between")
    root = flex("root", "column", [card], "PV/Shell", justify="flex-start", align="stretch")
    return view(root, defaults, pc, 104, 54)

# ----------------------------------------------------------------- demo view
DEMO = [("PT001", "Normal"), ("PT002", "High (H)"), ("PT003", "High-high (HH + H)"), ("PT004", "Low-low (LL + L)"), ("PT005", "HW fault")]

def build_demo():
    def embed(path, inst, w, h):
        return comp("ia.display.view", f"{path.split('/')[-1]}_{inst}",
                    {"path": f"{FOLDER}/{path}", "params": {"tagPath": f"[default]PV_Demo/{inst}"},
                     "style": {"height": vh(h)}}, FIX(vh(w)))
    def ctl(inst):
        return flex(f"Ctl_{inst}", "column", [
            label(f"Lbl_{inst}", "Text/Caption", f"{inst}  PV:", FIX("auto")),
            comp("ia.input.numeric-entry-field", f"PV_{inst}", {"format": "0,0.0", "style": {"classes": "Input/Setpoint"}},
                 FIX(vh(24)), prop_config={"props.value": {"binding": {"type": "tag", "config": {
                     "bidirectional": True, "mode": "direct", "tagPath": f"[default]PV_Demo/{inst}/PV", "fallbackDelay": 2.5}}}}),
            comp("ia.input.checkbox", f"Flt_{inst}", {"text": "HW_Fault", "style": {"classes": "Input/Check"}},
                 FIX("auto"), prop_config={"props.selected": {"binding": {"type": "tag", "config": {
                     "bidirectional": True, "mode": "direct", "tagPath": f"[default]PV_Demo/{inst}/HW_Fault", "fallbackDelay": 2.5}}}}),
        ], "", FIX(vh(160)))
    rows = []
    for inst, desc in DEMO:
        rows.append(flex(f"Row_{inst}", "row", [
            label(f"Desc_{inst}", "Text/Label", desc, FIX(vh(140))),
            embed("PV_StatusStrip", inst, 104, 54),
            embed("PV_RangeBar", inst, 104, 54),
            ctl(inst),
        ], "Util/Pad/S", FIX("auto"), align="center", pc=None))
        rows[-1]["props"]["style"]["gap"] = vh(16)
    kids = [label("Title", "Text/Title", "Process Value templates: PV_StatusStrip (A1) and PV_RangeBar (B2)", FIX("auto")),
            label("Hint", "Text/Caption Text/Mod/Wrap",
                  "Demo tags: [default]PV_Demo (DDT_Process_Value_Demo). Type a PV to cross the limits (LL 5, L 10, H 35, HH 42, range 0-50). "
                  "Acknowledge in an alarm table to see blink -> solid; return to normal before acking to see the faded cleared-unacked state.",
                  FIX("auto"))] + rows
    root = flex("root", "column", kids, "Container/Screen Util/Pad/L", justify="flex-start")
    root["props"]["style"]["gap"] = vh(8)
    return {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 1200, "height": 700}}, "root": root}

# ----------------------------------------------------------------- tags
def build_tags():
    def mem(name, dt, value, **kw): return {"name": name, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dt, "value": value, **kw}
    def expr(name, dt, e, **kw): return {"name": name, "tagType": "AtomicTag", "valueSource": "expr", "dataType": dt, "expression": e, **kw}
    def alarm(name, pri): return [{"name": name, "priority": pri, "mode": "Equality", "setpointA": 1.0}]
    def limit(name, sp, cmp, pri):
        return {"name": name, "tagType": "Folder", "tags": [
            mem("SP", "Float4", sp),
            mem("Inhibit", "Boolean", False),
            mem("Enabled", "Boolean", True),
            mem("DLY", "Int4", 0),
            expr("Alarm", "Boolean", f"{{[.]../PV}} {cmp} {{[.]SP}} && {{[.]Enabled}} && !{{[.]Inhibit}}", alarms=alarm(name, pri)),
        ]}
    udt = {"name": "DDT_Process_Value_Demo", "tagType": "UdtType", "tags": [
        mem("PV", "Float4", 28.2),
        expr("Name", "String", '"{InstanceName}"'),
        mem("Description", "String", "Demo pressure transmitter"),
        mem("Units", "String", "PSIG"),
        mem("Eng_Min", "Float4", 0.0), mem("Eng_Max", "Float4", 50.0),
        mem("HW_Fault", "Boolean", False, alarms=alarm("HW_Fault", "High")),
        expr("Overrange", "Boolean", "{[.]PV} > {[.]Eng_Max}", alarms=alarm("Overrange", "Diagnostic")),
        expr("Underrange", "Boolean", "{[.]PV} < {[.]Eng_Min}", alarms=alarm("Underrange", "Diagnostic")),
        limit("HH", 42.0, ">=", "Critical"), limit("H", 35.0, ">=", "Medium"),
        limit("L", 10.0, "<=", "Medium"), limit("LL", 5.0, "<=", "Critical"),
    ]}
    pvs = {"PT001": 28.2, "PT002": 37.6, "PT003": 44.1, "PT004": 3.2, "PT005": 28.2}
    inst = []
    for name, v in pvs.items():
        t = {"name": name, "tagType": "UdtInstance", "typeId": "DDT_Process_Value_Demo",
             "tags": [{"name": "PV", "tagType": "AtomicTag", "value": v}]}
        if name == "PT005":
            t["tags"].append({"name": "HW_Fault", "tagType": "AtomicTag", "value": True})
        inst.append(t)
    return {"tags": [{"name": "_types_", "tagType": "Folder", "tags": [udt]},
                     {"name": "PV_Demo", "tagType": "Folder", "tags": inst}]}

HW_FAULT_ALARM = {"name": "HW_Fault", "alarms": [{"name": "HW_Fault", "priority": "High", "mode": "Equality", "setpointA": 1.0,
                                                  "label": "Transmitter / hardware fault"}]}

# ----------------------------------------------------------------- writers
def resource_json(files):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return json.dumps({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": files,
                       "attributes": {"lastModification": {"actor": "build_pv.py", "timestamp": ts}}}, indent=2)

def build():
    os.makedirs(OUT, exist_ok=True)
    views = {f"{FOLDER}/PV_StatusStrip": build_a1(), f"{FOLDER}/PV_RangeBar": build_b2(), f"{FOLDER}/_Demo": build_demo()}
    zpath = os.path.join(OUT, f"{PROJECT}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps({"title": PROJECT, "description": "EFC Process Value templates (PV_StatusStrip, PV_RangeBar)",
                                               "parent": PARENT, "enabled": True, "inheritable": True}, indent=2))
        for path, v in views.items():
            z.writestr(f"{BASE}/views/{path}/view.json", json.dumps(v, indent=2))
            z.writestr(f"{BASE}/views/{path}/resource.json", resource_json(["view.json"]))
        for path, (body, _) in CLASSES.items():
            z.writestr(f"{BASE}/style-classes/{path}/style.json", json.dumps(body, indent=2))
            z.writestr(f"{BASE}/style-classes/{path}/resource.json", resource_json(["style.json"]))
    json.dump(build_tags(), open(os.path.join(OUT, "PV_Demo_Tags.json"), "w"), indent=2)
    with open(os.path.join(OUT, "pv_style_index.md"), "w") as fh:
        fh.write("| Class path | Use |\n|---|---|\n" + "".join(f"| `{p}` | {d} |\n" for p, (_, d) in CLASSES.items()))
    return zpath, views

if __name__ == "__main__":
    z, v = build()
    print(z, len(CLASSES), "classes")
