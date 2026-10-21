"""Wrapper templates + catalog views for the P&ID library. All text uses EFC_Styles classes."""

def expr(e): return {"binding": {"type": "expr", "config": {"expression": e}}}
def prop(p): return {"binding": {"type": "property", "config": {"path": p}}}
def tag(member): return {"binding": {"type": "tag", "config": {"mode": "indirect", "fallbackDelay": 2.5,
                         "references": {"0": "{view.params.tagPath}"}, "tagPath": "{0}/" + member}}}
def pin(): return {"paramDirection": "input", "persistent": True}
def pos(x, y, w, h): return {"x": x, "y": y, "width": w, "height": h}

def label(name, p, text="", classes="", cfg=None, meta=None):
    c = {"type": "ia.display.label", "version": 0, "meta": {"name": name, **(meta or {})}, "position": p,
         "props": {"text": text, "style": {"classes": classes}}}
    if cfg: c["propConfig"] = cfg
    return c

def embed(name, p, path, params, cfg=None, events=None):
    c = {"type": "ia.display.view", "version": 0, "meta": {"name": name}, "position": p,
         "props": {"path": path, "params": params, "useDefaultViewWidth": False, "useDefaultViewHeight": False}}
    if cfg: c["propConfig"] = cfg
    if events: c["events"] = events
    return c

def script(code): return {"type": "script", "scope": "G", "config": {"script": code}}

def view(params, children, size, custom=None, cfg=None):
    pc = {f"params.{k}": pin() for k in params}
    pc.update(cfg or {})
    return {"custom": custom or {}, "params": params, "propConfig": pc,
            "props": {"defaultSize": {"width": size[0], "height": size[1]}},
            "root": {"type": "ia.container.coord", "version": 0, "meta": {"name": "root"},
                     "props": {"mode": "percent"}, "children": children}}

# -------- shared expressions
TAGNAME = ('if(len({view.params.label}) > 0, {view.params.label}, '
           'substring({view.params.tagPath}, lastIndexOf({view.params.tagPath}, "/") + 1))')
FMT = ('if({view.params.good}, numberFormat({view.params.value}, case({view.params.decimals}, 0, "#,##0", 1, "#,##0.0", '
       '2, "#,##0.00", "#,##0.000")), "???")')
VALCLS = ('if({view.params.good}, "Container/ValueBox Text/Value Text/Mod/Right Text/Mod/NoWrap", '
          '"Container/ValueBox Text/Value Text/Mod/Right Text/Mod/NoWrap Value/BadQuality") + '
          'case({view.params.alarm}, 1, " Alarm/Low/Outline", 2, " Alarm/Medium/Outline", 3, " Alarm/High/Outline", '
          '4, " Alarm/Critical/Outline", "")')
POPUP = script("\tp = self.view.params\n\tif p.popupView:\n"
               "\t\tsystem.perspective.openPopup('pid_' + p.tagPath, p.popupView, params={'tagPath': p.tagPath}, title=p.label or p.tagPath)")
CLICK_CLS = 'if(len({view.params.popupView}) > 0, "Util/Pointer", "")'
VALVE_PATH = 'if(indexOf({view.params.symbol}, "/") >= 0, "PID/" + {view.params.symbol}, "PID/Valves/" + {view.params.symbol})'
TAG_CLS = "Text/TagName Text/Mod/Center Text/Mod/Ellipsis"

# =============================================================== Equipment (pumps, motors, fans, heaters ...)
def equipment():
    params = {"tagPath": "", "label": "P-101", "symbol": "Rotating/Pump_Centrifugal", "state": 0, "alarm": 0,
              "mode": 0, "statusText": "", "popupView": ""}
    status = ('if(len({view.params.statusText}) > 0, {view.params.statusText}, case({view.params.state}, 0, "STOPPED", '
              '1, "RUNNING", 2, "STARTING", 3, "FAULT", "UNKNOWN"))')
    st_cls = 'case({view.params.state}, 0, "State/Stopped", 1, "State/Running", 2, "State/Transition", 3, "State/Fault", "State/Unknown")'
    kids = [
        label("Tag", pos(0, 0, 1, 0.16), "P-101", TAG_CLS, {"props.text": expr(TAGNAME)}),
        embed("Symbol", pos(0.14, 0.17, 0.72, 0.6), "PID/Rotating/Pump_Centrifugal", {"state": 0, "alarm": 0},
              {"props.path": expr('"PID/" + {view.params.symbol}'), "props.params.state": prop("view.params.state"),
               "props.params.alarm": prop("view.params.alarm"), "props.style.classes": expr(CLICK_CLS)},
              {"dom": {"onClick": POPUP}}),
        label("Status", pos(0.06, 0.8, 0.62, 0.17), "STOPPED", "State/Stopped",
              {"props.text": expr(status), "props.style.classes": expr(st_cls)}),
        label("Mode", pos(0.71, 0.8, 0.27, 0.17), "MAN", "Mode/Manual Text/Size/XXS",
              {"props.text": expr('case({view.params.mode}, 1, "MAN", 2, "LOC", 3, "SIM", "")'),
               "props.style.classes": expr('case({view.params.mode}, 1, "Mode/Manual", 2, "Mode/Local", 3, "Mode/Simulated", "") + " Text/Size/XXS"'),
               "meta.visible": expr("{view.params.mode} >= 1")}),
    ]
    return view(params, kids, (110, 110))

# =============================================================== Valve (param driven, any valve symbol)
def _valve_kids(state_src, cmd_src, perm_src, intlk_src, status_expr):
    return [
        label("Tag", pos(0, 0, 1, 0.2), "XV-101", TAG_CLS, {"props.text": expr(TAGNAME)}),
        embed("Symbol", pos(0.309, 0.19, 0.382, 0.5), "PID/Valves/Valve_OnOff_Pneumatic", {"state": 0, "command": -1, "alarm": 0},
              {"props.path": expr(VALVE_PATH), "props.params.state": prop(state_src),
               "props.params.command": prop(cmd_src), "props.params.alarm": prop("view.params.alarm")}),
        label("P", pos(0.72, 0.3, 0.12, 0.22), "P", "Indicator/Permissive Text/Mod/Center", {"meta.visible": expr(f"!{{{perm_src}}}")},
              meta={"tooltip": {"enabled": True, "text": "Permissive missing - opening blocked"}}),
        label("I", pos(0.84, 0.3, 0.12, 0.22), "I", "Indicator/Interlock Text/Mod/Center", {"meta.visible": expr(f"{{{intlk_src}}}")},
              meta={"tooltip": {"enabled": True, "text": "Interlock active - opening blocked"}}),
        label("Status", pos(0.24, 0.72, 0.62, 0.24), "CLOSED", "Text/Status Text/Mod/Center",
              {"props.text": expr(status_expr),
               "props.style.classes": expr(f'if({{{state_src}}} = 3, "Text/Status Text/Color/Fault Text/Mod/Center", "Text/Status Text/Mod/Center")')}),
    ]

def valve():
    params = {"tagPath": "", "label": "XV-101", "symbol": "Valve_OnOff_Pneumatic", "state": 0, "command": -1,
              "alarm": 0, "permOK": True, "intlk": False}
    status = ('case({view.params.state}, 0, "CLOSED", 1, "OPEN", 2, if({view.params.command} = 1, "OPENING", '
              'if({view.params.command} = 0, "CLOSING", "TRAVEL")), 3, "FAULT", "???")')
    return view(params, _valve_kids("view.params.state", "view.params.command", "view.params.permOK", "view.params.intlk", status), (110, 84))

# =============================================================== AutoValve (PID_AutoValve UDT, v1-compatible params)
def autovalve():
    params = {"tagPath": "[default]Area1/XV101", "symbol": "Valve_OnOff_Pneumatic", "label": "", "hasFeedback": True, "alarm": 0}
    custom = {"cmd": False, "zso": False, "zsc": False, "perm": True, "intlk": False, "fault": False, "state": 0, "command": -1, "status": "CLOSED"}
    cfg = {"custom.cmd": tag("Cmd"), "custom.zso": tag("ZSO"), "custom.zsc": tag("ZSC"), "custom.perm": tag("PermOK"),
           "custom.intlk": tag("Intlk"), "custom.fault": tag("Fault"),
           "custom.state": expr("if({view.custom.fault} || ({view.custom.zso} && {view.custom.zsc}), 3, "
                                "if(!{view.params.hasFeedback}, if({view.custom.cmd}, 1, 0), "
                                "if({view.custom.zso}, 1, if({view.custom.zsc}, 0, 2))))"),
           "custom.command": expr("if({view.params.hasFeedback}, if({view.custom.cmd}, 1, 0), -1)"),
           "custom.status": expr('case({view.custom.state}, 0, "CLOSED", 1, "OPEN", 2, if({view.custom.cmd}, "OPENING", "CLOSING"), 3, "FAULT", "???")')}
    kids = _valve_kids("view.custom.state", "view.custom.command", "view.custom.perm", "view.custom.intlk", "{view.custom.status}")
    kids[-1]["position"] = pos(0.26, 0.72, 0.6, 0.24)
    press = script("\tif self.props.enabled:\n\t\tsystem.tag.writeBlocking([self.view.params.tagPath + '/PB'], [True])")
    release = script("\tsystem.tag.writeBlocking([self.view.params.tagPath + '/PB'], [False])")
    kids.append({"type": "ia.input.button", "version": 0,
                 "meta": {"name": "PB", "tooltip": {"enabled": True, "text": "Open"}},
                 "position": pos(0.145, 0.76, 0.091, 0.119),
                 "props": {"text": "", "enabled": True, "style": {"classes": "Button/Momentary"}},
                 "propConfig": {"props.enabled": expr("{view.custom.cmd} || ({view.custom.perm} && !{view.custom.intlk})"),
                                "meta.tooltip.text": expr('if({view.custom.cmd}, "Close", "Open")')},
                 "events": {"dom": {"onMouseDown": press, "onTouchStart": press,
                                    "onMouseUp": release, "onTouchEnd": release, "onMouseLeave": release}}})
    return view(params, kids, (110, 84), custom, cfg)

# =============================================================== Instrument (bubble + live value)
def instrument():
    params = {"tagPath": "", "bubble": "Instruments/HMI", "letters": "FI", "number": "101", "value": 0.0, "units": "",
              "decimals": 1, "good": True, "alarm": 0, "popupView": ""}
    kids = [
        embed("Bubble", pos(0, 0, 0.373, 1), "PID/Instruments/HMI", {"letters": "FI", "number": "101", "alarm": 0},
              {"props.path": expr('"PID/" + {view.params.bubble}'), "props.params.letters": prop("view.params.letters"),
               "props.params.number": prop("view.params.number"), "props.params.alarm": prop("view.params.alarm"),
               "props.style.classes": expr(CLICK_CLS)}, {"dom": {"onClick": POPUP}}),
        label("Value", pos(0.4, 0.22, 0.42, 0.56), "0.0", "Container/ValueBox Text/Value Text/Mod/Right",
              {"props.text": expr(FMT), "props.style.classes": expr(VALCLS)}),
        label("Units", pos(0.83, 0.22, 0.17, 0.56), "", "Text/Units Text/Mod/NoWrap", {"props.text": prop("view.params.units")}),
    ]
    return view(params, kids, (150, 56))

# =============================================================== Tank (vessel + level value)
def tank():
    params = {"tagPath": "", "label": "TK-101", "symbol": "Vessels/Tank_ConeRoof", "level": 50, "value": 50.0, "units": "%",
              "decimals": 1, "good": True, "alarm": 0, "state": 0, "popupView": ""}
    kids = [
        label("Tag", pos(0, 0, 1, 0.1), "TK-101", TAG_CLS, {"props.text": expr(TAGNAME)}),
        embed("Symbol", pos(0.08, 0.11, 0.84, 0.71), "PID/Vessels/Tank_ConeRoof", {"level": 50, "alarm": 0, "state": 0},
              {"props.path": expr('"PID/" + {view.params.symbol}'), "props.params.level": prop("view.params.level"),
               "props.params.alarm": prop("view.params.alarm"), "props.params.state": prop("view.params.state"),
               "props.style.classes": expr(CLICK_CLS)}, {"dom": {"onClick": POPUP}}),
        label("Value", pos(0.08, 0.84, 0.56, 0.13), "50.0", "Container/ValueBox Text/Value Text/Mod/Right",
              {"props.text": expr(FMT), "props.style.classes": expr(VALCLS)}),
        label("Units", pos(0.67, 0.84, 0.33, 0.13), "%", "Text/Units Text/Mod/NoWrap", {"props.text": prop("view.params.units")}),
    ]
    return view(params, kids, (110, 170))

# =============================================================== Catalog
_n = {}
def uid(b):
    i = _n.get(b, 0); _n[b] = i + 1
    return b if i == 0 else f"{b}_{i}"

def flex(name, children, direction="row", classes="", basis="auto", wrap=True, extra=None):
    props = {"direction": direction, "style": {"classes": classes, "gap": "8px", **(extra or {})}}
    if wrap: props["wrap"] = "wrap"
    return {"type": "ia.container.flex", "version": 0, "meta": {"name": uid(name)}, "position": {"basis": basis, "shrink": 0},
            "props": props, "children": children}

def cat_item(path, params, caption, h=64, w=118):
    return flex("Item", [
        {"type": "ia.display.view", "version": 0, "meta": {"name": "View"}, "position": {"basis": f"{h}px", "shrink": 0},
         "props": {"path": path, "params": params, "useDefaultViewWidth": False, "useDefaultViewHeight": False}},
        {"type": "ia.display.label", "version": 0, "meta": {"name": "Name"}, "position": {"basis": "28px", "shrink": 0},
         "props": {"text": caption, "style": {"classes": "Text/Caption Text/Mod/Center Text/Mod/Wrap"}}},
    ], direction="column", basis=f"{w}px", wrap=False, extra={"alignItems": "center", "gap": "2px"})

def section(title, items):
    return flex("Sec", [{"type": "ia.display.label", "version": 0, "meta": {"name": "Title"}, "position": {"basis": "28px", "shrink": 0},
                         "props": {"text": title, "style": {"classes": "Text/Header"}}},
                        flex("Grid", items)], direction="column", classes="Container/Panel", wrap=False)

def catalog(syms, cats):
    secs = [{"type": "ia.display.label", "version": 0, "meta": {"name": "Title"}, "position": {"basis": "44px", "shrink": 0},
             "props": {"text": f"P&ID Symbol Library v2 - {len(syms)} symbols", "style": {"classes": "Text/Title Container/Header"}}}]
    demo = [cat_item("PID/Rotating/Pump_Centrifugal", {"state": s, "alarm": 0}, f"state = {s}") for s in range(4)]
    demo += [cat_item("PID/Rotating/Pump_Centrifugal", {"state": 1, "alarm": a}, f"alarm = {a}") for a in range(1, 5)]
    demo += [cat_item("PID/Valves/Valve_Control", {"state": 0, "command": 1, "alarm": 0}, "command 1 / state 0"),
             cat_item("PID/Vessels/Tank_ConeRoof", {"level": 25, "alarm": 0, "state": 0}, "level = 25", h=84),
             cat_item("PID/Vessels/Tank_ConeRoof", {"level": 85, "alarm": 3, "state": 0}, "level 85, alarm 3", h=84)]
    secs.append(section("Parameter demo", demo))
    for c in cats:
        items = []
        for s in syms:
            if s.cat != c: continue
            ps = {"state": 1 if c == "Rotating" else 0, "alarm": 0, "command": -1, "level": 50}
            items.append(cat_item(f"PID/{s.cat}/{s.name}", ps, s.name, h=84 if s.vb[1] > s.vb[0] else 64))
        secs.append(section(c, items))
    return {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 1920, "height": 1080}},
            "root": {"type": "ia.container.flex", "version": 0, "meta": {"name": "root"},
                     "props": {"direction": "column", "style": {"classes": "Container/Screen", "gap": "10px", "padding": "10px", "overflowY": "auto"}},
                     "children": secs}}

def demo_templates():
    def t(path, params, w, h, cap):
        return cat_item(f"PID/Templates/{path}", params, cap, h=h, w=w)
    items = [
        t("Equipment", {"label": "P-101", "symbol": "Rotating/Pump_Centrifugal", "state": 1, "alarm": 0, "mode": 0}, 110, 110, "Equipment running"),
        t("Equipment", {"label": "P-102", "symbol": "Rotating/Pump_Centrifugal", "state": 3, "alarm": 4, "mode": 1}, 110, 110, "Fault + manual"),
        t("Equipment", {"label": "K-201", "symbol": "Rotating/Compressor_Centrifugal", "state": 0, "alarm": 0, "mode": 0}, 110, 110, "Compressor"),
        t("Equipment", {"label": "E-301", "symbol": "HeatTransfer/Heater_Electric", "state": 1, "alarm": 2, "mode": 2, "statusText": "ON"}, 110, 110, "Heater, local"),
        t("Valve", {"label": "XV-101", "symbol": "Valve_OnOff_Pneumatic", "state": 1, "command": 1}, 110, 84, "Valve open"),
        t("Valve", {"label": "XV-102", "symbol": "Valve_Ball_Piston", "state": 2, "command": 0, "permOK": False}, 110, 84, "Closing, no permissive"),
        t("Valve", {"label": "FV-103", "symbol": "Valve_Control", "state": 0, "command": -1, "intlk": True}, 110, 84, "Interlocked"),
        t("Instrument", {"bubble": "Instruments/HMI", "letters": "FI", "number": "101", "value": 123.45, "units": "SCFM", "decimals": 1}, 150, 56, "Instrument"),
        t("Instrument", {"bubble": "Instruments/PLC", "letters": "PIC", "number": "202", "value": 87.2, "units": "psig", "alarm": 3}, 150, 56, "High alarm"),
        t("Instrument", {"bubble": "Instruments/Instrument_Field", "letters": "TT", "number": "305", "value": 0, "units": "°F", "good": False}, 150, 56, "Bad quality"),
        t("Tank", {"label": "TK-101", "symbol": "Vessels/Tank_ConeRoof", "level": 62, "value": 62.0}, 110, 170, "Tank"),
        t("Tank", {"label": "CT-1", "symbol": "Vessels/Tank_Cryogenic", "level": 18, "value": 1820, "units": "gal", "decimals": 0, "alarm": 2}, 110, 170, "Cryo tank, low alarm"),
    ]
    root = flex("root", [section("Wrapper templates", items)], direction="column", classes="Container/Screen", wrap=False, extra={"padding": "10px"})
    root["meta"]["name"] = "root"
    return {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 1920, "height": 1080}}, "root": root}

def all_views(syms):
    from symbols import CATEGORIES
    return {"PID/Templates/Equipment": equipment(), "PID/Templates/Valve": valve(), "PID/Templates/AutoValve": autovalve(),
            "PID/Templates/Instrument": instrument(), "PID/Templates/Tank": tank(),
            "PID/_Catalog": catalog(syms, CATEGORIES), "PID/_Demo_Templates": demo_templates()}
