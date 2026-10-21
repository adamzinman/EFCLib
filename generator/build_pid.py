"""
PID_Symbols: one template per controlled-device symbol (design notes 20-21; see docs/design-notes.md).
  - Only parameter: tagPath (UDT instance)
  - The symbol is a Perspective Drawing (ia.shapes.svg) embedded in the template; element paints bound to state (v5.1)
  - Kept from notes 1-19: tag above / status below (centered), bottom-left actuation button, P left / I right clear of the
    process line, yellow mode letter, actuator head = command / body = feedback, EFC_Styles colors
  - Alarm outline: highest active alarm (priority 1-4) on any member of the UDT instance (isAlarmActiveFiltered)
  - Click on the symbol: nothing yet (faceplates to follow); control valve: no actuation button
  Normally run from the repo root:  python3 build.py
"""
import json, os, shutil, zipfile
import pid_common as v3
from pid_common import (expr, prop, tag, pin, script, label, frac, status_group, badges, resource_json, LAYOUT, PAL,
                      W_ALARM, W_OUTLINE, svg_tokens, source_expr, source_static, atom, BASE)
from active import resolve as resolve_role
_hex = lambda e: e   # v5.1: colors are plain #RRGGBB (bound straight onto Drawing element paints, no data URI)
from active import SYMS, BY, colors

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "pid")   # gitignored build output

# ---------------------------------------------------------------- shared custom props (all driven from the UDT)
# v5.1: isAlarmActiveFiltered returns Bad_NotFound quality when nothing under the instance has an alarm configured
# (seen on DDT_Valve). Each call is coalesced and forced to good quality, so "no alarms" reads as 0 and the bad quality
# can no longer propagate into line / lw.
def _alm(p):
    return ('forceQuality(coalesce(try(isAlarmActiveFiltered({view.params.tagPath} + "/*", "*", "*", %d, %d, 0, 1, 0), false), false))' % (p, p))
ALARM = "if(%s, 4, if(%s, 3, if(%s, 2, if(%s, 1, 0))))" % (_alm(4), _alm(3), _alm(2), _alm(1))
FILL = _hex('case({view.custom.state}, 0, "%s", 1, "%s", 2, "%s", 3, "%s", "%s")'
            % (PAL["stopped"], PAL["running"], PAL["transition"], PAL["fault"], PAL["transition"]))
HEAD = _hex('if({view.custom.command} < 0, {view.custom.fill}, if({view.custom.command} = 1, "%s", "%s"))' % (PAL["running"], PAL["stopped"]))
LINE = _hex('if({view.custom.state} = 3, "%s", case({view.custom.alarm}, 1, "%s", 2, "%s", 3, "%s", 4, "%s", "%s"))'
            % (PAL["fault_border"], PAL["alarm"][1], PAL["alarm"][2], PAL["alarm"][3], PAL["alarm"][4], PAL["outline"]))
CON = _hex('if({view.custom.state} = 3, "%s", "%s")' % (PAL["con_light"], PAL["con_dark"]))
TAGNAME = ('if(len(coalesce({view.custom.name}, "")) > 0, {view.custom.name}, '
           'substring({view.params.tagPath}, lastIndexOf({view.params.tagPath}, "/") + 1))')
TAG_CLS = "Text/TagName Text/Mod/Center Text/Mod/NoWrap"

def color_props(s, custom, cfg):
    c = colors(s)
    custom.update({"alarm": 0, "fill": _hex(c["state"]), "head": _hex(c["head"]), "line": _hex(c["line"]),
                   "lw": round(c["lw"], 3), "con": _hex(c["con"])})
    cfg.update({"custom.alarm": expr(ALARM), "custom.fill": expr(FILL), "custom.head": expr(HEAD), "custom.line": expr(LINE),
                "custom.con": expr(CON),
                "custom.lw": expr(f"if({{view.custom.alarm}} > 0 || {{view.custom.state}} = 3, {round(W_ALARM * s.k, 3)}, {round(W_OUTLINE * s.k, 3)})")})

# v5.1: the symbol is embedded as a Perspective Drawing (ia.shapes.svg). Every SVG element lives in the view JSON and its
# fill / stroke paint (and outline width) is bound to the state-driven custom props -- no image link, no data URI.
DYN_FILL = {"state": "fill", "head": "head", "cfill": "con"}
DYN_STROKE = {"state": "line", "body": "line", "head": "line", "cstroke": "con"}
def drawing_elements(s):
    from active import colors as _c
    c = _c(s); els, binds = [], {}
    for i, e in enumerate(s.elems):
        t, role, g, kw = e
        f, st, sw = resolve_role(e, s, c)
        el = {"type": t, "name": f"{role}{i}"}
        el.update({k: v for k, v in g.items()})
        el["fill"] = {"paint": f if f != "none" else "transparent"}
        if st != "none" or role in DYN_STROKE:
            el["stroke"] = {"paint": st, "width": round(sw, 3), "linejoin": "round"}
        else:
            el["stroke"] = {"paint": "transparent", "width": 0}
        els.append(el)
        if role in DYN_FILL: binds[f"props.elements[{i}].fill.paint"] = expr("{view.custom.%s}" % DYN_FILL[role])
        if role in DYN_STROKE: binds[f"props.elements[{i}].stroke.paint"] = expr("{view.custom.%s}" % DYN_STROKE[role])
        if role in ("state", "body", "head"): binds[f"props.elements[{i}].stroke.width"] = expr("{view.custom.lw}")
    return els, binds

def image(s, L, custom):
    els, binds = drawing_elements(s)
    return {"type": "ia.shapes.svg", "version": 0, "meta": {"name": "Symbol"}, "position": frac(L["sym"], L["size"]),
            "props": {"viewBox": f"0 0 {s.vb[0]} {s.vb[1]}", "preserveAspectRatio": "xMidYMid", "elements": els},
            "propConfig": binds}

def image_v4(s, L, custom):
    toks = svg_tokens(s)
    return {"type": "ia.display.image", "version": 0, "meta": {"name": "Symbol"}, "position": frac(L["sym"], L["size"]),
            "props": {"source": source_static(toks, custom), "fit": {"mode": "contain"}},
            "propConfig": {"props.source": expr(source_expr(toks))}}

def tag_label(L):
    return label("Tag", frac(L["tag"], L["size"]), "", TAG_CLS,
                 {"props.text": expr(TAGNAME), "meta.tooltip.text": expr('coalesce({view.custom.desc}, "")'),
                  "meta.tooltip.enabled": expr('len(coalesce({view.custom.desc}, "")) > 0')}, meta={"tooltip": {"enabled": False, "text": ""}})


# notes: P and I sit just outside the valve actuator, an equal gap from each side, centered on the actuator height
BADGE_GAP = 3   # px at 1080p
def valve_layout(s, base):
    import re as _re
    L = dict(base); sx, sy, sw, sh = L["sym"]; sc = sw / s.vb[0]
    t, role, g, kw = next(e for e in s.elems if e[1] == "head")
    if t == "rect":   x0, x1, y0, y1 = g["x"], g["x"] + g["width"], g["y"], g["y"] + g["height"]
    elif t == "circle": x0, x1, y0, y1 = g["cx"] - g["r"], g["cx"] + g["r"], g["cy"] - g["r"], g["cy"] + g["r"]
    else:              x0, x1, y0, y1 = 28, 72, 16, 32                 # diaphragm dome (Valve_Control): 28..72 wide, 16..32 tall
    ax0, ax1 = sx + x0 * sc, sx + x1 * sc; acy = sy + (y0 + y1) / 2 * sc
    bw, bh = L["P"][2], L["P"][3]
    L["P"] = (round(ax0 - BADGE_GAP - bw, 1), round(acy - bh / 2, 1), bw, bh)
    L["I"] = (round(ax1 + BADGE_GAP, 1), round(acy - bh / 2, 1), bw, bh)
    return L

def status_label(L, status_expr, cls_expr, m_vis=None):
    """Status below the symbol: a bordered state chip sized to its text, centered on the symbol (flex wrapper).
    m_vis: expression; when true a yellow 'M' segment (Mode/ManualSplit) joins the chip's left side at the same height."""
    kids = []
    if m_vis:
        # Hidden M must take zero width so the flex row centres the status chip alone on the symbol centreline:
        # meta.visible false removes it, and Util/Collapsed (display:none, 0 width/padding/border) guarantees no residual space.
        kids.append(label("M", None, "M", "Util/Collapsed",
                          {"meta.visible": expr(m_vis), "props.style.classes": expr(f'if({m_vis}, "Mode/ManualSplit", "Util/Collapsed")')},
                          position={"basis": "auto", "shrink": 0, "grow": 0}))
        cls_expr = f'{cls_expr} + if({m_vis}, " Mode/ManualJoined", "")'
    kids.append(label("Status", None, "", "State/Stopped", {"props.text": expr(status_expr), "props.style.classes": expr(cls_expr)},
                      position={"basis": "auto", "shrink": 0}))
    return {"type": "ia.container.flex", "version": 0, "meta": {"name": "StatusGroup"}, "position": frac(L["status"], L["size"]),
            "props": {"direction": "row", "justify": "center", "alignItems": "stretch", "style": {"classes": ""}}, "children": kids}

# note 25: vertical position indicator for analog valves (fill = actual Pos, blue pointer = commanded Out)
BAR_TRACK, BAR_FILL, BAR_CMD = "#FFFFFF", "#4D4D4D", "#1F4E99"
def position_bar(L):
    """v5.1: embedded Drawing. Track rect, fill rect (y/height bound to Pos), command pointer (path d bound to Out)."""
    els = [{"type": "rect", "name": "track", "x": 8, "y": 2, "width": 11, "height": 96,
            "fill": {"paint": BAR_TRACK}, "stroke": {"paint": "#595959", "width": 1.5}},
           {"type": "rect", "name": "pos", "x": 8, "y": 98, "width": 11, "height": 0,
            "fill": {"paint": BAR_FILL}, "stroke": {"paint": "transparent", "width": 0}},
           {"type": "path", "name": "cmd", "d": "M0 91 L7 98 L0 105 Z",
            "fill": {"paint": BAR_CMD}, "stroke": {"paint": "transparent", "width": 0}}]
    return {"type": "ia.shapes.svg", "version": 0, "meta": {"name": "PositionBar", "tooltip": {"enabled": True, "text": ""}},
            "position": frac(L["bar"], L["size"]),
            "props": {"viewBox": "0 -6 20 112", "preserveAspectRatio": "none", "elements": els},
            "propConfig": {"props.elements[1].y": expr("98 - 0.96 * {view.custom.posC}"),
                           "props.elements[1].height": expr("0.96 * {view.custom.posC}"),
                           "props.elements[2].d": expr('"M0 " + toStr(91 - 0.96 * {view.custom.outC}) + " L7 " + toStr(98 - 0.96 * {view.custom.outC}) + " L0 " + toStr(105 - 0.96 * {view.custom.outC}) + " Z"'),
                           "meta.tooltip.text": expr('"Position " + numberFormat({view.custom.posC}, "0") + " % / Command " + numberFormat({view.custom.outC}, "0") + " %"')}}

def view(path_default, custom, cfg, kids, size, use_button=False):
    params = {"tagPath": path_default}
    if use_button: params["useButton"] = True          # True: manual command button; False: click the symbol, yellow M shows Manual
    pc = {f"params.{k}": pin() for k in params}; pc.update(cfg)
    return {"custom": custom, "params": params, "propConfig": pc,
            "props": {"defaultSize": {"width": size[0], "height": size[1]}},
            "root": {"type": "ia.container.coord", "version": 0, "meta": {"name": "root"}, "props": {"mode": "percent"}, "children": kids}}

# ---------------------------------------------------------------- discrete valve (plant discrete-valve UDT)
ILIST_TIP = '\t# InterlockList is a document: {Status, Description[], InterlockName[], Used[]}\n\thead = "Interlock active - open blocked"\n\ttry:\n\t\tnames = list(value["InterlockName"] or [])\n\t\tused = list(value["Used"] or [])\n\t\tdesc = list(value["Description"] or [])\n\t\titems = []\n\t\tfor i in range(len(names)):\n\t\t\tif i < len(used) and used[i] and names[i]:\n\t\t\t\td = desc[i] if i < len(desc) and desc[i] else ""\n\t\t\t\titems.append(str(names[i]) + (" - " + str(d) if d else ""))\n\t\treturn head + (":\\n" + "\\n".join(items) if items else "")\n\texcept:\n\t\treturn head'

def onoff_template(s, demo_path):
    L = valve_layout(s, LAYOUT["AutoValve"])
    custom = {"cmd": False, "zso": False, "zsc": True, "fb": True, "permMissing": False, "intlk": False, "ilist": None,
              "manual": False, "off": False, "locked": False, "name": "", "desc": "", "state": 0, "command": 0}
    cfg = {"custom.cmd": tag("CMD"), "custom.zso": tag("ZSO"), "custom.zsc": tag("ZSC"), "custom.fb": tag("Feedback_Enabled"),
           "custom.permMissing": tag("Permissive"), "custom.intlk": tag("Interlock"), "custom.ilist": tag("InterlockList"),
           "custom.manual": tag("Manual"), "custom.off": tag("Off"), "custom.locked": tag("LockedOut"),
           "custom.name": tag("Name"), "custom.desc": tag("Description"),
           "custom.state": expr("if({view.custom.zso} && {view.custom.zsc}, 3, if(!{view.custom.fb}, if({view.custom.cmd}, 1, 0), "
                                "if({view.custom.zso}, 1, if({view.custom.zsc}, 0, 2))))"),
           "custom.command": expr("if({view.custom.fb}, if({view.custom.cmd}, 1, 0), -1)")}
    color_props(s, custom, cfg)
    status = 'case({view.custom.state}, 0, "CLOSED", 1, "OPEN", 2, if({view.custom.cmd}, "OPENING", "CLOSING"), 3, "FAULT", "???")'
    cls = 'case({view.custom.state}, 0, "State/Stopped", 1, "State/Running", 2, "State/Transition", 3, "State/Fault", "State/Unknown")'   # bordered state chip, same as running equipment
    click = script("\tcmd = bool(self.view.custom.cmd)\n\tsystem.tag.writeBlocking([self.view.params.tagPath + '/HMI_CMD'], [not cmd])")
    custom["canCmd"] = False
    cfg["custom.canCmd"] = expr("{view.custom.manual} && !{view.custom.locked} && !{view.custom.off} && "
                                "({view.custom.cmd} || (!{view.custom.permMissing} && !{view.custom.intlk}))")
    btn = {"type": "ia.input.button", "version": 0, "meta": {"name": "PB", "tooltip": {"enabled": True, "text": "Open"}},
           "position": frac(L["pb"], L["size"]), "props": {"text": "", "enabled": False, "style": {"classes": "Button/Command"}},
           "propConfig": {"meta.visible": expr("{view.params.useButton} && {view.custom.manual}"),   # shown only in Manual, when useButton
                          "props.enabled": expr("{view.custom.canCmd}"),
                          "meta.tooltip.text": expr('if({view.custom.locked}, "Locked out", if(!{view.custom.manual}, "Manual mode required", '
                                                    'if({view.custom.cmd}, "Close", "Open")))')},
           "events": {"component": {"onActionPerformed": click}}}
    i_tip = '"Interlock active - open blocked" + if(len(coalesce(toStr({view.custom.ilist}), "")) > 0, ": " + toStr({view.custom.ilist}), "")'
    img = image(s, L, custom)                                   # useButton = false: click the symbol (same rules as the button)
    img["propConfig"]["props.style.classes"] = expr('if(!{view.params.useButton} && {view.custom.canCmd}, "Util/Pointer", "")')
    img["events"] = {"dom": {"onClick": script(
        "\tif self.view.params.useButton or not self.view.custom.canCmd:\n\t\treturn\n"
        "\tcmd = bool(self.view.custom.cmd)\n\tsystem.tag.writeBlocking([self.view.params.tagPath + '/HMI_CMD'], [not cmd])")}}
    kids = [tag_label(L), img] + badges(L, p_vis="{view.custom.permMissing}", i_vis="{view.custom.intlk}", i_tip=i_tip) + \
           [status_label(L, status, cls, m_vis="!{view.params.useButton} && {view.custom.manual}"), btn]
    for k in kids:                                              # I tooltip from the InterlockList document (names of used interlocks)
        if k["meta"]["name"] == "I":
            k["propConfig"]["meta.tooltip.text"] = {"binding": {"type": "property", "config": {"path": "view.custom.ilist"},
                                                                 "transforms": [{"type": "script", "code": ILIST_TIP}]}}
    return view(demo_path, custom, cfg, kids, L["size"], use_button=True)

# ---------------------------------------------------------------- control valve (PID_ControlValve UDT); no actuation button
def control_template(s, demo_path):
    L = valve_layout(s, LAYOUT["ControlValve"])
    custom = {"out": 0.0, "pos": 0.0, "fb": True, "perm": True, "intlk": False, "fault": False, "mode": 0, "name": "", "desc": "",
              "state": 0, "command": 0}
    cfg = {"custom.out": tag("Out"), "custom.pos": tag("Pos"), "custom.fb": tag("Feedback_Enabled"), "custom.perm": tag("PermOK"),
           "custom.intlk": tag("Intlk"), "custom.fault": tag("Fault"), "custom.mode": tag("Mode"),
           "custom.name": tag("Name"), "custom.desc": tag("Description"),
           "custom.state": expr("if({view.custom.fault}, 3, if((if({view.custom.fb}, {view.custom.pos}, {view.custom.out})) > 1, 1, 0))"),
           "custom.command": expr("if({view.custom.fb}, if({view.custom.out} > 1, 1, 0), -1)")}
    color_props(s, custom, cfg)
    status = 'if({view.custom.state} = 3, "FAULT", numberFormat(if({view.custom.fb}, {view.custom.pos}, {view.custom.out}), "0") + " %")'
    cls = 'case({view.custom.state}, 0, "State/Stopped", 1, "State/Running", 2, "State/Transition", 3, "State/Fault", "State/Unknown") + " Text/Mod/Tabular"'
    custom.update({"posC": 0.0, "outC": 0.0})
    cfg.update({"custom.posC": expr("max(0, min(100, coalesce({view.custom.pos}, 0)))"),
                "custom.outC": expr("max(0, min(100, coalesce({view.custom.out}, 0)))")})
    kids = [tag_label(L), image(s, L, custom)] + badges(L) + [status_label(L, status, cls), position_bar(L)]
    return view(demo_path, custom, cfg, kids, L["size"])

# ---------------------------------------------------------------- running equipment (PID_Motor UDT)
def motor_template(s, demo_path):
    L = dict(LAYOUT["Motor"])
    if s.badge_i == "low": L["I"] = L["I_low"]          # clear of a top-right discharge
    custom = {"cmd": False, "run": False, "fb": True, "perm": True, "intlk": False, "fault": False, "mode": 0, "name": "", "desc": "",
              "state": 0, "command": -1}
    cfg = {"custom.cmd": tag("Cmd"), "custom.run": tag("Run"), "custom.fb": tag("Feedback_Enabled"), "custom.perm": tag("PermOK"),
           "custom.intlk": tag("Intlk"), "custom.fault": tag("Fault"), "custom.mode": tag("Mode"),
           "custom.name": tag("Name"), "custom.desc": tag("Description"),
           "custom.state": expr("if({view.custom.fault}, 3, if(!{view.custom.fb}, if({view.custom.cmd}, 1, 0), "
                                "if({view.custom.run} && {view.custom.cmd}, 1, if(!{view.custom.run} && !{view.custom.cmd}, 0, 2))))")}
    color_props(s, custom, cfg)
    status = 'case({view.custom.state}, 0, "STOPPED", 1, "RUNNING", 2, if({view.custom.cmd}, "STARTING", "STOPPING"), 3, "FAULT", "???")'
    cls = 'case({view.custom.state}, 0, "State/Stopped", 1, "State/Running", 2, "State/Transition", 3, "State/Fault", "State/Unknown")'
    pb = v3.pb_button(L, "Stop", "Start")
    pb["props"]["style"]["classes"] = "Button/Command"
    pb["propConfig"]["meta.visible"] = expr("{view.params.useButton} && {view.custom.mode} = 1")      # shown only in Manual, when useButton
    custom["canCmd"] = False
    cfg["custom.canCmd"] = expr("{view.custom.mode} = 1 && ({view.custom.cmd} || ({view.custom.perm} && !{view.custom.intlk}))")
    img = image(s, L, custom)                                   # useButton = false: press/release on the symbol drives PB
    img["propConfig"]["props.style.classes"] = expr('if(!{view.params.useButton} && {view.custom.canCmd}, "Util/Pointer", "")')
    press = script("\tif self.view.params.useButton or not self.view.custom.canCmd:\n\t\treturn\n"
                   "\tsystem.tag.writeBlocking([self.view.params.tagPath + '/PB'], [True])")
    release = script("\tif self.view.params.useButton:\n\t\treturn\n\tsystem.tag.writeBlocking([self.view.params.tagPath + '/PB'], [False])")
    img["events"] = {"dom": {"onMouseDown": press, "onTouchStart": press, "onMouseUp": release, "onTouchEnd": release, "onMouseLeave": release}}
    kids = [tag_label(L), img] + badges(L) + [status_label(L, status, cls, m_vis="!{view.params.useButton} && {view.custom.mode} = 1"), pb]
    return view(demo_path, custom, cfg, kids, L["size"], use_button=True)

def template_for(s):
    if s.kind == "onoff":   return onoff_template
    if s.kind == "control": return control_template
    return motor_template

# ---------------------------------------------------------------- tags (PID_Motor / PID_ControlValve gain Name, Description, Feedback_Enabled)
EXTRA = [atom("Name", "String", ""), atom("Description", "String", ""), atom("Feedback_Enabled", "Boolean", True)]
UDTS = dict(v3.UDTS)
UDTS["PID_Motor"] = UDTS["PID_Motor"] + EXTRA
UDTS["PID_ControlValve"] = UDTS["PID_ControlValve"] + EXTRA
# demo alarm so the outline can be seen: Fault = 1 raises a High alarm on PID_Motor
for m in UDTS["PID_Motor"]:
    if m["name"] == "Fault": m["alarms"] = [{"name": "Fault", "mode": "Equality", "setpointA": 1.0, "priority": "High"}]

DEMO = [  # instance, UDT, member overrides, template symbol
    ("XV101", "Valve_Discrete_Demo", {"Auto": True, "CMD": True, "ZSO": True, "ZSC": False, "Name": "XV-101", "Description": "N2 supply isolation"}, "Valve_OnOff_Pneumatic"),
    ("XV102", "Valve_Discrete_Demo", {"Manual": True, "Permissive": True, "Name": "XV-102"}, "Valve_Solenoid"),
    ("XV103", "Valve_Discrete_Demo", {"Manual": True, "CMD": True, "ZSC": False, "Name": "XV-103"}, "Valve_MOV"),
    ("XV104", "Valve_Discrete_Demo", {"Off": True, "Interlock": True, "InterlockList": "PSH-201 high pressure", "Name": "XV-104"}, "Valve_OnOff_Pneumatic"),
    ("XV105", "Valve_Discrete_Demo", {"LockedOut": True, "ZSO": True, "ZSC": True, "Name": "XV-105"}, "Valve_OnOff_Pneumatic"),
    ("FV101", "PID_ControlValve", {"Out": 45.0, "Pos": 43.0, "Name": "FV-101"}, "Valve_Control"),
    ("FV102", "PID_ControlValve", {"Out": 20.0, "Pos": 20.0, "Mode": 1, "Name": "FV-102"}, "Valve_Control"),
    ("P101", "PID_Motor", {"Cmd": True, "Run": True, "Name": "P-101"}, "Pump_Centrifugal"),
    ("P102", "PID_Motor", {"PermOK": False, "Intlk": True, "Name": "P-102"}, "Pump_PD_Rotary"),
    ("K201", "PID_Motor", {"Cmd": True, "Run": True, "Mode": 1, "Name": "K-201"}, "Compressor_Diaphragm"),
    ("K202", "PID_Motor", {"Fault": True, "Name": "K-202"}, "Compressor_Centrifugal"),
    ("B301", "PID_Motor", {"Cmd": True, "Name": "B-301"}, "Blower"),
    ("PV501", "PID_Motor", {"Cmd": True, "Run": True, "Mode": 1, "Name": "PV-501"}, "Pump_Vacuum"),
    ("E401", "PID_Motor", {"Cmd": True, "Run": True, "Name": "E-401"}, "Heater_Electric"),
]
NO_BUTTON = {"XV103", "PV501"}   # demo instances shown with useButton = false
def tpl_path(s): return f"Templates/{s.cat}/{s.name}"   # imports straight into Views/Templates

def tags_files():
    d = os.path.join(OUT, "tags"); os.makedirs(d, exist_ok=True)
    for n, members in UDTS.items():
        json.dump({"name": n, "tagType": "UdtType", "tags": members}, open(os.path.join(d, f"{n}_UDT.json"), "w"), indent=2)
    inst = [{"name": n, "tagType": "UdtInstance", "typeId": u, "tags": [{"name": k, "tagType": "AtomicTag", "value": v} for k, v in ov.items()]}
            for n, u, ov, _ in DEMO]
    json.dump({"name": "PID_Demo", "tagType": "Folder", "tags": inst}, open(os.path.join(d, "PID_Demo_Instances.json"), "w"), indent=2)

def demo_view():
    items = []
    for n, u, ov, sym in DEMO:
        s = BY[sym]; L = LAYOUT["AutoValve" if s.kind == "onoff" else "ControlValve" if s.kind == "control" else "Motor"]
        w, h = L["size"]
        prm = {"tagPath": f"[default]PID_Demo/{n}"}
        if n in NO_BUTTON: prm["useButton"] = False
        items.append(v3.item(tpl_path(s), prm, w * 1.5, h * 1.5, f"{n} · {sym}" + (" · useButton=false" if n in NO_BUTTON else "")))
    return {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 1920, "height": 1080}},
            "root": {"type": "ia.container.flex", "version": 0, "meta": {"name": "root"},
                     "props": {"direction": "column", "style": {"classes": "Container/Screen", "gap": "10px", "padding": "10px", "overflowY": "auto"}},
                     "children": [v3.section("Templates bound to [default]PID_Demo (1.5x). Params: tagPath (+ useButton on valves and running equipment)", items)]}}


# ---------------------------------------------------------------- null-safety (live-gateway fix 2026-10-06)
# Tag-bound customs read null while a member is missing, bad or still loading (e.g. the new Permissive member);
# null inside && / || / if() puts the dependent bindings in error. Wrap every read of a tag-bound custom in coalesce().
NULL_DEFAULTS = {"cmd": "false", "zso": "false", "zsc": "false", "fb": "true", "permMissing": "false", "intlk": "false",
                 "manual": "false", "off": "false", "locked": "false", "run": "false", "perm": "true", "fault": "false",
                 "mode": "0", "out": "0", "pos": "0"}
def _harden_expr(e):
    import re as _re
    e = _re.sub(r"\{view\.custom\.(\w+)\}", lambda m: f"coalesce({{view.custom.{m.group(1)}}}, {NULL_DEFAULTS[m.group(1)]})"
                if m.group(1) in NULL_DEFAULTS else m.group(0), e)
    return e
def harden(o):
    if isinstance(o, dict):
        if o.get("type") == "expr" and "expression" in o.get("config", {}):
            o["config"]["expression"] = _harden_expr(o["config"]["expression"])
        for v in o.values(): harden(v)
    elif isinstance(o, list):
        for v in o: harden(v)
    return o

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    views = {}
    for s in SYMS:
        demo = next((f"[default]PID_Demo/{n}" for n, _, _, sym in DEMO if sym == s.name),
                    "[default]PID_Demo/" + {"onoff": "XV101", "control": "FV101"}.get(s.kind, "P101"))
        views[tpl_path(s)] = harden(template_for(s)(s, demo))
    views["Templates/_Demo"] = demo_view()
    raw = os.path.join(OUT, "_raw.zip")
    with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps({"title": "PID_Symbols", "description": "EFC controlled-device templates (generated). Parent: EFC_Styles",
                                               "parent": "EFC_Styles", "enabled": True, "inheritable": True}, indent=2))
        for p, v in views.items():
            z.writestr(f"{BASE}/views/{p}/view.json", json.dumps(v, indent=2))
            z.writestr(f"{BASE}/views/{p}/resource.json", resource_json(["view.json"]))
    from make_project_zip import redo
    redo(raw, os.path.join(OUT, "PID_Symbols_PROJECT.zip")); os.remove(raw)
    tags_files()
    v3.OUT = OUT; n = v3.static_symbols()
    print(f"{len(views) - 1} templates, {n} SVGs")

if __name__ == "__main__":
    build()

# Packaging, project export and checks live in ../build.py (repo root).
