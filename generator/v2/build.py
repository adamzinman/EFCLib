"""
Build the EFC P&ID symbol library (v2) for Ignition Perspective 8.1.
  python3 build.py   ->  dist/PID_Symbols.zip, dist/svg/<Category>/<Name>.svg, dist/preview.html, dist/symbol_index.md
"""
import json, os, re, zipfile, datetime, shutil, html
from symbols import SYMS, PALETTE as PAL, CATEGORIES, BUBBLES, W_OUTLINE, W_ALARM, W_DETAIL, W_PIPE
import templates

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist")
PROJECT = "PID_Symbols"
BASE = "com.inductiveautomation.perspective"
DEFAULTS = {"state": 0, "command": -1, "alarm": 0, "level": 50}

ALARM_EXPR = ('case({view.params.alarm}, 1, "%s", 2, "%s", 3, "%s", 4, "%s", "%s")'
              % (PAL["alarm"][1], PAL["alarm"][2], PAL["alarm"][3], PAL["alarm"][4], PAL["outline"]))
BODY_EXPR = ('case({view.params.state}, 0, "%s", 1, "%s", 2, "%s", 3, "%s", "%s")'
             % (PAL["stopped"], PAL["running"], PAL["transition"], PAL["fault"], PAL["transition"]))
HEAD_EXPR = ('if({view.params.command} < 0, {view.custom.body}, if({view.params.command} = 1, "%s", "%s"))'
             % (PAL["running"], PAL["stopped"]))
SHELL_EXPR = 'if({view.params.state} = 3, "%s", "%s")' % (PAL["fault"], PAL["shell"])

def r3(x): return round(x, 3)

def state_color(st): return {0: PAL["stopped"], 1: PAL["running"], 2: PAL["transition"], 3: PAL["fault"]}.get(st, PAL["transition"])

def colors(sym, p):
    body = state_color(p["state"])
    head = body if p["command"] < 0 else (PAL["running"] if p["command"] == 1 else PAL["stopped"])
    shell = PAL["fault"] if p["state"] == 3 else PAL["shell"]
    line = PAL["alarm"].get(p["alarm"], PAL["outline"])
    lw = (W_ALARM if p["alarm"] > 0 else W_OUTLINE) * sym.k
    return dict(body=body, head=head, shell=shell, line=line, lw=lw)

ALARM_ROLES = {"body", "head", "shell", "face", "outline"}
FILL_ROLE = {"body": "body", "head": "head", "shell": "shell"}

def resolve(e, sym, c, p):
    """Return (fill, stroke, width, dash) for an element under params p."""
    k, a = sym.k, e.a
    dash = " ".join(str(r3(float(v) * k)) for v in a["dash"].split()) if "dash" in a else None
    if e.role in ALARM_ROLES:
        fill = {"body": c["body"], "head": c["head"], "shell": c["shell"], "face": PAL["face"], "outline": "none"}[e.role]
        return fill, c["line"], c["lw"], dash
    if e.role == "plain":  return PAL["plain"], PAL["detail"], a.get("width", W_DETAIL) * k, dash
    if e.role == "detail": return "none", PAL["detail"], a.get("width", W_DETAIL) * k, dash
    if e.role == "dark":   return PAL["dark"], "none", 0, None
    if e.role == "pipe":   return "none", PAL[a.get("color", "pipe")], a.get("width", W_PIPE) * k, dash
    if e.role == "level":  return PAL["level"], "none", 0, None
    raise ValueError(e.role)

def geom(e, sym, p):
    a = e.a
    if e.kind == "path":   return {"d": a["d"]}
    if e.kind == "circle": return {"cx": a["cx"], "cy": a["cy"], "r": a["r"]}
    g = {"x": a["x"], "y": a["y"], "width": a["w"], "height": a["h"]}
    if a.get("rx"): g["rx"] = a["rx"]; g["ry"] = a["rx"]
    if e.role == "level":
        f = max(0, min(100, p["level"])) / 100.0
        g["y"] = r3(a["y"] + a["h"] * (1 - f)); g["height"] = r3(a["h"] * f)
    return g

# ------------------------------------------------------------------ SVG export
def svg(sym, p=None, px=None):
    p = dict(DEFAULTS, **(p or {}))
    c = colors(sym, p)
    w, h = sym.size
    if px: w, h = px, round(px * sym.vb[1] / sym.vb[0])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sym.vb[0]} {sym.vb[1]}" width="{w}" height="{h}">']
    for i, e in enumerate(sym.elems):
        fill, stroke, sw, dash = resolve(e, sym, c, p)
        attrs = {"id": f"{e.role}{i}", **geom(e, sym, p), "fill": fill, "stroke": stroke}
        if stroke != "none": attrs["stroke-width"] = r3(sw)
        if dash: attrs["stroke-dasharray"] = dash
        tag = e.kind
        out.append(f'<{tag} ' + " ".join(f'{k}="{v}"' for k, v in attrs.items()) + "/>")
    out.append("</svg>")
    return "\n".join(out)

# ------------------------------------------------------------------ Perspective view
def expr(e): return {"binding": {"type": "expr", "config": {"expression": e}}}
def prop(path): return {"binding": {"type": "property", "config": {"path": path}}}

def sym_params(sym):
    roles = sym.roles
    ps = {}
    if roles & {"body", "head", "shell"}: ps["state"] = 0
    if sym.command: ps["command"] = -1
    if roles & ALARM_ROLES: ps["alarm"] = 0
    if sym.level: ps["level"] = 50
    return ps

def symbol_view(sym):
    p = dict(DEFAULTS)
    c = colors(sym, p)
    roles = sym.roles
    custom, cfg = {}, {}
    if roles & {"body", "head"}:  custom["body"] = c["body"]; cfg["custom.body"] = expr(BODY_EXPR)
    if "head" in roles:           custom["head"] = c["head"]; cfg["custom.head"] = expr(HEAD_EXPR)
    if "shell" in roles:          custom["shell"] = c["shell"]; cfg["custom.shell"] = expr(SHELL_EXPR)
    if roles & ALARM_ROLES:
        custom["line"] = c["line"]; cfg["custom.line"] = expr(ALARM_EXPR)
        custom["lw"] = r3(c["lw"])
        cfg["custom.lw"] = expr(f"if({{view.params.alarm}} > 0, {r3(W_ALARM * sym.k)}, {r3(W_OUTLINE * sym.k)})")
    if sym.level:
        custom["lvl"] = 0.5; cfg["custom.lvl"] = expr("max(0, min(100, {view.params.level})) / 100.0")
    params = sym_params(sym)
    for k in params: cfg[f"params.{k}"] = {"paramDirection": "input", "persistent": True}

    elements, ecfg = [], {}
    for i, e in enumerate(sym.elems):
        fill, stroke, sw, dash = resolve(e, sym, c, p)
        el = {"type": e.kind, "name": f"{e.role}{i}", **geom(e, sym, p), "fill": {"paint": fill}, "stroke": {"paint": stroke, "width": r3(sw)}}
        if dash: el["stroke"]["dasharray"] = dash
        elements.append(el)
        base = f"props.elements[{i}]"
        if e.role in FILL_ROLE: ecfg[f"{base}.fill.paint"] = prop(f"view.custom.{FILL_ROLE[e.role]}")
        if e.role in ALARM_ROLES:
            ecfg[f"{base}.stroke.paint"] = prop("view.custom.line")
            ecfg[f"{base}.stroke.width"] = prop("view.custom.lw")
        if e.role == "level":
            a = e.a
            ecfg[f"{base}.y"] = expr(f"{a['y']} + {a['h']} * (1 - {{view.custom.lvl}})")
            ecfg[f"{base}.height"] = expr(f"{a['h']} * {{view.custom.lvl}}")

    w, h = sym.size
    drawing = {"type": "ia.shapes.svg", "version": 0, "meta": {"name": "Symbol"},
               "position": {"x": 0, "y": 0, "width": 1, "height": 1},
               "props": {"viewBox": f"0 0 {sym.vb[0]} {sym.vb[1]}", "preserveAspectRatio": "xMidYMid meet", "elements": elements}}
    if ecfg: drawing["propConfig"] = ecfg
    children = [drawing]
    if sym.name in BUBBLES:   # ISA tag letters / loop number overlaid with EFC text classes
        params["letters"] = "FIC"; params["number"] = "101"
        cfg["params.letters"] = {"paramDirection": "input", "persistent": True}
        cfg["params.number"] = {"paramDirection": "input", "persistent": True}
        for nm, y, cls, src in (("Letters", 0.22, "Text/TagName Text/Mod/Center Text/Mod/NoWrap", "letters"),
                                ("Number", 0.52, "Text/Caption Text/Color/Default Text/Mod/Center Text/Mod/NoWrap", "number")):
            children.append({"type": "ia.display.label", "version": 0, "meta": {"name": nm},
                             "position": {"x": 0.1, "y": y, "width": 0.8, "height": 0.26},
                             "props": {"text": params[src], "style": {"classes": cls}},
                             "propConfig": {"props.text": prop(f"view.params.{src}")}})
    view = {"custom": custom, "params": params, "propConfig": cfg,
            "props": {"defaultSize": {"width": w, "height": h}},
            "root": {"type": "ia.container.coord", "version": 0, "meta": {"name": "root"},
                     "props": {"mode": "percent"}, "children": children}}
    return view

# ------------------------------------------------------------------ packaging
def resource_json(files):
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return json.dumps({"scope": "G", "version": 1, "restricted": False, "overridable": True, "files": files,
                       "attributes": {"lastModification": {"actor": "build.py", "timestamp": ts}}}, indent=2)

def write_view(z, path, view):
    z.writestr(f"{BASE}/views/{path}/view.json", json.dumps(view, indent=2))
    z.writestr(f"{BASE}/views/{path}/resource.json", resource_json(["view.json"]))

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    names = [s.name for s in SYMS]
    assert len(names) == len(set(names)), "duplicate symbol names"
    with zipfile.ZipFile(os.path.join(OUT, f"{PROJECT}.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps({"title": PROJECT, "description": "EFC ISA P&ID symbol library v2 (generated). Parent: EFC_Styles",
                                               "parent": "EFC_Styles", "enabled": True, "inheritable": True}, indent=2))
        for s in SYMS:
            write_view(z, f"PID/{s.cat}/{s.name}", symbol_view(s))
            d = os.path.join(OUT, "svg", s.cat); os.makedirs(d, exist_ok=True)
            open(os.path.join(d, f"{s.name}.svg"), "w").write(svg(s))
        for path, view in templates.all_views(SYMS).items():
            write_view(z, path, view)
    build_preview(); build_index()
    print(f"{len(SYMS)} symbols")

def build_index():
    rows = ["| View path | Size @1080p | Params | Description |", "|---|---|---|---|"]
    for s in SYMS:
        ps = list(sym_params(s)) + (["letters", "number"] if s.name in BUBBLES else [])
        rows.append(f"| `PID/{s.cat}/{s.name}` | {s.size[0]}×{s.size[1]} | {', '.join(ps) or '—'} | {s.desc} |")
    open(os.path.join(OUT, "symbol_index.md"), "w").write("\n".join(rows) + "\n")

def build_preview():
    parts = ["<!doctype html><html><head><meta charset='utf-8'><title>P&ID Symbols v2</title><style>",
             "body{background:#D9D9D9;font-family:'Noto Sans',Arial,sans-serif;margin:0;color:#1F1F1F}",
             "h2{font-size:20px;margin:0 0 8px}.sec{background:#E6E6E6;border:1px solid #A6A6A6;margin:10px;padding:10px;border-radius:3px}",
             ".g{display:flex;flex-wrap:wrap;gap:6px}.it{width:118px;display:flex;flex-direction:column;align-items:center;gap:4px}",
             ".box{height:84px;display:flex;align-items:center;justify-content:center}.n{font-size:11px;text-align:center;word-break:break-all}",
             ".bub{position:relative}.bub span{position:absolute;left:0;right:0;text-align:center;font-weight:700;font-size:12px}",
             "</style></head><body>"]
    def item(s, p=None, label=None, px=None):
        w, h = s.size
        scale = min(1.5, 80 / max(w, h)) if px is None else px / w
        sv = svg(s, p, px=round(w * scale))
        if s.name in BUBBLES:
            hh = round(h * scale)
            sv = (f"<div class='bub' style='width:{round(w*scale)}px;height:{hh}px'>{sv}"
                  f"<span style='top:{hh*0.24}px'>FIC</span><span style='top:{hh*0.53}px;font-weight:400;font-size:11px'>101</span></div>")
        return f"<div class='it'><div class='box'>{sv}</div><div class='n'>{html.escape(label or s.name)}</div></div>"
    by = {s.name: s for s in SYMS}
    demo = []
    for st, lab in ((0, "stopped"), (1, "running"), (2, "transition"), (3, "fault")):
        demo.append(item(by["Pump_Centrifugal"], {"state": st}, f"state={st} {lab}"))
    for al in (1, 2, 3, 4):
        demo.append(item(by["Pump_Centrifugal"], {"state": 1, "alarm": al}, f"alarm={al}"))
    demo.append(item(by["Valve_Control"], {"state": 0, "command": 1}, "cmd open, body closed"))
    demo.append(item(by["Valve_MOV"], {"state": 2, "command": 0}, "cmd close, travelling"))
    for lv in (15, 60, 95):
        demo.append(item(by["Tank_ConeRoof"], {"level": lv}, f"level={lv}"))
    demo.append(item(by["Tank_Cryogenic"], {"level": 70, "alarm": 3}, "level 70, alarm 3"))
    parts.append(f"<div class='sec'><h2>Parameter states</h2><div class='g'>{''.join(demo)}</div></div>")
    for cat in CATEGORIES:
        its = "".join(item(s, {"state": 1} if s.cat in ("Rotating",) else None) for s in SYMS if s.cat == cat)
        parts.append(f"<div class='sec'><h2>{cat} ({sum(1 for s in SYMS if s.cat == cat)})</h2><div class='g'>{its}</div></div>")
    parts.append("</body></html>")
    open(os.path.join(OUT, "preview.html"), "w").write("".join(parts))

if __name__ == "__main__":
    build()
