"""
Build PID_Symbols v3: active controlled-device templates for Ignition Perspective 8.1.
  Shared helpers (layout, bindings, static SVG export) used by build_pid.py.
Outputs in dist/:
  PID_Symbols.zip           Perspective project (parent EFC_Styles): active symbol views, templates, demo
  tags/*.json               UDT definitions + demo instances
  symbols/<Category>/*.svg  every static symbol (v2 set, standards palette) + symbols/Active/*
  preview.html              template + symbol preview
"""
import json, os, sys, shutil, zipfile, datetime
from active import SYMS, BY, PAL, W_ALARM, W_OUTLINE, svg, colors, resolve

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "build", "pid")   # gitignored build output
BASE = "com.inductiveautomation.perspective"

def expr(e): return {"binding": {"type": "expr", "config": {"expression": e}}}
def prop(p): return {"binding": {"type": "property", "config": {"path": p}}}
def tag(m): return {"binding": {"type": "tag", "config": {"mode": "indirect", "fallbackDelay": 2.5,
                    "references": {"0": "{view.params.tagPath}"}, "tagPath": "{0}/" + m}}}
def pin(): return {"paramDirection": "input", "persistent": True}
def script(code): return {"type": "script", "scope": "G", "config": {"script": code}}

# =================================================================== symbol views
STATE_EXPR = ('case({view.params.state}, 0, "%s", 1, "%s", 2, "%s", 3, "%s", "%s")'
              % (PAL["stopped"], PAL["running"], PAL["transition"], PAL["fault"], PAL["transition"]))
HEAD_EXPR = ('if({view.params.command} < 0, {view.custom.fill}, if({view.params.command} = 1, "%s", "%s"))' % (PAL["running"], PAL["stopped"]))
LINE_EXPR = ('case({view.params.alarm}, 1, "%s", 2, "%s", 3, "%s", 4, "%s", "%s")'
             % (PAL["alarm"][1], PAL["alarm"][2], PAL["alarm"][3], PAL["alarm"][4], PAL["outline"]))
CON_EXPR = 'if({view.params.state} = 3, "%s", "%s")' % (PAL["con_light"], PAL["con_dark"])

from urllib.parse import quote
def _enc(txt): return quote(txt, safe="/:=,.-'()")   # data-URI safe (#, <, >, spaces encoded)
def _hex(e): return e.replace("#", "%23")            # colors stored pre-encoded for the data URI

def svg_tokens(s):
    """SVG markup as a list of ('lit', text) / ('var', custom-prop) tokens. Colors that change at runtime are vars."""
    k = s.k
    toks = [("lit", f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {s.vb[0]} {s.vb[1]}' preserveAspectRatio='xMidYMid meet'>")]
    for e in s.elems:
        t, role, g, kw = e
        f, st, sw = resolve(e, s, colors(s))
        dyn_fill = {"state": "fill", "head": "head", "cfill": "con"}.get(role)
        dyn_stroke = {"state": "line", "body": "line", "head": "line", "cstroke": "con"}.get(role)
        dyn_w = role in ("state", "body", "head")
        toks.append(("lit", f"<{t} " + " ".join(f"{a}='{v}'" for a, v in g.items()) + " fill='"))
        toks.append(("var", dyn_fill) if dyn_fill else ("lit", f))
        if st == "none" and not dyn_stroke:
            toks.append(("lit", "'/>")); continue
        toks.append(("lit", "' stroke='"))
        toks.append(("var", dyn_stroke) if dyn_stroke else ("lit", st))
        toks.append(("lit", "' stroke-width='"))
        toks.append(("var", "lw") if dyn_w else ("lit", str(round(sw, 3))))
        toks.append(("lit", "' stroke-linejoin='round'/>"))
    toks.append(("lit", "</svg>"))
    return toks

def source_expr(toks):
    parts = ['"data:image/svg+xml;utf8,"']
    buf = ""
    for kind, v in toks:
        if kind == "lit": buf += v
        else:
            if buf: parts.append('"' + _enc(buf) + '"'); buf = ""
            parts.append("toStr({view.custom.lw})" if v == "lw" else "{view.custom." + v + "}")
    if buf: parts.append('"' + _enc(buf) + '"')
    return " + ".join(parts)

def source_static(toks, custom):
    out = "data:image/svg+xml;utf8,"
    buf = ""
    for kind, v in toks:
        if kind == "lit": buf += v
        else: out += _enc(buf) + str(custom[v]); buf = ""
    return out + _enc(buf)

def symbol_view(s):
    """Symbol view = one Image component whose source is an embedded SVG data URI, rebuilt by expression when params change."""
    c = colors(s)
    roles = s.roles
    custom = {"fill": _hex(c["state"]), "line": _hex(c["line"]), "lw": round(c["lw"], 3)}
    cfg = {"custom.fill": expr(_hex(STATE_EXPR)), "custom.line": expr(_hex(LINE_EXPR)),
           "custom.lw": expr(f"if({{view.params.alarm}} > 0, {round(W_ALARM * s.k, 3)}, {round(W_OUTLINE * s.k, 3)})")}
    params = {"state": 0, "alarm": 0}
    if "head" in roles:
        custom["head"] = _hex(c["head"]); cfg["custom.head"] = expr(_hex(HEAD_EXPR)); params["command"] = -1
    if roles & {"cstroke", "cfill"}:
        custom["con"] = _hex(c["con"]); cfg["custom.con"] = expr(_hex(CON_EXPR))
    for p in params: cfg[f"params.{p}"] = pin()
    toks = svg_tokens(s)
    w, h = s.size
    image = {"type": "ia.display.image", "version": 0, "meta": {"name": "Symbol"},
             "position": {"x": 0, "y": 0, "width": 1, "height": 1},
             "props": {"source": source_static(toks, custom), "fit": {"mode": "contain"}},
             "propConfig": {"props.source": expr(source_expr(toks))}}
    return {"custom": custom, "params": params, "propConfig": cfg, "props": {"defaultSize": {"width": w, "height": h}},
            "root": {"type": "ia.container.coord", "version": 0, "meta": {"name": "root"}, "props": {"mode": "percent"}, "children": [image]}}

# =================================================================== template layouts (px at 1080p; one source for JSON + preview)
LAYOUT = {
    "AutoValve":    {"size": (120, 100), "tag": (0, 1, 120, 15), "sym": (38, 18, 44, 44), "P": (15, 22, 14, 14), "I": (91, 22, 14, 14),
                     "status": (20, 65, 80, 18), "pb": (3, 65, 18, 18), "line": 0.70},
    "ControlValve": {"size": (120, 100), "tag": (0, 1, 120, 15), "sym": (38, 18, 44, 44), "P": (20, 22, 14, 14), "I": (91, 22, 14, 14),
                     "status": (20, 65, 80, 18), "pb": None, "line": 0.70, "bar": (18, 9, 13, 37)},   # bar left of the valve, just outside the P badge, taller
    "Motor":        {"size": (120, 116), "tag": (0, 1, 120, 15), "sym": (27, 18, 66, 66), "P": (6, 22, 14, 14), "I": (100, 22, 14, 14),
                     "I_low": (100, 62, 14, 14), "status": (17, 90, 86, 18), "pb": (2, 90, 18, 18), "line": 0.52},
}
def frac(box, size): x, y, w, h = box; W, H = size; return {"x": round(x / W, 4), "y": round(y / H, 4), "width": round(w / W, 4), "height": round(h / H, 4)}

TAGNAME = ('if(len({view.params.label}) > 0, {view.params.label}, '
           'substring({view.params.tagPath}, lastIndexOf({view.params.tagPath}, "/") + 1))')
POPUP = script("\tp = self.view.params\n\tif p.popupView:\n"
               "\t\tsystem.perspective.openPopup('pid_' + p.tagPath, p.popupView, params={'tagPath': p.tagPath}, title=p.label or p.tagPath)")

def label(name, pos, text, classes, cfg=None, meta=None, position=None):
    c = {"type": "ia.display.label", "version": 0, "meta": {"name": name, **(meta or {})},
         "position": position or pos, "props": {"text": text, "style": {"classes": classes}}}
    if cfg: c["propConfig"] = cfg
    return c

def status_group(L, status_expr, status_cls_expr, letter_expr='if({view.custom.mode} = 1, "M", "")'):
    """Centered status; an abnormal mode adds a dark letter segment on its left (note 17, option C2): M manual, D off, L locked out."""
    m = label("M", None, "M", "Mode/ManualSplit", {"props.text": expr(letter_expr), "meta.visible": expr(f"len({letter_expr}) > 0")},
              position={"basis": "auto", "shrink": 0})
    st = label("Status", None, "", "Text/Status", {"props.text": expr(status_expr), "props.style.classes": expr(status_cls_expr)},
               position={"basis": "auto", "shrink": 0})
    return {"type": "ia.container.flex", "version": 0, "meta": {"name": "StatusGroup"}, "position": frac(L["status"], L["size"]),
            "props": {"direction": "row", "justify": "center", "alignItems": "stretch", "style": {"classes": ""}}, "children": [m, st]}

def badges(L, i_pos_expr=None, p_vis="!{view.custom.perm}", i_vis="{view.custom.intlk}", i_tip=None):
    P_ = label("P", frac(L["P"], L["size"]), "P", "Indicator/PermissiveBadge", {"meta.visible": expr(p_vis)},
               meta={"tooltip": {"enabled": True, "text": "Permissive missing - start/open blocked"}})
    I_ = label("I", frac(L["I"], L["size"]), "I", "Indicator/InterlockBadge", {"meta.visible": expr(i_vis)},
               meta={"tooltip": {"enabled": True, "text": "Interlock active - start/open blocked"}})
    if i_tip: I_["propConfig"]["meta.tooltip.text"] = expr(i_tip)
    if i_pos_expr: I_["propConfig"]["position.y"] = expr(i_pos_expr)
    return [P_, I_]

def pb_button(L, tip_on, tip_off):
    press = script("\tif self.props.enabled:\n\t\tsystem.tag.writeBlocking([self.view.params.tagPath + '/PB'], [True])")
    release = script("\tsystem.tag.writeBlocking([self.view.params.tagPath + '/PB'], [False])")
    return {"type": "ia.input.button", "version": 0, "meta": {"name": "PB", "tooltip": {"enabled": True, "text": tip_off}},
            "position": frac(L["pb"], L["size"]), "props": {"text": "", "enabled": True, "style": {"classes": "Button/Momentary"}},
            "propConfig": {"props.enabled": expr("{view.custom.cmd} || ({view.custom.perm} && !{view.custom.intlk})"),
                           "meta.tooltip.text": expr(f'if({{view.custom.cmd}}, "{tip_on}", "{tip_off}")')},
            "events": {"dom": {"onMouseDown": press, "onTouchStart": press, "onMouseUp": release, "onTouchEnd": release, "onMouseLeave": release}}}

def embed(L, path_expr, default, params_cfg, dparams=None):
    cfg = {"props.path": expr(path_expr), "props.style.classes": expr('if(len({view.params.popupView}) > 0, "Util/Pointer", "")')}
    cfg.update(params_cfg)
    return {"type": "ia.display.view", "version": 0, "meta": {"name": "Symbol"}, "position": frac(L["sym"], L["size"]),
            "props": {"path": default, "params": dparams or {"state": 0, "command": -1, "alarm": 0}, "useDefaultViewWidth": False, "useDefaultViewHeight": False},
            "propConfig": cfg, "events": {"dom": {"onClick": POPUP}}}

def template(params, custom, cfg, children, size):
    pc = {f"params.{k}": pin() for k in params}; pc.update(cfg)
    return {"custom": custom, "params": params, "propConfig": pc, "props": {"defaultSize": {"width": size[0], "height": size[1]}},
            "root": {"type": "ia.container.coord", "version": 0, "meta": {"name": "root"}, "props": {"mode": "percent"}, "children": children}}

COMMON_TAGS = {"custom.perm": tag("PermOK"), "custom.intlk": tag("Intlk"), "custom.fault": tag("Fault"), "custom.mode": tag("Mode")}

def autovalve():
    """Discrete valve template mapped to the plant's discrete-valve UDT (members: Auto, Auto_Perm, CMD, Cycle_Count, Description,
    Feedback_Enabled, HMI_Auto, HMI_CMD, HMI_Lockout, HMI_Manual, HMI_Off, Interlock, InterlockList, LockedOut, Man_Perm, Manual,
    Name, Off, Permissive, REQ, Reset_Count, ZSC, ZSO)."""
    L = LAYOUT["AutoValve"]
    params = {"tagPath": "[default]PID_Demo/XV101", "symbol": "Valve_OnOff_Pneumatic", "label": "", "alarm": 0, "popupView": ""}
    custom = {"cmd": False, "zso": False, "zsc": True, "fb": True, "permMissing": False, "intlk": False, "ilist": "",
              "manual": False, "off": False, "locked": False, "name": "", "desc": "", "state": 0, "command": -1, "letter": ""}
    cfg = {"custom.cmd": tag("CMD"), "custom.zso": tag("ZSO"), "custom.zsc": tag("ZSC"), "custom.fb": tag("Feedback_Enabled"),
           "custom.permMissing": tag("Permissive"), "custom.intlk": tag("Interlock"), "custom.ilist": tag("InterlockList"),
           "custom.manual": tag("Manual"), "custom.off": tag("Off"), "custom.locked": tag("LockedOut"),
           "custom.name": tag("Name"), "custom.desc": tag("Description"),
           # both limits made = fault; no feedback -> symbol follows CMD
           "custom.state": expr("if({view.custom.zso} && {view.custom.zsc}, 3, if(!{view.custom.fb}, if({view.custom.cmd}, 1, 0), "
                                "if({view.custom.zso}, 1, if({view.custom.zsc}, 0, 2))))"),
           "custom.command": expr("if({view.custom.fb}, if({view.custom.cmd}, 1, 0), -1)"),
           "custom.letter": expr('if({view.custom.locked}, "L", if({view.custom.off}, "D", if({view.custom.manual}, "M", "")))')}
    status = 'case({view.custom.state}, 0, "CLOSED", 1, "OPEN", 2, if({view.custom.cmd}, "OPENING", "CLOSING"), 3, "FAULT", "???")'
    cls = ('if({view.custom.state} = 3, "State/Fault", "Text/Status") + '
           'if(len({view.custom.letter}) > 0 && {view.custom.state} != 3, " Mode/ManualSplitStatus", "")')
    tagname = ('if(len({view.params.label}) > 0, {view.params.label}, if(len(coalesce({view.custom.name}, "")) > 0, {view.custom.name}, '
               'substring({view.params.tagPath}, lastIndexOf({view.params.tagPath}, "/") + 1)))')
    tag_lbl = label("Tag", frac(L["tag"], L["size"]), "", "Text/TagName Text/Mod/Center Text/Mod/NoWrap",
                    {"props.text": expr(tagname), "meta.tooltip.text": expr('coalesce({view.custom.desc}, "")'),
                     "meta.tooltip.enabled": expr('len(coalesce({view.custom.desc}, "")) > 0')}, meta={"tooltip": {"enabled": False, "text": ""}})
    # single click writes HMI_CMD = NOT CMD; usable in Manual only, not Locked Out; opening blocked by P or I, closing always allowed
    click = script("\tcmd = bool(self.view.custom.cmd)\n\tsystem.tag.writeBlocking([self.view.params.tagPath + '/HMI_CMD'], [not cmd])")
    btn = {"type": "ia.input.button", "version": 0, "meta": {"name": "PB", "tooltip": {"enabled": True, "text": "Open"}},
           "position": frac(L["pb"], L["size"]), "props": {"text": "", "enabled": False, "style": {"classes": "Button/Momentary"}},
           "propConfig": {"props.enabled": expr("{view.custom.manual} && !{view.custom.locked} && !{view.custom.off} && "
                                                "({view.custom.cmd} || (!{view.custom.permMissing} && !{view.custom.intlk}))"),
                          "meta.tooltip.text": expr('if({view.custom.locked}, "Locked out", if(!{view.custom.manual}, "Manual mode required", '
                                                    'if({view.custom.cmd}, "Close", "Open")))')},
           "events": {"component": {"onActionPerformed": click}}}
    i_tip = ('"Interlock active - open blocked" + if(len(coalesce(toStr({view.custom.ilist}), "")) > 0, ": " + toStr({view.custom.ilist}), "")')
    kids = [tag_lbl,
            embed(L, 'if(indexOf({view.params.symbol}, "/") >= 0, "PID/" + {view.params.symbol}, "PID/Valves/" + {view.params.symbol})',
                  "PID/Valves/Valve_OnOff_Pneumatic", {"props.params.state": prop("view.custom.state"), "props.params.command": prop("view.custom.command"),
                                                       "props.params.alarm": prop("view.params.alarm")})] + \
           badges(L, p_vis="{view.custom.permMissing}", i_vis="{view.custom.intlk}", i_tip=i_tip) + \
           [status_group(L, status, cls, "{view.custom.letter}"), btn]
    return template(params, custom, cfg, kids, L["size"])

def controlvalve():
    L = LAYOUT["ControlValve"]
    params = {"tagPath": "[default]PID_Demo/FV101", "symbol": "Valve_Control", "label": "", "hasFeedback": True, "alarm": 0, "popupView": ""}
    custom = {"out": 0.0, "pos": 0.0, "perm": True, "intlk": False, "fault": False, "mode": 0, "state": 0, "command": -1}
    cfg = dict(COMMON_TAGS, **{"custom.out": tag("Out"), "custom.pos": tag("Pos"),
        "custom.state": expr("if({view.custom.fault}, 3, if((if({view.params.hasFeedback}, {view.custom.pos}, {view.custom.out})) > 1, 1, 0))"),
        "custom.command": expr("if({view.params.hasFeedback}, if({view.custom.out} > 1, 1, 0), -1)")})
    status = 'if({view.custom.state} = 3, "FAULT", numberFormat(if({view.params.hasFeedback}, {view.custom.pos}, {view.custom.out}), "0") + " %")'
    cls = 'if({view.custom.state} = 3, "State/Fault", "Text/Status Text/Mod/Tabular") + if({view.custom.mode} = 1 && {view.custom.state} != 3, " Mode/ManualSplitStatus", "")'
    kids = [label("Tag", frac(L["tag"], L["size"]), "", "Text/TagName Text/Mod/Center Text/Mod/NoWrap", {"props.text": expr(TAGNAME)}),
            embed(L, 'if(indexOf({view.params.symbol}, "/") >= 0, "PID/" + {view.params.symbol}, "PID/Valves/" + {view.params.symbol})',
                  "PID/Valves/Valve_Control", {"props.params.state": prop("view.custom.state"), "props.params.command": prop("view.custom.command"),
                                              "props.params.alarm": prop("view.params.alarm")})] + badges(L) + [status_group(L, status, cls)]
    return template(params, custom, cfg, kids, L["size"])

LOW_I = [s.name for s in SYMS if s.badge_i == "low"]
def motor():
    L = LAYOUT["Motor"]
    params = {"tagPath": "[default]PID_Demo/P101", "symbol": "Rotating/Pump_Centrifugal", "label": "", "hasFeedback": True, "alarm": 0, "popupView": ""}
    custom = {"cmd": False, "run": False, "perm": True, "intlk": False, "fault": False, "mode": 0, "state": 0}
    cfg = dict(COMMON_TAGS, **{"custom.cmd": tag("Cmd"), "custom.run": tag("Run"),
        "custom.state": expr("if({view.custom.fault}, 3, if(!{view.params.hasFeedback}, if({view.custom.cmd}, 1, 0), "
                             "if({view.custom.run} && {view.custom.cmd}, 1, if(!{view.custom.run} && !{view.custom.cmd}, 0, 2))))")})
    status = 'case({view.custom.state}, 0, "STOPPED", 1, "RUNNING", 2, if({view.custom.cmd}, "STARTING", "STOPPING"), 3, "FAULT", "???")'
    cls = 'case({view.custom.state}, 0, "State/Stopped", 1, "State/Running", 2, "State/Transition", 3, "State/Fault", "State/Unknown")'
    low = " || ".join(f'indexOf({{view.params.symbol}}, "{n}") >= 0' for n in LOW_I)   # 8.1 has no endsWith()
    i_y = f'if({low}, {round(L["I_low"][1] / L["size"][1], 4)}, {round(L["I"][1] / L["size"][1], 4)})'
    kids = [label("Tag", frac(L["tag"], L["size"]), "", "Text/TagName Text/Mod/Center Text/Mod/NoWrap", {"props.text": expr(TAGNAME)}),
            embed(L, '"PID/" + {view.params.symbol}', "PID/Rotating/Pump_Centrifugal",
                  {"props.params.state": prop("view.custom.state"), "props.params.alarm": prop("view.params.alarm")}, {"state": 0, "alarm": 0})] + badges(L, i_y) + \
           [status_group(L, status, cls), pb_button(L, "Stop", "Start")]
    return template(params, custom, cfg, kids, L["size"])

# =================================================================== tags
def atom(n, dt, v): return {"name": n, "tagType": "AtomicTag", "valueSource": "memory", "dataType": dt, "value": v}
UDTS = {
    # Demo stand-in with the same member names as the plant discrete-valve UDT (memory tags). Point the template at real instances instead.
    "Valve_Discrete_Demo": [atom(n, "Boolean", False) for n in ("Auto", "Auto_Perm", "CMD", "HMI_Auto", "HMI_CMD", "HMI_Lockout", "HMI_Manual",
                            "HMI_Off", "Interlock", "LockedOut", "Man_Perm", "Manual", "Off", "Permissive", "REQ", "Reset_Count", "ZSO")] +
                           [atom("ZSC", "Boolean", True), atom("Feedback_Enabled", "Boolean", True), atom("Cycle_Count", "Int4", 0),
                            atom("Description", "String", ""), atom("InterlockList", "String", ""), atom("Name", "String", "")],
    "PID_Motor":        [atom("Cmd", "Boolean", False), atom("Run", "Boolean", False), atom("PB", "Boolean", False), atom("PermOK", "Boolean", True),
                         atom("Intlk", "Boolean", False), atom("Fault", "Boolean", False), atom("Mode", "Int2", 0)],
    "PID_ControlValve": [atom("Out", "Float4", 0.0), atom("Pos", "Float4", 0.0), atom("PermOK", "Boolean", True), atom("Intlk", "Boolean", False),
                         atom("Fault", "Boolean", False), atom("Mode", "Int2", 0)],
}
DEMO = [  # name, udt, overrides, template, params
    ("XV101", "Valve_Discrete_Demo", {"Auto": True, "CMD": True, "ZSO": True, "ZSC": False, "Name": "XV-101", "Description": "N2 supply isolation"}, "AutoValve", {}),
    ("XV102", "Valve_Discrete_Demo", {"Manual": True, "Permissive": True, "Name": "XV-102"}, "AutoValve", {"symbol": "Valve_Solenoid"}),
    ("XV103", "Valve_Discrete_Demo", {"Manual": True, "CMD": True, "ZSC": False, "Name": "XV-103"}, "AutoValve", {"symbol": "Valve_MOV"}),
    ("XV104", "Valve_Discrete_Demo", {"Off": True, "Interlock": True, "InterlockList": "PSH-201 high pressure", "Name": "XV-104"}, "AutoValve", {}),
    ("XV105", "Valve_Discrete_Demo", {"LockedOut": True, "ZSO": True, "ZSC": True, "Name": "XV-105"}, "AutoValve", {"alarm": 4}),
    ("FV101", "PID_ControlValve", {"Out": 45.0, "Pos": 43.0}, "ControlValve", {}),
    ("FV102", "PID_ControlValve", {"Out": 20.0, "Pos": 20.0, "Mode": 1}, "ControlValve", {}),
    ("P101", "PID_Motor", {"Cmd": True, "Run": True}, "Motor", {}),
    ("P102", "PID_Motor", {"PermOK": False, "Intlk": True}, "Motor", {"symbol": "Rotating/Pump_PD_Rotary"}),
    ("K201", "PID_Motor", {"Cmd": True, "Run": True, "Mode": 1}, "Motor", {"symbol": "Rotating/Compressor_Diaphragm"}),
    ("K202", "PID_Motor", {"Fault": True}, "Motor", {"symbol": "Rotating/Compressor_Centrifugal", "alarm": 3}),
    ("B301", "PID_Motor", {"Cmd": True}, "Motor", {"symbol": "Rotating/Blower"}),
    ("E401", "PID_Motor", {"Cmd": True, "Run": True}, "Motor", {"symbol": "HeatTransfer/Heater_Electric"}),
]
def tags_files():
    d = os.path.join(OUT, "tags"); os.makedirs(d, exist_ok=True)
    for n, members in UDTS.items():
        json.dump({"name": n, "tagType": "UdtType", "tags": members}, open(os.path.join(d, f"{n}_UDT.json"), "w"), indent=2)
    inst = [{"name": n, "tagType": "UdtInstance", "typeId": u, "tags": [{"name": k, "tagType": "AtomicTag", "value": v} for k, v in ov.items()]}
            for n, u, ov, _, _ in DEMO]
    json.dump({"name": "PID_Demo", "tagType": "Folder", "tags": inst}, open(os.path.join(d, "PID_Demo_Instances.json"), "w"), indent=2)

# =================================================================== demo view
_n = {}
def uid(b): i = _n.get(b, 0); _n[b] = i + 1; return b if i == 0 else f"{b}_{i}"
def fx(name, kids, direction="row", classes="", wrap=True, extra=None, basis="auto"):
    p = {"direction": direction, "style": {"classes": classes, "gap": "14px", **(extra or {})}}
    if wrap: p["wrap"] = "wrap"
    return {"type": "ia.container.flex", "version": 0, "meta": {"name": uid(name)}, "position": {"basis": basis, "shrink": 0}, "props": p, "children": kids}
def ev(path, params, w, h):
    return {"type": "ia.display.view", "version": 0, "meta": {"name": uid("V")}, "position": {"basis": f"{h}px", "shrink": 0},   # column flex: basis = height
            "props": {"path": path, "params": params, "useDefaultViewWidth": False, "useDefaultViewHeight": False, "style": {"width": f"{w}px"}}}
def cap(t): return {"type": "ia.display.label", "version": 0, "meta": {"name": uid("Cap")}, "position": {"basis": "auto", "shrink": 0},
                    "props": {"text": t, "style": {"classes": "Text/Caption Text/Mod/Center"}}}
def item(path, params, w, h, caption):
    return fx("Item", [ev(path, params, w, h), cap(caption)], direction="column", wrap=False, extra={"alignItems": "center", "gap": "2px"}, basis=f"{max(w, 90)}px")
def section(title, items):
    return fx("Sec", [{"type": "ia.display.label", "version": 0, "meta": {"name": uid("T")}, "position": {"basis": "28px", "shrink": 0},
                       "props": {"text": title, "style": {"classes": "Text/Header"}}}, fx("Grid", items)], direction="column", classes="Container/Panel", wrap=False)
def demo_view():
    t_items = []
    for n, u, ov, tpl, p in DEMO:
        w, h = LAYOUT[tpl]["size"]
        t_items.append(item(f"PID/Templates/{tpl}", {"tagPath": f"[default]PID_Demo/{n}", **p}, w * 1.5, h * 1.5, n))
    s_items = []
    for s in SYMS:
        for st in (0, 1, 3):
            prm = {"state": st, "alarm": 0}
            if "head" in s.roles: prm["command"] = -1
            s_items.append(item(f"PID/{s.cat}/{s.name}", prm, 72, 72, f"{s.name} [{st}]"))
    return {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 1920, "height": 1080}},
            "root": {"type": "ia.container.flex", "version": 0, "meta": {"name": "root"},
                     "props": {"direction": "column", "style": {"classes": "Container/Screen", "gap": "10px", "padding": "10px", "overflowY": "auto"}},
                     "children": [section("Templates (bound to [default]PID_Demo, shown at 1.5x)", t_items), section("Active symbols: state 0 / 1 / 3", s_items)]}}

# =================================================================== static SVG library (note 2)
def static_symbols():
    v2 = os.path.join(HERE, "v2") if os.path.isdir(os.path.join(HERE, "v2")) else os.path.join(os.path.dirname(HERE), "pid_v2")
    sys.path.insert(0, v2)
    import symbols as v2sym
    v2sym.PALETTE["fault"] = PAL["fault"]           # standards palette
    import build as v2build
    n = 0
    for s in v2sym.SYMS:
        d = os.path.join(OUT, "symbols", s.cat); os.makedirs(d, exist_ok=True)
        art = svg(BY[s.name]) if s.name == "Compressor_Diaphragm" else v2build.svg(s)   # user's base image supersedes v2 geometry
        fname = "Pump_Vacuum_LiquidRing" if s.name == "Pump_Vacuum" else s.name        # new active Pump_Vacuum takes the plain name
        open(os.path.join(d, f"{fname}.svg"), "w").write(art); n += 1
    for s in SYMS:
        d = os.path.join(OUT, "symbols", "Active", s.cat); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, f"{s.name}.svg"), "w").write(svg(s)); n += 1
    return n

# =================================================================== package
def resource_json(files):
    ts = os.environ.get("EFC_BUILD_TIMESTAMP", "2026-10-07T00:00:00Z")   # fixed (from VERSION via build.py) so rebuilds diff cleanly in git
    return json.dumps({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": files,
                       "attributes": {"lastModification": {"actor": "efc-ignition-library", "timestamp": ts}}}, indent=2)

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    views = {f"PID/{s.cat}/{s.name}": symbol_view(s) for s in SYMS}
    views.update({"PID/Templates/AutoValve": autovalve(), "PID/Templates/ControlValve": controlvalve(),
                  "PID/Templates/Motor": motor(), "PID/_Demo": demo_view()})
    with zipfile.ZipFile(os.path.join(OUT, "PID_Symbols.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps({"title": "PID_Symbols", "description": "EFC active device templates v3 (generated). Parent: EFC_Styles",
                                               "parent": "EFC_Styles", "enabled": True, "inheritable": True}, indent=2))
        for p, v in views.items():
            z.writestr(f"{BASE}/views/{p}/view.json", json.dumps(v, indent=2))
            z.writestr(f"{BASE}/views/{p}/resource.json", resource_json(["view.json"]))
    tags_files()
    n = static_symbols()
    print(f"{len(SYMS)} active symbols, {len(views)} views, {n} SVGs")

if __name__ == "__main__":
    build()
