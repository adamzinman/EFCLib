import json, zipfile, copy
TS = "2026-10-13T00:00:00Z"
BASE = "com.inductiveautomation.perspective"
FONT = "'Noto Sans', 'Segoe UI', Arial, sans-serif"
def V(px): return f"{px/10.8:.3f}vh"
def res(files):
    return json.dumps({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": files,
        "attributes": {"lastModification": {"actor": "efc-ignition-library", "timestamp": TS}}}, indent=2)
def expr(e): return {"binding": {"type": "expr", "config": {"expression": e}}}
def tagb(member): return {"binding": {"type": "tag", "config": {"mode": "indirect", "tagPath": "{1}/" + member,
    "references": {"1": "{view.params.TagPath}"}, "fallbackDelay": 2.5}}}

# ---------------------------------------------------------------- style classes
SC = "Indicator/Analog/"
CLASSES = {
 "Card": {"backgroundColor": "#F4F4F4", "border": f"1px solid #BDBDBD", "borderRadius": V(6), "padding": f"{V(10)} {V(12)} {V(8)}", "boxSizing": "border-box", "fontFamily": FONT, "color": "#1F1F1F"},
 "CardCompact": {"backgroundColor": "#F4F4F4", "border": "1px solid #BDBDBD", "borderRadius": V(4), "padding": f"{V(4)} {V(8)} {V(5)}", "boxSizing": "border-box", "fontFamily": FONT, "color": "#1F1F1F"},
 "Track": {"backgroundColor": "#C4C4C4", "borderRadius": V(5), "overflow": "hidden", "boxShadow": "inset 0 0 0 1px rgba(0,0,0,0.18)"},
 "ZoneLL": {"backgroundColor": "#A6A6A6"},
 "ZoneL": {"backgroundColor": "#C4C4C4"},
 "ZoneNormal": {"backgroundColor": "#FFFFFF"},
 "ZoneIdeal": {"backgroundColor": "#9DB4D0"},
 "ValueBox": {"backgroundColor": "#FFFFFF", "boxShadow": "inset 0 0 0 1px #BDBDBD", "borderRadius": V(4), "padding": f"0 {V(6)}", "textAlign": "right", "fontWeight": "600", "fontVariantNumeric": "tabular-nums", "whiteSpace": "nowrap", "fontFamily": FONT},
 "Desc": {"fontSize": V(11), "color": "#5A5A5A", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "fontFamily": FONT},
 "DescTitle": {"fontSize": V(12), "fontWeight": "600", "color": "#1F1F1F", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "fontFamily": FONT},
 "Header": {"fontSize": V(10), "fontWeight": "700", "letterSpacing": "0.02em", "color": "#1F1F1F", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "textAlign": "center", "fontFamily": FONT},
 "Chip": {"fontSize": V(10), "fontWeight": "700", "letterSpacing": "0.05em", "padding": f"0 {V(7)}", "borderRadius": V(9), "lineHeight": V(14), "border": "1px solid rgba(0,0,0,0.25)", "color": "#1F1F1F", "whiteSpace": "nowrap", "fontFamily": FONT},
 "ChipBad": {"backgroundColor": "#EDEDED", "color": "#B000B0", "border": "1px dashed #B000B0"},
 "Scale": {"fontSize": V(10), "lineHeight": V(12), "color": "#4D4D4D", "fontVariantNumeric": "tabular-nums", "whiteSpace": "nowrap", "fontFamily": FONT},
}
DESC = {"Card": "Analog indicator card (options A/B/D)", "CardCompact": "Analog indicator card, compact row (option C)",
 "Track": "Rounded zone track", "ZoneLL": "Inactive LL/HH zone", "ZoneL": "Inactive L/H zone", "ZoneNormal": "Normal, off-ideal zone (white)",
 "ZoneIdeal": "Ideal operating zone (muted blue)", "ValueBox": "Live value readout box; add Alarm/<Pri>/Outline or Value/BadQuality",
 "Desc": "Secondary description text", "DescTitle": "Description used as title", "Header": "Mini column header",
 "Chip": "Alarm chip shape; add Alarm/<Pri>/Fill|Unacked or ChipBad", "ChipBad": "Bad-quality chip", "Scale": "Scale/limit labels"}

# ---------------------------------------------------------------- shared view custom props
TAGM = {"pv": "Val_PV", "eu": "Cfg_EU", "desc": "Cfg_Desc", "sdesc": "Cfg_ShortDesc", "tag": "Cfg_Tag",
        "min": "Cfg_EUMin", "max": "Cfg_EUMax", "iLo": "Cfg_IdealLo", "iHi": "Cfg_IdealHi", "q": "Sts_Quality"}
for k, a in [("ll", "Alm_LL"), ("l", "Alm_L"), ("h", "Alm_H"), ("hh", "Alm_HH")]:
    TAGM.update({k: a + "/Cfg_Lim", k + "En": a + "/Cfg_En", k + "A": a + "/Sts_Active",
                 k + "U": a + "/Sts_Unack", k + "P": a + "/Cfg_Priority"})
c = lambda k: "{view.custom." + k + "}"
def pct(k): return f"min(max(({c(k)} - {c('min')}) / {c('span')}, 0), 1) * 100"
IDEAL = f"{c('iLo')} < {c('iHi')}"
DERIVED = {
 "good": f"{c('q')} != 2",
 "span": f"max({c('max')} - {c('min')}, 0.000001)",
 "p": pct("pv"), "pLL": pct("ll"), "pL": pct("l"), "pH": pct("h"), "pHH": pct("hh"),
 "pIL": f"if({IDEAL}, {pct('iLo')}, {c('pL')})", "pIH": f"if({IDEAL}, {pct('iHi')}, {c('pL')})",
 # active limit alarm, worst first; PLC Cfg_Priority 1=Emergency 2=High 3=Medium 4=Low
 "lvl": f"if({c('hhA')}, 'HH', if({c('llA')}, 'LL', if({c('hA')}, 'H', if({c('lA')}, 'L', ''))))",
 "almUnack": f"case({c('lvl')}, 'HH', {c('hhU')}, 'LL', {c('llU')}, 'H', {c('hU')}, 'L', {c('lU')}, false)",
 "almPri": f"case({c('lvl')}, 'HH', {c('hhP')}, 'LL', {c('llP')}, 'H', {c('hP')}, 'L', {c('lP')}, 3)",
 "pri": f"case(toInt({c('almPri')}), 1, 'Critical', 2, 'High', 3, 'Medium', 4, 'Low', 'Medium')",
 "almCls": f"if({c('lvl')} = '', '', 'Alarm/' + {c('pri')} + if({c('almUnack')}, '/Unacked', '/Fill'))",
 "ptrColor": f"if({c('lvl')} = '', '#1F1F1F', case({c('pri')}, 'Critical', '#D50000', 'High', '#FF7A00', 'Medium', '#FFD200', 'Low', '#00A3E0', '#6E6E6E'))",
 "valCls": f"'Indicator/Analog/ValueBox' + if(!{c('good')}, ' Value/BadQuality', if({c('lvl')} != '', ' Alarm/' + {c('pri')} + '/Outline', if({c('q')} = 1, ' Value/Simulated', '')))",
 "valText": f"numberFormat({c('pv')}, {{view.params.Format}})",
 "chipVis": f"!{c('good')} || {c('lvl')} != ''",
 "chipCls": f"'Indicator/Analog/Chip ' + if(!{c('good')}, 'Indicator/Analog/ChipBad', {c('almCls')})",
 "zLL": f"max({c('pLL')}, 0) + '%'", "zL": f"max({c('pL')} - {c('pLL')}, 0) + '%'", "zW1": f"max({c('pIL')} - {c('pL')}, 0) + '%'",
 "zI": f"max({c('pIH')} - {c('pIL')}, 0) + '%'", "zW2": f"max({c('pH')} - {c('pIH')}, 0) + '%'", "zH": f"max({c('pHH')} - {c('pH')}, 0) + '%'",
 "zHH": f"max(100 - {c('pHH')}, 0) + '%'",
 "cLL": f"if({c('lvl')} = 'LL', {c('almCls')}, if({c('llEn')}, 'Indicator/Analog/ZoneLL', if({c('lEn')}, 'Indicator/Analog/ZoneL', 'Indicator/Analog/ZoneNormal')))",
 "cL": f"if({c('lvl')} = 'L', {c('almCls')}, if({c('lEn')}, 'Indicator/Analog/ZoneL', 'Indicator/Analog/ZoneNormal'))",
 "cH": f"if({c('lvl')} = 'H', {c('almCls')}, if({c('hEn')}, 'Indicator/Analog/ZoneL', 'Indicator/Analog/ZoneNormal'))",
 "cHH": f"if({c('lvl')} = 'HH', {c('almCls')}, if({c('hhEn')}, 'Indicator/Analog/ZoneLL', if({c('hEn')}, 'Indicator/Analog/ZoneL', 'Indicator/Analog/ZoneNormal')))",
}
CHIP_LONG = f"if(!{c('good')}, 'BAD Q', case({c('lvl')}, 'HH', 'HIHI', 'H', 'HI', 'L', 'LO', 'LL', 'LOLO', ''))"
CHIP_SHORT = f"if(!{c('good')}, 'BAD', case({c('lvl')}, 'HH', 'HH', 'H', 'HI', 'L', 'LO', 'LL', 'LL', ''))"

# ---------------------------------------------------------------- component helpers
def comp(t, name, props=None, pos=None, pc=None, children=None):
    d = {"type": t, "version": 0, "meta": {"name": name}, "position": pos or {}, "props": props or {}}
    if pc: d["propConfig"] = pc
    if children is not None: d["children"] = children
    return d
def flex(name, direction, children, basis=None, cls="", grow=0, shrink=0, extra=None, pc=None):
    props = {"direction": direction, "style": {"classes": cls}}
    if extra: props.update(extra)
    pos = {"shrink": shrink, "grow": grow}
    if basis: pos["basis"] = basis
    return comp("ia.container.flex", name, props, pos, pc, children)
def label(name, text=None, cls="", basis=None, grow=0, shrink=0, pc=None, textExpr=None, clsExpr=None, display=None):
    pc = dict(pc or {})
    if textExpr: pc["props.text"] = expr(textExpr)
    if clsExpr: pc["props.style.classes"] = expr(clsExpr)
    if display: pc["position.display"] = expr(display)
    pos = {"shrink": shrink, "grow": grow}
    if basis: pos["basis"] = basis
    return comp("ia.display.label", name, {"text": text or "", "style": {"classes": cls}}, pos, pc or None)
def spacer(name, basisExpr=None, basis="0px", grow=0):
    pc = {"position.basis": expr(basisExpr)} if basisExpr else None
    return comp("ia.container.flex", name, {"style": {"classes": ""}}, {"basis": basis, "grow": grow, "shrink": 0}, pc, [])
def pointer(name, vb, points, size, margin):
    el = {"type": "polygon", "name": "ptr", "points": points, "fill": {"paint": "#1F1F1F"},
          "stroke": {"paint": "#1F1F1F", "width": 1, "linejoin": "round"}}
    return comp("ia.shapes.svg", name, {"viewBox": vb, "elements": [el], "style": margin},
                {"basis": size, "shrink": 0, "grow": 0},
                {"props.elements[0].fill.paint": expr(c("ptrColor")), "meta.visible": expr(c("good"))})
def zones(name, direction, basis=None, grow=0, extra=None):
    kids = []
    for z, cls in [("LL", "cLL"), ("L", "cL"), ("W1", None), ("I", None), ("W2", None), ("H", "cH"), ("HH", "cHH")]:
        static = {"W1": "Indicator/Analog/ZoneNormal", "W2": "Indicator/Analog/ZoneNormal", "I": "Indicator/Analog/ZoneIdeal"}.get(z, "")
        pc = {"position.basis": expr(c("z" + z))}
        if cls: pc["props.style.classes"] = expr(c(cls))
        kids.append(comp("ia.container.flex", "Zone" + z, {"style": {"classes": static}}, {"basis": "0%", "shrink": 0, "grow": 0}, pc, []))
    return flex(name, direction, kids, basis=basis, cls="Indicator/Analog/Track", grow=grow, extra=extra)
def chip(name, textExpr, basis=None):
    return label(name, cls="Indicator/Analog/Chip", textExpr=textExpr, clsExpr=c("chipCls"), display=c("chipVis"))
def value_row(size_cls):
    return flex("ValueRow", "row", [
        label("Value", cls="Indicator/Analog/ValueBox", textExpr=c("valText"), clsExpr=c("valCls") + f" + ' {size_cls}'"),
        label("Units", cls="Text/Units", textExpr=c("eu"))], extra={"alignItems": "baseline", "style": {"classes": "", "gap": V(3)}})

def make_view(root, w, h, params, extra_custom=None):
    custom = {k: None for k in TAGM}; custom.update({k: None for k in DERIVED})
    pcfg = {}
    for k, m in TAGM.items(): pcfg["custom." + k] = tagb(m)
    for k, e in DERIVED.items(): pcfg["custom." + k] = expr(e)
    for k, e in (extra_custom or {}).items():
        custom[k] = None; pcfg["custom." + k] = expr(e)
    for p in params: pcfg["params." + p] = {"paramDirection": "input", "persistent": True}
    return {"custom": custom, "params": params, "propConfig": pcfg,
            "props": {"defaultSize": {"width": w, "height": h}}, "root": root}

# ---------------------------------------------------------------- A: Range Bar
A_params = {"TagPath": "[default]KPI/KPI_101", "LabelMode": "Both", "ShowMinMax": True, "Format": "#,##0.0"}
A_root = flex("root", "column", [
    flex("Header", "row", [
        flex("Title", "column", [
            label("Tag", cls="Text/TagName", textExpr=c("tag"), display="{view.params.LabelMode} != 'Desc'"),
            label("Desc", cls="Indicator/Analog/Desc", textExpr=c("desc"),
                  clsExpr="if({view.params.LabelMode} = 'Desc', 'Indicator/Analog/DescTitle', 'Indicator/Analog/Desc')",
                  display="{view.params.LabelMode} != 'Tag'")], grow=1, shrink=1),
        value_row("Text/Size/XL")], extra={"justify": "space-between", "alignItems": "flex-start"}),
    flex("PointerRow", "row", [spacer("PtrOffset", f"{c('p')} + '%'"),
        pointer("Pointer", "0 0 14 11", "1,1 13,1 7,10", V(14), {"classes": "", "marginLeft": V(-7)})], basis=V(11)),
    zones("Track", "row", basis=V(10)),
    flex("Footer", "row", [
        label("Min", cls="Indicator/Analog/Scale", grow=1, textExpr="if({view.params.ShowMinMax}, numberFormat({view.custom.min}, '#,##0.##'), '')"),
        chip("Chip", CHIP_LONG),
        label("Max", cls="Indicator/Analog/Scale Text/Mod/Right", grow=1, textExpr="if({view.params.ShowMinMax}, numberFormat({view.custom.max}, '#,##0.##'), '')")],
        basis=V(16), extra={"alignItems": "center"}),
], cls="Indicator/Analog/Card", extra={"style": {"classes": "Indicator/Analog/Card", "gap": V(6)}})

# ---------------------------------------------------------------- B: Pointer Scale
B_params = {"TagPath": "[default]KPI/KPI_101", "ShowLimitType": True, "ShowLimitValue": True, "Format": "#,##0.0"}
def lim(k, typ, en):
    return (f"if({c(en)}, trim(if({{view.params.ShowLimitType}}, '{typ}', '') + ' ' + "
            f"if({{view.params.ShowLimitValue}}, numberFormat({c(k)}, '#,##0.##'), '')), '')")
LBLH = 12
limit_col = flex("Limits", "column-reverse", [
    spacer("G1", f"'calc(' + {c('pLL')} + '% - {LBLH/2/10.8:.3f}vh)'"),
    label("LL", cls="Indicator/Analog/Scale Text/Mod/Right", basis=V(LBLH), textExpr=lim("ll", "LL", "llEn")),
    spacer("G2", f"'calc(' + max({c('pL')} - {c('pLL')}, 0) + '% - {LBLH/10.8:.3f}vh)'"),
    label("L", cls="Indicator/Analog/Scale Text/Mod/Right", basis=V(LBLH), textExpr=lim("l", "L", "lEn")),
    spacer("G3", f"'calc(' + max({c('pH')} - {c('pL')}, 0) + '% - {LBLH/10.8:.3f}vh)'"),
    label("H", cls="Indicator/Analog/Scale Text/Mod/Right", basis=V(LBLH), textExpr=lim("h", "H", "hEn")),
    spacer("G4", f"'calc(' + max({c('pHH')} - {c('pH')}, 0) + '% - {LBLH/10.8:.3f}vh)'"),
    label("HH", cls="Indicator/Analog/Scale Text/Mod/Right", basis=V(LBLH), textExpr=lim("hh", "HH", "hhEn")),
], basis=V(36), pc={"position.basis": expr(f"if({{view.params.ShowLimitType}} && {{view.params.ShowLimitValue}}, '{V(36)}', if({{view.params.ShowLimitType}}, '{V(18)}', '{V(22)}'))"),
                       "position.display": expr("{view.params.ShowLimitType} || {view.params.ShowLimitValue}")})
B_root = flex("root", "column", [
    label("Tag", cls="Text/TagName Text/Mod/Center", textExpr=c("tag")),
    label("Desc", cls="Indicator/Analog/Desc Text/Mod/Center", textExpr=c("desc")),
    flex("Scale", "row", [limit_col,
        zones("Track", "column-reverse", extra={"style": {"classes": "Indicator/Analog/Track"}}),
        flex("PtrCol", "column-reverse", [spacer("PtrOffset", f"{c('p')} + '%'"),
            pointer("Pointer", "0 0 14 14", "1,7 13,1 13,13", V(14), {"classes": "", "marginBottom": V(-7)})], basis=V(16))],
        basis=V(206), extra={"style": {"classes": "", "gap": V(4), "padding": f"{V(3)} 0"}}),
    value_row("Text/Size/L"),
    flex("ChipRow", "row", [chip("Chip", CHIP_LONG)], basis=V(16), extra={"justify": "center", "alignItems": "center"}),
], extra={"alignItems": "center", "style": {"classes": "Indicator/Analog/Card", "gap": V(6)}})
# track width for vertical bar
B_root["children"][2]["children"][1]["position"]["basis"] = V(12)

# ---------------------------------------------------------------- C: Compact Row
C_params = {"TagPath": "[default]KPI/KPI_101", "Header": "Tag", "Format": "#,##0.0"}
HEAD = "if({view.params.Header} = 'Desc', coalesce({view.custom.sdesc}, {view.custom.desc}), {view.custom.tag})"
C_root = flex("root", "column", [
    flex("Top", "row", [
        label("Header", cls="Text/TagName", textExpr=HEAD, shrink=1),
        chip("Chip", CHIP_SHORT),
        spacer("Fill", grow=1),
        value_row("Text/Size/M")], basis=V(20), extra={"alignItems": "center", "style": {"classes": "", "gap": V(6)}}),
    flex("PointerRow", "row", [spacer("PtrOffset", f"{c('p')} + '%'"),
        pointer("Pointer", "0 0 10 8", "1,1 9,1 5,7", V(10), {"classes": "", "marginLeft": V(-5)})], basis=V(8)),
    zones("Track", "row", basis=V(6)),
], extra={"justify": "space-between", "style": {"classes": "Indicator/Analog/CardCompact", "gap": V(1)}})

# ---------------------------------------------------------------- D: Mini Column
D_params = {"TagPath": "[default]KPI/KPI_101", "Header": "Tag", "Format": "#,##0.0"}
D_root = flex("root", "column", [
    label("Header", cls="Indicator/Analog/Header", textExpr=HEAD, basis=V(14)),
    label("Value", cls="Indicator/Analog/ValueBox Text/Size/M", textExpr=c("valText"), clsExpr=c("valCls") + " + ' Text/Size/M Text/Mod/Center'"),
    label("Units", cls="Text/Units Text/Mod/Center", textExpr=c("eu")),
    flex("Bar", "row", [
        zones("Track", "column-reverse"),
        flex("PtrCol", "column-reverse", [spacer("PtrOffset", f"{c('p')} + '%'"),
            pointer("Pointer", "0 0 10 10", "1,5 9,1 9,9", V(10), {"classes": "", "marginBottom": V(-5)})], basis=V(11))],
        basis=V(108), extra={"style": {"classes": "", "gap": V(2)}}),
    flex("ChipRow", "row", [chip("Chip", CHIP_SHORT)], basis=V(14), extra={"justify": "center", "alignItems": "center"}),
], extra={"alignItems": "center", "style": {"classes": "Indicator/Analog/Card", "gap": V(4), "padding": f"{V(6)} {V(4)}"}})
D_root["children"][3]["children"][0]["position"]["basis"] = V(8)

VIEWS = {
 "A_RangeBar": make_view(A_root, 256, 120, A_params),
 "B_PointerScale": make_view(B_root, 128, 330, B_params),
 "C_CompactRow": make_view(C_root, 200, 46, C_params),
 "D_MiniColumn": make_view(D_root, 64, 200, D_params),
}

# ---------------------------------------------------------------- examples view
def emb(name, path, w, h, params):
    return comp("ia.display.view", name, {"path": "EFC/AnalogIndicator/" + path, "params": params, "useDefaultViewWidth": False, "useDefaultViewHeight": False},
                {"basis": f"{w}px", "shrink": 0, "grow": 0}) | {"position": {"basis": f"{w}px", "shrink": 0, "grow": 0, "height": h}}
tp = "[default]KPI/KPI_101"
ex_root = flex("root", "row", [
    flex("A", "column", [comp("ia.display.view", "A1", {"path": "EFC/AnalogIndicator/A_RangeBar", "params": {"TagPath": tp, "LabelMode": "Both", "ShowMinMax": True, "Format": "#,##0.0"}}, {"basis": "120px", "shrink": 0})], basis="256px"),
    flex("B", "column", [comp("ia.display.view", "B1", {"path": "EFC/AnalogIndicator/B_PointerScale", "params": {"TagPath": tp, "ShowLimitType": True, "ShowLimitValue": True, "Format": "#,##0.0"}}, {"basis": "330px", "shrink": 0})], basis="128px"),
    flex("C", "column", [comp("ia.display.view", f"C{i}", {"path": "EFC/AnalogIndicator/C_CompactRow", "params": {"TagPath": tp, "Header": hdr, "Format": "#,##0.0"}}, {"basis": "46px", "shrink": 0}) for i, hdr in [(1, "Tag"), (2, "Desc")]], basis="200px", extra={"style": {"classes": "", "gap": "4px"}}),
    flex("D", "row", [comp("ia.display.view", f"D{i}", {"path": "EFC/AnalogIndicator/D_MiniColumn", "params": {"TagPath": tp, "Header": hdr, "Format": "#,##0.0"}}, {"basis": "64px", "shrink": 0}) for i, hdr in [(1, "Tag"), (2, "Desc")]], basis="134px", extra={"style": {"classes": "", "gap": "6px"}, "alignItems": "flex-start"}),
], extra={"alignItems": "flex-start", "style": {"classes": "Container/Screen", "gap": "24px", "padding": "24px"}})
EXAMPLES = {"custom": {}, "params": {}, "props": {"defaultSize": {"width": 900, "height": 420}}, "root": ex_root}

# ---------------------------------------------------------------- write
with zipfile.ZipFile("build/EFC_AnalogIndicators.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("project.json", json.dumps({"title": "EFC_AnalogIndicators", "description": "Analog indicator templates A-D + Indicator/Analog style classes. Merge into EFC_Styles / EFC_ProcessValues via Designer File > Import.",
        "parent": "EFC_Styles", "enabled": True, "inheritable": True}, indent=2))
    for k, st in CLASSES.items():
        d = f"{BASE}/style-classes/{SC}{k}"
        z.writestr(f"{d}/style.json", json.dumps({"base": {"style": st}, "variants": []}, indent=2))
        z.writestr(f"{d}/resource.json", res(["style.json"]))
    for name, v in list(VIEWS.items()) + [("_Examples", EXAMPLES)]:
        d = f"{BASE}/views/EFC/AnalogIndicator/{name}"
        z.writestr(f"{d}/view.json", json.dumps(v, indent=2))
        z.writestr(f"{d}/resource.json", res(["view.json"]))
print("ok")
